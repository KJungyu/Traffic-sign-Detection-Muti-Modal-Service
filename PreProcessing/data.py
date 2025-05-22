# 데이터 전처리 과정 (데이터 셋 분할)


import os
import shutil
import yaml

def split_by_class(source_dir, output_root, data_yaml_path):
    with open(data_yaml_path, 'r') as f:
        yaml_data = yaml.safe_load(f)

    class_names = yaml_data.get('names', [])
    print(f"\n총 클래스 수: {len(class_names)} - {class_names}")

    for class_idx, class_name in enumerate(class_names):
        print(f"\n 클래스 {class_idx} ({class_name}) 추출 중")

        class_output_dir = os.path.join(output_root, f'class_{class_idx}')
        os.makedirs(class_output_dir, exist_ok=True)

        image_dst_dir = os.path.join(class_output_dir, 'images')
        label_dst_dir = os.path.join(class_output_dir, 'labels')
        os.makedirs(image_dst_dir, exist_ok=True)
        os.makedirs(label_dst_dir, exist_ok=True)

        new_yaml = {
            'names': class_names,
            'nc': len(class_names),
            'train': image_dst_dir,
            'val': image_dst_dir,
            'test': image_dst_dir,
        }
        with open(os.path.join(class_output_dir, 'data.yaml'), 'w') as f:
            yaml.dump(new_yaml, f, sort_keys=False)

        for split in ['train', 'valid', 'test']:
            image_src_dir = os.path.join(source_dir, split, 'images')
            label_src_dir = os.path.join(source_dir, split, 'labels')

            if not os.path.exists(image_src_dir) or not os.path.exists(label_src_dir):
                print(f"  {split} 경로 없으면 점프")
                continue

            for label_file in os.listdir(label_src_dir):
                if not label_file.endswith('.txt'):
                    continue

                label_path = os.path.join(label_src_dir, label_file)
                with open(label_path, 'r') as f:
                    lines = f.readlines()

                # 해당 클래스만 남기고 클래스 번호는 유지
                filtered_lines = [
                    line
                    for line in lines
                    if line.strip() and int(line.strip().split()[0]) == class_idx
                ]

                if filtered_lines:
                    image_base = os.path.splitext(label_file)[0]
                    possible_exts = ['.jpg', '.jpeg', '.png', '.bmp']
                    image_found = False
                    for ext in possible_exts:
                        image_path = os.path.join(image_src_dir, image_base + ext)
                        if os.path.exists(image_path):
                            shutil.copy2(image_path, os.path.join(image_dst_dir, image_base + ext))
                            image_found = True
                            break
                    if not image_found:
                        print(f" 이미지 누락: {image_base}")
                        continue

                    with open(os.path.join(label_dst_dir, label_file), 'w') as f:
                        f.writelines(filtered_lines)

        print(f" 클래스 {class_idx} 처리 완료 → {class_output_dir}")

if __name__ == "__main__":
    source_directory = r"C:\Users\a6351\Downloads\Japan roadsign second 2.v3i.yolov8"
    data_yaml_path = os.path.join(source_directory, "data.yaml")
    output_directory = os.path.join(source_directory, "split_by_class")

    split_by_class(source_directory, output_directory, data_yaml_path)
