# concept — 사이클 상태기계 패턴 (저점→급등→고점→급락→매수 대기)

두 시스템(OMG 크립토, Taesan 한국주식)이 독립적으로 같은 구조를 사용 — 이 포트폴리오의 핵심 매매 프레임.

## 공통 구조 (사실)

1. 사이클 **저점 L**을 추적한다
2. 저점 대비 일정 배율 급등 시 **랠리 모드** — 고점 H를 갱신
3. 고점 대비 일정 비율 급락 시 **H 동결, 매수 대기 모드** 진입
4. 분할 매수 후, 반등·목표 도달 시 분할 매도
5. 저점 대비 재급등 시 **사이클 리셋** (모든 상태 초기화)

## 시스템별 구현 (배율·비율 등 실수치는 raw 참조)

| 시스템 | 대상 | 상수 위치 | 출처 |
|---|---|---|---|
| OMG Phase 1.5 | 크립토 (Binance 일봉) | raw/inbox/PORTFOLIO_LOGIC_FULL.md | 동 파일 |
| Taesan | KOSPI·KOSDAQ 보통주 | taesan/config.py (PORTFOLIO 총람 기재) | raw/inbox/2026-06-07-taesan-design.md |

## 설계 원칙 (원본 근거)

- 고점은 사후 선택이 아니라 **트레일링으로 실시간 판정** ([decisions/2026-06-07-taesan-trailing-state-machine](../decisions/2026-06-07-taesan-trailing-state-machine.md))
- 순수 상태기계로 구현 (I/O 없음) — 같은 입력이면 같은 출력, 백테스트 재현 가능 (출처: omg/CLAUDE.md 설계 노트)

## 연결

- [sources/2026-06-07-taesan-design](../sources/2026-06-07-taesan-design.md)
- [sources/portfolio-logic-full](../sources/portfolio-logic-full.md)
