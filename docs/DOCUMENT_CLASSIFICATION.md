# 문서 공개 범위 분류

> 상태: 초안 v0.1 (2026-11-08) · 이 저장소는 **현재 Public**이다. 공개 저장소에 올린 내용은 삭제해도 Git 기록에 남을 수 있으므로, 민감한 내용은 처음부터 커밋하지 않는다.

## 1. 분류

| 구분 | 내용 | 관리 |
|---|---|---|
| **공개** | README(Product Vision, High-level Architecture), 제품 원칙, 요구사항 수준 문서, 평가 항목 정의, 가상 시나리오, 저작권 고지 | 저장소 `docs/` |
| **비공개 (커밋 금지)** | 개인화 내부 로직(신호 가중치, 순위·필터 규칙, 프롬프트), 평가 케이스 원본·정답 기준, 평가 결과 상세, 사업·가격·수익 모델, 사용자 데이터, 계정·키 | 로컬 `private/` (Git 제외) 또는 오너가 고른 별도 비공개 저장소 |
| **재검토 필요** | `DATA_STRATEGY.md`(데이터 활용 전략 부분), `MODEL_REGISTRY.md`의 자체 평가 결과, `TECH_OPTIONS.md`의 비용·사업 판단 | 오너 결정 |

## 2. 규칙

1. 비공개 항목은 `/private/` 아래에만 두며 `.gitignore`로 막는다.
2. 이미 공개된 문서(`DATA_STRATEGY.md`, `MODEL_REGISTRY.md`, `TECH_OPTIONS.md`)는 이 PR에서 삭제·이동하지 않는다. 옮길지는 오너가 정한다. (Git 기록에는 남는다)
3. 공개 README는 Product Vision과 High-level Architecture, 저작권 고지만 담는다.
4. 비공개 문서가 생기면 파일명과 한 줄 목적만 이 문서에 적는다. 내용은 적지 않는다.

## 3. 비공개 문서 목록 (내용 없음, 이름만)

| 파일 | 목적 | 상태 |
|---|---|---|
| `private/PERSONALIZATION_LOGIC.md` | 신호 가중치, 요약 규칙, 프롬프트 설계 | 아직 없음 (구현 직전에 작성) |
| `private/EVAL_CASES.md` | 평가 케이스·정답 기준 | 아직 없음 |
| `private/BUSINESS.md` | 가격·수익·사업 판단 | 아직 없음 |
