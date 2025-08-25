import sys, os, cv2, math
from ultralytics import YOLO

# ====== 설정(정확도 최우선) ======
MODEL_PATH    = "yolov8x.pt"   # 최대 성능
DEFAULT_CONF  = 0.15           # 낮출수록 더 많이 잡음(오탐↑). 0.10~0.25 권장
IMG_SIZE      = 1536           # 모델 입력 크기(클수록 정확↑, 속도/메모리↓)
TILE_SIZE     = 1024           # 타일 한 변(작게 보이는 사람 잡기)
OVERLAP       = 0.40           # 타일 겹침 비율(0.3~0.5 권장)
USE_TTA       = True           # test-time augmentation(ultralytics 내부 flip/scale)
MULTI_SCALES  = [1.0, 1.5, 2.0]# 원본, 1.5배, 2배 업샘플 후 추론
WBF_IOU       = 0.55           # WBF 병합 IoU(0.5~0.6 권장)
DRAW_RADIUS_K = 0.22           # 머리 원 반경 비
# =================================

def iou_xyxy(a, b):
    ax1, ay1, ax2, ay2 = a; bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0: return 0.0
    area_a = max(1e-9, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1e-9, (bx2 - bx1) * (by2 - by1))
    return inter / (area_a + area_b - inter)

def wbf_merge(boxes, scores, iou_thr=WBF_IOU):
    """간단 WBF: IoU가 임계 이상인 박스들 가중평균(가중치=score)으로 병합"""
    if not boxes: return [], []
    idxs = sorted(range(len(boxes)), key=lambda i: scores[i], reverse=True)
    used = [False]*len(boxes)
    merged_boxes, merged_scores = [], []
    for i in idxs:
        if used[i]: continue
        group, group_scores = [boxes[i]], [scores[i]]
        used[i] = True
        for j in idxs:
            if used[j]: continue
            if iou_xyxy(boxes[i], boxes[j]) >= iou_thr:
                group.append(boxes[j]); group_scores.append(scores[j]); used[j] = True
        # 가중 평균
        w = sum(group_scores)
        xs1 = sum(b[0]*s for b,s in zip(group, group_scores))/w
        ys1 = sum(b[1]*s for b,s in zip(group, group_scores))/w
        xs2 = sum(b[2]*s for b,s in zip(group, group_scores))/w
        ys2 = sum(b[3]*s for b,s in zip(group, group_scores))/w
        merged_boxes.append([int(xs1), int(ys1), int(xs2), int(ys2)])
        merged_scores.append(max(group_scores))  # 보수적으로 최대 점수 유지
    return merged_boxes, merged_scores

def draw_head_circles(img, boxes):
    for (x1, y1, x2, y2) in boxes:
        cx = int((x1 + x2) / 2)
        h  = max(1, int(y2 - y1))
        cy = int(y1 + 0.18 * h)
        r  = max(6, int(DRAW_RADIUS_K * h))
        cv2.circle(img, (cx, cy), r, (0, 0, 255), 2)

def infer_tile(model, tile_bgr, conf):
    res = model(
        tile_bgr,
        imgsz=min(IMG_SIZE, max(tile_bgr.shape[:2])),
        conf=conf,
        verbose=False,
        augment=USE_TTA
    )[0]
    boxes, scores = [], []
    for b in res.boxes:
        if int(b.cls.item()) == 0:  # person
            x1, y1, x2, y2 = map(float, b.xyxy[0].tolist())
            boxes.append([x1, y1, x2, y2])
            scores.append(float(b.conf.item()))
    return boxes, scores

