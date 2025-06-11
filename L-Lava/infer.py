from model import load_model
from transformers import AutoProcessor
from PIL import Image
import torch
'''
def infer(image_path, user_prompt="Please describe this image.", model_path=None):
    model, processor = load_model()
    
    # ✅ LlavaProcessor 자체에 patch_size 강제 설정 (가장 중요!)
    if not hasattr(processor, 'patch_size') or processor.patch_size is None:
        processor.patch_size = 14
        print("✅ processor.patch_size를 14로 강제 설정했습니다.")
    
    # 추가 안전장치: image_processor에도 설정
    if not hasattr(processor.image_processor, 'patch_size') or processor.image_processor.patch_size is None:
        processor.image_processor.patch_size = 14
        print("✅ processor.image_processor.patch_size를 14로 설정했습니다.")
    
    if model_path:
        model.load_state_dict(torch.load(model_path))
    model.eval().cuda()

    image = Image.open(image_path).convert("RGB")

    # 사용자 프롬프트 기반 챗 형식
    prompt = f"<image>\nUSER: {user_prompt}\nASSISTANT:"

    # ✅ 이미지 크기 수동 지정 (patch_size 문제 회피)
    inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt",
        do_resize=True,
        size={"height": 336, "width": 336},  # TinyLLaVA 기본 해상도에 맞춤
    ).to("cuda")

    with torch.no_grad():
        output = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            pixel_values=inputs["pixel_values"],
            do_sample=True,
            temperature=0.7,
            max_new_tokens=256
        )
        caption = processor.batch_decode(output, skip_special_tokens=True)[0]

    return caption
infer_chat = infer'''

from model import load_model
from transformers import AutoProcessor
from PIL import Image
import torch

def infer(image_path, user_prompt="Please describe this image.", model_path=None):
    # ── 모델·프로세서 로딩 ────────────────────────────────
    if model_path:
        # model_path가 디렉터리일 경우, 디렉터리 내의 config.json/.safetensors 등을 이용해 from_pretrained
        model, processor = load_model(model_path)
    else:
        # model_path가 없으면 기본(사전학습) 모델 로드
        model, processor = load_model()

    # ── LlavaProcessor patch_size 강제 설정 ───────────────────
    if not hasattr(processor, 'patch_size') or processor.patch_size is None:
        processor.patch_size = 14
        print("✅ processor.patch_size를 14로 강제 설정했습니다.")
    
    # 추가 안전장치: processor.image_processor.patch_size 설정
    if not hasattr(processor.image_processor, 'patch_size') or processor.image_processor.patch_size is None:
        processor.image_processor.patch_size = 14
        print("✅ processor.image_processor.patch_size를 14로 설정했습니다.")
    
    model.eval().cuda()

    # ── 이미지 열기 ─────────────────────────────────────────
    image = Image.open(image_path).convert("RGB")

    # ── 사용자 프롬프트 기반 챗 형식 ─────────────────────────
    prompt = f"<image>\nUSER: {user_prompt}\nASSISTANT:"

    # ── 이미지 + 텍스트 전처리 (patch_size 이슈 회피) ──────────
    inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt",
        truncation=False,
        max_length=None,
        do_resize=True,
        size={"height": 336, "width": 336},
    ).to("cuda")

    # ── 추론: generate ───────────────────────────────────────
    with torch.no_grad():
        output = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            pixel_values=inputs["pixel_values"],
            do_sample=True,
            temperature=0.7,
            max_new_tokens=256
        )
        caption = processor.batch_decode(output, skip_special_tokens=True)[0]

    return caption

# infer_chat은 infer와 동일하게 동작하도록 지정
infer_chat = infer
