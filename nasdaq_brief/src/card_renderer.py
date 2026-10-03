"""card_renderer.py — Jinja2 + Playwright -> PNG"""

import os
import math
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"


def _sector_style(pct: float):
    if pct >= 2.0:   return "rgba(34,197,94,0.40)",  "#86EFAC"
    elif pct >= 1.0: return "rgba(34,197,94,0.22)",  "#86EFAC"
    elif pct >= 0.3: return "rgba(34,197,94,0.10)",  "#6EE7B7"
    elif pct >= -0.3:return "rgba(255,255,255,0.05)","#94A3B8"
    elif pct >= -1.0:return "rgba(239,68,68,0.10)",  "#FCA5A5"
    elif pct >= -2.0:return "rgba(239,68,68,0.22)",  "#F87171"
    else:            return "rgba(239,68,68,0.40)",  "#EF4444"


def _compute_chart(chart_raw: dict, svg_w=380, svg_h=110):
    nasdaq = chart_raw.get("nasdaq", [])
    kospi  = chart_raw.get("kospi", [])
    dates  = chart_raw.get("dates", [])
    if not nasdaq or len(nasdaq) < 2:
        return {}

    all_vals = nasdaq + (kospi if kospi else [])
    min_v = min(all_vals) - 0.3
    max_v = max(all_vals) + 0.3
    y_range = max_v - min_v or 1
    n = len(nasdaq)
    x_step = svg_w / max(n - 1, 1)

    def to_x(i): return round(i * x_step, 1)
    def to_y(v): return round(svg_h - (v - min_v) / y_range * svg_h, 1)

    def path(vals):
        pts = [(to_x(i), to_y(v)) for i, v in enumerate(vals)]
        return "M " + " L ".join(f"{x},{y}" for x, y in pts), pts

    nasdaq_path, nasdaq_pts = path(nasdaq)
    kospi_path,  _          = path(kospi) if kospi else ("", [])

    return {
        "nasdaq_path":   nasdaq_path,
        "kospi_path":    kospi_path,
        "last_x":        nasdaq_pts[-1][0],
        "nasdaq_last_y": nasdaq_pts[-1][1],
        "date_labels":   [{"x": to_x(i), "date": d} for i, d in enumerate(dates)],
        "svg_w": svg_w,
        "svg_h": svg_h,
    }


def _translate_titles(news_raw):
    """영어 제목 → 한국어 (실패 시 원문)"""
    try:
        from deep_translator import GoogleTranslator
        tr = GoogleTranslator(source="auto", target="ko")
        for item in news_raw:
            try:
                item["title_ko"] = tr.translate(item["title_en"])
            except Exception:
                item["title_ko"] = item["title_en"]
    except Exception:
        for item in news_raw:
            item["title_ko"] = item["title_en"]
    return news_raw


def _news_impact(title_en: str) -> str:
    t = title_en.lower()
    kw_map = {
        "fed":       "연준 정책 방향에 따라 성장주 변동성 확대 가능.",
        "rate":      "금리 경로 불확실성이 기술주 밸류에이션에 영향.",
        "inflation": "인플레 재점화 우려 시 연준 금리 인하 지연 가능.",
        "earnings":  "실적 서프라이즈 여부가 섹터 전반 흐름을 주도.",
        "nvidia":    "NVDA 모멘텀은 국내 반도체(하이닉스)와 직결.",
        "apple":     "나스닥 시총 최대 종목 — 지수 방향성 선도.",
        "china":     "미중 긴장 고조 시 반도체·소재 섹터 변동성 주의.",
        "job":       "강한 고용 = 금리 인하 지연 우려 → 성장주 부담.",
        "oil":       "유가 급변은 에너지·운송 섹터에 즉각 반영.",
        "bitcoin":   "위험자산 선호 심리의 선행 지표로 기능.",
    }
    for kw, impact in kw_map.items():
        if kw in t:
            return impact
    return "시장 전반에 단기 변동성 요인으로 작용할 수 있음."


def build_context(data: dict, date_str_ko: str, date_str_en: str, timestamp: str):
    indices   = data["indices"]
    chart_raw = data["chart_raw"]
    sectors   = data["sectors"]
    fg        = data["fear_greed"]
    news_raw  = data["news_raw"]
    checkpts  = data["checkpoints"]
    verif     = data.get("verification", [])

    # Sectors with color
    sectors_ctx = []
    for s in sectors:
        bg, text = _sector_style(s["pct"])
        sectors_ctx.append({**s, "bg_color": bg, "text_color": text})

    # Chart
    chart = _compute_chart(chart_raw)

    # 뉴스 제목만 번역 (임팩트 설명 제거)
    news_raw = _translate_titles(news_raw)
    news_ctx = [{"title": item["title_ko"]} for item in news_raw]

    return {
        "date_ko": date_str_ko,
        "date_en": date_str_en,
        "timestamp": timestamp,
        "indices": indices,
        "chart": chart,
        "sectors": sectors_ctx,
        "fg": fg,
        "news": news_ctx,
        "checkpoints": checkpts,
        "verification": verif,
    }


def render_card(context: dict, out_png: str | None = None) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if out_png is None:
        out_png = str(OUTPUT_DIR / "market_card.png")
    html_path = out_png.replace(".png", ".html")

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("market_card.html")
    html = template.render(**context)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 420, "height": 900})
        page.goto(f"file:///{html_path.replace(os.sep, '/')}")
        page.wait_for_timeout(2500)  # Google Fonts 로드 대기
        page.screenshot(path=out_png, full_page=True)
        browser.close()

    print(f"  카드 저장: {out_png}")
    return out_png
