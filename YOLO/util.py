import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_learning_curve(df, train_loss_col, val_loss_col, title, save_dir=None):
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=df, x='epoch', y=train_loss_col, label='Train Loss', color='#141140', linestyle='-', linewidth=2)
    sns.lineplot(data=df, x='epoch', y=val_loss_col, label='Validation Loss', color='orangered', linestyle='--', linewidth=2)
    plt.title(title)
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_dir:
        filename = title.lower().replace(" ", "_").replace("📦", "").replace("🧠", "").replace("📐", "") + ".png"
        save_path = os.path.join(save_dir, filename)
        plt.savefig(save_path)
        print(f"📊 Plot saved to: {save_path}")
    else:
        plt.show()

def visualize_training_curves(post_training_files_path):
    results_csv_path = os.path.join(post_training_files_path, 'results.csv')
    df = pd.read_csv(results_csv_path)
    df.columns = df.columns.str.strip()

    # ✅ CSV 백업 저장
    save_csv_path = os.path.join(post_training_files_path, 'cleaned_results.csv')
    df.to_csv(save_csv_path, index=False)
    print(f"✅ Cleaned CSV saved to: {save_csv_path}")

    # ✅ 그래프 시각화 및 저장
    plot_learning_curve(df, 'train/box_loss', 'val/box_loss', '📦 Box Loss Learning Curve', post_training_files_path)
    plot_learning_curve(df, 'train/cls_loss', 'val/cls_loss', '🧠 Classification Loss Learning Curve', post_training_files_path)
    plot_learning_curve(df, 'train/dfl_loss', 'val/dfl_loss', '📐 Distribution Focal Loss Learning Curve', post_training_files_path)
