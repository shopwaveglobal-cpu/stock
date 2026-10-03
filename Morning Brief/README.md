# Morning Brief — 데이터 적재 구조

## 폴더 구성

- `data/market_history.json` — 7개 지표 일별 종가 히스토리 (시드: 2025-12 ~ 2026-06-09, Yahoo Finance 실데이터)
- `update_history.py` — 당일 종가 1줄 추가 (같은 날짜는 덮어씀, 부분 업데이트 가능)
- `generate_card3.py` — 히스토리에서 카드3 PNG 생성 → `cards/`
- `cards/` — 생성된 카드 보관

## 매일 흐름 (예약 작업: morning-brief-data-append, 화 ~ 토 07:00)

1. 전일 종가 7개만 수집 (Chrome 연결 시 Yahoo, 아니면 웹검색)
2. `python3 update_history.py '{"date":"YYYY-MM-DD","gold":4260,...,"jpy":9.54}'`
3. `python3 generate_card3.py`

## 지표 키

gold(금 $/oz) · silver(은 $/oz) · btc · eth · usd(USD/KRW) · eur(EUR/KRW) · jpy(1엔당 원, 카드에는 ×100 표시)
