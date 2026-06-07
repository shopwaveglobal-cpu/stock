# Taesan Monitoring System Design

## Purpose

Build a Taesan swing monitoring system for all ordinary KOSPI and KOSDAQ stocks. The first release is a deployable scanner that sends buy-focused alerts, but its core must simulate the full Taesan strategy state so later portfolio management can reuse the same engine.

This is an information and monitoring system only. It does not place orders.

## Scope

### First Release

- Scan all KOSPI and KOSDAQ ordinary stocks.
- Exclude non-ordinary listings such as SPACs, ETFs, ETNs, preferred shares, REITs, halted/delisted names, and other special products where detectable.
- Run Taesan state simulation from at least 2020-01-01 so the COVID crash period is included in validation.
- Detect 1st through 5th buy candidates.
- Simulate virtual buys and virtual sells according to Taesan rules.
- Use the simulated sell count to decide the next add-buy basis.
- Send buy-focused alerts near the close and after daily confirmation.
- Generate Excel/CSV reports for review and manual trading decisions.

### Later Release

- Add personal portfolio mode.
- Allow the user to enter actual buy/sell fills, quantities, and average prices.
- Compare strategy-simulated state with personal actual state.
- Add sell-focused alerts for the user's actual holdings.

## Strategy Rules

### Cycle Start and High Tracking

Taesan must avoid hindsight-based fixed highs. It uses a trailing state machine.

1. Track the cycle low `L`.
2. When `high >= L * 2.0`, the stock has risen at least 100% from its low and enters rally tracking.
3. While no 50% drawdown has happened, update `H = max(H, today_high)`.
4. When `low <= H * 0.50`, freeze that cycle high and enter 1st-buy waiting.
5. If the stock later rises 100% from the current cycle low, reset the cycle and start again.

### Buy Rules

The scanner tracks 1st through 5th buy candidates.

- 1st buy: after a 50% drawdown from `H`, the first daily bullish candle.
- 2nd buy: after the 1st virtual buy, wait for a drop of at least 10% from the applicable basis, then the next daily bullish candle.
- 3rd buy: same rule from the 2nd basis.
- 4th buy: same rule from the 3rd basis.
- 5th buy: same rule from the 4th basis.

A bullish candle means `close > open` on the daily candle. Near-close monitoring may use `current_price > open` only as a pre-close candidate alert, not as a confirmed signal.

### Add-Buy Basis Rule

The add-buy basis changes after enough strategy sells have occurred.

- If `virtual_sell_count < 3`, the next add-buy basis is the previous virtual buy price.
- If `virtual_sell_count >= 3`, the next add-buy basis is the lowest price updated after the latest buy.
- In both cases, the candidate zone is basis price minus 10%, followed by a bullish daily candle.

### Virtual Sell Rules

Even in public scanner mode, sells are simulated from strategy rules so the scanner can know whether the next add-buy should use the previous buy price or the post-buy low.

Virtual sells occur when one of these levels is touched:

- Average virtual buy price +5%.
- Average virtual buy price +10%.
- Average virtual buy price +15%.
- Average virtual buy price +20%.
- Average virtual buy price +25%.
- MA20, MA60, or MA120 touch, even if the position is at a loss.

Profit target sells are treated as 20% position reductions each. Moving-average sells are additional strategy sell events. The system records `virtual_sell_count`, `remaining_virtual_position_pct`, and which targets have already been sold.

No buy or sell signal is emitted on limit-up or limit-down days.

## Alert Model

### Daily Scan

After market close, the batch scanner analyzes all stocks and writes the next-day watch list.

Signal classes:

- `READY_NEAR`: price is above the next buy trigger but close enough to watch.
- `UNDER_LINE_WAIT_BULLISH`: price has moved below the next buy trigger and is waiting for a bullish candle.
- `BULLISH_SIGNAL`: daily candle confirms a buy candidate.
- `NOT_READY`: strategy state exists but no actionable setup.
- `EXCLUDED`: stock excluded from the universe.

