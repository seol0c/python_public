import sys
sys.path.append(r"D:\seolgit\python_packages")

import os
import cv2
import numpy as np
from ultralytics import YOLO
from glob import glob

MODEL_DIR = r"D:\seolgit\python_packages"
IMAGE_DIR = r"C:\Users\seolpc\Desktop\drone"

def detect_people_folder():
    image_paths = glob(os.path.join(IMAGE_DIR, "*.JPG"))
    if not image_paths:
        print("분석할 JPG 파일이 없습니다.")
        return

    summary = {}

    for IMAGE_PATH in image_paths:
        print(f"\n{os.path.basename(IMAGE_PATH)} 분석 중...")

        name, ext = os.path.splitext(IMAGE_PATH)
        OUTPUT_PATH = name + "_2" + ext

        img = cv2.imread(IMAGE_PATH)
        if img is None:
            print(f"이미지를 불러올 수 없습니다: {IMAGE_PATH}")
            continue

        # YOLO 설정
        params = dict(
            imgsz=2048,       # 메모리 절약
            conf=0.003,
            iou=0.9,
            classes=[0],
            agnostic_nms=False,
            save=False,
            verbose=False
        )

        # 1️⃣ yolov8x.pt 모델
        model_a = YOLO(os.path.join(MODEL_DIR, "yolov8x.pt"))
        results_a = model_a.predict(source=img, **params)
        del model_a  # 메모리 확보

        # 2️⃣ yolov8x-seg.pt 모델
        model_b = YOLO(os.path.join(MODEL_DIR, "yolov8x-seg.pt"))
        results_b = model_b.predict(source=img, **params)
        del model_b  # 메모리 확보

        # 결과 병합
        boxes_all = []
        for results in [results_a, results_b]:
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                w, h = x2 - x1, y2 - y1

                if w < 10 or h < 10:
                    continue
                if w > 400 or h > 400:
                    continue
                aspect = h / w if w > 0 else 0
                if aspect > 3 or aspect < 0.3:
                    continue

                boxes_all.append((x1, y1, x2, y2))

        # IoU 중복 제거
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
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # 인원수 표시
        count = len(final_boxes)
        text = f"People: {count}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 2.0
        thickness = 6
        cv2.putText(img, text, (30, img.shape[0] - 50),
                    font, scale, (255, 255, 255), thickness + 2, cv2.LINE_AA)
        cv2.putText(img, text, (30, img.shape[0] - 50),
                    font, scale, (0, 0, 0), thickness, cv2.LINE_AA)

        cv2.imwrite(OUTPUT_PATH, img)
        print(f"{os.path.basename(OUTPUT_PATH)} 저장 완료 (탐지된 사람 수: {count}명)")

        summary[os.path.basename(IMAGE_PATH)] = count

    # 요약 출력
    print("\n==================== 결과 요약 ====================")
    total_people = sum(summary.values())
    for fname, cnt in summary.items():
        print(f"{fname}: {cnt}명")
    print(f"총합: {total_people}명")
    print("===================================================")

if __name__ == "__main__":
    detect_people_folder()
