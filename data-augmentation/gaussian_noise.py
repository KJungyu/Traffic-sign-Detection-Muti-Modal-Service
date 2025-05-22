import os
import shutil
import cv2
import numpy as np

# [1] 경로 설정
input_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\7.section_end\images'
input_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\7.section_end\labels'

output_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\7.section_end\images_gaussian_noise'
output_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\7.section_end\labels_gaussian_noise'

os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_label_dir, exist_ok=True)

# [2] 노이즈 함수 정의
def add_gaussian_noise(image, mean=0, std=15):
    """이미지에 가우시안 노이즈 추가"""
    noise = np.random.normal(mean, std, image.shape).astype(np.uint8)
    noisy_img = cv2.add(image, noise)
    return noisy_img

# [3] 이미지 파일 순회
image_files = [f for f in os.listdir(input_image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

for img_name in image_files:
    base_name = os.path.splitext(img_name)[0]
    label_name = base_name + '.txt'
    label_path = os.path.join(input_label_dir, label_name)

    if not os.path.exists(label_path):
        print("라벨 없음: {label_name}")
        continue

    # 이미지 읽기
    img_path = os.path.join(input_image_dir, img_name)
    img = cv2.imread(img_path)

    # 가우시안 노이즈 추가
    noisy_img = add_gaussian_noise(img)

    # 저장할 이름 설정
    new_img_name = f"{base_name}_noise.jpg"
    new_label_name = f"{base_name}_noise.txt"

    # 이미지 저장
    cv2.imwrite(os.path.join(output_image_dir, new_img_name), noisy_img)

    # 라벨 복사
    shutil.copyfile(label_path, os.path.join(output_label_dir, new_label_name))

    print("처리 완료: {new_img_name}")

print("가우시안 노이즈 증강 및 라벨 복사 완료")
