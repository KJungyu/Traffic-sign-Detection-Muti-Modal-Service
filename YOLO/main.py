import argparse

def main():
    parser = argparse.ArgumentParser(description="YOLO 표지판 탐지 파이프라인")
    parser.add_argument("--mode", type=str, choices=["train", "infer", "check_data"], required=True, help="실행 모드")
    args = parser.parse_args()

    if args.mode == "train":
        from train import run_training
        run_training()
    elif args.mode == "infer":
        from infer import run_inference
        run_inference()
    elif args.mode == "check_data":
        from dataset import check_dataset_info
        check_dataset_info()

if __name__ == "__main__":
    main()
