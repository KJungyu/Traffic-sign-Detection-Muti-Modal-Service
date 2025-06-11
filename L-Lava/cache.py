import torch

# 현재 디바이스 확인
current_device = torch.cuda.current_device()
print(f"현재 디바이스: cuda:{current_device}")

# cuda:3으로 전환하고 캐시 삭제
torch.cuda.set_device(3)
torch.cuda.empty_cache()

# 메모리 사용량 확인
memory_allocated = torch.cuda.memory_allocated(3)
memory_reserved = torch.cuda.memory_reserved(3)
print(f"cuda:3 할당된 메모리: {memory_allocated / 1024**2:.2f} MB")
print(f"cuda:3 예약된 메모리: {memory_reserved / 1024**2:.2f} MB")

# 원래 디바이스로 복원
torch.cuda.set_device(current_device)
