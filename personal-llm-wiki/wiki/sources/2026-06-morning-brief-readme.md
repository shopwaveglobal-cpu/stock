# source — Morning Brief 데이터 적재 구조

- 원본: raw/inbox/2026-06-morning-brief-readme.md ("Morning Brief/README.md"에서 복사)
- 날짜: 추정 2026-06경 (본문의 시드 범위가 ~2026-06-09까지) / 유형: 운영 문서

## 요약

매크로 카드(카드3)용 데이터 파이프라인. 7개 지표의 일별 종가를 market_history.json에 누적하고 PNG 카드를 생성. 예약 작업 `morning-brief-data-append`가 화~토 07:00에 실행.

## 핵심 사실 (원본 기재)

- 지표 7종: gold, silver, btc, eth, usd(USD/KRW), eur(EUR/KRW), jpy
- **jpy 단위 함정**: 히스토리에는 "1엔당 원"으로 저장, 카드 표시만 ×100 — 값을 다룰 때 단위 혼동 주의
- update_history.py는 같은 날짜 재입력 시 덮어씀 (부분 업데이트 가능)
- 수집 경로: Chrome 연결 시 Yahoo, 아니면 웹검색

## 교차 확인 (2026-07-06)

- PORTFOLIO 총람의 Morning Brief 항목(지표 7종, jpy ×100 표시, 같은 날 덮어쓰기)과 일치 — 충돌 없음 ([sources/portfolio-logic-full](portfolio-logic-full.md))

## 연결

- [projects/stock-automation](../projects/stock-automation.md)
