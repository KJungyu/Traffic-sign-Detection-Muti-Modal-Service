import os
from model import model
from dataset import yaml_file_path
from util import visualize_training_curves
from ultralytics import YOLO

def run_training():
    results = model.train(
        data=yaml_file_path,
        epochs=50,
        imgsz=640,
        patience=20,
        batch=16,
        optimizer='AdamW',
        lr0=0.001,
        lrf=0.2,
        dropout=0.1
    )

    post_training_files_path = '/workspace/ckYolo/runs/detect/train'
    best_model_path = os.path.join(post_training_files_path, 'weights/best.pt')

    best_model = YOLO(best_model_path)
    metrics = best_model.val(split='val')
    print(f"📊 Validation metrics: {metrics}")

    visualize_training_curves(post_training_files_path)