### Pre-Close Alert

Around 30 minutes before close, monitor only the watch list from the previous scan.

Send alerts for `UNDER_LINE_WAIT_BULLISH` stocks where the current price is above the day's open. The alert text must clearly say this is a pre-close candidate and needs end-of-day confirmation.

### Confirmed Daily Report

After the close, send a confirmed report containing:

- Confirmed 1st through 5th buy candidates.
- Near candidates for the next day.
- Current simulated Taesan stage.
- Next buy trigger price.
- Add-buy basis type: previous buy price or post-buy low.
- Virtual buy count, virtual sell count, virtual average price, and remaining virtual position percentage.

## Architecture

Create a new `taesan/` folder rather than modifying S1 or S12 directly.

Planned modules:

- `config.py`: paths, thresholds, scan settings, alert settings.
- `kiwoom_client.py`: Kiwoom token and market data calls.
- `universe_builder.py`: KOSPI/KOSDAQ universe and exclusions.
- `taesan_state_machine.py`: pure strategy simulation, no API calls or file writes.
- `daily_scanner.py`: fetch historical data, run simulations, write reports.
- `preclose_monitor.py`: monitor previous watch list near close.
- `report_writer.py`: Excel and CSV output.
- `telegram_notifier.py`: Telegram alerts.
- `slack_notifier.py`: Slack alerts.
- `trading_day_utils.py`: trading day and market-hour helpers.

Output files:

- `output/taesan_universe.xlsx`
- `output/taesan_signals.xlsx`
- `output/taesan_state_snapshots.csv`
- `output/taesan_events.csv`
- `output/taesan_backtest_2020.csv`

## Data Model

Core simulated fields:

- `ticker`
- `name`
- `market`
- `date`
- `mode`
- `cycle_low`
- `cycle_high`
- `drawdown_trigger_price`
- `buy_stage`
- `next_buy_stage`
- `next_buy_trigger_price`
- `next_buy_basis_price`
- `next_buy_basis_type`
- `post_buy_low`
- `virtual_buy_count`
- `virtual_sell_count`
- `virtual_avg_price`
- `remaining_virtual_position_pct`
- `sold_profit_targets`
- `sold_ma_targets`
- `signal_class`
- `event`

## Backtest and Validation

Validation must include data from 2020-01-01 onward, including the COVID crash period.

The first validation pass should not optimize returns. Its purpose is to prove the state machine behaves correctly:

- Highs are updated before a 50% drawdown is confirmed.
- 1st buy appears only after the first bullish candle after the drawdown zone.
- 2nd through 5th buy candidates follow the correct basis.
- Virtual sell counts change the add-buy basis after 3 or more sells.
- A 100% rise from the current cycle low resets the cycle.
- Limit-up and limit-down days suppress buy/sell events.

Manual review artifacts:

- A summary sheet sorted by current actionable candidates.
- Event logs for selected stocks.
- Per-stock debug CSV for difficult cases.

## Pre-Deployment Review Loop

The system should not be treated as deployment-ready after the first implementation pass. Before full deployment, it must go through repeated data and backtest review with the user.

The review loop is:

1. Run the scanner and backtest over the full available history from 2020-01-01 onward.
2. Select representative stocks, including COVID-crash names, strong rebound names, failed rebound names, and ambiguous edge cases.
3. Review per-stock event logs with the user.
4. Check whether each Taesan event matches the intended interpretation of the strategy.
5. Fix rule interpretation, state transitions, filters, or alert wording when the simulation disagrees with the intended behavior.
6. Re-run the same cases after each rule change.
7. Promote to deployment only after the scanner produces stable and explainable results across repeated review passes.

Each review pass should preserve its output under `output/reviews/` with a timestamp so results can be compared across rule changes.

## Open Implementation Notes

- Historical data depth must be enough to cover 2020 onward. If Kiwoom limits daily candle history per call, pagination or cached incremental history will be required.
- Financial filters are intentionally delayed. The first release should leave a filter interface where revenue, operating profit, and net income rules can be added.
- Public scanner results are strategy-simulated state, not the user's actual filled position. Alerts must use wording such as "virtual strategy state" where relevant.

