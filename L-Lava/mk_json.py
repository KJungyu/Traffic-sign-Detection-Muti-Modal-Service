import os
import json
import re

# 원본 JSON과 경로 루트 설정
src_root = "/home/dsc/work/LLAVA_final/dataset"
dst_root = "/workspace/LLAVA/dataset"

# 원본 데이터 로드
orig_path = os.path.join(src_root, "data.json")
orig = json.load(open(orig_path, encoding="utf-8"))

conv = []
for item in orig:
    old_path = item.get("image_path")
    ans = item.get("answer", "")

    # 1) 원본 경로 기준 상대경로 계산
    rel_path = os.path.relpath(old_path, src_root)
    # 2) 실제 이미지 루트에 상대경로 붙이기
    new_path = os.path.normpath(os.path.join(dst_root, rel_path))

    # 3) 질문 텍스트 선택 (한국어/영어)
    if re.search(r"[ㄱ-ㅎ가-힣]", ans):
        q = "이 표지판은 무엇을 의미하나요?"
    else:
        q = "What does this sign mean, and how should I act?"

    # 4) LLAVA 포맷으로 변환
    conv.append({
        "image": new_path,
        "conversations": [
            {"from": "human", "value": f"<image>\n{q}"},
            {"from": "gpt",   "value": ans}
        ]
    })

# 5) LLAVA용 JSON 저장
out_path = os.path.join(src_root, "llava_data.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(conv, f, ensure_ascii=False, indent=2)

print(f"✅ Converted {len(conv)} entries and saved to {out_path}")
