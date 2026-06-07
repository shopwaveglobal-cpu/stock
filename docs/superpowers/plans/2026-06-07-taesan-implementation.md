# Taesan Scanner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first Taesan scanner that can simulate strategy state from 2020 onward, produce buy-focused candidate reports, and preserve review artifacts for double-checking before deployment.

**Architecture:** Create a new `taesan/` package. Keep the Taesan strategy as a pure state machine with no API or file I/O, then layer data fetching, report writing, and review runners around it. The first implementation intentionally stops before production scheduling and full alert delivery so strategy behavior can be reviewed with historical cases.

**Tech Stack:** Python, pandas, openpyxl, requests, python-dotenv, pytest, Kiwoom REST API patterns copied from `S12`.

---

## File Structure

- Create `taesan/__init__.py`: package marker.
- Create `taesan/config.py`: constants for thresholds, dates, paths, and market settings.
- Create `taesan/models.py`: dataclasses and enums for candles, state, events, and scan results.
- Create `taesan/state_machine.py`: pure Taesan simulation from daily candles to snapshots/events.
- Create `taesan/report_writer.py`: CSV and Excel output for scanner and review artifacts.
- Create `taesan/backtest_runner.py`: command-line runner for historical simulations from cached CSV data.
- Create `taesan/kiwoom_client.py`: minimal Kiwoom API wrapper, adapted from S12 later in the plan.
- Create `taesan/daily_scanner.py`: daily scanner orchestration.
- Create `taesan/preclose_monitor.py`: near-close candidate checker stub for the first release.
- Create `taesan/README.md`: Korean usage guide.
- Create `tests/taesan/test_state_machine.py`: unit tests for the strategy rules.
- Create `tests/taesan/test_report_writer.py`: report output tests.
- Create `tests/taesan/fixtures/*.csv`: small synthetic candle fixtures.
- Modify root or `taesan/requirements.txt`: add `pytest` if missing.

---

## Task 1: Scaffold Package and Models

**Files:**
- Create: `taesan/__init__.py`
- Create: `taesan/config.py`
- Create: `taesan/models.py`
- Test: `tests/taesan/test_state_machine.py`

- [ ] **Step 1: Write the initial model import test**

Create `tests/taesan/test_state_machine.py`:

```python
from taesan.models import Candle, SignalClass, TaesanMode


def test_models_import_and_construct():
    candle = Candle(
        date="2020-03-19",
        open=100.0,
        high=120.0,
        low=90.0,
        close=110.0,
    )

    assert candle.is_bullish is True
    assert TaesanMode.BASE.value == "BASE"
    assert SignalClass.NOT_READY.value == "NOT_READY"
```

- [ ] **Step 2: Run the test and verify it fails**

Run:

```powershell
python -m pytest tests/taesan/test_state_machine.py -v
```

Expected: FAIL because `taesan.models` does not exist.

- [ ] **Step 3: Create the package files**

Create `taesan/__init__.py`:

```python
"""Taesan stock monitoring package."""
```

Create `taesan/config.py`:

```python
from pathlib import Path

TAESAN_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = TAESAN_DIR / "output"
REVIEW_DIR = OUTPUT_DIR / "reviews"

BACKTEST_START_DATE = "2020-01-01"
RALLY_MULTIPLIER = 2.0
DRAWDOWN_MULTIPLIER = 0.50
ADD_BUY_DROP_PCT = 10.0
MAX_BUY_STAGE = 5
PROFIT_TARGET_PCTS = (5, 10, 15, 20, 25)
MA_TARGETS = (20, 60, 120)
NEAR_DISTANCE_PCT = 5.0
```

