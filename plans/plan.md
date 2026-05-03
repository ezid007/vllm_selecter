# Project Plan — vLLM Selecter

이 문서는 프로젝트의 진행 상황과 향후 계획을 추적합니다.

## Phase 1: 시스템 구축 (Complete)

- [x] 프로젝트 디렉토리 구조 확인
- [x] 가상 환경(`.venv`) 생성
- [x] `hesamation/Qwen3.6-35B-A3B-Claude-4.6-Opus-Reasoning-Distilled` 모델 분석 완료
- [x] `readme.md` 초기화 및 모델 상세 정보 기록
- [x] `/home/aiis/vllm_selecter/`에 독립 실행형 필수 파일 재구성 완료
    - [x] `.env` 초기화
    - [x] `run_vllm_bg.py` (vLLM 실행 엔진)
    - [x] `select_vllm.py` (인터랙티브 선택 인터페이스)
- [x] `.bashrc` 알리아스 신규 경로 연동 완료
- [x] 컨테이너 이름 `qwen-vllm` 통일
- [x] 기본 선택값(1번: 122B) 설정

## Phase 2: vLLM 0.20.0 업그레이드 (In Progress)

- [x] 문제 진단: 2번 모델(Qwen 3.6 35B) `TokenizersBackend` 토크나이저 오류 확인
- [x] 근본 원인 분석: vLLM 0.18.2 + transformers 4.57이 최신 토크나이저 클래스 미지원
- [x] `run_vllm_bg.py` 코드 정리: sed 패치 워크어라운드 제거, v0.20.0 기준 리팩토링
- [x] `--language-model-only` 옵션 적용 (텍스트 전용 모델 메모리 최적화)
- [x] 문서 업데이트 (README, CHANGELOG, plan.md)
- [x] Docker 이미지 빌드: `build-and-copy.sh --vllm-ref v0.20.0 --tf5 --rebuild-vllm`
- [x] 빌드 완료 후 2번 모델 정상 실행 테스트
- [x] 1번 모델(122B) 호환성 테스트 완료 (OOM 및 MoE 백엔드 충돌 문제 해결)
- [x] 보안 및 유연성 강화: 하드코딩된 Docker 설정값(컨테이너 명, SHM, 네트워크) .env 이전 완료

## Phase 3: 시스템 안정화 및 고도화 (In Progress)

- [x] 인터랙티브 Thinking 모드 선택 기능 구현 (`select_vllm.py`)
- [ ] 모델 벤치마크 수행:
   - MMLU-Pro 등 실제 성능 테스트를 위한 harness 구축.
2. **vLLM 서빙 최적화**:
   - Grace Blackwell 환경에서 최적화된 설정값(Context Window, Chunk Size, MTP 등) 미세 조정.
   - MTP (Multi-Token Prediction) 활성화 검토: `--speculative-config` 옵션 (v0.20.0 신기능).
3. **추가 모델 등록**:
   - 새로운 모델이 로컬에 다운로드될 경우 `select_vllm.py`의 MODELS 리스트와 `TEXT_ONLY_MODELS` 리스트 업데이트.
4. **모니터링 기능**:
   - vLLM 서버 헬스체크 및 자동 재시작 로직 구현 검토.
