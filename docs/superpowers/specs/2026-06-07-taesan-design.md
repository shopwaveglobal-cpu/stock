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