Create `taesan/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class TaesanMode(str, Enum):
    BASE = "BASE"
    RALLY = "RALLY"
    WAIT_BUY = "WAIT_BUY"


class SignalClass(str, Enum):
    READY_NEAR = "READY_NEAR"
    UNDER_LINE_WAIT_BULLISH = "UNDER_LINE_WAIT_BULLISH"
    BULLISH_SIGNAL = "BULLISH_SIGNAL"
    NOT_READY = "NOT_READY"
    EXCLUDED = "EXCLUDED"


class BasisType(str, Enum):
    LAST_BUY_PRICE = "LAST_BUY_PRICE"
    POST_BUY_LOW = "POST_BUY_LOW"


@dataclass(frozen=True)
class Candle:
    date: str
    open: float
    high: float
    low: float
    close: float

    @property
    def is_bullish(self) -> bool:
        return self.close > self.open


@dataclass
class TaesanEvent:
    date: str
    event: str
    stage: Optional[int]
    price: Optional[float]
    note: str = ""


@dataclass
class TaesanSnapshot:
    ticker: str
    name: str
    date: str
    mode: TaesanMode
    cycle_low: Optional[float]
    cycle_high: Optional[float]
    buy_stage: int
    next_buy_stage: Optional[int]
    next_buy_trigger_price: Optional[float]
    next_buy_basis_price: Optional[float]
    next_buy_basis_type: Optional[BasisType]
    post_buy_low: Optional[float]
    virtual_buy_count: int
    virtual_sell_count: int
    virtual_avg_price: Optional[float]
    remaining_virtual_position_pct: float
    sold_profit_targets: Tuple[int, ...] = field(default_factory=tuple)
    sold_ma_targets: Tuple[int, ...] = field(default_factory=tuple)
    signal_class: SignalClass = SignalClass.NOT_READY
    event: str = ""
```

- [ ] **Step 4: Run the test and verify it passes**

Run:

```powershell
python -m pytest tests/taesan/test_state_machine.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add taesan/__init__.py taesan/config.py taesan/models.py tests/taesan/test_state_machine.py
git commit -m "Add Taesan package models"
```

---

## Task 2: Implement Cycle High Tracking and First Buy

**Files:**
- Create: `taesan/state_machine.py`
- Modify: `tests/taesan/test_state_machine.py`

- [ ] **Step 1: Add failing tests for trailing high and first bullish buy**

Append to `tests/taesan/test_state_machine.py`:

```python
from taesan.models import SignalClass, TaesanMode
from taesan.state_machine import simulate_taesan


def test_trailing_high_updates_until_first_50pct_drawdown():
    candles = [
        Candle("2020-01-02", 100, 100, 100, 100),
        Candle("2020-01-03", 100, 200, 95, 190),
        Candle("2020-01-06", 190, 260, 180, 250),
        Candle("2020-01-07", 250, 270, 140, 150),
        Candle("2020-01-08", 150, 160, 130, 155),
    ]

    result = simulate_taesan("000001", "TEST", candles)
    last = result.snapshots[-1]

    assert last.mode == TaesanMode.WAIT_BUY
    assert last.cycle_high == 270
    assert result.events[-1].event == "BUY_1"
    assert last.signal_class == SignalClass.BULLISH_SIGNAL


def test_first_buy_waits_for_bullish_candle_after_drawdown():
    candles = [
        Candle("2020-01-02", 100, 100, 100, 100),
        Candle("2020-01-03", 100, 210, 95, 200),
        Candle("2020-01-06", 200, 220, 100, 90),
        Candle("2020-01-07", 90, 100, 88, 85),
        Candle("2020-01-08", 85, 95, 80, 92),
    ]

    result = simulate_taesan("000001", "TEST", candles)

    buy_events = [event for event in result.events if event.event == "BUY_1"]
    assert len(buy_events) == 1
    assert buy_events[0].date == "2020-01-08"
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m pytest tests/taesan/test_state_machine.py -v
```

Expected: FAIL because `simulate_taesan` is not implemented.

- [ ] **Step 3: Implement minimal cycle and first-buy logic**

