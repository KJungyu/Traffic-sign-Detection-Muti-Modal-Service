# debug_full.py
import torch
from torch.utils.data import DataLoader
from model import load_model
from dataset import CaptionDataset

def print_tensor_info(tag, tensor):
    """
    간단히 텐서의 dtype과 shape를 출력합니다.
    """
    print(f"  - {tag}: dtype={tensor.dtype}, shape={tuple(tensor.shape)}")

def main():
    print("▶️ 1) load_model() 호출")
    model, processor = load_model("bczhou/tiny-llava-v1-hf")
    model.eval()
    print(f"[INFO] processor type: {type(processor)}")
    print()

    # ── 2) CaptionDataset 생성
    json_path = "/workspace/LLAVA/dataset/data.json"
    print(f"▶️ 2) CaptionDataset 생성 (json_path={json_path})")
    dataset = CaptionDataset(json_path=json_path, processor=processor)
    print()

    # ── 3) 첫 번째 샘플만 뽑아서 확인
    print("▶️ 3) 첫 번째 샘플 가져오기 (__getitem__(0))")
    sample = dataset[0]  # {pixel_values, image_token_type_ids?, spatial_mask?, input_ids, attention_mask, labels, target_text}
    print(">>> sample.keys():", list(sample.keys()))
    for key, val in sample.items():
        if torch.is_tensor(val):
            print_tensor_info(key, val)
        else:
            print(f"  - {key}: (non-tensor) type={type(val)}, value={val}")
    print()

    # ── 4) processor(...) 결과만 따로 뽑아보기
    #     (image_token_type_ids나 spatial_mask가 실제로 생성되는지 확인)
    print("▶️ 4) processor(text, images) 직접 호출해 보기")
    # (CaptionDataset 내부에서 쓰는 그대로) 
    #    processor(...) 호출 시, 리턴되는 키들을 살펴봅니다.
    from PIL import Image
    import json
    # 데이터 JSON에서 첫 아이템 가져오기
    with open(json_path, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    first_item = data_list[0]
    img_path = first_item["image_path"]
    image = Image.open(img_path).convert("RGB")

    proc_outputs = processor(
        text=dataset.prompt,
        images=image,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=dataset.max_length
    )
    print(">>> proc_outputs.keys():", list(proc_outputs.keys()))
    for k, v in proc_outputs.items():
        if torch.is_tensor(v):
            print_tensor_info(f"proc_outputs['{k}']", v)
        else:
            print(f"  - proc_outputs['{k}']: (non-tensor) type={type(v)}")
    print()

    # ── 5) 만약 proc_outputs에 image_token_type_ids가 없으면, 수동으로 길이 계산해 보기
    print("▶️ 5) image_size와 계산된 num_patches 확인")
    ps = processor.image_processor.patch_size
    crop = processor.image_processor.crop_size
    height, width = crop["height"], crop["width"]
    num_patches = (height // ps) * (width // ps)
    print(f"  - processor.image_processor.patch_size = {ps}")
    print(f"  - processor.image_processor.crop_size = {crop}")
    print(f"  - 계산된 num_patches = ( {height} // {ps} ) * ( {width} // {ps} ) = {num_patches}")
    print()

    # ── 6) 만약 image_token_type_ids가 빠졌다면, 수동으로 생성해 보겠습니다.
    if "image_token_type_ids" not in proc_outputs:
        print("▶️ 6) image_token_type_ids가 proc_outputs에 없음 → 수동 생성해 보기")
        manual_tokens = torch.ones(num_patches, dtype=torch.long)
        print_tensor_info("manual image_token_type_ids", manual_tokens)
        manual_mask = torch.ones(num_patches, dtype=torch.long)
        print_tensor_info("manual spatial_mask", manual_mask)
    else:
        print("▶️ 6) proc_outputs에 image_token_type_ids가 이미 있음 → 수동 생성 불필요")
    print()

    # ── 7) 마지막으로, model이 요구하는 입력 형태(patch features vs tokens)를 확인하기 위해,
    #      pixel_values를 직접 vision encoder에 넣어보고 features 길이를 확인해 봅니다.
    print("▶️ 7) model의 vision encoder에 pixel_values를 넣어 feature 개수 확인")
    pixel_values = proc_outputs["pixel_values"].to(next(model.parameters()).device)
    with torch.no_grad():
        # LlavaForConditionalGeneration 내부에서 vision encoder는 .visual_encoder 속성에 있을 수 있습니다.
        # 예시: 모델에 따라 아래처럼 접근
        try:
            features = model.vision_model(pixel_values)[0]  # [batch_size, num_patches, hidden_dim]
            print(f"  - vision_model(pixel_values).shape = {tuple(features.shape)}")
            _, num_feat, _ = features.shape
            print(f"  - num_feat (patch count) = {num_feat}")
        except Exception as e:
            print(f"⚠️ vision encoder 호출 실패: {e}")
    print()

    # ── 8) 마무리
    print("✅ 디버깅 완료: 위 출력 내역을 보고 'tokens' vs 'features' mismatch 원인을 확인하세요.")

if __name__ == "__main__":
    main()
