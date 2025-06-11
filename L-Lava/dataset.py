import os
import json
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset
import torch

class CaptionDataset(Dataset):
    def __init__(self, json_path: str, processor, max_length: int = 256):
        """
        json_path: 학습용 JSON 파일(.json) 경로
                   각 아이템에 'image' 또는 'image_path' 필드,
                   및 'answer' 또는 'conversations' 필드를 가져야 함.
        processor: LlavaProcessor 인스턴스
        max_length: 최대 토큰 길이 (텍스트 부분)
        """
        # JSON 파일 로드 및 normalization
        with open(json_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        self.data = []
        for item in raw_data:
            img_p = item.get("image_path") or item.get("image") or ""
            if "answer" in item:
                ans = item["answer"]
            else:
                ans = ""
                for conv in reversed(item.get("conversations", [])):
                    if conv.get("from") == "gpt":
                        ans = conv.get("value", "")
                        break
            self.data.append({"image_path": img_p, "answer": ans})

        self.processor = processor
        self.max_length = max_length    # 텍스트 최대 길이
        self.base_dir = os.path.dirname(json_path)

        # image_processor.patch_size가 None이면 기본값 설정
        img_proc = self.processor.image_processor
        if getattr(img_proc, "patch_size", None) is None:
            try:
                img_proc.patch_size = 14
            except Exception:
                pass

        # 프롬프트 텍스트
        self.text_prefix = "What does this sign mean, and how should I act?"

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        img_path = item["image_path"]
        # 절대/상대 경로 보정
        if not os.path.exists(img_path):
            found = False
            alt1 = os.path.join(self.base_dir, img_path)
            alt2 = os.path.join(self.base_dir, img_path.lstrip(os.sep))
            if os.path.exists(alt1):
                img_path, found = alt1, True
            elif os.path.exists(alt2):
                img_path, found = alt2, True
            else:
                parts = Path(img_path).parts
                if "dataset" in parts:
                    idx0 = parts.index("dataset")
                    alt3 = os.path.join(self.base_dir, *parts[idx0+1:])
                    if os.path.exists(alt3):
                        img_path, found = alt3, True
            if not found:
                raise FileNotFoundError(f"이미지 없음: {item['image_path']}")

        # 이미지 로드 및 multimodal inputs 생성
        image = Image.open(img_path).convert("RGB")
        prompt = "<image> " + self.text_prefix
        inputs = self.processor(
            images=image,
            text=prompt,
            return_tensors="pt",
            padding="max_length",
            max_length=self.max_length,
            truncation=False
        )
        # 배치 축 제거
        inputs = {k: v.squeeze(0) for k, v in inputs.items()}

        # 레이블 생성 (input_ids 길이에 맞춰서 생성)
        input_ids = inputs["input_ids"]            # shape: [seq_len]
        seq_len = input_ids.size(0)
        # 텍스트 토큰 (max_length 길이)
        text_tokens = self.processor.tokenizer(
            item["answer"],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=self.max_length
        ).input_ids.squeeze(0)                   # shape: [max_length]
        # 전체 시퀀스 길이만큼 -100으로 채우기
        labels = torch.full((seq_len,), fill_value=-100, dtype=torch.long)
        # 텍스트 부분(마지막 max_length 토큰)에 text_tokens 채움
        labels[-self.max_length:] = text_tokens
        # pad 토큰 위치 무시
        pad_id = self.processor.tokenizer.pad_token_id
        labels[labels == pad_id] = -100
        inputs["labels"] = labels

        inputs["target_text"] = item.get("answer", "")
        return inputs
