# DayOS Model Registry

> 최종 조사: 2026-10-31 · 출처: Hugging Face 공식 모델 카드·`config.json`·Hub API(파일 크기/commit), 기술 보고서 링크
> 기계 판독용 목록: [`registry/models.json`](../registry/models.json) (다운로드 스크립트가 사용)
> **검증되지 않은 값은 `미확인`으로 표기한다. 추정치는 `(추정)`으로 명시한다.**

## 0. 기록 규칙

- **공식 Benchmark**(제조사 발표)와 **DayOS 자체 평가**는 절대 같은 표에 섞지 않는다 (§4 vs §5).
- 공식 Benchmark는 제조사의 평가 조건(모드, 비교 대상, 버전)을 함께 기록한다. 서로 다른 표의 수치는 직접 비교하지 않는다.
- 파라미터 수만으로 비교하지 않는다. MoE는 Active Parameter, 정밀도, 컨텍스트, 실행 하드웨어를 함께 본다.
- 모든 다운로드는 Revision(commit hash)을 고정한다.

## 1. SKT A.X 계열 요약

개발사: **SK Telecom (대한민국)** — 전 모델 공통

| 항목 | A.X 3.1 Light | A.X 4.0 Light | A.X 3.1 | A.X 4.0 | A.X K1 | A.X K2 |
|---|---|---|---|---|---|---|
| HF repo | `skt/A.X-3.1-Light` | `skt/A.X-4.0-Light` | `skt/A.X-3.1` | `skt/A.X-4.0` | `skt/A.X-K1` | `skt/A.X-K2` |
| 공개일 (HF repo 생성) | 2025-07-10 | 2025-07-02 (발표 07-03) | 2025-07-23 | 2025-07-02 (발표 07-03) | 2025-12-29 | 2026-07-28 |
| 고정 Revision | `9b41bb2406…` | `ba21c20ea1…` | `1d99449133…` | `a3393fd67b…` | `bb56f50f36…` | `d0805cfd1f…` |
| 학습 방식 | 자체 from-scratch (1.65T tokens) | **Qwen2.5-7B 기반** 추가 학습 | 자체 from-scratch | **Qwen2.5-72B 기반** | 자체 from-scratch | 자체 from-scratch (8.2T tokens, FP8 native) |
| Architecture | Llama (dense) | Qwen2 (dense) | Llama (dense) | Qwen2 (dense) | MoE + MLA | MoE + MLA + Sparse Gated Attention |
| Dense / MoE | Dense | Dense | Dense | Dense | MoE (192+1 experts, top-8) | MoE (256+1 experts, top-8) |
| Total params | 7.26B | 7.26B | 34.7B | 71.9B | 519B | 688B |
| Active params | 7.26B | 7.26B | 34.7B | 71.9B | 33B | 33B |
| Context | 32,768 | 16,384 | 32,768 | 131,072 | 131,072 | 262,144 (128K native + YaRN) |
| 배포 정밀도 | BF16 | BF16 | BF16 | BF16 | BF16 | FP8 (E4M3 block) / 별도 NVFP4·GGUF |
| 다운로드 크기 | **14.5 GB** | **14.5 GB** | 69.4 GB | 143.8 GB | **1,038 GB** | **694 GB** (NVFP4 398GB, GGUF IQ4_XS 370GB) |
| Thinking 모드 | 없음 | 없음 | 없음 | 없음 | Think / Non-Think | Think / Non-Think |
| Tool calling | 지원 (vLLM `hermes` parser 예시) | 지원 (동일) | 카드 예시 있음 | 지원 | 미확인 (카드 내 언급 없음) | 지원 (vLLM `hermes`) |
| License | Apache-2.0 | Apache-2.0 | Apache-2.0 | **Qwen License** (MAU 1억 초과 시 별도 계약) | Apache-2.0 | Apache-2.0 |
| 상업적 사용 | 가능 | 가능 | 가능 | 조건부 가능 | 가능 | 가능 |
| 기술 보고서 | – | – | – | – | arXiv 2601.09200 | arXiv 2608.30181 |

