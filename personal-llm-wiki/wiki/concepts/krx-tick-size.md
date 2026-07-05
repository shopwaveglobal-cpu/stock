# concept — 한국 주식 호가 단위 (공개 정보)

가격 구간별 최소 호가 단위. S1/S12 매수선 계산(ceil_tick)과 StockCal 계산기가 공통 사용.

## 표 (사실, 출처: raw/inbox/PORTFOLIO_LOGIC_FULL.md — 원본에 "공개 정보, 마스킹 불필요" 명시)

| 가격 구간 | 호가 단위 |
|---|---|
| 2,000원 미만 | 1원 |
| 2,000 ~ 5,000원 | 5원 |
| 5,000 ~ 20,000원 | 10원 |
| 20,000 ~ 50,000원 | 50원 |
| 50,000 ~ 200,000원 | 100원 |
| 200,000 ~ 500,000원 | 500원 |
| 500,000원 이상 | 1,000원 |

## 사용처 (사실)

- S1/S12 매수선의 ceil_tick 반올림 (출처: raw/inbox/PORTFOLIO_LOGIC_FULL.md)
- StockCal iOS 포팅의 tickSize 테스트가 이 표와 동일 값 검증 (출처: raw/inbox/2026-06-10-stockcalc-ios-appstore.md, StockCalcEngineTests)

## 연결

- [sources/portfolio-logic-full](../sources/portfolio-logic-full.md)
- [sources/2026-06-10-stockcalc-ios-appstore](../sources/2026-06-10-stockcalc-ios-appstore.md)
