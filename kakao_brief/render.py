"""카드 3장(1080x1080 PNG) 렌더링. Pillow만 사용."""
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from config import DOWN, INDICES, MACRO, SECTORS, TOP_N, UP

W = H = 1080
BG, PANEL, LINE = (13, 17, 28), (23, 30, 47), (40, 50, 72)
TXT, MUTED, ACCENT = (240, 244, 250), (138, 150, 172), (96, 165, 250)
DAYS = "월화수목금토일"

_FONT_DIRS = [
    os.environ.get("BRIEF_FONT_DIR", ""),
    str(Path(__file__).parent / "fonts"),
    "/usr/share/fonts/opentype/noto",
    "/usr/share/fonts/truetype/noto",
    "/usr/share/fonts/truetype/nanum",
    "/usr/share/fonts/truetype/wqy",
    "C:/Windows/Fonts",
]
_REG = ["NotoSansCJK-Regular.ttc", "NotoSansKR-Regular.otf", "NanumGothic.ttf", "malgun.ttf", "wqy-zenhei.ttc"]
_BOLD = ["NotoSansCJK-Bold.ttc", "NotoSansKR-Bold.otf", "NanumGothicBold.ttf", "malgunbd.ttf"]


def _find(names):
    for d in _FONT_DIRS:
        for n in names:
            p = Path(d) / n
            if d and p.exists():
                return str(p)
    return None


_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _cache:
        path = _find(_BOLD) if bold else None
        fake = bold and path is None
        path = path or _find(_REG)
        if not path:
            raise RuntimeError("한글 폰트를 찾지 못했습니다. fonts-noto-cjk 설치 또는 BRIEF_FONT_DIR 지정")
        _cache[key] = (ImageFont.truetype(path, size, index=1 if path.endswith(".ttc") and "Noto" in path else 0), fake)
    return _cache[key]


def put(d, xy, s, size, fill=TXT, bold=False, anchor="la"):
    f, fake = font(size, bold)
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=1 if fake else 0, stroke_fill=fill)


def width(d, s, size, bold=False):
    return d.textlength(s, font=font(size, bold)[0])


def col(pct):
    return UP if pct >= 0 else DOWN


def fpct(p):
    return f"{'+' if p >= 0 else ''}{p:.2f}%"


def fnum(v, dec=2, pre="", suf=""):
    return f"{pre}{v:,.{dec}f}{suf}"


def spark(d, box, vals, color):
    x0, y0, x1, y1 = box
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    pts = [(x0 + (x1 - x0) * i / (len(vals) - 1), y1 - (y1 - y0) * (v - lo) / rng) for i, v in enumerate(vals)]
    d.line(pts, fill=color, width=4, joint="curve")
    r = 6
    d.ellipse((pts[-1][0] - r, pts[-1][1] - r, pts[-1][0] + r, pts[-1][1] + r), fill=color)


def base(title, sub, page):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 8), fill=ACCENT)
    put(d, (60, 44), "NASDAQ MORNING BRIEF", 20, ACCENT, True)
    put(d, (60, 76), title, 46, TXT, True)
    put(d, (W - 60, 92), sub, 22, MUTED, anchor="ra")
    put(d, (60, H - 44), "Yahoo Finance 종가 기준 · 투자 권유 아님", 18, MUTED)
    put(d, (W - 60, H - 44), f"{page}/3", 18, MUTED, anchor="ra")
    return im, d


def header_sub(data):
    kst = datetime.now(timezone(timedelta(hours=9)))
    us = data.get("^IXIC", {}).get("date", "")
    us_txt = f"미국 {int(us[5:7])}/{int(us[8:])} 마감" if us else ""
    return f"{kst.month}/{kst.day} ({DAYS[kst.weekday()]}) · {us_txt}"


def tile(d, x, y, w, h, label, big, pct, sub, hist):
    d.rounded_rectangle((x, y, x + w, y + h), 22, fill=PANEL, outline=LINE, width=2)
    c = col(pct)
    put(d, (x + 28, y + 24), label, 26, MUTED, True)
    put(d, (x + 28, y + 64), big, 44, TXT, True)
    put(d, (x + 28, y + 122), f"{'▲' if pct >= 0 else '▼'} {fpct(pct)}", 30, c, True)
    if sub:
        put(d, (x + 28, y + 164), sub, 22, MUTED)
    if hist and len(hist) > 1:
        spark(d, (x + 32, y + h - 120, x + w - 32, y + h - 40), hist, c)


