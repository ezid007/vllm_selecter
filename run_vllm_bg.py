#!/usr/bin/env python3
"""
run_vllm_bg.py — vLLM 백그라운드 실행 스크립트 (vLLM >= 0.20.0 + transformers >= 5)

.env 설정에 따라 vLLM 서버를 Docker 백그라운드 데몬(-d)으로 시작합니다.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# ─── 상수 ───────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / ".env"

CONTEXT_MAP = {
    "32k": 32768,
    "64k": 65536,
    "128k": 131072,
    "256k": 262144,
}

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
NC = "\033[0m"




def load_env(env_path: Path) -> dict[str, str]:
    """간단한 KEY=VALUE 형식의 .env 파일 파싱."""
    env_vars: dict[str, str] = {}
    if not env_path.exists():
        return env_vars
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip()
    return env_vars


def get_env(env_vars: dict[str, str], key: str) -> str:
    """환경 변수 또는 .env에서 값을 가져오고, 없으면 오류 종료."""
    value = os.environ.get(key, env_vars.get(key))
    if value is None:
        print(f"  {RED}✗ .env에 '{key}'가 설정되어 있지 않습니다.{NC}")
        sys.exit(1)
    return value


def start_vllm_bg(env_vars: dict[str, str]):
    model_name = get_env(env_vars, "VLLM_MODEL_NAME")
    ctx_key = get_env(env_vars, "VLLM_CONTEXT_LENGTH").lower()
    max_model_len = CONTEXT_MAP.get(ctx_key, 131072)

    port = get_env(env_vars, "VLLM_PORT")
    gpu_util = get_env(env_vars, "VLLM_GPU_UTIL")
    docker_image = get_env(env_vars, "VLLM_DOCKER_IMAGE")
    api_key = get_env(env_vars, "OPENAI_API_KEY")
    enable_thinking = get_env(env_vars, "VLLM_ENABLE_THINKING").lower() == "true"
    moe_backend = env_vars.get("VLLM_MOE_BACKEND", "")
    
    container_name = get_env(env_vars, "VLLM_CONTAINER_NAME")
    shm_size = get_env(env_vars, "VLLM_SHM_SIZE")
    docker_network = get_env(env_vars, "VLLM_DOCKER_NETWORK")

    hf_cache = Path.home() / ".cache" / "huggingface"
    hf_token_file = hf_cache / "token"
    hf_token = hf_token_file.read_text().strip() if hf_token_file.exists() else ""

    print(f"{YELLOW}기존 vLLM 컨테이너({container_name}) 정리 중...{NC}")
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

    # ─── vLLM serve 인자 조립 ────────────────────────────────
    vllm_args = [
        "vllm", "serve", model_name,
        "--host", "0.0.0.0", "--port", port,
        "--api-key", api_key,
        "--reasoning-parser", "qwen3",
        "--enable-prefix-caching",
        "--enable-auto-tool-choice",
        "--tool-call-parser", "qwen3_coder",
        "--max-model-len", str(max_model_len),
        "--max-num-batched-tokens", "8192",
        "--default-chat-template-kwargs", json.dumps({"enable_thinking": enable_thinking}),
        "--trust-remote-code",
        "--gpu-memory-utilization", gpu_util,
    ]

    if moe_backend:
        vllm_args.extend(["--moe_backend", moe_backend])

    # ─── Docker 명령어 조립 ──────────────────────────────────
    docker_cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "--runtime=nvidia",
        "--gpus", "all",
        "--shm-size", shm_size,
        "--network", docker_network,
        "-v", f"{hf_cache}:/root/.cache/huggingface",
        "-e", "HF_HOME=/root/.cache/huggingface",
    ]

    if hf_token:
        docker_cmd.extend(["-e", f"HUGGING_FACE_HUB_TOKEN={hf_token}"])

    docker_cmd.extend([docker_image] + vllm_args)

    print(f"\n{GREEN}vLLM 서버 시작 중... ({model_name}){NC}")

    try:
        subprocess.run(docker_cmd, check=True)
        print(f"\n{GREEN}✓ vLLM 데몬 실행 완료!{NC}")
        print(f"로그 확인: {YELLOW}docker logs -f {container_name}{NC}")
    except subprocess.CalledProcessError:
        print(f"\n{RED}✗ vLLM 데몬 실행에 실패했습니다.{NC}")


if __name__ == "__main__":
    env = load_env(ENV_FILE)
    if not env:
        print(f"{RED}오류: .env 파일을 로드할 수 없습니다.{NC}")
        sys.exit(1)
    start_vllm_bg(env)
