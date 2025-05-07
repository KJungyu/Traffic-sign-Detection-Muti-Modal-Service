import os
import cv2
import randomcon
import pandas as pd
import matplotlib.pyplot as plt
from ultralytics import YOLO

# ✅ best.pt 경로에서 모델 로드
best_model_path = '/workspace/ckYolo/runs/detect/train2/weights/best.pt'
model = YOLO(best_model_path)

def run_inference():
    test_dir = '/workspace/Ckdataset/test/images'
    output_dir = '/workspace/ckYolo/infer_results'
    os.makedirs(output_dir, exist_ok=True)

    image_files = [f for f in os.listdir(test_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"📸 Found {len(image_files)} test images.")

    # 추론 결과 저장용
    predictions = []

    # 3개 이미지만 무작위 시각화용으로 추출
    sample_images = random.sample(image_files, min(3, len(image_files)))

    for img_file in image_files:
        img_path = os.path.join(test_dir, img_file)
        results = model.predict(source=img_path, imgsz=640, conf=0.7, verbose=False)
        result = results[0]

        # 시각화 이미지 저장
        plotted_img = result.plot(line_width=2)
        save_path = os.path.join(output_dir, f"pred_{img_file}")
        cv2.imwrite(save_path, plotted_img)

        # 결과 추출
        boxes = result.boxes
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            predictions.append({
                "image": img_file,
                "class": cls,
                "confidence": round(conf, 4),
                "x1": int(xyxy[0]),
                "y1": int(xyxy[1]),
                "x2": int(xyxy[2]),
                "y2": int(xyxy[3])
            })

        # 무작위 3장만 시각화
        if img_file in sample_images:
            img_rgb = cv2.cvtColor(plotted_img, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(10, 8))
            plt.imshow(img_rgb)
            plt.title(f"Detected: {img_file}", fontsize=14)
            plt.axis('off')
            plt.tight_layout()
            plt.show()

    # CSV로 저장
    csv_path = os.path.join(output_dir, 'inference_results.csv')
    pd.DataFrame(predictions).to_csv(csv_path, index=False)
    print(f"✅ Inference results saved to CSV: {csv_path}")
