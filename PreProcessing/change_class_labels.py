## 데이터 레이블 수정

import os
import yaml
import shutil

class_mapping = {
    'handcar': {3: 0},
    'bike': {0: 1},
    'car': {13: 2},
    'horn': {14: 3},
    'no_crossing': {4: 4},
    'two_seater': {11: 5},
    'start': {9: 8}
}

new_class_names = {
    0: 'handcar',
    1: 'bike',
    2: 'car',
    3: 'horn',
    4: 'no_crossing',
    5: 'two_seater',
    8: 'start'
}

root_dir = r'C:\Users\a6351\OneDrive\Desktop\Japan roadsign second 2.v3i.yolov8\split_by_class'

for folder_name, label_map in class_mapping.items():
    label_dir = os.path.join(root_dir, folder_name, 'labels')
    if not os.path.exists(label_dir):
        print(f"라벨 폴더 없음: {label_dir}")
        continue

    for filename in os.listdir(label_dir):
        if not filename.endswith('.txt'):
            continue

        file_path = os.path.join(label_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            old_class = int(parts[0])
            new_class = label_map.get(old_class, old_class)
            parts[0] = str(new_class)
            new_lines.append(' '.join(parts))

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))

        print(f"클래스 번호 변경 완료: {file_path}")

sorted_class_names = [name for _, name in sorted(new_class_names.items())]
yaml_content = {
    'names': sorted_class_names,
    'nc': len(sorted_class_names),
    'train': 'images/train',
    'val': 'images/val',
    'test': 'images/test'
}

temp_yaml_path = os.path.join(root_dir, 'temp_data.yaml')
with open(temp_yaml_path, 'w', encoding='utf-8') as f:
    yaml.dump(yaml_content, f, allow_unicode=True)
print(f"data.yaml 생성 완료 -> {temp_yaml_path}")

for folder in class_mapping.keys():
    dest_path = os.path.join(root_dir, folder, 'data.yaml')
    shutil.copy(temp_yaml_path, dest_path)
    print(f"복사 완료 -> {dest_path}")

os.remove(temp_yaml_path)
print("임시 파일 제거 완료")
