import torch
from transformers import LlavaForConditionalGeneration
from peft import get_peft_model_state_dict

# 설정
model_path = "bczhou/tiny-llava-v1-hf"  # 베이스 모델
lora_model_path = "your_lora_model_path"  # LoRA 학습된 모델 경로
device = "cuda" if torch.cuda.is_available() else "cpu"

print("=== Multi-Modal Projector LoRA 확인 ===")

try:
    # 1. 베이스 모델 로드
    print("1. 베이스 모델 로드 중...")
    base_model = LlavaForConditionalGeneration.from_pretrained(model_path).to(device)
    print("✓ 베이스 모델 로드 완료")
    
    # 2. Multi-Modal Projector 구조 확인
    print("\n=== Multi-Modal Projector 구조 ===")
    projector = base_model.multi_modal_projector
    print(f"Projector 타입: {type(projector).__name__}")
    print(f"Projector 구조:")
    print(projector)
    
    # 3. 각 레이어 상세 정보
    print("\n=== 각 레이어 상세 정보 ===")
    projector_modules = {
        'linear_1': projector.linear_1,
        'act': projector.act,
        'linear_2': projector.linear_2
    }
    
    for name, module in projector_modules.items():
        print(f"\n{name}:")
        print(f"  타입: {type(module).__name__}")
        if hasattr(module, 'weight'):
            print(f"  가중치 크기: {module.weight.shape}")
            print(f"  파라미터 수: {module.weight.numel():,}")
        if hasattr(module, 'bias') and module.bias is not None:
            print(f"  편향 크기: {module.bias.shape}")
            print(f"  편향 파라미터 수: {module.bias.numel():,}")
        print(f"  requires_grad: {next(module.parameters()).requires_grad}")
        print(f"  디바이스: {next(module.parameters()).device}")
        print(f"  dtype: {next(module.parameters()).dtype}")
        params = list(module.parameters())
        if params:
            weight = getattr(module, 'weight', None)
            bias   = getattr(module, 'bias',   None)
        if weight is not None:
            print(f"  가중치 크기: {weight.shape}")
            print(f"  파라미터 수: {weight.numel():,}")
        if bias is not None:
            print(f"  편향 크기: {bias.shape}")
            print(f"  편향 파라미터 수: {bias.numel():,}")

        p0 = params[0]
        print(f"  requires_grad: {p0.requires_grad}")
        print(f"  디바이스: {p0.device}")
        print(f"  dtype: {p0.dtype}")
    else:
        print("  학습 가능한 파라미터 없음 (activation 모듈 등)")
    
    # 4. 전체 프로젝터 파라미터 통계
    print(f"\n=== 전체 Projector 통계 ===")
    total_params = sum(p.numel() for p in projector.parameters())
    trainable_params = sum(p.numel() for p in projector.parameters() if p.requires_grad)
    print(f"전체 파라미터: {total_params:,}")
    print(f"훈련 가능한 파라미터: {trainable_params:,}")
    
    # 5. LoRA 모델 로드 및 비교 (경로가 있는 경우)
    try:
        print(f"\n=== LoRA 모델 로드 시도 ===")
        # LoRA 모델 로드 방법은 사용한 라이브러리에 따라 다름
        # PEFT 사용한 경우의 예시
        from peft import PeftModel
        lora_model = PeftModel.from_pretrained(base_model, lora_model_path)
        print("✓ LoRA 모델 로드 성공")
        
        # LoRA 어댑터 정보 확인
        print(f"\n=== LoRA 어댑터 정보 ===")
        if hasattr(lora_model, 'peft_config'):
            for adapter_name, config in lora_model.peft_config.items():
                print(f"어댑터 이름: {adapter_name}")
                print(f"LoRA 타입: {config.peft_type}")
                print(f"r (rank): {config.r}")
                print(f"alpha: {config.lora_alpha}")
                print(f"dropout: {config.lora_dropout}")
                if hasattr(config, 'target_modules'):
                    print(f"타겟 모듈: {config.target_modules}")
        
        # LoRA 파라미터 확인
        lora_params = get_peft_model_state_dict(lora_model)
        print(f"\n=== LoRA 파라미터 ===")
        projector_lora_params = {k: v for k, v in lora_params.items() 
                               if 'multi_modal_projector' in k}
        
        for param_name, param_tensor in projector_lora_params.items():
            print(f"{param_name}: {param_tensor.shape}")
            
    except Exception as e:
        print(f"LoRA 모델 로드 실패 (경로 확인 필요): {e}")
    
    # 6. 프로젝터 입출력 차원 확인
    print(f"\n=== 입출력 차원 확인 ===")
    # 일반적으로 linear_1이 입력 차원, linear_2가 출력 차원
    if hasattr(projector.linear_1, 'in_features'):
        print(f"입력 차원 (비전 특성): {projector.linear_1.in_features}")
    if hasattr(projector.linear_2, 'out_features'):
        print(f"출력 차원 (언어 모델 임베딩): {projector.linear_2.out_features}")
    
    # 7. 간단한 forward 테스트
    print(f"\n=== Forward 테스트 ===")
    # 비전 인코더 출력과 유사한 더미 입력 생성
    if hasattr(projector.linear_1, 'in_features'):
        dummy_input = torch.randn(1, 576, projector.linear_1.in_features).to(device)  # 24x24 패치
        print(f"더미 입력 크기: {dummy_input.shape}")
        
        with torch.no_grad():
            output = projector(dummy_input)
            print(f"출력 크기: {output.shape}")
            print(f"출력 통계 - 평균: {output.mean():.4f}, 표준편차: {output.std():.4f}")
            print("✓ Forward 테스트 성공")
    
    print(f"\n=== 모델별 차이점 확인 ===")
    print("Tiny-LLaVA 특징:")
    print("- 경량화된 비전 인코더 사용")
    print("- 작은 언어 모델 (1.1B 파라미터)")
    print("- Multi-modal projector가 핵심 연결 역할")
    print("- LoRA 튜닝으로 효율적인 파인튜닝 가능")

except Exception as e:
    print(f"❌ 오류 발생: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 프로젝터 확인 완료 ===")

# 추가: 파라미터 이름 전체 출력 (선택사항)
print(f"\n=== 전체 모델 파라미터 이름 (multi_modal_projector 관련) ===")
for name, param in base_model.named_parameters():
    if 'multi_modal_projector' in name:
        print(f"{name}: {param.shape} (requires_grad: {param.requires_grad})")
