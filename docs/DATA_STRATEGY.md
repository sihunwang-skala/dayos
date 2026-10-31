# DayOS Data Strategy

> 최종 조사: 2026-10-31 · 기계 판독용 목록: [`registry/datasets.json`](../registry/datasets.json)
> **검증되지 않은 값은 `미확인`으로 표기한다.**

## 1. 원칙

1. **샘플 우선.** 전체 데이터가 필요하다는 근거(평가 설계)가 생기기 전에는 `sample`만 받는다.
2. **원본은 외장하드**(`$DAYOS_ASSETS_ROOT/datasets/raw/`), GitHub에는 다운로드 스크립트·registry·manifest 형식만 둔다.
3. **Revision 고정.** URL은 commit hash가 포함된 raw URL, HF는 commit sha를 쓴다.
4. **개인정보·라이선스 확인 전에는 다운로드하지 않는다.** 실제 사용자 화면·로그가 포함된 데이터는 메타데이터만 받는다.
5. 마이크로데이터(통계청 MDIS 등)는 **수동 신청·수동 다운로드**만 허용한다. 스크립트는 안내만 출력한다.
6. DayOS 원칙과의 정합성: 이 데이터들은 *의도 파싱, 알림 문구, 선택적 추천, 승인 기반 에이전트*의 평가에 쓴다. **AI가 일정을 임의 재배치하도록 학습시키는 용도로 쓰지 않는다.**

## 2. 데이터셋 목록

| 데이터셋 | 공개 | 규모 | 형식 | 라이선스 / 상업적 사용 | 개인정보 | DayOS 활용 | 스크립트 |
|---|---|---|---|---|---|---|---|
| **SMCalFlow** (Microsoft Semantic Machines) | 2020 (TACL 2020) | 대화 약 4만 건 규모 `미확인(정확한 수치)` | JSONL, dataflow program | **CC BY-SA 4.0** — 상업 가능, 파생 데이터에 ShareAlike 적용 | 크라우드소싱 대화, 낮음 | 캘린더 자연어 → 구조화(일정 생성/수정/참석자 참조) 파싱 평가 | 비활성 (공식 아카이브 URL 고정 필요) |
| **Taskmaster-1** (Google) | 2019 (EMNLP) | 13,215 대화 (spoken 5,507 / written 7,708), 6개 도메인 | JSON | **CC BY 4.0** — 상업 가능(출처 표기) | WoZ·크라우드, 낮음 | 예약형 slot filling, 확인 질문(clarification) 패턴 | `taskmaster1` |
| **Taskmaster-2** (Google) | 2020 | 7개 도메인 JSON 합계 약 123MB | JSON | **CC BY 4.0** | 낮음 | 다중 도메인 slot filling | `taskmaster2` (sample = food-ordering 5.4MB) |
| **Taskmaster-3** | 2020 | 영화 티켓 도메인 `미확인(규모)` | JSON | CC BY 4.0 `미확인(재확인)` | 낮음 | 보조 | 미등록 |
| **ProactiveAgent / ProactiveBench** (THUNLP) | 2024-09 (arXiv 2410.12361) | 이벤트 6,790건 (repo README 기준) | JSON / YAML | **Apache-2.0** | 생성·주석 데이터, 낮음 | **선제 제안(proactive suggestion) 수용/거절 예측** — DayOS "선택적 AI 추천"의 핵심 평가 | `proactive-agent` (sample 3 files) |
| **ProAgentBench** (HF `qv9n2xk7m1z8pt4/ProAgentBench`) | HF 2026-05-05 | 참가자 17명, 이벤트 28,528, 스크린샷 167,423, 10–100GB | SQLite + PNG | `other` — **미확인** | **높음** (실사용자 화면, 익명 업로더, 출처 논문 미확인) | 실사용 맥락 기반 선제 지원 평가 | `proagentbench` (README만, full 차단) |
| **NL2API** | 2017 (Su et al., CIKM, Microsoft) `미확인(데이터 공개 여부)` | 미확인 | 미확인 | 미확인 | 미확인 | 자연어 → API 호출 | 미등록. 대안: BFCL 등 tool-calling 평가셋 검토 필요 |
| **한국 생활시간조사** (통계청, 현 국가데이터처 `미확인(기관명 개편)`) | 1999년부터 5년 주기, 최신 2024년 조사 (결과 2025 공표) | 2024년: 약 12,750가구 10세 이상, 2일 × 10분 간격 시간일지 | 집계표(KOSIS), 마이크로데이터(MDIS) | MDIS 이용약관 — 재배포 제한, 상업 이용 **미확인** | 비식별 처리되나 미시자료 → 내부 보관만 | 한국인 하루 시간 배분 prior (기상·식사·수면 시간대 → 알림 시간 기본값) | `kr-time-use` (manual) |
| **ATUS** (미국 BLS) | 2003년부터 매년; 2025년 결과 2026-06-25 공표 | 2025년 약 6,100명 `(보도 기준)` | CSV/DAT | 미국 연방정부 저작물(퍼블릭 도메인) `미확인(재확인)` | 식별정보 제거 | 활동 시퀀스·시간대 분포 (한국 데이터와 비교 baseline). 2025 Q4는 셧다운 영향 주의 | `atus` (manual) |

## 3. 다운로드 정책

```bash
python3 scripts/download-dataset.py --list
python3 scripts/download-dataset.py taskmaster2 --dry-run      # 크기·라이선스·대상 경로
python3 scripts/download-dataset.py taskmaster2                 # sample (승인 후)
python3 scripts/download-dataset.py taskmaster2 --full          # 근거가 있을 때만
```

- `url` 소스: 외장하드 `tmp/`에 받아 원자적으로 이동, 로컬 SHA-256을 manifest에 기록.
- `hf` 소스: `HF_*` 캐시를 외장하드로 설정한 뒤 `snapshot_download`.
- `manual` 소스: 안내문만 출력하고 종료.
- 모든 다운로드는 `$DAYOS_ASSETS_ROOT/manifests/dataset-<key>-<variant>.json`에 기록.

## 4. 미해결 항목

- SMCalFlow 공식 데이터 아카이브 URL·버전 확정 후 `registry/datasets.json` 활성화
- ProAgentBench 출처 논문·라이선스·동의 절차 확인 전까지 full 다운로드 금지
- NL2API가 가리키는 정확한 데이터셋 확인 (사용자/기획 측 확인 필요)
- 생활시간조사 2024 마이크로데이터 MDIS 제공 여부·이용 조건 확인
- 한국어 일정/캘린더 대화 데이터는 공개셋이 부족 → DayOS 자체 합성/수집 데이터 정책 별도 수립 필요
