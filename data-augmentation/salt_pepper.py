import os
import cv2
import numpy as np
import shutil

# 경로 설정
image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\0.handcar\images'
label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\0.handcar\labels'

output_image_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\0.handcar\images_salt_pepper'
output_label_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\0.handcar\labels_salt_pepper'

os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_label_dir, exist_ok=True)

# Salt and Pepper 노이즈 함수
def add_salt_pepper_noise(image, prob=0.01):
    noisy = image.copy()
    total_pixels = image.size

    # Salt
    num_salt = int(prob * total_pixels)
    coords = [np.random.randint(0, i - 1, num_salt) for i in image.shape[:2]]
    noisy[coords[0], coords[1]] = 255

    # Pepper
    num_pepper = int(prob * total_pixels)
    coords = [np.random.randint(0, i - 1, num_pepper) for i in image.shape[:2]]
    noisy[coords[0], coords[1]] = 0

    return noisy

# 이미지 리스트 순회
for img_name in os.listdir(image_dir):
    if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    base_name = os.path.splitext(img_name)[0]
    label_name = base_name + '.txt'
    label_path = os.path.join(label_dir, label_name)

    if not os.path.exists(label_path):
        print("라벨 없음: {label_name}")
        continue

    # 이미지 읽기 및 노이즈 적용
    img_path = os.path.join(image_dir, img_name)
    image = cv2.imread(img_path)

    noisy_img = add_salt_pepper_noise(image, prob=0.01)

    # 저장 파일명
    new_img_name = f"{base_name}_sp.jpg"
    new_label_name = f"{base_name}_sp.txt"

    # 이미지 저장
    cv2.imwrite(os.path.join(output_image_dir, new_img_name), noisy_img)

    # 라벨 복사
    shutil.copyfile(label_path, os.path.join(output_label_dir, new_label_name))

    print("저장 완료: {new_img_name}, {new_label_name}")

print("Salt and Pepper 증강 및 라벨 복사 완료")