def tiled_inference_single_scale(model, img_bgr, conf):
    H, W = img_bgr.shape[:2]
    step = int(TILE_SIZE * (1.0 - OVERLAP))
    if step <= 0: raise ValueError("OVERLAP이 너무 큽니다.")
    all_boxes, all_scores = [], []

    # 내부 타일 루프
    def process_window(x0, y0, x1, y1):
        tile = img_bgr[y0:y1, x0:x1]
        boxes, scores = infer_tile(model, tile, conf)
        for (bx1, by1, bx2, by2), sc in zip(boxes, scores):
            gx1, gy1 = bx1 + x0, by1 + y0
            gx2, gy2 = bx2 + x0, by2 + y0
            gx1, gy1 = max(0, gx1), max(0, gy1)
            gx2, gy2 = min(W - 1, gx2), min(H - 1, gy2)
            if gx2 > gx1 and gy2 > gy1:
                all_boxes.append([gx1, gy1, gx2, gy2]); all_scores.append(sc)

    # 메인 그리드
    for y0 in range(0, max(1, H - TILE_SIZE + 1), step):
        for x0 in range(0, max(1, W - TILE_SIZE + 1), step):
            process_window(x0, y0, min(x0 + TILE_SIZE, W), min(y0 + TILE_SIZE, H))
    # 오른쪽/아래 가장자리 커버
    if (W - TILE_SIZE) % step != 0:
        x0 = max(0, W - TILE_SIZE)
        for y0 in range(0, max(1, H - TILE_SIZE + 1), step):
            process_window(x0, y0, W, min(y0 + TILE_SIZE, H))
    if (H - TILE_SIZE) % step != 0:
        y0 = max(0, H - TILE_SIZE)
        for x0 in range(0, max(1, W - TILE_SIZE + 1), step):
            process_window(x0, y0, min(x0 + TILE_SIZE, W), H)

    return all_boxes, all_scores

def multi_scale_inference(model, img_bgr, conf):
    H, W = img_bgr.shape[:2]
    all_boxes, all_scores = [], []
    for s in MULTI_SCALES:
        if s == 1.0:
            up = img_bgr
        else:
            up = cv2.resize(img_bgr, (int(W*s), int(H*s)), interpolation=cv2.INTER_CUBIC)
        boxes, scores = tiled_inference_single_scale(model, up, conf)
        # 스케일 원복
        if s != 1.0:
            inv = 1.0 / s
            for i in range(len(boxes)):
                boxes[i] = [boxes[i][0]*inv, boxes[i][1]*inv, boxes[i][2]*inv, boxes[i][3]*inv]
        all_boxes.extend(boxes); all_scores.extend(scores)
    # WBF로 최종 병합
    merged_boxes, merged_scores = wbf_merge(all_boxes, all_scores, iou_thr=WBF_IOU)
    return merged_boxes, merged_scores

def main():
    if len(sys.argv) < 2:
        print(f"사용법: python {os.path.basename(__file__)} <이미지경로> [conf(기본={DEFAULT_CONF})]")
        sys.exit(1)

    img_path = sys.argv[1]
    conf = float(sys.argv[2]) if len(sys.argv) >= 3 else DEFAULT_CONF

    img = cv2.imread(img_path)
    if img is None:
        print("이미지 로드 실패:", img_path); sys.exit(1)

    model = YOLO(MODEL_PATH)
    boxes, scores = multi_scale_inference(model, img, conf)

    out = img.copy()
    draw_head_circles(out, boxes)
    count = len(boxes)
    cv2.putText(out, f"People: {count}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 255), 3, cv2.LINE_AA)

    root, ext = os.path.splitext(img_path)
    save_ext = ext if ext.lower() in [".jpg",".jpeg",".png",".bmp"] else ".jpg"
    out_path = f"{root}_out{save_ext}"
    cv2.imwrite(out_path, out)

    print("사람 수:", count)
    print("저장:", out_path)
    print(f"conf={conf}, model={MODEL_PATH}, imgsz={IMG_SIZE}, tile={TILE_SIZE}, overlap={OVERLAP}, TTA={USE_TTA}, scales={MULTI_SCALES}, WBF_IOU={WBF_IOU}")

if __name__ == "__main__":
    main()