Create `taesan/state_machine.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .config import ADD_BUY_DROP_PCT, DRAWDOWN_MULTIPLIER, MAX_BUY_STAGE, NEAR_DISTANCE_PCT, RALLY_MULTIPLIER
from .models import BasisType, Candle, SignalClass, TaesanEvent, TaesanMode, TaesanSnapshot


@dataclass
class TaesanSimulationResult:
    ticker: str
    name: str
    snapshots: List[TaesanSnapshot]
    events: List[TaesanEvent]


def _classify_signal(candle: Candle, trigger_price: Optional[float]) -> SignalClass:
    if trigger_price is None:
        return SignalClass.NOT_READY
    if candle.close <= trigger_price and candle.is_bullish:
        return SignalClass.BULLISH_SIGNAL
    if candle.low <= trigger_price:
        return SignalClass.UNDER_LINE_WAIT_BULLISH
    distance_pct = ((candle.close - trigger_price) / trigger_price) * 100
    if 0 < distance_pct <= NEAR_DISTANCE_PCT:
        return SignalClass.READY_NEAR
    return SignalClass.NOT_READY


def _weighted_average(existing_avg: Optional[float], existing_pct: float, add_price: float, add_pct: float) -> float:
    if existing_avg is None or existing_pct <= 0:
        return add_price
    return ((existing_avg * existing_pct) + (add_price * add_pct)) / (existing_pct + add_pct)


def simulate_taesan(ticker: str, name: str, candles: Iterable[Candle]) -> TaesanSimulationResult:
    snapshots: List[TaesanSnapshot] = []
    events: List[TaesanEvent] = []
    rows = list(candles)

    mode = TaesanMode.BASE
    cycle_low: Optional[float] = None
    cycle_high: Optional[float] = None
    buy_stage = 0
    virtual_buy_count = 0
    virtual_sell_count = 0
    virtual_avg_price: Optional[float] = None
    remaining_pct = 0.0
    last_buy_price: Optional[float] = None
    post_buy_low: Optional[float] = None

    for candle in rows:
        event_name = ""
        if cycle_low is None or candle.low < cycle_low:
            cycle_low = candle.low

        if mode == TaesanMode.BASE and cycle_low and candle.high >= cycle_low * RALLY_MULTIPLIER:
            mode = TaesanMode.RALLY
            cycle_high = candle.high

        if mode == TaesanMode.RALLY:
            cycle_high = max(cycle_high or candle.high, candle.high)
            if candle.low <= cycle_high * DRAWDOWN_MULTIPLIER:
                mode = TaesanMode.WAIT_BUY

        next_stage = buy_stage + 1 if buy_stage < MAX_BUY_STAGE else None
        if next_stage == 1 and cycle_high:
            trigger_price = cycle_high * DRAWDOWN_MULTIPLIER
            basis_price = cycle_high
            basis_type = BasisType.LAST_BUY_PRICE
        elif next_stage and last_buy_price:
            basis_price = last_buy_price
            basis_type = BasisType.LAST_BUY_PRICE
            trigger_price = basis_price * (1 - ADD_BUY_DROP_PCT / 100.0)
        else:
            trigger_price = None
            basis_price = None
            basis_type = None

        if mode == TaesanMode.WAIT_BUY and next_stage and trigger_price and candle.low <= trigger_price and candle.is_bullish:
            buy_stage = next_stage
            virtual_buy_count += 1
            fill_price = candle.close
            last_buy_price = fill_price
            post_buy_low = candle.low
            virtual_avg_price = _weighted_average(virtual_avg_price, remaining_pct, fill_price, 20.0)
            remaining_pct += 20.0
            event_name = f"BUY_{buy_stage}"
            events.append(TaesanEvent(candle.date, event_name, buy_stage, fill_price))

        signal_class = _classify_signal(candle, trigger_price)
        if event_name:
            signal_class = SignalClass.BULLISH_SIGNAL

        snapshots.append(TaesanSnapshot(
            ticker=ticker,
            name=name,
            date=candle.date,
            mode=mode,
            cycle_low=cycle_low,
            cycle_high=cycle_high,
            buy_stage=buy_stage,
            next_buy_stage=buy_stage + 1 if buy_stage < MAX_BUY_STAGE else None,
            next_buy_trigger_price=trigger_price,
            next_buy_basis_price=basis_price,
            next_buy_basis_type=basis_type,
            post_buy_low=post_buy_low,
            virtual_buy_count=virtual_buy_count,
            virtual_sell_count=virtual_sell_count,
            virtual_avg_price=virtual_avg_price,
            remaining_virtual_position_pct=remaining_pct,
            signal_class=signal_class,
            event=event_name,
        ))

    return TaesanSimulationResult(ticker=ticker, name=name, snapshots=snapshots, events=events)
```

- [ ] **Step 4: Run tests and verify pass**

Run:

```powershell
python -m pytest tests/taesan/test_state_machine.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add taesan/state_machine.py tests/taesan/test_state_machine.py
git commit -m "Implement Taesan cycle and first buy simulation"
```

---

## Task 3: Add 1st Through 5th Buy Stages and 3-Sell Basis Switch

**Files:**
- Modify: `taesan/state_machine.py`
- Modify: `tests/taesan/test_state_machine.py`

