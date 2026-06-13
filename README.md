# MarketBrief

**Automated, self-hosted market-intelligence pipeline.** MarketBrief monitors
equities (KOSPI / NASDAQ) and cryptocurrencies in real time, generates scheduled
daily briefings, and delivers actionable alerts straight to Slack — so an
investor gets a clear, pushed summary where they already work instead of staring
at charts.

It runs in production today on a daily schedule, generating and delivering
reports automatically.

---

## What it does

| Module | What it does |
|--------|--------------|
| **Real-time stock monitor** (`S12/Real_Time_Monitor.py`) | 24/7 loop that watches a watchlist, computes a live 20-day moving average, and alerts when price approaches a buy line — once per state per day to avoid spam. Idle outside trading hours/days. |
| **KOSPI 20MA tracker** (`kospi_20ma.py`) | Pulls KOSPI OHLCV, tracks the 20-day moving average, and fires Slack alerts on key crossings. |
| **Crypto real-time monitor** (`omg/crypto_realtime_monitor.py`) | 5-minute polling against per-coin reference levels with cutoff/forbidden-level alert logic and daily auto-refresh. |
| **NASDAQ morning brief** (`nasdaq_brief/`) | Fetches data, renders briefing cards, and posts a morning summary to Slack. |
| **Morning Brief cards** (`Morning Brief/`) | Maintains a daily close history for 7 macro indicators (gold, silver, BTC, ETH, USD/KRW, EUR/KRW, JPY) and renders summary cards. |
| **Slack / Telegram delivery** (`omg/slack_notifier.py`, `omg/telegram_notifier.py`) | Multi-channel push of reports and alerts using Slack Block Kit. |

## Highlights

- **Production-ready scheduling** — Windows Task Scheduler + watchdog supervisors
  keep monitors running 24/7 and restart them on failure.
- **Spam-aware alerting** — state-based de-duplication ensures one alert per
  meaningful event per day, not a flood.
- **Multi-market** — Korean equities, US equities, and crypto in one toolkit.
- **Real data sources** — Naver Finance, Yahoo Finance, exchange APIs.

## Tech stack

Python · pandas · requests · BeautifulSoup · `schedule` · Slack Block Kit ·
Telegram Bot API

## Getting started

```bash
# 1. Install dependencies
pip install -r nasdaq_brief/requirements.txt   # pandas, requests, beautifulsoup4, holidays, schedule ...

# 2. Configure delivery (environment variables)
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"

# 3. Run a monitor
python kospi_20ma.py                       # KOSPI 20-day MA tracker
python omg/crypto_realtime_monitor.py      # crypto real-time monitor
python S12/Real_Time_Monitor.py            # 24/7 stock monitor
```

## Status & roadmap

MarketBrief is an actively-developed, early-stage project running in real daily
use. Near-term roadmap:

- [ ] Package the report engine and alerting modules as an installable library
- [ ] Cross-platform scheduling (systemd / cron) alongside Windows
- [ ] Configurable watchlists and alert rules via a single config file
- [ ] Test coverage and CI

## License

MIT (see `LICENSE`).
