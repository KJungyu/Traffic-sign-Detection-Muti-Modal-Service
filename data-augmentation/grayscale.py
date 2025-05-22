# GrayScale 데이터 증강
import os
from PIL import Image
import shutil

input_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\images'
input_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\labels'

output_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\images_grayscale'
output_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\labels_grayscale'

os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_label_dir, exist_ok=True)

image_files = [f for f in os.listdir(input_image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

for img_name in image_files:
    base_name = os.path.splitext(img_name)[0]
    label_name = base_name + '.txt'
    label_path = os.path.join(input_label_dir, label_name)

    if not os.path.exists(label_path):
        print(f"라벨 파일 없음: {label_name}")
        continue

    img_path = os.path.join(input_image_dir, img_name)
    img = Image.open(img_path).convert("RGB")

    gray_img = img.convert("L").convert("RGB")
    gray_img_name = f"{base_name}_gray.jpg"
    gray_label_name = f"{base_name}_gray.txt"

    gray_img.save(os.path.join(output_image_dir, gray_img_name))
    shutil.copyfile(label_path, os.path.join(output_label_dir, gray_label_name))

    print(f"변환 완료: {gray_img_name}")

print("Grayscale 증강 및 라벨 복사 완료")
