import os
import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from tqdm import tqdm

from peft import get_peft_model, LoraConfig
from model import load_model
from dataset import CaptionDataset
from utils import compute_metrics, save_predictions_to_csv

# ── 기본 하이퍼파라미터 ────────────────────────────────
TRAIN_JSON  = "/home/dsc/work/LLAVA_final/dataset/llava_data.json"
EPOCHS      = 50
BATCH_SIZE  = 16
LR          = 5e-5
MODEL_NAME  = "bczhou/tiny-llava-v1-hf"
OUTPUT_DIR  = "/home/dsc/work/LLAVA_final/outputs"
DEVICE      = torch.device("cuda:3" if torch.cuda.is_available() else "cpu")
# ───────────────────────────────────────────────────────


def run_train(
    train_json: str = TRAIN_JSON,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    lr: float = LR,
    model_name: str = MODEL_NAME,
    output_dir: str = OUTPUT_DIR
):
    # 1) 모델·프로세서 로드
    if train_json is None:
        train_json = TRAIN_JSON
    model, processor = load_model(model_name)
    model.to(DEVICE)

    # 2) LoRA 설정 및 적용
    lora_cfg = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["multi_modal_projector.linear_1", "multi_modal_projector.linear_2"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    for name, module in model.named_modules():
        if 'projector' in name.lower():
            print(name)

    model = get_peft_model(model, lora_cfg).to(DEVICE)
    model.print_trainable_parameters()

    # 3) 데이터셋·데이터로더 준비
    dataset = CaptionDataset(train_json, processor)

    # ── Debug: token parsing 확인 ──────────────────────────
    image_token_id = processor.tokenizer.convert_tokens_to_ids("<image>")
    sample = dataset[0]
    input_ids = sample["input_ids"].tolist()
    print("ID of <image>:", image_token_id)
    print("input_ids[:20]:", input_ids[:20])
    print("Contains <image> token?", image_token_id in input_ids)
    print("Count of <image> tokens:", input_ids.count(image_token_id))
    # ───────────────────────────────────────────────────────

    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # 4) 옵티마이저: LoRA 파라미터만 업데이트
    optimizer = AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=lr
    )

    # 5) 출력 디렉토리 준비
    os.makedirs(output_dir, exist_ok=True)
    best_dir = os.path.join(output_dir, "checkpoint-best")
    last_dir = os.path.join(output_dir, "checkpoint-last")
    best_metric = float("-inf")

    all_preds, all_refs = [], []

    # 6) Training Loop
    model.train()
    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        epoch_preds, epoch_refs = [], []

        for batch in tqdm(dataloader, desc=f"Epoch {epoch}"):
            inputs = {
                "pixel_values": batch["pixel_values"].to(DEVICE),
                "input_ids":    batch["input_ids"].to(DEVICE),
                "attention_mask": batch["attention_mask"].to(DEVICE),
            }
            labels = batch["labels"].to(DEVICE)

            outputs = model(**inputs, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            total_loss += loss.item()

            # 예측 생성
            # 예측 생성 (generation 모드)
            with torch.no_grad():
                gen_ids = model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    num_beams=4,
                )
            preds = processor.tokenizer.batch_decode(gen_ids, skip_special_tokens=True)
            preds = [p.strip() for p in preds]
            refs = batch["target_text"]

            epoch_preds.extend(preds)
            epoch_refs.extend(refs)

        # 에폭별 메트릭 계산
        avg_loss = total_loss / len(dataloader)
        metrics = compute_metrics(epoch_preds, epoch_refs)
        print(
            f"[Epoch {epoch}] "
            f"Loss: {avg_loss:.4f} | "
            f"BLEU: {metrics['bleu']:.4f} | "
            f"ROUGE-L: {metrics['rougeL']:.4f}"
        )

        # Best checkpoint 저장
        if metrics['rougeL'] > best_metric:
            best_metric = metrics['rougeL']
            os.makedirs(best_dir, exist_ok=True)
            model.save_pretrained(best_dir)
            processor.save_pretrained(best_dir)
            print(f"✅ New best checkpoint → {best_dir}")

        # 마지막 에폭 체크포인트 저장
        if epoch == epochs-1:
            os.makedirs(last_dir, exist_ok=True)
            model.save_pretrained(last_dir)
            processor.save_pretrained(last_dir)
            print(f"✅ Last checkpoint → {last_dir}")

        all_preds.extend(epoch_preds)
        all_refs.extend(epoch_refs)

    # 7) 모든 예측 결과 CSV 저장
    csv_path = os.path.join(output_dir, "predictions_all_epochs.csv")
    save_predictions_to_csv(all_preds, all_refs, output_path=csv_path)
    print(f"✅ All epochs saved → {csv_path}")

    return model, processor
