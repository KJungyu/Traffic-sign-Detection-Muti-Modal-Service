from PIL import Image
import os
import random

def crop_and_adjust_bbox(yolo_lines, crop_left, crop_top, crop_w, crop_h, img_w, img_h, min_visibility=0.5):
    new_lines = []
    for line in yolo_lines:
        parts = line.strip().split()
        cls = int(parts[0])
        x, y, w, h = map(float, parts[1:5])
        
        # 절대 좌표로 변환
        x_abs = x * img_w
        y_abs = y * img_h
        w_abs = w * img_w
        h_abs = h * img_h
        
        # bbox의 경계 계산
        x_min = x_abs - w_abs/2
        y_min = y_abs - h_abs/2
        x_max = x_abs + w_abs/2
        y_max = y_abs + h_abs/2
        
        # 크롭 영역과의 교차 영역 계산
        inter_x_min = max(x_min, crop_left)
        inter_y_min = max(y_min, crop_top)
        inter_x_max = min(x_max, crop_left + crop_w)
        inter_y_max = min(y_max, crop_top + crop_h)
        
        # 교차 영역이 없으면 스킵
        if inter_x_min >= inter_x_max or inter_y_min >= inter_y_max:
            continue
            
        # 객체의 크롭 영역 내 가시 비율 계산
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        box_area = (x_max - x_min) * (y_max - y_min)
        visibility = inter_area / box_area
        
        # 최소 가시성 기준 미달 시 스킵
        if visibility < min_visibility:
            continue
            
        # 크롭 영역 기준으로 좌표 재계산
        x_new = ((inter_x_min + inter_x_max) / 2 - crop_left) / crop_w
        y_new = ((inter_y_min + inter_y_max) / 2 - crop_top) / crop_h
        w_new = (inter_x_max - inter_x_min) / crop_w
        h_new = (inter_y_max - inter_y_min) / crop_h
        
        # 좌표가 0~1 범위를 벗어나면 조정
        x_new = max(0, min(1, x_new))
        y_new = max(0, min(1, y_new))
        w_new = max(0, min(1, w_new))
        h_new = max(0, min(1, h_new))
        
        new_lines.append(f"{cls} {x_new:.6f} {y_new:.6f} {w_new:.6f} {h_new:.6f}")
    
    return new_lines

def generate_640_crop_variants(img_w, img_h, crop_size=640, num_crops=4):
    """640x640 고정 크기 랜덤 크롭 생성"""
    variants = []

    # 중앙 크롭
    center_left = max(0, (img_w - crop_size) // 2)
    center_top = max(0, (img_h - crop_size) // 2)
    variants.append((center_left, center_top, crop_size, crop_size, 'center'))

    # 랜덤 크롭
    for i in range(num_crops - 1):
        left = random.randint(0, max(0, img_w - crop_size))
        top = random.randint(0, max(0, img_h - crop_size))
        variants.append((left, top, crop_size, crop_size, f'random{i+1}'))

    return variants


# 메인 로직
input_image_dir = '/kaggle/input/horn-dataset/3.horn/images'
input_label_dir = '/kaggle/input/horn-dataset/3.horn/labels'
output_image_dir = 'horn-dataset/3.horn/images_cropped'
output_label_dir = 'horn-dataset/3.horn/labels_cropped'

os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_label_dir, exist_ok=True)

for img_name in os.listdir(input_image_dir):
    if not img_name.endswith(('.jpg', '.png')):
        continue
        
    base_name = os.path.splitext(img_name)[0]
    img_path = os.path.join(input_image_dir, img_name)
    label_path = os.path.join(input_label_dir, base_name + '.txt')
    
    if not os.path.exists(label_path):
        continue
        
    img = Image.open(img_path)
    img_w, img_h = img.size
    
    # 라벨 로드
    with open(label_path, 'r') as f:
        yolo_lines = f.readlines()
    
    # 다양한 크롭 영역 생성
    crop_variants = generate_crop_variants(img_w, img_h)
    
    # 각 크롭 영역에 대해 처리
    for crop_left, crop_top, crop_w, crop_h, crop_type in crop_variants:
        # 크롭
        crop_box = (crop_left, crop_top, crop_left + crop_w, crop_top + crop_h)
        cropped_img = img.crop(crop_box)
        
        # 저장 경로
        crop_name = f"{base_name}_{crop_type}_crop.jpg"
        cropped_img.save(os.path.join(output_image_dir, crop_name))
        
        # 라벨 조정
        new_lines = crop_and_adjust_bbox(
            yolo_lines, crop_left, crop_top, crop_w, crop_h, img_w, img_h, min_visibility=0.5
        )
        
        if new_lines:  # 유효한 객체가 하나 이상 있는 경우만 라벨 파일 생성
            with open(os.path.join(output_label_dir, f"{base_name}_{crop_type}_crop.txt"), 'w') as f:
                f.write('\n'.join(new_lines))
        else:
            # 객체가 없는 크롭 이미지 삭제
            os.remove(os.path.join(output_image_dir, crop_name))

print("✅ 다양한 크롭 + bbox 좌표 조정 완료")

