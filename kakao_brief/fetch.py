"""Yahoo chart 엔드포인트로 시세 수집 (키 불필요, 비공식). LLM/검색 호출 없음."""
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import requests

from config import INDICES, MACRO, SECTORS, TOP_N

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=10d&interval=1d"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_one(sym, retries=3):
    for i in range(retries):
        try:
            r = requests.get(URL.format(sym), headers=HEADERS, timeout=15)
            r.raise_for_status()
            res = r.json()["chart"]["result"][0]
            bars = [(t, c) for t, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]) if c is not None]
            if len(bars) < 2:
                return None
            closes = [c for _, c in bars]
            return {
                "sym": sym,
                "close": closes[-1],
                "prev": closes[-2],
                "chg": closes[-1] - closes[-2],
                "pct": (closes[-1] / closes[-2] - 1) * 100,
                "hist": closes[-5:],
                "date": datetime.fromtimestamp(bars[-1][0], timezone.utc).strftime("%Y-%m-%d"),
            }
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def fetch_many(syms):
    with ThreadPoolExecutor(max_workers=8) as ex:
        return dict(zip(syms, ex.map(fetch_one, syms)))


def collect():
    """지수 4 + 섹터 ETF 11 + 매크로 7 → 상·하위 섹터 대표종목 최대 18. 없는 값은 None."""
    base = [s for _, s in INDICES] + [e for e, _, _ in SECTORS] + [m[1] for m in MACRO]
    data = fetch_many(base)
    ranked = sorted((e for e, _, _ in SECTORS if data.get(e)), key=lambda e: data[e]["pct"], reverse=True)
    picked = ranked[:TOP_N] + ranked[-TOP_N:]
    stocks = sorted({t for e, _, ts in SECTORS if e in picked for t in ts})
    data.update(fetch_many(stocks))
    return data
