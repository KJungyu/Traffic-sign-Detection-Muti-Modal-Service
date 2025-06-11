# model.py
from transformers import LlavaForConditionalGeneration, LlavaProcessor

def load_model(model_name="bczhou/tiny-llava-v1-hf"):
    # 1) 모델 로드
    model = LlavaForConditionalGeneration.from_pretrained(model_name)
    # 2) LlavaProcessor 로 생성
    processor = LlavaProcessor.from_pretrained(model_name)

    # 3) vision_config에서 patch_size(dimension) 가져오기
    model_patch_size = model.config.vision_config.patch_size

    # ── (A) processor 자체에 patch_size 속성이 없으면 강제로 생성합니다.
    setattr(processor, "patch_size", model_patch_size)
    print(f"✅ processor.patch_size를 {model_patch_size}로 설정했습니다.")

    # ── (B) image_processor.patch_size를 무조건 14로 설정
    #     (딕셔너리나 객체 구분 없이, 해당 속성이 있으면 덮어씌웁니다.)
    try:
        setattr(processor.image_processor, "patch_size", model_patch_size)
        print(f"✅ processor.image_processor.patch_size를 {model_patch_size}로 설정했습니다.")
    except Exception as e:
        # 보통 image_processor가 dict 구조가 아니라 간단한 객체이므로 위 코드가 동작합니다.
        print(f"⚠️ image_processor.patch_size 설정 실패: {e}")

    # ── 최종 상태 출력 ──
    print("🔍 최종 Processor 상태:")
    print(f"  - processor.patch_size: {getattr(processor, 'patch_size', None)}")
    print(f"  - image_processor.patch_size: {getattr(processor.image_processor, 'patch_size', None)}")

    return model, processor