> A.X 4.0 계열은 Qwen2.5(Alibaba, 중국) 기반이다. "소버린 AI" 요건이 있는 경우 3.1 / K1 / K2(from-scratch)와 구분해야 한다.

## 2. 이 Mac에서의 실행 가능성 (M2 Pro, 32GB 통합 메모리)

메모리 추정은 `가중치 + KV cache`이며, OS·앱이 약 8–10GB를 쓴다고 가정했다 `(추정)`.

| 모델 | 가중치 메모리 | KV cache (최대 컨텍스트) | Mac 실행 | 비고 |
|---|---|---|---|---|
| A.X 4.0 Light BF16 | ~14.5GB | ~0.9GB @16K (GQA 4 KV heads) `(추정)` | **가능** | MLX/transformers(MPS)/llama.cpp |
| A.X 4.0 Light Q4_K_M (GGUF, 커뮤니티) | ~4.4GB | ~0.9GB @16K | **가능, 여유** | `mykor/A.X-4.0-Light-gguf` — SKT 공식 아님 |
| A.X 3.1 Light BF16 | ~14.5GB | **~17GB @32K** (KV heads 32, GQA 없음) `(추정)` | 가능, 단 컨텍스트 8K 이하 권장 | 8K ≈ 4.3GB |
| A.X 3.1 BF16 | ~69GB | – | **불가** | 4-bit 양자화 시 ~20GB `(추정)`, 공식 양자화 없음 |
| A.X 4.0 BF16 | ~144GB | – | **불가** | |
| A.X K1 | ~1TB | – | **불가** | 공식 예시: 4노드 TP=32 |
| A.X K2 | ~647GiB (FP8) | – | **불가** | 공식: 총 GPU 메모리 ≥800GiB (B300×4) |

**결론:** 로컬 후보는 **A.X 4.0 Light**와 **A.X 3.1 Light** 두 개뿐이다. K1/K2/4.0/3.1은 로컬 다운로드 대상이 아니며, 필요하면 API 또는 클라우드 GPU로만 평가한다.

## 3. 비용

| 항목 | 값 |
|---|---|
| SKT A.X API 가격 | **미확인** (공개 가격표를 찾지 못함. 엔터프라이즈 문의: a.x@sk.com) |
| 로컬 추론 (Light, Mac) | 추가 비용 거의 없음. 전력 수십 W 수준 `(추정)` |
| K2 자가 호스팅 | B300급 GPU 4장 이상 필요 → 개인 개발 범위 밖. 클라우드 시간당 비용 **미확인** |
| 외장하드 | Light 모델 2종 + 캐시 + 데이터셋 샘플 기준 **≥100GB 여유** 권장 `(추정)`; K2 GGUF까지 고려하면 ≥1TB |

## 4. 공식 Benchmark (제조사 발표 — DayOS 평가 아님)

### 4.1 Light 모델 (출처: 각 HF 모델 카드, 비추론 모드 비교)

| Benchmark | 언어 | A.X 4.0 Light | A.X 3.1 Light | Qwen3-8B (w/o reasoning) |
|---|---|---:|---:|---:|
| KMMLU | ko | 64.15 | 61.70 | 63.53 |
| KMMLU-Pro | ko | 50.28 | 45.54 | 50.71 |
| CLIcK | ko | 68.05 | 71.22 | 62.71 / 63.31 ※ |
| KoBALT | ko | 30.29 | 27.43 | 26.57 |
| Ko-IFEval | ko | 72.99 | 70.04 | 73.39 |
| IFEval | en | 84.68 | 79.86 | 85.38 |
| MMLU | en | 75.43 | 66.95 | 82.89 |
| Ko-MT-Bench | ko | 79.50 | 78.56 | 64.06 |
| HRM8K | ko(math) | 40.12 | 41.70 | 52.50 |
| HumanEval+ | en(code) | 75.61 | 73.78 | 77.44 |
| Tool calling (FunctionChatBench 등) | – | 미확인 (Light 표에 없음) | 미확인 | – |

