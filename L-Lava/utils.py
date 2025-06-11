import torch
import csv
import os
import evaluate


# 평가 지표: BLEU & ROUGE
bleu = evaluate.load("bleu")
rouge = evaluate.load("rouge")

def compute_metrics(predictions, references):
    # REFERENCES를 [[ref], …] 형태로 맞춰줍니다.
    refs = [[r] for r in references]

    # 1) 빈(prediction이 공백) 샘플 제거
    filtered_preds = []
    filtered_refs  = []
    for p, rs in zip(predictions, refs):
        if p.strip():  # 공백이 아닌 경우에만
            filtered_preds.append(p)
            filtered_refs.append(rs)

    # 2) BLEU 계산 (smoothing=True) — 예외 시 0으로 지정
    try:
        if filtered_preds:
            bleu_res = bleu.compute(
                predictions=filtered_preds,
                references=filtered_refs,
                smooth=True
            )
            bleu_score = bleu_res["bleu"]
        else:
            bleu_score = 0.0
    except ZeroDivisionError:
        bleu_score = 0.0

    # 3) ROUGE-L 계산 (원래대로)
    rouge_res = rouge.compute(predictions=predictions, references=references)

    return {
        # BLEU 평가 결과를 bleu_score 변수에서 바로 꺼내 쓰기
        "bleu": bleu_score,
        # ROUGE-L은 rouge_res에서
        "rougeL": rouge_res["rougeL"]
    }

def save_predictions_to_csv(preds, refs, output_path="predictions.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Prediction", "Reference"])
        for p, r in zip(preds, refs):
            writer.writerow([p, r])
    print(f"📄 예측 결과가 CSV로 저장되었습니다: {output_path}")