---

# 태산 모니터링 시스템 설계

## 목적

코스피와 코스닥의 일반 종목 전체를 대상으로 태산 스윙 기법을 감시하는 시스템을 만든다. 1차 버전은 매수 후보를 찾아 알림을 주는 배포용 스캐너지만, 내부 엔진은 태산의 매수와 매도 상태를 가상으로 시뮬레이션해야 한다. 그래야 나중에 개인 보유 포지션 관리 기능을 같은 엔진 위에 붙일 수 있다.

이 시스템은 정보 제공과 모니터링용이며, 실제 주문은 실행하지 않는다.

## 1차 범위

- 코스피와 코스닥 전체 일반 종목을 스캔한다.
- 스팩, ETF, ETN, 우선주, 리츠, 거래정지/상장폐지 종목 등 일반 종목이 아닌 대상은 가능한 범위에서 제외한다.
- 2020-01-01 이후 데이터를 기준으로 태산 상태를 시뮬레이션한다. 코로나 폭락 구간 검증을 반드시 포함한다.
- 1차부터 5차까지 매수 후보를 탐지한다.
- 태산 규칙에 따라 가상 매수와 가상 매도를 시뮬레이션한다.
- 가상 매도 횟수를 기준으로 다음 추가매수 기준을 결정한다.
- 장마감 전 후보 알림과 장마감 후 확정 리포트를 보낸다.
- 검토용 엑셀과 CSV 리포트를 생성한다.

## 추후 범위

- 개인 포트폴리오 모드를 추가한다.
- 사용자가 실제 매수/매도 체결가, 수량, 평단을 입력할 수 있게 한다.
- 전략상 가상 상태와 사용자의 실제 보유 상태를 비교한다.
- 실제 보유 종목 기준 매도 알림을 추가한다.

## 전략 규칙

### 사이클 시작과 고점 추적

태산은 결과론적으로 고점을 고정하면 안 된다. 실시간으로 갱신되는 상태 머신으로 처리한다.

1. 현재 사이클의 저점 `L`을 추적한다.
2. `high >= L * 2.0` 이 되면 저점 대비 100% 이상 상승한 것으로 보고 상승 추적 상태로 들어간다.
3. 아직 50% 하락이 나오지 않았다면 `H = max(H, today_high)` 로 고점을 계속 갱신한다.
4. `low <= H * 0.50` 이 처음 나오면 그 시점의 `H`를 기준 고점으로 확정하고 1차 매수 대기 상태로 들어간다.
5. 이후 현재 사이클 저점 대비 다시 100% 상승하면 기존 사이클을 리셋하고 새 사이클을 시작한다.

### 매수 규칙

- 1차 매수: `H` 대비 50% 이상 하락한 뒤 나오는 첫 일봉 양봉.
- 2차 매수: 1차 가상 매수가 이후 적용 기준가에서 10% 이상 하락한 뒤 나오는 일봉 양봉.
- 3차 매수: 2차 기준에서 같은 방식.
- 4차 매수: 3차 기준에서 같은 방식.
- 5차 매수: 4차 기준에서 같은 방식.

일봉 양봉은 `종가 > 시가`로 정의한다. 장마감 전 모니터링에서는 `현재가 > 시가`를 예비 후보로 볼 수 있지만, 확정 신호는 장마감 후 일봉 기준으로만 판단한다.

### 추가매수 기준 전환

전략상 매도 횟수에 따라 다음 추가매수 기준이 바뀐다.

- `virtual_sell_count < 3`: 직전 가상 매수가 대비 -10% 이후 양봉을 기다린다.
- `virtual_sell_count >= 3`: 최신 매수 이후 갱신되는 최저가 대비 -10% 이후 양봉을 기다린다.