※ 두 모델 카드에서 같은 비교 모델의 CLIcK 점수가 다르게 보고됨(62.71 vs 63.31) → 카드 간 평가 조건 차이 가능성. 직접 비교 주의.

### 4.2 A.X 4.0 (72B) — FunctionChatBench(Tool-use) 85.96, KMMLU 78.32, LongBench<128K 56.70 (비교: GPT-4o 95.70 / 72.51 / 47.50). 출처: 모델 카드.

### 4.3 A.X K1 / K2 (Thinking 모드, 출처: 모델 카드)

| Benchmark | A.X K2 | A.X K1 (K2 카드 기준) |
|---|---:|---:|
| KMMLU-Pro | 80.5 | 68.9 |
| CLIcK | 91.6 | 85.3 |
| IFBench | 75.9 | 63.2 |
| τ²-Bench Telecom* | 98.0 | 86.0 |
| BrowseComp (≤10 searches) | 9.3 | – |
| AA-LCR | 66.0 | 26.0 |

\* Artificial Analysis 측정. K1 카드 자체 표에서는 KMMLU-Pro 68.1, τ² Telecom 58.1 → **K1 수치는 카드마다 평가 조건이 달라 값이 다름.** K2 카드는 에이전트 성능이 "moderate"라고 스스로 명시.

## 5. DayOS 자체 평가 (공식 수치와 분리)

| 모델 | Revision | 평가셋 | 지표 | 결과 | 날짜 |
|---|---|---|---|---|---|
| (아직 없음) | | | | | |

평가 계획(초안): 한국어 일정 생성 의도 파싱(slot filling), 알림 문구 생성, 추천 수용 여부 판단, **승인 기반 tool call** 정확도(사용자 승인 없이 일정 변경을 시도하는지 = 실패로 기록).

## 6. 다운로드 후보 판단 (§6 정책)

| 기준 | A.X 4.0 Light | A.X 3.1 Light | 4.0 Light GGUF Q4 | 그 외 |
|---|---|---|---|---|
| DayOS 기능에 필요? | 추천·알림 문구·의도 파싱 로컬 실험 | 소버린(from-scratch) 대안 비교 | 빠른 반복 실험 | 현재 불필요 |
| Mac에서 실행? | 예 | 예 (짧은 컨텍스트) | 예 | 아니오 |
| 외장하드 공간 | 14.5GB | 14.5GB | 4.4GB | 370GB–1TB |
| API 대비 로컬 합리성 | 개인정보(캘린더) 로컬 처리 이점 | 동일 | 동일 | API/클라우드가 합리적 |
| 개선 검증 가능? | §5 평가셋 구축 후 | 동일 | 동일 | – |

**권장 순서 (승인 필요):** ① `ax-4.0-light-gguf-q4km` (4.4GB) 또는 `ax-4.0-light` (14.5GB) → ② `ax-3.1-light` (14.5GB). 합계 최대 33.4GB + 헤드룸.

## 7. 공식 URL

- https://huggingface.co/skt (모델 목록)
- https://github.com/SKT-AI/A.X-K1 · https://github.com/SKT-AI/A.X-K2
- K2 변형: `skt/A.X-K2-NVFP4`, `skt/A.X-K2-GGUF`, `skt/A.X-K2-EAGLE3`, `skt/A.X-K2-DSpark`
- 기타: `skt/A.X-4.0-VL-Light`(비전), `skt/A.X-Encoder-base`(인코더), `skt/A.X-K2-ALM`(오디오) — 현재 DayOS 범위 밖, 미조사
