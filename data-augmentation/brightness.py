# 이미지 밝기 조절 데이터 증강
import os
from PIL import Image, ImageEnhance
import shutil

# 경로 설정
input_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\images'
input_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\labels'

output_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\images_brightness_aug'
output_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\labels_brightness_aug'

os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_label_dir, exist_ok=True)

brightness_factors = [0.5, 1.5]

image_files = [f for f in os.listdir(input_image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

for img_name in image_files:
    base_name = os.path.splitext(img_name)[0]
    label_name = base_name + '.txt'
    label_path = os.path.join(input_label_dir, label_name)

    if not os.path.exists(label_path):
        print(f"라벨 파일 없음: {label_name}")
        continue

    img = Image.open(os.path.join(input_image_dir, img_name))

    for factor in brightness_factors:
        enhancer = ImageEnhance.Brightness(img)
        img_enhanced = enhancer.enhance(factor)

        suffix = f"bright{int(factor * 10)}"
        new_img_name = f"{base_name}_{suffix}.jpg"
        new_label_name = f"{base_name}_{suffix}.txt"

        img_enhanced.save(os.path.join(output_image_dir, new_img_name))
        shutil.copyfile(label_path, os.path.join(output_label_dir, new_label_name))

print("이미지 + 라벨 복사 완료")