- [ ] **Step 1: Add failing tests for staged buys and post-buy-low basis**

Append to `tests/taesan/test_state_machine.py`:

```python
def test_add_buy_uses_last_buy_price_before_three_virtual_sells():
    candles = [
        Candle("2020-01-02", 100, 100, 100, 100),
        Candle("2020-01-03", 100, 220, 95, 210),
        Candle("2020-01-06", 210, 220, 100, 90),
        Candle("2020-01-07", 90, 120, 88, 110),
        Candle("2020-01-08", 110, 112, 98, 99),
        Candle("2020-01-09", 99, 105, 95, 104),
    ]

    result = simulate_taesan("000001", "TEST", candles)
    buy_events = [event.event for event in result.events if event.event.startswith("BUY_")]

    assert buy_events == ["BUY_1", "BUY_2"]
    assert result.snapshots[-1].next_buy_stage == 3
    assert result.snapshots[-1].next_buy_basis_type == BasisType.LAST_BUY_PRICE


def test_add_buy_uses_post_buy_low_after_three_virtual_sells():
    candles = [
        Candle("2020-01-02", 100, 100, 100, 100),
        Candle("2020-01-03", 100, 220, 95, 210),
        Candle("2020-01-06", 210, 220, 100, 90),
        Candle("2020-01-07", 90, 140, 88, 110),
        Candle("2020-01-08", 110, 135, 100, 132),
        Candle("2020-01-09", 132, 133, 80, 90),
        Candle("2020-01-10", 90, 100, 70, 95),
    ]

    result = simulate_taesan("000001", "TEST", candles)
    last = result.snapshots[-1]

    assert last.virtual_sell_count >= 3
    assert last.next_buy_basis_type == BasisType.POST_BUY_LOW
    assert last.next_buy_basis_price == 70
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m pytest tests/taesan/test_state_machine.py -v
```

Expected: FAIL because virtual sells and post-buy-low basis switching are not complete.

- [ ] **Step 3: Implement virtual sell counting and basis selection**

Modify `taesan/state_machine.py`:

```python
from .config import ADD_BUY_DROP_PCT, DRAWDOWN_MULTIPLIER, MAX_BUY_STAGE, NEAR_DISTANCE_PCT, PROFIT_TARGET_PCTS, RALLY_MULTIPLIER
```

Add helpers above `simulate_taesan`:

```python
def _sell_targets_hit(high: float, avg_price: Optional[float], sold_targets: set[int]) -> list[int]:
    if avg_price is None:
        return []
    hits: list[int] = []
    for pct in PROFIT_TARGET_PCTS:
        if pct in sold_targets:
            continue
        if high >= avg_price * (1 + pct / 100.0):
            hits.append(pct)
    return hits


def _next_basis(virtual_sell_count: int, last_buy_price: Optional[float], post_buy_low: Optional[float]) -> tuple[Optional[float], Optional[BasisType]]:
    if virtual_sell_count >= 3 and post_buy_low is not None:
        return post_buy_low, BasisType.POST_BUY_LOW
    if last_buy_price is not None:
        return last_buy_price, BasisType.LAST_BUY_PRICE
    return None, None
```

Inside `simulate_taesan`, initialize:

```python
sold_profit_targets: set[int] = set()
```

After updating `post_buy_low`, before computing the next trigger:

```python
if remaining_pct > 0 and post_buy_low is not None:
    post_buy_low = min(post_buy_low, candle.low)

for pct in _sell_targets_hit(candle.high, virtual_avg_price, sold_profit_targets):
    sold_profit_targets.add(pct)
    virtual_sell_count += 1
    remaining_pct = max(0.0, remaining_pct - 20.0)
    events.append(TaesanEvent(candle.date, f"SELL_PROFIT_{pct}", buy_stage, virtual_avg_price, f"avg+{pct}%"))
```

Replace add-buy basis calculation with:

```python
elif next_stage:
    basis_price, basis_type = _next_basis(virtual_sell_count, last_buy_price, post_buy_low)
    trigger_price = basis_price * (1 - ADD_BUY_DROP_PCT / 100.0) if basis_price else None
```

Set `sold_profit_targets=tuple(sorted(sold_profit_targets))` in the snapshot constructor.

- [ ] **Step 4: Run tests and verify pass**

Run:

```powershell
python -m pytest tests/taesan/test_state_machine.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add taesan/state_machine.py tests/taesan/test_state_machine.py
git commit -m "Add Taesan staged buys and sell-count basis switch"
```

---

## Task 4: Add Moving Average Sell Events and Cycle Reset

**Files:**
- Modify: `taesan/state_machine.py`
- Modify: `tests/taesan/test_state_machine.py`

- [ ] **Step 1: Add failing tests for moving-average sells and 100% reset**

Append to `tests/taesan/test_state_machine.py`:

```python
def test_ma_touch_records_virtual_sell_event():
    candles = [Candle(f"2020-01-{day:02d}", 100, 100, 90, 95) for day in range(2, 22)]
    candles += [
        Candle("2020-01-22", 95, 200, 90, 190),
        Candle("2020-01-23", 190, 200, 100, 90),
        Candle("2020-01-24", 90, 130, 80, 120),
    ]

    result = simulate_taesan("000001", "TEST", candles)

    assert any(event.event.startswith("SELL_MA20") for event in result.events)


def test_cycle_resets_after_100pct_rise_from_current_cycle_low():
    candles = [
        Candle("2020-01-02", 100, 100, 100, 100),
        Candle("2020-01-03", 100, 220, 95, 210),
        Candle("2020-01-06", 210, 220, 100, 90),
        Candle("2020-01-07", 90, 120, 80, 110),
        Candle("2020-01-08", 110, 170, 80, 165),
    ]

    result = simulate_taesan("000001", "TEST", candles)

    assert any(event.event == "CYCLE_RESET_100PCT" for event in result.events)
    assert result.snapshots[-1].mode == TaesanMode.RALLY
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
python -m pytest tests/taesan/test_state_machine.py -v
```

Expected: FAIL because MA sells and post-buy cycle reset are missing.

- [ ] **Step 3: Implement MA calculations and reset**

Add helper functions:

```python
def _moving_average(candles: list[Candle], end_idx: int, period: int) -> Optional[float]:
    start = end_idx - period + 1
    if start < 0:
        return None
    window = candles[start:end_idx + 1]
    return sum(c.close for c in window) / period


def _touches_level(candle: Candle, price: Optional[float]) -> bool:
    if price is None:
        return False
    return candle.low <= price <= candle.high
```

In the loop, use `for idx, candle in enumerate(rows):`.

Initialize:

```python
sold_ma_targets: set[int] = set()
```

After profit sell logic:

```python
if remaining_pct > 0:
    for period in MA_TARGETS:
        if period in sold_ma_targets:
            continue
        ma_price = _moving_average(rows, idx, period)
        if _touches_level(candle, ma_price):
            sold_ma_targets.add(period)
            virtual_sell_count += 1
            remaining_pct = max(0.0, remaining_pct - 20.0)
            events.append(TaesanEvent(candle.date, f"SELL_MA{period}", buy_stage, ma_price, "moving average touch"))
```

Before normal mode processing, add cycle reset when a current cycle low doubles:

```python
if cycle_low is not None and candle.high >= cycle_low * RALLY_MULTIPLIER and buy_stage > 0:
    mode = TaesanMode.RALLY
    cycle_high = candle.high
    buy_stage = 0
    virtual_buy_count = 0
    virtual_sell_count = 0
    virtual_avg_price = None
    remaining_pct = 0.0
    last_buy_price = None
    post_buy_low = None
    sold_profit_targets.clear()
    sold_ma_targets.clear()
    event_name = "CYCLE_RESET_100PCT"
    events.append(TaesanEvent(candle.date, event_name, None, candle.high))
```

Set `sold_ma_targets=tuple(sorted(sold_ma_targets))` in snapshots.

- [ ] **Step 4: Run tests and verify pass**

Run:

```powershell
python -m pytest tests/taesan/test_state_machine.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add taesan/state_machine.py tests/taesan/test_state_machine.py
git commit -m "Add Taesan moving-average sells and cycle reset"
```

---

## Task 5: Write CSV and Excel Reports

**Files:**
- Create: `taesan/report_writer.py`
- Create: `tests/taesan/test_report_writer.py`

- [ ] **Step 1: Add failing report writer test**

Create `tests/taesan/test_report_writer.py`:

```python
from pathlib import Path

import pandas as pd

from taesan.models import Candle
from taesan.report_writer import write_review_outputs
from taesan.state_machine import simulate_taesan


def test_write_review_outputs_creates_csv_and_xlsx(tmp_path: Path):
    candles = [
        Candle("2020-01-02", 100, 100, 100, 100),
        Candle("2020-01-03", 100, 220, 95, 210),
        Candle("2020-01-06", 210, 220, 100, 90),
        Candle("2020-01-07", 90, 120, 80, 110),
    ]
    result = simulate_taesan("000001", "TEST", candles)

    paths = write_review_outputs([result], tmp_path, "review_test")

    assert paths["snapshots_csv"].exists()
    assert paths["events_csv"].exists()
    assert paths["workbook"].exists()
    df = pd.read_csv(paths["events_csv"])
    assert "BUY_1" in set(df["event"])
```

- [ ] **Step 2: Run test and verify failure**

Run:

```powershell
python -m pytest tests/taesan/test_report_writer.py -v
```

Expected: FAIL because `report_writer` is missing.

- [ ] **Step 3: Implement report writer**

Create `taesan/report_writer.py`:

```python
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable

import pandas as pd

from .state_machine import TaesanSimulationResult


def _snapshot_rows(results: Iterable[TaesanSimulationResult]) -> list[dict]:
    rows: list[dict] = []
    for result in results:
        for snapshot in result.snapshots:
            row = asdict(snapshot)
            row["mode"] = snapshot.mode.value
            row["signal_class"] = snapshot.signal_class.value
            row["next_buy_basis_type"] = snapshot.next_buy_basis_type.value if snapshot.next_buy_basis_type else ""
            rows.append(row)
    return rows


def _event_rows(results: Iterable[TaesanSimulationResult]) -> list[dict]:
    rows: list[dict] = []
    for result in results:
        for event in result.events:
            row = asdict(event)
            row["ticker"] = result.ticker
            row["name"] = result.name
            rows.append(row)
    return rows


def write_review_outputs(results: list[TaesanSimulationResult], output_dir: Path, label: str) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshots_csv = output_dir / f"{label}_snapshots.csv"
    events_csv = output_dir / f"{label}_events.csv"
    workbook = output_dir / f"{label}.xlsx"

    snapshots_df = pd.DataFrame(_snapshot_rows(results))
    events_df = pd.DataFrame(_event_rows(results))

    snapshots_df.to_csv(snapshots_csv, index=False, encoding="utf-8-sig")
    events_df.to_csv(events_csv, index=False, encoding="utf-8-sig")

    latest_df = snapshots_df.sort_values(["ticker", "date"]).groupby("ticker", as_index=False).tail(1)
    candidates_df = latest_df[latest_df["signal_class"].isin(["READY_NEAR", "UNDER_LINE_WAIT_BULLISH", "BULLISH_SIGNAL"])]

    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        candidates_df.to_excel(writer, sheet_name="Candidates", index=False)
        latest_df.to_excel(writer, sheet_name="Latest", index=False)
        events_df.to_excel(writer, sheet_name="Events", index=False)

    return {
        "snapshots_csv": snapshots_csv,
        "events_csv": events_csv,
        "workbook": workbook,
    }
```

- [ ] **Step 4: Run report tests**

Run:

```powershell
python -m pytest tests/taesan/test_report_writer.py -v
```

Expected: PASS.

- [ ] **Step 5: Run all Taesan tests**

Run:

```powershell
python -m pytest tests/taesan -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add taesan/report_writer.py tests/taesan/test_report_writer.py
git commit -m "Add Taesan review report writer"
```

---

## Task 6: Add Backtest Runner for Cached CSV Data

**Files:**
- Create: `taesan/backtest_runner.py`
- Create: `tests/taesan/fixtures/sample_000001.csv`

- [ ] **Step 1: Create a sample fixture CSV**

Create `tests/taesan/fixtures/sample_000001.csv`:

```csv
date,open,high,low,close
2020-01-02,100,100,100,100
2020-01-03,100,220,95,210
2020-01-06,210,220,100,90
2020-01-07,90,120,80,110
```

- [ ] **Step 2: Add a runner smoke test**

Append to `tests/taesan/test_report_writer.py`:

