#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# 색상 정의
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
NC = "\033[0m"

MODELS = [
    {
        "name": "Qwen 3.5 122B (FP4)",
        "id": "RedHatAI/Qwen3.5-122B-A10B-NVFP4",
        "gpu_util": "0.90",
        "ctx": "256k",
        "moe_backend": ""
    },
    {
        "name": "Qwen 3.6 35B (MoE / Claude-Distilled)",
        "id": "hesamation/Qwen3.6-35B-A3B-Claude-4.6-Opus-Reasoning-Distilled",
        "gpu_util": "0.80",
        "ctx": "64k",
        "moe_backend": "flashinfer_cutlass"
    }
]

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
RUN_SCRIPT = SCRIPT_DIR / "run_vllm_bg.py"

def load_container_name():
    """ .env에서 VLLM_CONTAINER_NAME을 가져옵니다. """
    if not ENV_PATH.exists():
        return "qwen-vllm" # 기본값
    with open(ENV_PATH, "r") as f:
        for line in f:
            if line.startswith("VLLM_CONTAINER_NAME="):
                return line.split("=")[1].strip()
    return "qwen-vllm"

def select_model():
    print(f"\n{CYAN}========== vLLM 모델 선택 (Selecter) =========={NC}")
    for i, model in enumerate(MODELS, 1):
        print(f"{i}. {model['name']}")
        print(f"   ID: {model['id']}")
    print(f"{CYAN}============================================={NC}")
    
    try:
        choice = input(f"\n실행할 모델 번호를 입력하세요 (기본값: 1): ").strip()
        if not choice:
            choice = "1"
            
        idx = int(choice) - 1
        if 0 <= idx < len(MODELS):
            return MODELS[idx]
        else:
            print("잘못된 번호입니다.")
            return None
    except ValueError:
        print("숫자를 입력해주세요.")
        return None
    except KeyboardInterrupt:
        print("\n취소되었습니다.")
        sys.exit(0)

def update_env(model):
    if not ENV_PATH.exists():
        print(f"오류: .env 파일을 찾을 수 없습니다 ({ENV_PATH})")
        return False
    
    with open(ENV_PATH, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    has_moe = False
    for line in lines:
        if line.startswith("VLLM_MODEL_NAME="):
            new_lines.append(f"VLLM_MODEL_NAME={model['id']}\n")
        elif line.startswith("OPENAI_MODEL="):
            new_lines.append(f"OPENAI_MODEL={model['id']}\n")
        elif line.startswith("VLLM_GPU_UTIL="):
            new_lines.append(f"VLLM_GPU_UTIL={model['gpu_util']}\n")
        elif line.startswith("VLLM_CONTEXT_LENGTH="):
            new_lines.append(f"VLLM_CONTEXT_LENGTH={model['ctx']}\n")
        elif line.startswith("VLLM_MOE_BACKEND="):
            new_lines.append(f"VLLM_MOE_BACKEND={model.get('moe_backend', '')}\n")
            has_moe = True
        else:
            new_lines.append(line)
            
    if not has_moe and model.get('moe_backend'):
        new_lines.append(f"VLLM_MOE_BACKEND={model['moe_backend']}\n")
    elif not has_moe and not model.get('moe_backend'):
        new_lines.append(f"VLLM_MOE_BACKEND=\n")
            
    with open(ENV_PATH, "w") as f:
        f.writelines(new_lines)
    
    print(f"\n{GREEN}✓ .env 설정이 {model['name']}으로 업데이트되었습니다.{NC}")
    return True

def main():
    selected = select_model()
    if not selected:
        return

    # 기존 컨테이너 종료는 run_vllm_bg.py에서도 수행하지만, 
    # 여기서 한 번 더 명시적으로 처리 (사용자 경험 피드백용)
    container_name = load_container_name()
    print(f"\n{YELLOW}기존 vLLM 세션({container_name}) 정리 중...{NC}")
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    
    if update_env(selected):
        # run_vllm_bg.py 실행
        os.execv(sys.executable, [sys.executable, str(RUN_SCRIPT)])

if __name__ == "__main__":
    main()
