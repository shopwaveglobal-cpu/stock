"""오프라인 미리보기용 가짜 데이터 (실제 시세 아님)."""
import random

from config import INDICES, MACRO, SECTORS


def _row(sym, base, pct):
    prev = base
    close = prev * (1 + pct / 100)
    hist = [prev * (1 + random.uniform(-1.5, 1.5) / 100) for _ in range(3)] + [prev, close]
    return {"sym": sym, "close": close, "prev": prev, "chg": close - prev, "pct": pct, "hist": hist, "date": "2026-09-28"}


def make():
    random.seed(7)
    d = {}
    for (_, s), b in zip(INDICES, [22500, 6800, 46200, 900]):
        d[s] = _row(s, b, random.uniform(-1.2, 1.4))
    for e, _, ts in SECTORS:
        d[e] = _row(e, 100, random.uniform(-1.8, 2.0))
        for t in ts:
            d[t] = _row(t, 100, random.uniform(-3, 3))
    for (_, s, *_), b in zip(MACRO, [3900, 47, 112000, 4100, 1390, 1630, 9.3]):
        d[s] = _row(s, b, random.uniform(-2, 2))
    return d