```python
from taesan.backtest_runner import load_candles_from_csv, run_cached_backtest


def test_cached_backtest_runner_reads_csv_and_writes_outputs(tmp_path: Path):
    source = Path("tests/taesan/fixtures/sample_000001.csv")

    candles = load_candles_from_csv(source)
    assert candles[0].date == "2020-01-02"

    paths = run_cached_backtest(
        inputs=[("000001", "TEST", source)],
        output_dir=tmp_path,
        label="cached_review",
    )

    assert paths["workbook"].exists()
```

- [ ] **Step 3: Run tests and verify failure**

Run:

```powershell
python -m pytest tests/taesan/test_report_writer.py -v
```

Expected: FAIL because `backtest_runner` does not exist.

- [ ] **Step 4: Implement cached backtest runner**

Create `taesan/backtest_runner.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Tuple

import pandas as pd

from .config import REVIEW_DIR
from .models import Candle
from .report_writer import write_review_outputs
from .state_machine import simulate_taesan


def load_candles_from_csv(path: Path) -> list[Candle]:
    df = pd.read_csv(path)
    required = {"date", "open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {path}: {sorted(missing)}")
    return [
        Candle(
            date=str(row["date"]),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
        )
        for _, row in df.iterrows()
    ]


def run_cached_backtest(inputs: Iterable[Tuple[str, str, Path]], output_dir: Path = REVIEW_DIR, label: str = "taesan_review"):
    results = []
    for ticker, name, path in inputs:
        candles = load_candles_from_csv(path)
        results.append(simulate_taesan(ticker, name, candles))
    return write_review_outputs(results, output_dir, label)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Taesan backtest from cached OHLC CSV files.")
    parser.add_argument("--input-dir", required=True, help="Directory containing CSV files with date/open/high/low/close columns.")
    parser.add_argument("--output-dir", default=str(REVIEW_DIR), help="Directory for review outputs.")
    parser.add_argument("--label", default="taesan_review", help="Output file label.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    inputs = []
    for path in sorted(input_dir.glob("*.csv")):
        ticker = path.stem
        inputs.append((ticker, ticker, path))

    paths = run_cached_backtest(inputs, Path(args.output_dir), args.label)
    for key, path in paths.items():
        print(f"{key}: {path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests**

Run:

```powershell
python -m pytest tests/taesan -v
```

Expected: PASS.

- [ ] **Step 6: Run the CLI smoke test**

Run:

```powershell
python -m taesan.backtest_runner --input-dir tests/taesan/fixtures --output-dir taesan/output/reviews --label smoke
```

Expected:

```text
snapshots_csv: taesan\output\reviews\smoke_snapshots.csv
events_csv: taesan\output\reviews\smoke_events.csv
workbook: taesan\output\reviews\smoke.xlsx
```

- [ ] **Step 7: Commit**

```powershell
git add taesan/backtest_runner.py tests/taesan/fixtures/sample_000001.csv tests/taesan/test_report_writer.py
git commit -m "Add Taesan cached backtest runner"
```

---

## Task 7: Add Kiwoom Client and Daily Scanner Skeleton

**Files:**
- Create: `taesan/kiwoom_client.py`
- Create: `taesan/daily_scanner.py`
- Create: `taesan/preclose_monitor.py`
- Create: `taesan/README.md`

- [ ] **Step 1: Implement Kiwoom client skeleton**

Create `taesan/kiwoom_client.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests

from .models import Candle


KIWOOM_BASE_URL = "https://api.kiwoom.com"
KIWOOM_TOKEN_URL = "https://api.kiwoom.com/oauth2/token"


@dataclass
class KiwoomClient:
    appkey: str
    secret: str
    token: Optional[str] = None

    def get_access_token(self) -> str:
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        body = {"grant_type": "client_credentials", "appkey": self.appkey, "secretkey": self.secret}
        response = requests.post(KIWOOM_TOKEN_URL, headers=headers, json=body, timeout=20)
        response.raise_for_status()
        data = response.json()
        token = data.get("token") or data.get("access_token")
        if not token:
            raise RuntimeError(f"Kiwoom token missing from response: {data}")
        self.token = token
        return token

    def fetch_daily_candles(self, ticker: str, start_date: str = "2020-01-01") -> list[Candle]:
        raise NotImplementedError("Wire this to the Kiwoom daily candle endpoint after confirming pagination limits.")