따라서 공용 스캐너에서도 실제 사용자의 매도 기록이 없어도, 태산 규칙상 가상 매도 이벤트를 계산해서 다음 추가매수 기준을 판단할 수 있다.

### 가상 매도 규칙

공용 스캐너에서도 매도는 가상으로 시뮬레이션한다. 그래야 매도 횟수가 3회 이상인지 판단할 수 있다.

가상 매도는 아래 조건에서 발생한다.

- 가상 평단 대비 +5%.
- 가상 평단 대비 +10%.
- 가상 평단 대비 +15%.
- 가상 평단 대비 +20%.
- 가상 평단 대비 +25%.
- 20일선, 60일선, 120일선 터치. 손실 상태여도 매도 이벤트로 기록한다.

수익 목표 매도는 각각 20% 비중 매도로 본다. 이동평균선 매도는 추가 매도 이벤트로 기록한다. 시스템은 `virtual_sell_count`, `remaining_virtual_position_pct`, 이미 매도된 수익 목표와 이동평균 목표를 저장한다.

점상과 점하에서는 매수/매도 신호를 내지 않는다.

## 알림 구조

### 장마감 후 일일 스캔

장마감 후 전체 종목을 분석해서 다음날 볼 종목 리스트를 만든다.

분류는 다음과 같다.

- `READY_NEAR`: 아직 다음 매수선 위에 있지만 근접 중인 종목.
- `UNDER_LINE_WAIT_BULLISH`: 이미 다음 매수선 아래로 내려왔고 양봉만 기다리는 종목.
- `BULLISH_SIGNAL`: 일봉 양봉까지 확정된 매수 후보.
- `NOT_READY`: 태산 상태는 있으나 당장 볼 신호는 없는 종목.
- `EXCLUDED`: 제외 대상 종목.

### 장마감 30분 전 알림

장마감 약 30분 전에는 전 종목을 다시 보는 것이 아니라, 전날 생성된 관심군만 본다.

`UNDER_LINE_WAIT_BULLISH` 종목 중 현재가가 당일 시가보다 높은 종목만 알림을 보낸다. 메시지에는 반드시 “장마감 전 후보이며 종가 확정 필요”라는 뜻이 들어가야 한다.

### 장마감 후 확정 리포트

장마감 후 리포트에는 다음 내용을 포함한다.

- 1차부터 5차까지 확정 매수 후보.
- 다음날 볼 근접 후보.
- 현재 가상 태산 단계.
- 다음 매수 트리거 가격.
- 추가매수 기준 유형: 직전 매수가 기준 또는 매수 이후 최저가 기준.
- 가상 매수 횟수, 가상 매도 횟수, 가상 평단, 남은 가상 포지션 비중.

## 아키텍처

S1이나 S12를 직접 수정하지 않고 새 `taesan/` 폴더를 만든다.

예상 파일 구조:

- `config.py`: 경로, 기준값, 스캔 설정, 알림 설정.
- `kiwoom_client.py`: 키움 토큰과 시세 데이터 호출.
- `universe_builder.py`: 코스피/코스닥 유니버스 생성과 제외 처리.
- `taesan_state_machine.py`: 순수 전략 시뮬레이션. API 호출과 파일 저장 없음.
- `daily_scanner.py`: 과거 데이터 수집, 시뮬레이션 실행, 리포트 생성.
- `preclose_monitor.py`: 장마감 전 관심군 모니터링.
- `report_writer.py`: 엑셀과 CSV 출력.
- `telegram_notifier.py`: 텔레그램 알림.
- `slack_notifier.py`: 슬랙 알림.
- `trading_day_utils.py`: 거래일과 장중 시간 유틸리티.

예상 출력 파일:

- `output/taesan_universe.xlsx`
- `output/taesan_signals.xlsx`
- `output/taesan_state_snapshots.csv`
- `output/taesan_events.csv`
- `output/taesan_backtest_2020.csv`

## 데이터 모델

핵심 상태 컬럼:

- `ticker`: 종목 코드.
- `name`: 종목명.
- `market`: 시장.
- `date`: 기준일.
- `mode`: 현재 태산 상태.
- `cycle_low`: 현재 사이클 저점.
- `cycle_high`: 현재 사이클 고점.
- `drawdown_trigger_price`: 50% 하락 기준 가격.
- `buy_stage`: 현재 매수 단계.
- `next_buy_stage`: 다음 매수 단계.
- `next_buy_trigger_price`: 다음 매수 트리거 가격.
- `next_buy_basis_price`: 다음 매수 기준가.
- `next_buy_basis_type`: 직전 매수가 기준인지, 매수 이후 최저가 기준인지.
- `post_buy_low`: 최신 매수 이후 갱신된 최저가.
- `virtual_buy_count`: 가상 매수 횟수.
- `virtual_sell_count`: 가상 매도 횟수.
- `virtual_avg_price`: 가상 평단.
- `remaining_virtual_position_pct`: 남은 가상 포지션 비중.
- `sold_profit_targets`: 이미 매도된 수익 목표.
- `sold_ma_targets`: 이미 매도된 이동평균 목표.
- `signal_class`: 현재 알림 분류.
- `event`: 해당 일자에 발생한 이벤트.

## 백테스트와 검증

검증은 반드시 2020-01-01 이후 데이터를 포함한다. 코로나 폭락 구간은 필수 검증 대상이다.

첫 검증의 목적은 수익률 최적화가 아니라 상태 머신이 의도대로 움직이는지 확인하는 것이다.

확인할 항목:

- 50% 하락이 확정되기 전까지 고점이 계속 갱신되는지.
- 1차 매수가 50% 하락 구간 이후 첫 양봉에서만 발생하는지.
- 2차부터 5차 매수가 올바른 기준가를 따르는지.
- 가상 매도 횟수 3회 이상부터 추가매수 기준이 바뀌는지.
- 현재 사이클 저점 대비 100% 상승하면 사이클이 리셋되는지.
- 점상/점하에서는 매수와 매도 이벤트가 억제되는지.

검토 산출물:

- 현재 매수 후보 중심 요약 시트.
- 종목별 이벤트 로그.
- 애매한 케이스 검토용 종목별 디버그 CSV.

## 배포 전 리뷰 루프

이 시스템은 첫 구현이 끝났다고 바로 완전 배포용으로 보지 않는다. 배포 전에는 사용자와 함께 데이터와 백테스트를 반복 검토해야 한다.

리뷰 루프:

1. 2020-01-01 이후 전체 데이터로 스캐너와 백테스트를 돌린다.
2. 코로나 폭락 종목, 강한 반등 종목, 반등 실패 종목, 애매한 경계 케이스를 골라 본다.
3. 종목별 이벤트 로그를 사용자와 함께 확인한다.
4. 각 태산 이벤트가 실제 의도한 전략 해석과 맞는지 확인한다.
5. 시뮬레이션 결과가 의도와 다르면 규칙 해석, 상태 전환, 필터, 알림 문구를 수정한다.
6. 수정 후 같은 케이스를 다시 돌려 비교한다.
7. 여러 번의 리뷰에서도 결과가 안정적이고 설명 가능할 때만 배포 단계로 올린다.

각 리뷰 결과는 `output/reviews/` 아래에 타임스탬프를 붙여 저장한다. 그래야 규칙 변경 전후 결과를 비교할 수 있다.

## 구현 메모

- 2020년 이후 데이터를 충분히 가져올 수 있어야 한다. 키움 일봉 API가 한 번에 가져오는 기간을 제한한다면 페이지네이션이나 캐시 기반 누적 저장이 필요하다.
- 재무 필터는 1차에서는 미룬다. 다만 매출액, 영업이익, 당기순이익 조건을 나중에 붙일 수 있도록 필터 인터페이스는 남겨둔다.
- 공용 스캐너 결과는 실제 사용자 체결 상태가 아니라 전략상 가상 상태다. 알림 문구에는 필요할 때 “전략상 가상 상태”라는 의미가 드러나야 한다.
