import argparse
from train import TRAIN_JSON
from torch.utils.data import DataLoader
import torch
from train import run_train
from infer import infer, infer_chat
def main():
    parser = argparse.ArgumentParser(description="LLaVA Traffic Sign CLI")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # ── train 서브커맨드 ─────────────────────────────────────────────
    train_parser = subparsers.add_parser(
        "train",
        help="LoRA 방식으로 학습 시작 (하이퍼파라미터는 train_lora.py에 정의됨)"
    )
    train_parser.add_argument(
        "train_json",
        nargs="?",
        default=None,
        help=(
            "학습용 JSON 파일(.json) 경로 또는 JSON 디렉토리 "
            "(생략 시 train_lora.py 기본 경로 사용)"
        )
    )

    # ── infer 서브커맨드 ─────────────────────────────────────────────
    infer_parser = subparsers.add_parser(
        "infer",
        help="Fine-tuned 모델로 단일 이미지 추론"
    )
    infer_parser.add_argument("image", help="이미지 파일 경로")
    infer_parser.add_argument("model", help="Fine-tuned 모델(디렉토리) 경로")

    # ── pretrained 서브커맨드 ───────────────────────────────────────
    pre_parser = subparsers.add_parser(
        "pretrained",
        help="사전학습만으로 단일 이미지 추론"
    )
    pre_parser.add_argument("image", help="이미지 파일 경로")

    # ── chat 서브커맨드 ────────────────────────────────────────────
    chat_parser = subparsers.add_parser(
        "chat",
        help="Chat 모드 (추론 + 질문 포함)"
    )
    chat_parser.add_argument("image", help="이미지 파일 경로")
    chat_parser.add_argument(
        "--model",
        help="Fine-tuned 모델(디렉토리) 경로 (생략 시 사전학습만 사용)"
    )
    chat_parser.add_argument(
        "--question",
        default="What does this sign mean, and how should I act?",
        help="질문 텍스트 (default: 표지판 의미와 행동 요령)"
    )

    args = parser.parse_args()

    if args.mode == "train":
        # ── 학습 실행 (LoRA 방식)
        json_path = args.train_json if args.train_json is not None else None
        # train_json 인자가 없으면 train.py의 TRAIN_JSON 사용
        json_path = args.train_json or TRAIN_JSON
        run_train(train_json=json_path)
    elif args.mode == "infer":
        caption = infer(image_path=args.image, model_path=args.model)
        print(f"🧾 생성된 설명 (Fine-tuned): {caption}")
    elif args.mode == "pretrained":
        caption = infer(image_path=args.image, model_path=None)
        print(f"🧾 생성된 설명 (Pretrained): {caption}")
    elif args.mode == "chat":
        reply = infer_chat(
            image_path=args.image,
            user_prompt=args.question,
            model_path=args.model
        )
        print(f"🤖 {reply}")

if __name__ == "__main__":
    main()

