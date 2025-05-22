## 추가 데이터 전송으로 기존 데이터셋 파일과 결합

import os
import shutil
import yaml

source_dir = r'C:\Users\a6351\Downloads\japan-roadsign-ver.2.2.v2i.yolov11\split_by_class\class_5'

target_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class\7.section_end'
os.makedirs(os.path.join(target_dir, 'images'), exist_ok=True)
os.makedirs(os.path.join(target_dir, 'labels'), exist_ok=True)


old_class = "5"
new_class = "7"


src_images = os.path.join(source_dir, 'images')
dst_images = os.path.join(target_dir, 'images')

for fname in os.listdir(src_images):
    if fname.endswith(('.jpg', '.jpeg', '.png')):
        shutil.copy(os.path.join(src_images, fname), os.path.join(dst_images, fname))


src_labels = os.path.join(source_dir, 'labels')
dst_labels = os.path.join(target_dir, 'labels')

for fname in os.listdir(src_labels):
    if not fname.endswith('.txt'):
        continue

    src_path = os.path.join(src_labels, fname)
    dst_path = os.path.join(dst_labels, fname)

    new_lines = []
    with open(src_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if parts[0] == old_class:
                parts[0] = new_class
            new_lines.append(' '.join(parts))

    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

print("이미지 및 라벨 복사 완료 (클래스 번호 변경 포함)")


yaml_path = os.path.join(target_dir.replace('7.section_end', '0.handcar'), 'data.yaml') 
with open(yaml_path, 'r', encoding='utf-8') as f:
    data_yaml = yaml.safe_load(f)

if 'section_end' not in data_yaml['names']:
    data_yaml['names'].append('section_end')
    data_yaml['nc'] = len(data_yaml['names'])

 
    split_root = os.path.dirname(target_dir)
    for folder in os.listdir(split_root):
        folder_path = os.path.join(split_root, folder)
        if os.path.isdir(folder_path):
            yaml_save_path = os.path.join(folder_path, 'data.yaml')
            with open(yaml_save_path, 'w', encoding='utf-8') as f:
                yaml.dump(data_yaml, f, allow_unicode=True)
    print("모든 클래스 폴더에 data.yaml 업데이트 완료")
else:
    print("'section_end' 클래스는 이미 존재함. yaml 수정 안함.")
