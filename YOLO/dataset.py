import yaml
import os
from PIL import Image

dataset_path = '/workspace/Ckdataset'
yaml_file_path = os.path.join(dataset_path, 'data.yaml')

def check_dataset_info():
    with open(yaml_file_path, 'r') as file:
        yaml_content = yaml.load(file, Loader=yaml.FullLoader)
        print("📄 YAML Content:")
        print(yaml.dump(yaml_content, default_flow_style=False))

    train_image_path = os.path.join(dataset_path, 'train', 'images')
    validation_image_path = os.path.join(dataset_path, 'valid', 'images')

    num_train_images = 0
    num_valid_images = 0
    train_image_size = set()
    valid_image_size = set()

    for filename in os.listdir(train_image_path):
        if filename.endswith('.jpg'):
            num_train_images += 1
            image_path = os.path.join(train_image_path, filename)
            with Image.open(image_path) as img:
                train_image_size.add(img.size)

    for filename in os.listdir(validation_image_path):
        if filename.endswith('.jpg'):
            num_valid_images += 1
            image_path = os.path.join(validation_image_path, filename)
            with Image.open(image_path) as img:
                valid_image_size.add(img.size)

    print(f"📁 Number of training images: {num_train_images}")
    print(f"📁 Number of validation images: {num_valid_images}")

    if len(train_image_size) == 1:
        print(f"📐 All training images have the same size: {train_image_size.pop()}")
    else:
        print("⚠️ Training images have varying sizes.")

    if len(valid_image_size) == 1:
        print(f"📐 All validation images have the same size: {valid_image_size.pop()}")
    else:
        print("⚠️ Validation images have varying sizes.")