```

- [ ] **Step 2: Implement daily scanner skeleton**

Create `taesan/daily_scanner.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from .backtest_runner import run_cached_backtest
from .config import REVIEW_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Taesan scanner.")
    parser.add_argument("--cached-input-dir", help="Use cached CSV candles instead of Kiwoom API.")
    parser.add_argument("--output-dir", default=str(REVIEW_DIR))
    parser.add_argument("--label", default="taesan_daily")
    args = parser.parse_args()

    if not args.cached_input_dir:
        raise SystemExit("First implementation supports --cached-input-dir. Kiwoom universe scan is added after data pagination is confirmed.")

    input_dir = Path(args.cached_input_dir)
    inputs = [(path.stem, path.stem, path) for path in sorted(input_dir.glob("*.csv"))]
    paths = run_cached_backtest(inputs, Path(args.output_dir), args.label)
    for key, path in paths.items():
        print(f"{key}: {path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Implement pre-close monitor skeleton**

Create `taesan/preclose_monitor.py`:

```python
from __future__ import annotations


def main() -> None:
    raise SystemExit("Pre-close monitoring will be enabled after daily scanner output is validated with historical reviews.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Add Korean README**

Create `taesan/README.md`:

```markdown
# Taesan Scanner

태산 스윙 기법을 코스피/코스닥 전체 일반 종목에 적용하기 위한 상태 시뮬레이션 기반 스캐너입니다.

## 현재 단계

완전 배포 전 검증 단계입니다. 먼저 2020년 이후 일봉 데이터로 백테스트를 반복 실행하고, 사용자와 이벤트 로그를 더블체크합니다.

## 캐시 CSV 백테스트

CSV 컬럼:

- `date`
- `open`
- `high`
- `low`
- `close`

실행:

```powershell
python -m taesan.daily_scanner --cached-input-dir tests/taesan/fixtures --output-dir taesan/output/reviews --label smoke
```

출력:

- `*_snapshots.csv`
- `*_events.csv`
- `*.xlsx`
```

- [ ] **Step 5: Run all tests**

Run:

```powershell
python -m pytest tests/taesan -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add taesan/kiwoom_client.py taesan/daily_scanner.py taesan/preclose_monitor.py taesan/README.md
git commit -m "Add Taesan scanner entry points"
```

---

## Task 8: Final Verification and Review Artifact

**Files:**
- No new code unless verification exposes a bug.

- [ ] **Step 1: Run Taesan unit tests**

Run:

```powershell
python -m pytest tests/taesan -v
```

Expected: all tests PASS.

- [ ] **Step 2: Generate a smoke review artifact**

Run:

```powershell
python -m taesan.daily_scanner --cached-input-dir tests/taesan/fixtures --output-dir taesan/output/reviews --label smoke
```

Expected output files:

- `taesan/output/reviews/smoke_snapshots.csv`
- `taesan/output/reviews/smoke_events.csv`
- `taesan/output/reviews/smoke.xlsx`

- [ ] **Step 3: Inspect the smoke event CSV**

Run:

```powershell
Import-Csv taesan/output/reviews/smoke_events.csv | Format-Table
```

Expected: at least one `BUY_1` event row for `sample_000001`.

- [ ] **Step 4: Check git status**

Run:

```powershell
git status --short
```

Expected: no uncommitted Taesan source/test changes except generated review artifacts if intentionally left untracked.

---

## Self-Review

Spec coverage:

- All-stock KOSPI/KOSDAQ API collection is represented by `kiwoom_client.py` and `daily_scanner.py`, but full pagination is intentionally gated until historical data limits are confirmed.
- Pure state simulation, 1st through 5th buy candidates, virtual sell count basis switching, MA sells, cycle reset, and review output are covered by Tasks 1-6.
- Pre-close alerts and Slack/Telegram delivery are not in this first implementation plan. They should be a second plan after historical state behavior is reviewed.
- The 2020 COVID validation requirement is supported through cached CSV backtests and review artifact preservation.

Placeholder scan:

- No implementation step uses open-ended TODO wording.
- The only `NotImplementedError` is explicit in `KiwoomClient.fetch_daily_candles` because API pagination must be confirmed before wiring production data. This is a deliberate deployment gate, not a hidden implementation placeholder.

Type consistency:

- `Candle`, `TaesanSnapshot`, `TaesanEvent`, `TaesanMode`, `SignalClass`, and `BasisType` are defined before use.
- `simulate_taesan` returns `TaesanSimulationResult`, which is consumed by `report_writer` and `backtest_runner`.

