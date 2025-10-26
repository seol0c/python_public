import sys
sys.path.append(r"D:\seolgit\python_packages")

import os
import cv2
import numpy as np
from ultralytics import YOLO
from glob import glob

# ─────────────────────────────────────────────
# 설정
#  - yolov8x.pt + yolov8x-seg.pt 병합 (Union)
#  - 대상 폴더: C:\Users\seolpc\Desktop\drone
#  - 사각형만 표시
#  - 너무 큰 박스 제거 (400px 이상 필터)
# ─────────────────────────────────────────────
MODEL_DIR = r"D:\seolgit\python_packages"
IMAGE_DIR = r"C:\Users\seolpc\Desktop\drone"

def detect_people_folder():
    model_a = YOLO(os.path.join(MODEL_DIR, "yolov8x.pt"))
    model_b = YOLO(os.path.join(MODEL_DIR, "yolov8x-seg.pt"))

    # 📂 폴더 내 모든 JPG 파일 탐색
    image_paths = glob(os.path.join(IMAGE_DIR, "*.JPG"))
    if not image_paths:
        print("⚠️ 분석할 JPG 파일이 없습니다.")
        return

    for IMAGE_PATH in image_paths:
        print(f"\n▶ {os.path.basename(IMAGE_PATH)} 분석 중...")

        # 결과 파일명 설정
        name, ext = os.path.splitext(IMAGE_PATH)
        OUTPUT_PATH = name + "_2" + ext

        # 이미지 읽기
        img = cv2.imread(IMAGE_PATH)
        if img is None:
            print(f"❌ 이미지를 불러올 수 없습니다: {IMAGE_PATH}")
            continue

        # YOLO 파라미터
        params = dict(
            imgsz=4096,     # 초고해상도
            conf=0.001,     # 민감도 극대화
            iou=0.9,        # 겹침 허용
            classes=[0],    # 사람만
            agnostic_nms=False,
            save=False,
            verbose=False
        )

        # 두 모델로 예측
        results_a = model_a.predict(source=img, **params)
        results_b = model_b.predict(source=img, **params)

        # 결과 병합
        boxes_all = []
        for results in [results_a, results_b]:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2 - x1, y2 - y1

                # ❌ 노이즈 제거 조건
                if w < 10 or h < 10:     # 너무 작은 것 제거
                    continue
                if w > 400 or h > 400:   # 너무 큰 것 제거 (건물/그림자)
                    continue
                aspect = h / w if w > 0 else 0
                if aspect > 3 or aspect < 0.3:  # 지나치게 길거나 넓은 것 제외
                    continue

                boxes_all.append((x1, y1, x2, y2))

        # IoU 기반 중복 제거
        final_boxes = []
        for (x1, y1, x2, y2) in boxes_all:
            overlap = False
            for (fx1, fy1, fx2, fy2) in final_boxes:
                inter_w = max(0, min(x2, fx2) - max(x1, fx1))
                inter_h = max(0, min(y2, fy2) - max(y1, fy1))
                inter_area = inter_w * inter_h
                union_area = (x2 - x1) * (y2 - y1) + (fx2 - fx1) * (fy2 - fy1) - inter_area
                if union_area == 0:
                    continue
                iou = inter_area / union_area
                if iou > 0.4:
                    overlap = True
                    break
            if not overlap:
                final_boxes.append((x1, y1, x2, y2))

        # 사각형 표시
        for (x1, y1, x2, y2) in final_boxes:
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)  # 파란색 테두리

        # 결과 저장
        cv2.imwrite(OUTPUT_PATH, img)
        print(f"✅ {os.path.basename(OUTPUT_PATH)} 저장 완료 (탐지된 사람 수: {len(final_boxes)}명)")

if __name__ == "__main__":
    detect_people_folder()
