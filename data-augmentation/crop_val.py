from PIL import Image, ImageDraw, ImageFont
import os
import matplotlib.pyplot as plt
import numpy as np

def draw_bboxes(img_path, label_path, output_path=None, color=(255, 0, 0, 180)):
    """이미지에 바운딩 박스를 그리는 함수"""
    # 이미지 열기
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img, 'RGBA')
    width, height = img.size
    
    # 라벨 파일 읽기
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            lines = f.readlines()
            
        # 각 객체에 대해 바운딩 박스 그리기
        for line in lines:
            parts = line.strip().split()
            class_id = parts[0]
            x_center, y_center, w, h = map(float, parts[1:5])
            
            # YOLO 형식(normalized)에서 픽셀 좌표로 변환
            x1 = int((x_center - w/2) * width)
            y1 = int((y_center - h/2) * height)
            x2 = int((x_center + w/2) * width)
            y2 = int((y_center + h/2) * height)
            
            # 바운딩 박스 그리기
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            # 클래스 ID 텍스트 그리기
            text_color = (255, 255, 255)
            draw.rectangle([x1, y1, x1+20, y1+15], fill=color[:3])
            draw.text((x1+5, y1), class_id, fill=text_color)
    
    # 저장 또는 반환
    if output_path:
        img.save(output_path)
    return img

def verify_crop_bboxes(original_img_path, original_label_path, 
                       cropped_img_path, cropped_label_path,
                       crop_params=None, output_dir='verification_images'):
    """원본 이미지와 크롭된 이미지의 바운딩 박스를 시각적으로 비교"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 파일 이름 추출
    base_name = os.path.basename(original_img_path).split('.')[0]
    crop_name = os.path.basename(cropped_img_path).split('.')[0]
    
    # 원본 이미지에 바운딩 박스 그리기
    original_with_bbox = draw_bboxes(original_img_path, original_label_path)
    
    # 크롭된 이미지에 바운딩 박스 그리기
    cropped_with_bbox = draw_bboxes(cropped_img_path, cropped_label_path)
    
    # 원본 이미지에 크롭 영역 표시 (선택 사항)
    if crop_params:
        crop_left, crop_top, crop_w, crop_h = crop_params
        draw = ImageDraw.Draw(original_with_bbox, 'RGBA')
        draw.rectangle(
            [crop_left, crop_top, crop_left + crop_w, crop_top + crop_h],
            outline=(0, 255, 0, 180),
            width=3
        )
    
    # 결과 시각화
    fig, axes = plt.subplots(1, 2, figsize=(15, 7))
    
    # 원본 이미지 표시
    axes[0].imshow(np.array(original_with_bbox))
    axes[0].set_title(f'Original: {base_name}')
    axes[0].axis('off')
    
    # 크롭된 이미지 표시
    axes[1].imshow(np.array(cropped_with_bbox))
    axes[1].set_title(f'Cropped: {crop_name}')
    axes[1].axis('off')
    
    # 저장
    output_path = os.path.join(output_dir, f'{base_name}_vs_{crop_name}_verification.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    return output_path

def verify_all_images(input_image_dir, input_label_dir, 
                    output_image_dir, output_label_dir,
                    crop_params=None, max_samples=5):
    """모든 이미지에 대한 검증 수행 (샘플링)"""
    # 크롭된 이미지 목록
    cropped_images = [f for f in os.listdir(output_image_dir) 
                     if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    # 결과 저장 디렉토리
    verification_dir = 'bbox_verification_results'
    os.makedirs(verification_dir, exist_ok=True)
    
    # 샘플링 (최대 이미지 수 제한)
    if len(cropped_images) > max_samples:
        import random
        cropped_images = random.sample(cropped_images, max_samples)
    
    verification_paths = []
    for cropped_image in cropped_images:
        # 원본 이미지 이름 추출 (크롭된 이미지 이름에서)
        base_name = cropped_image.split('_crop')[0]
        if '_' in base_name:  # 개선된 코드에서의 이름 형식 처리
            parts = base_name.split('_')
            if parts[-1] in ['center', 'random1', 'random2', 'random3']:
                base_name = '_'.join(parts[:-1])
        
        # 파일 경로
        original_img_path = os.path.join(input_image_dir, f"{base_name}.jpg")
        if not os.path.exists(original_img_path):
            original_img_path = os.path.join(input_image_dir, f"{base_name}.png")
        
        original_label_path = os.path.join(input_label_dir, f"{base_name}.txt")
        cropped_img_path = os.path.join(output_image_dir, cropped_image)
        cropped_label_path = os.path.join(output_label_dir, 
                                        os.path.splitext(cropped_image)[0] + '.txt')
        
        # 검증 수행
        if os.path.exists(original_img_path) and os.path.exists(cropped_label_path):
            output_path = verify_crop_bboxes(
                original_img_path, original_label_path,
                cropped_img_path, cropped_label_path,
                crop_params, verification_dir
            )
            verification_paths.append(output_path)
    
    return verification_paths

# 실행 코드
if __name__ == "__main__":
    # 디렉토리 설정
    input_image_dir = '/kaggle/input/horn-dataset/3.horn/images'
    input_label_dir = '/kaggle/input/horn-dataset/3.horn/labels'
    output_image_dir = '/kaggle/working/horn-dataset/3.horn/images_cropped'
    output_label_dir = '/kaggle/working/horn-dataset/3.horn/labels_cropped'
    
    # 원래 사용한 크롭 매개변수
    crop_params = (100, 50, 400, 300)  # left, top, width, height
    
    # 검증 실행 (최대 10개 이미지 샘플링)
    verification_paths = verify_all_images(
        input_image_dir, input_label_dir,
        output_image_dir, output_label_dir,
        crop_params, max_samples=10
    )
    
    print(f"✅ 검증 이미지가 '{os.path.abspath('bbox_verification_results')}' 에 저장되었습니다.")
    print(f"✅ 총 {len(verification_paths)}개의 검증 이미지가 생성되었습니다.")
    
    # 첫 번째 검증 이미지 표시 (선택 사항)
    if verification_paths:
        img = Image.open(verification_paths[0])
        plt.figure(figsize=(15, 7))
        plt.imshow(np.array(img))
        plt.axis('off')
        plt.title("검증 예시")
        plt.show()
