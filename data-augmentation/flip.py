# 이미지 좌우반전 데이터 증강
import os
from PIL import Image
import shutil

def flip_bbox_x_center(yolo_label_line):
    parts = yolo_label_line.strip().split()
    cls, x, y, w, h = parts
    new_x = str(1 - float(x))  # x_center 좌우 반전
    return f"{cls} {new_x} {y} {w} {h}"

input_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\images'
input_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\labels'
output_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\images_flipped'
output_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\8.start\labels_flipped'

os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_label_dir, exist_ok=True)

image_files = [f for f in os.listdir(input_image_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

for img_name in image_files:
    base_name = os.path.splitext(img_name)[0]
    img_path = os.path.join(input_image_dir, img_name)
    label_path = os.path.join(input_label_dir, base_name + '.txt')

    if not os.path.exists(label_path):
        print(f"라벨 없음: {label_path}")
        continue

    img = Image.open(img_path)
    img_flipped = img.transpose(Image.FLIP_LEFT_RIGHT)

    new_img_name = base_name + '_flipped.jpg'
    new_label_name = base_name + '_flipped.txt'
    img_flipped.save(os.path.join(output_image_dir, new_img_name))

    with open(label_path, 'r') as lf:
        lines = lf.readlines()

    new_lines = [flip_bbox_x_center(line) for line in lines]

    with open(os.path.join(output_label_dir, new_label_name), 'w') as lf:
        lf.write('\n'.join(new_lines))

print("좌우 반전 + 라벨 좌표 조정 완료")
