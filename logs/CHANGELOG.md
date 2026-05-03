# Changelog

이 프로젝트의 모든 중요한 변경 사항은 이 파일에 기록됩니다.

## [0.3.3] - 2026-05-04

### Added
- **인터랙티브 Thinking 모드 설정**: 모델 선택 후 Thinking 모드 활성화 여부(`true`/`false`)를 직접 선택할 수 있는 인터페이스 추가.
- `select_vllm.py`에서 선택된 값을 `.env`의 `VLLM_ENABLE_THINKING` 항목에 자동 반영.

## [0.3.2] - 2026-05-04

### Refactored
- 보안 및 유연성 강화를 위해 하드코딩된 Docker 설정값을 `.env`로 이전:
  - `VLLM_CONTAINER_NAME`, `VLLM_SHM_SIZE`, `VLLM_DOCKER_NETWORK` 환경 변수 도입.
  - `select_vllm.py` 및 `run_vllm_bg.py`에서 위 환경 변수를 사용하도록 리팩토링.
- `readme.md` 및 `plans/plan.md`를 최신 시스템 구조에 맞게 업데이트.

## [0.3.1] - 2026-05-04

### Fixed
- 1번 모델 (Qwen 3.5 122B) 실행 실패 문제 해결:
  - GPU 메모리 할당 초과(OOM) 오류를 방지하기 위해 `gpu_util`을 0.87에서 0.80으로 하향 조정.
  - `--moe_backend flashinfer_cutlass` 옵션이 Non-MoE 모델에 하드코딩되어 있던 문제를 수정하여 `.env` (`VLLM_MOE_BACKEND`)를 통해 동적으로 주입되도록 리팩토링.

## [0.3.0] - 2026-05-03

### Added
- **.gitignore 설정**: 보안 및 효율성을 위해 `.env`, `.venv`, 데이터베이스 파일 등을 버전 관리에서 제외.
- **메모리 최적화**: `Talk With Me` 환경(STT/TTS 병행)을 고려하여 `gpu_util: 0.80`, `ctx: 64k`로 최적화 설정 조정.

## [0.2.0] - 2026-05-03

### Changed
- **vLLM 0.20.0 업그레이드**: Docker 이미지를 `vllm-node:latest` (v0.20.0 + transformers>=5) 기반으로 재빌드.
- `run_vllm_bg.py` 전면 리팩토링:
  - `TokenizersBackend` 토크나이저 패치 워크어라운드 **전부 제거** (v0.20.0에서 네이티브 지원).
  - `_needs_tokenizer_patch()` 함수 및 `sed`/`bash -c` entrypoint 오버라이드 삭제.
  - `shlex` import 제거, Docker 명령어 단순화.
  - `TEXT_ONLY_MODELS` 리스트 도입: 텍스트 전용 모델 판별 로직 일반화.
  - 모듈 docstring 추가 (vLLM 버전 요구사항 명시).

### Added
- `--language-model-only` 옵션: 텍스트 전용 파인튜닝 모델(hesamation 등)에서 비전 인코더 로딩 스킵 → 메모리 절약.

### Fixed
- 2번 모델(Qwen 3.6 35B) 실행 시 `ValueError: Tokenizer class TokenizersBackend does not exist` 오류 해결.

---

## [0.1.0] - 2026-05-03

### Added
- `hesamation/Qwen3.6-35B-A3B-Claude-4.6-Opus-Reasoning-Distilled` 모델 상세 설명 추가.
- `/home/aiis/vllm_selecter/`에 독립적인 vLLM 선택 및 실행 시스템 재구성.
- `select_vllm.py`: Qwen 3.5 122B와 Qwen 3.6 35B 모델 중 선택하여 실행할 수 있는 인터랙티브 스크립트. (Enter 입력 시 122B 기본 선택 기능 추가)
- `run_vllm_bg.py`: Docker 기반 vLLM 백그라운드 실행 엔진 (컨테이너 이름: `qwen-vllm`).
- `.bashrc`: `vllm` 알리아스를 신규 경로의 선택 스크립트로 연동.
- 프로젝트 기본 문서 시스템 초기화 및 구조화.
