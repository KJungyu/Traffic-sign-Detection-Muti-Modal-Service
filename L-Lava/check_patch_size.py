'''from model import load_model
import inspect

model, processor = load_model()

print("\n[🔍 PROCESSOR 구조 분석]")
print("processor type:", type(processor))
print("processor.image_processor type:", type(processor.image_processor))

# processor.image_processor의 모든 속성 확인
print("\n[📋 image_processor 속성들]")
for attr in dir(processor.image_processor):
    if not attr.startswith('_'):
        try:
            value = getattr(processor.image_processor, attr)
            if not callable(value):
                print(f"  - {attr}: {value}")
        except:
            print(f"  - {attr}: (접근 불가)")

# patch_size 관련 속성들 찾기
print("\n[🎯 patch 관련 속성들]")
for attr in dir(processor.image_processor):
    if 'patch' in attr.lower():
        try:
            value = getattr(processor.image_processor, attr)
            print(f"  - {attr}: {value}")
        except:
            print(f"  - {attr}: (접근 불가)")

# config 속성 확인
print("\n[⚙️ config 관련 속성들]")
if hasattr(processor.image_processor, 'config'):
    print("processor.image_processor.config:", processor.image_processor.config)
    if hasattr(processor.image_processor.config, 'patch_size'):
        print("processor.image_processor.config.patch_size:", processor.image_processor.config.patch_size)'''




from model import load_model

model, processor = load_model()

print("\n[✅ MODEL CONFIG CHECK]")
print("model.config.vision_config.patch_size:", model.config.vision_config.patch_size)

print("\n[✅ PROCESSOR CHECK]")
if isinstance(processor.image_processor, dict):
    print("processor.image_processor is a dict:")
    for key in processor.image_processor:
        sub_processor = processor.image_processor[key]
        patch_size = getattr(sub_processor, "patch_size", "⛔ 없음")
        print(f"  - {key}.patch_size = {patch_size}")
else:
    patch_size = getattr(processor.image_processor, "patch_size", "⛔ 없음")
    print(f"patch_size = {patch_size}")
