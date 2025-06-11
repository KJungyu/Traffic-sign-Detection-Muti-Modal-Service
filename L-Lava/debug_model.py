from transformers import LlavaForConditionalGeneration, LlavaProcessor
def load_model(model_name="bczhou/tiny-llava-v1-hf"):
    # 1) 모델 로드
    model = LlavaForConditionalGeneration.from_pretrained(model_name)
    # 2) LlavaProcessor 로 생성
    processor = LlavaProcessor.from_pretrained(model_name)

    # 토크나이저가 <image> 토큰을 special token으로 인식하는지 확인
    id_image = processor.tokenizer.convert_tokens_to_ids("<image>")
    
    
    print("ID of <image> token:", id_image)           # -1 이 나오면 등록 안 된 것
    print("Does vocab contain <image>?", "<image>" in processor.tokenizer.get_vocab())