def card1(data, sub):
    im, d = base("시장 지수", sub, 1)
    tw, th, gx, gy, y0 = 460, 360, 40, 40, 200
    for i, (name, sym) in enumerate(INDICES):
        x, y = 60 + (i % 2) * (tw + gx), y0 + (i // 2) * (th + gy)
        r = data.get(sym)
        if not r:
            d.rounded_rectangle((x, y, x + tw, y + th), 22, fill=PANEL, outline=LINE, width=2)
            put(d, (x + 28, y + 24), name, 26, MUTED, True)
            put(d, (x + 28, y + 90), "데이터 없음", 34, MUTED)
            continue
        sign = "+" if r["chg"] >= 0 else ""
        tile(d, x, y, tw, th, name, fnum(r["close"]), r["pct"], f"{sign}{r['chg']:,.2f} pt", r["hist"])
    put(d, (60, y0 + 2 * th + gy + 22), "우측 선: 최근 5거래일 종가 흐름", 20, MUTED)
    return im


def stock_line(d, x, y, tickers, data):
    for t in tickers:
        r = data.get(t)
        s = f"{t} {fpct(r['pct'])}" if r else f"{t} -"
        put(d, (x, y), s, 18, col(r["pct"]) if r else MUTED)
        x += width(d, s, 18) + 22


def card2(data, sub):
    im, d = base("섹터 등락률", sub, 2)
    rows = [(e, n, ts) for e, n, ts in SECTORS if data.get(e)]
    rows.sort(key=lambda r: data[r[0]]["pct"], reverse=True)
    hi = {r[0] for r in rows[:TOP_N]} | {r[0] for r in rows[-TOP_N:]}
    mx = max((abs(data[r[0]]["pct"]) for r in rows), default=1) or 1
    zero, half, rh, y0 = 640, 250, 74, 190
    d.line((zero, y0 - 8, zero, y0 + rh * len(rows)), fill=LINE, width=2)
    for i, (e, n, ts) in enumerate(rows):
        y, p = y0 + i * rh, data[e]["pct"]
        pick = e in hi
        put(d, (60, y + 6), e, 26, TXT, True)
        put(d, (60, y + 38), n, 18, MUTED)
        bw = max(4, half * abs(p) / mx)
        by = y + (8 if pick else 20)
        x0, x1 = (zero, zero + bw) if p >= 0 else (zero - bw, zero)
        d.rounded_rectangle((x0, by, x1, by + 24), 6, fill=col(p))
        put(d, (W - 60, y + 6), fpct(p), 26, col(p), True, "ra")
        if pick:
            stock_line(d, 330, y + 42, ts, data)
    return im


def card3(data, sub):
    im, d = base("매크로 지표", sub, 3)
    tw, th, gx, gy, y0 = 460, 180, 40, 20, 190
    for i, (label, sym, mul, pre, suf, dec) in enumerate(MACRO):
        x, y = 60 + (i % 2) * (tw + gx), y0 + (i // 2) * (th + gy)
        r = data.get(sym)
        if not r:
            d.rounded_rectangle((x, y, x + tw, y + th), 22, fill=PANEL, outline=LINE, width=2)
            put(d, (x + 28, y + 24), label, 26, MUTED, True)
            put(d, (x + 28, y + 80), "데이터 없음", 30, MUTED)
            continue
        hist = [v * mul for v in r["hist"]]
        d.rounded_rectangle((x, y, x + tw, y + th), 22, fill=PANEL, outline=LINE, width=2)
        c = col(r["pct"])
        put(d, (x + 28, y + 22), label, 24, MUTED, True)
        put(d, (x + 28, y + 58), fnum(r["close"] * mul, dec, pre, suf), 38, TXT, True)
        put(d, (x + 28, y + 114), f"{'▲' if r['pct'] >= 0 else '▼'} {fpct(r['pct'])}", 28, c, True)
        spark(d, (x + tw - 170, y + th - 90, x + tw - 34, y + th - 34), hist, c)
    x, y = 60 + (len(MACRO) % 2) * (tw + gx), y0 + (len(MACRO) // 2) * (th + gy)
    put(d, (x + 28, y + 40), "금·은: 선물(GC=F, SI=F)", 20, MUTED)
    put(d, (x + 28, y + 76), "BTC·ETH·환율: 24시간 시세라", 20, MUTED)
    put(d, (x + 28, y + 108), "당일 진행 값이 섞일 수 있음", 20, MUTED)
    return im


def render_all(data, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sub = header_sub(data)
    paths = []
    for i, fn in enumerate((card1, card2, card3), 1):
        p = out / f"card{i}.png"
        fn(data, sub).save(p, optimize=True)
        paths.append(p)
    return paths
