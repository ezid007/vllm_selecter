# vLLM Selecter — 모델 선택 & 실행 시스템

NVIDIA DGX Spark (Grace Blackwell 128GB) 환경에서 vLLM 모델을 인터랙티브하게 선택하고 Docker 백그라운드로 실행하는 시스템입니다.

## Quick Start

```bash
# 터미널에서 바로 실행 (bashrc 알리아스 등록됨)
vllm
```

메뉴에서 번호를 선택하면 기존 컨테이너가 자동 정리되고 새 모델이 실행됩니다.
모델 선택 후 **Thinking 모드(ON/OFF)**를 추가로 선택할 수 있습니다.
아무 것도 입력하지 않고 Enter를 누르면 **1번 (122B)** 모델과 **Thinking ON**이 기본 선택됩니다.

## Requirements

| 구성 요소 | 버전 |
|---|---|
| **vLLM Docker 이미지** | `>= 0.20.0` (`vllm-node:latest`) |
| **transformers** | `>= 5.0` (Docker 이미지 내부) |
| **Docker + NVIDIA Container Toolkit** | DGX OS 기본 포함 |
| **Python** | 3.x (스크립트 실행용) |

> Docker 이미지 빌드: `~/spark-vllm-docker/build-and-copy.sh --vllm-ref v0.20.0 --tf5 --rebuild-vllm`

## Registered Models

| # | 모델 | ID | 활성 파라미터 |
|---|---|---|---|
| 1 | Qwen 3.5 122B (FP4) | `RedHatAI/Qwen3.5-122B-A10B-NVFP4` | ~10B |
| 2 | Qwen 3.6 35B (MoE / Claude-Distilled) | `hesamation/Qwen3.6-35B-A3B-Claude-4.6-Opus-Reasoning-Distilled` | ~3B |

### Model 2: Qwen3.6-35B-A3B-Claude-4.6-Opus-Reasoning-Distilled

- **기반 모델**: `Qwen/Qwen3.6-35B-A3B` (MoE 아키텍처, 256 experts / 8+1 activated)
- **훈련**: Claude 4.6 Opus 추론 과정을 SFT + LoRA로 증류 학습
- **컨텍스트**: 262,144 토큰 (네이티브), 최대 1,010,000 토큰 (YaRN)
- **특이사항**: 텍스트 전용 파인튜닝 → `--language-model-only` 옵션으로 비전 인코더 스킵하여 메모리 절약

## File Structure

```
vllm_selecter/
vllm_selecter/
├── .env                    # 모델 및 Docker 실행 설정 (컨테이너 명, 포트, GPU, SHM 등)
├── .gitignore              # Git 제외 설정
├── select_vllm.py          # 모델 선택 인터페이스 (alias: vllm)
├── run_vllm_bg.py          # Docker vLLM 백그라운드 실행 엔진
├── docs/                   # 모델별 README 문서
├── logs/
│   └── CHANGELOG.md        # 변경 이력
├── plans/
│   └── plan.md             # 진행 상황 및 향후 계획
└── readme.md               # 이 파일
```

## Usage

### 모델 실행

```bash
vllm              # 인터랙티브 모델 선택
```

### 컨테이너 관리

```bash
# 로그 확인
docker logs -f $(grep VLLM_CONTAINER_NAME .env | cut -d'=' -f2)

# 컨테이너 중지 및 삭제
docker rm -f $(grep VLLM_CONTAINER_NAME .env | cut -d'=' -f2)
```

## Hardware Optimization (Grace Blackwell)

- **128GB Unified Memory**: MoE 모델의 전체 가중치를 메모리에 적재하면서도 큰 KV 캐시 확보 가능
- **NVLink-C2C**: CPU-GPU 간 고속 데이터 전송으로 MoE 라우팅 오버헤드 최소화
- **ARM64 (aarch64)**: `spark-vllm-docker` 빌드 시스템으로 네이티브 ARM64 최적화 바이너리 사용
