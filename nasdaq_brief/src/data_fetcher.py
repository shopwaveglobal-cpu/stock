"""data_fetcher.py — 시장 데이터 수집 모듈"""

import requests
import feedparser
import yfinance as yf
import pytz
from datetime import datetime

KST = pytz.timezone("Asia/Seoul")

SECTOR_MAP = {
    "XLK":  "기술",
    "XLY":  "임의소비재",
    "XLC":  "통신",
    "XLF":  "금융",
    "XLV":  "헬스케어",
    "XLI":  "산업재",
    "XLE":  "에너지",
    "XLP":  "필수소비재",
    "XLU":  "유틸리티",
    "XLB":  "소재",
    "XLRE": "부동산",
}

RSS_FEEDS = [
    "https://www.cnbc.com/id/20910258/device/rss/rss.html",   # CNBC Markets
    "https://www.cnbc.com/id/10000664/device/rss/rss.html",   # CNBC Economy
    "https://feeds.reuters.com/reuters/businessNews",          # Reuters Business
    "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",  # MarketWatch Pulse
]

# 뉴스 필터링: 이 단어 포함 시 스킵 (광고성/비관련)
NEWS_SKIP_KEYWORDS = [
    "should you invest", "best etf", "best stock", "buy now", "sell now",
    "top picks", "dividend", "retirement", "401k", "portfolio tip",
    "watch list", "undervalued", "overvalued", "price target",
]


def _pct(hist):
    if len(hist) < 2:
        return None
    prev = float(hist["Close"].iloc[-2])
    curr = float(hist["Close"].iloc[-1])
    return curr, (curr - prev) / prev * 100


def fetch_indices():
    """NASDAQ / S&P500 / DOW 종가 + 등락"""
    specs = [
        ("^IXIC", "NASDAQ"),
        ("^GSPC", "S&P500"),
        ("^DJI", "DOW"),
    ]
    result = []
    for sym, name in specs:
        try:
            hist = yf.Ticker(sym).history(period="5d")
            price, pct = _pct(hist)
            result.append({
                "name": name, "symbol": sym,
                "price": price,
                "pct": pct,
                "price_fmt": f"{price:,.0f}" if price > 1000 else f"{price:,.2f}",
            })
        except Exception as e:
            print(f"  [{name}] 조회 실패: {e}")
    return result


def fetch_chart_data():
    """NASDAQ + KOSPI 최근 5거래일 정규화 (base=100)"""
    result = {"dates": [], "nasdaq": [], "kospi": []}
    for sym, key in [("^IXIC", "nasdaq"), ("^KS11", "kospi")]:
        try:
            hist = yf.Ticker(sym).history(period="10d").tail(5)
            closes = [float(v) for v in hist["Close"].values]
            if not closes:
                continue
            base = closes[0]
            result[key] = [c / base * 100 for c in closes]
            if not result["dates"]:
                result["dates"] = [d.strftime("%m/%d") for d in hist.index]
        except Exception as e:
            print(f"  [chart/{key}] 실패: {e}")
    return result


def fetch_sectors():
    """11개 섹터 ETF 등락률, 정렬 후 반환"""
    result = []
    for etf, name in SECTOR_MAP.items():
        try:
            hist = yf.Ticker(etf).history(period="5d")
            _, pct = _pct(hist)
            result.append({"etf": etf, "name": name, "pct": pct})
        except Exception:
            pass
    return sorted(result, key=lambda x: x["pct"], reverse=True)


def fetch_fear_greed():
    """CNN Fear & Greed (실패 시 VIX 폴백)"""
    # CNN API
    try:
        resp = requests.get(
            "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8,
        )
        if resp.status_code == 200:
            score = int(resp.json()["fear_and_greed"]["score"])
            return _fg_info(score, "CNN")
    except Exception:
        pass

    # VIX 폴백
    try:
        hist = yf.Ticker("^VIX").history(period="2d")
        vix = float(hist["Close"].iloc[-1])
        if vix <= 13:   score = 78
        elif vix <= 16: score = 62
        elif vix <= 20: score = 50
        elif vix <= 25: score = 35
        elif vix <= 30: score = 22
        else:           score = 12
        return _fg_info(score, f"VIX {vix:.1f}")
    except Exception:
        pass

    return _fg_info(50, "N/A")


def _fg_info(score: int, source: str = ""):
    if score >= 75:   label, label_ko, color = "Extreme Greed", "극탐욕",  "#22C55E"
    elif score >= 55: label, label_ko, color = "Greed",         "탐욕",    "#86EFAC"
    elif score >= 45: label, label_ko, color = "Neutral",       "중립",    "#FCD34D"
    elif score >= 25: label, label_ko, color = "Fear",          "공포",    "#F97316"
    else:             label, label_ko, color = "Extreme Fear",  "극공포",  "#EF4444"
    return {
        "score": score, "label": label, "label_ko": label_ko,
        "color": color, "pct": score, "source": source,
    }


def fetch_news(max_items: int = 3):
    """RSS 피드에서 시장 관련 뉴스 헤드라인 수집"""
    items, seen = [], set()
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                title = (entry.get("title") or "").strip()
                if not title or title in seen or len(title) < 20:
                    continue
                # 광고성/비관련 필터링
                tl = title.lower()
                if any(kw in tl for kw in NEWS_SKIP_KEYWORDS):
                    continue
                seen.add(title)
                items.append({"title_en": title})
                if len(items) >= max_items * 3:
                    break
        except Exception:
            continue
        if len(items) >= max_items * 3:
            break
    return items[:max_items]


def fetch_all():
    """전체 데이터 수집 진입점"""
    print("  인덱스 수집...")
    indices = fetch_indices()

    print("  차트 데이터 수집...")
    chart_raw = fetch_chart_data()

    print("  섹터 수집...")
    sectors = fetch_sectors()

    print("  공포탐욕 수집...")
    fear_greed = fetch_fear_greed()

    print("  뉴스 수집...")
    news_raw = fetch_news(3)

    return {
        "indices": indices,
        "chart_raw": chart_raw,
        "sectors": sectors,
        "fear_greed": fear_greed,
        "news_raw": news_raw,
    }
