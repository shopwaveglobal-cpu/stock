# source — Taesan 모니터링 시스템 설계서

- 원본: raw/inbox/2026-06-07-taesan-design.md (docs/superpowers/specs/에서 복사, git 커밋 951e171d)
- 날짜: 2026-06-07 (파일명 기준) / 유형: 시스템 설계서
- 주의: 이 설계서는 공개 저장소에 이미 커밋돼 있음. 단 wiki 요약에는 일관성을 위해 세부 수치를 옮기지 않는다 — 수치는 raw 참조

## 요약

KOSPI·KOSDAQ 전 보통주 대상 Taesan 스윙 모니터링 스캐너 설계. 매수 후보 1~5차 감지 + 가상 매수/매도 시뮬레이션. 주문 실행 없는 정보 시스템. 1차는 매수 알림 스캐너, 이후 개인 포트폴리오 모드 확장 예정.

## 핵심 사실 (원본 기재)

- **트레일링 상태기계**: 사이클 저점 L 추적 → 저점 대비 급등 시 랠리 추적(H 갱신) → 고점 대비 급락 시 H 동결·1차 매수 대기 → 재급등 시 사이클 리셋. "사후확신(hindsight) 고정 고점을 피해야 한다"가 명시된 설계 동기
- 매수 신호는 기준가 하락 후 **일봉 양봉 확인** 필수. 장 마감 30분 전 알림은 "미확정 후보"로만 발송
- **가상 매도 시뮬레이션을 스캐너 모드에서도 수행** — 매도 횟수가 다음 추가매수 기준(직전 매수가 vs 매수 후 최저가)을 바꾸기 때문
- 상한가·하한가 당일은 신호 미발생
- 시뮬레이션은 2020-01-01부터 (코로나 급락 구간 포함 검증)
- 상태 신호 5종: READY_NEAR / UNDER_LINE_WAIT_BULLISH / BULLISH_SIGNAL / NOT_READY / EXCLUDED

## 연결

- [decisions/2026-06-07-taesan-trailing-state-machine](../decisions/2026-06-07-taesan-trailing-state-machine.md)
- [concepts/cycle-state-machine](../concepts/cycle-state-machine.md) — OMG와 공유하는 패턴
- [sources/portfolio-logic-full](portfolio-logic-full.md) — 실제 상수는 taesan/config.py 기재
- [projects/stock-automation](../projects/stock-automation.md)
