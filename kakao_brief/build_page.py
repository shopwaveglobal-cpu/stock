"""HTML 브리핑 페이지 생성 (모바일 우선, 외부 의존 없음). 지금은 목업 데이터.
사용: python build_page.py [출력폴더=mockup]"""
import sys
from html import escape
from pathlib import Path

UP, DOWN = "#2ecc71", "#ff5c5c"


def spark(vals, w=96, h=32, color=None):
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    pad = 5
    pts = " ".join(f"{pad + i * (w - 2 * pad) / (len(vals) - 1):.1f},{h - pad - (h - 2 * pad) * (v - lo) / rng:.1f}" for i, v in enumerate(vals))
    c = color or (UP if vals[-1] >= vals[0] else DOWN)
    x, y = pts.split()[-1].split(",")
    return f'<svg class="sp" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="{x}" cy="{y}" r="3" fill="{c}"/></svg>'


def cls(p):
    return "up" if p >= 0 else "dn"


def fp(p):
    return f"{'+' if p >= 0 else ''}{p:.2f}%"


# ---------------- 목업 데이터 (실제 시세 아님) ----------------
DATE = "10/1 (수)"
US_DATE = "미국 9/30 마감"
INDICES = [
    ("코스피", 3387.83, -0.36, [3420, 3441, 3398, 3430, 3388]),
    ("코스닥", 901.74, 0.19, [893, 890, 899, 900, 902]),
    ("나스닥", 22251.93, -1.10, [22480, 22310, 22400, 22499, 22252]),
    ("S&P 500", 6793.45, -0.10, [6810, 6770, 6788, 6800, 6793]),
    ("다우", 46399.27, 0.43, [46100, 46000, 46150, 46200, 46399]),
    ("나스닥100 선물", 25131.89, 0.34, [24900, 25100, 24990, 25050, 25132]),
]
TAESAN = [  # 티커, 이름, 상태, 현재가, 등락률, 매수선, 20MA, 거래량배수, 시각, 흐름
    ("005930", "삼성전자", "near", 71800, -0.83, 70500, 72300, 1.4, "09:42", [73200, 72900, 72600, 72400, 71800]),
    ("000660", "SK하이닉스", "hit", 231500, -2.11, 232000, 238500, 2.1, "10:15", [242000, 240000, 237500, 235000, 231500]),
    ("NVDA", "엔비디아", "near", 186.4, 0.72, 181.0, 184.2, 0.9, "22:31", [179, 182, 184, 185, 186.4]),
    ("TSLA", "테슬라", "break", 412.3, -3.4, 420.0, 431.5, 1.8, "23:05", [438, 432, 428, 421, 412.3]),
]
SIGNALS = [  # 티커, 이름, 태그들, 점수(5), 메모, 현재가, 등락률, 흐름
    ("035420", "NAVER", ["박스권 돌파", "거래량 급증"], 5, "20일 박스 상단 돌파 + 거래량 3.2배. 종가 유지 시 추세 전환 후보.", "251,500", 3.85, [231, 235, 233, 240, 251.5]),
    ("AVGO", "브로드컴", ["수급 유입", "신고가 근접"], 4, "기관 순매수 3일 연속. 전고점 대비 -1.2% 구간.", "$392.1", 1.42, [370, 376, 381, 388, 392]),
    ("086520", "에코프로", ["눌림목", "20일선 지지"], 3, "20일선 지지 확인 중. 거래량 감소 구간, 반등 확인 필요.", "84,300", -0.6, [88, 86, 85, 84.6, 84.3]),
]
SECTORS = [("통신·미디어", 1.83), ("에너지", 0.66), ("유틸리티", 0.53), ("경기소비재", 0.44), ("금융", -0.08), ("필수소비재", -0.31),
           ("소재·화학", -0.55), ("IT·반도체", -1.25), ("산업재·방산", -1.49), ("헬스케어·바이오", -1.65), ("부동산·리츠", -1.71)]
MACRO = [("금", "$3,835.2", -1.66, [3900, 3890, 3880, 3860, 3835]), ("은", "$47.47", 1.00, [46, 46.4, 47.2, 46.8, 47.5]),
         ("BTC", "$111,250", -0.67, [113000, 112400, 111800, 112000, 111250]), ("ETH", "$4,084", -0.39, [4100, 4090, 4060, 4110, 4084]),
         ("USD/KRW", "1,369.3원", -1.49, [1390, 1395, 1385, 1378, 1369]), ("EUR/KRW", "1,606.9원", -1.42, [1630, 1625, 1620, 1612, 1607]),
         ("JPY 100엔", "924.4원", -0.60, [930, 934, 931, 929, 924]), ("WTI 원유", "$69.28", 1.88, [66, 67, 68.5, 67.4, 69.3])]
EVENTS = [("21:30", "미국 8월 PCE 물가 발표", "high"), ("23:00", "ISM 제조업지수", "mid"), ("익일 03:00", "연준 위원 연설", "low")]
NEWS = [("연준 인사 \"추가 인하 서두를 이유 없다\"", "물가 지표를 확인하겠다는 발언에 금리 인하 기대가 후퇴하며 기술주가 일제히 약세."),
        ("반도체 업종 차익 실현 매물 출회", "AI 반도체 랠리 이후 단기 과열 부담으로 SOX 지수 -2% 하락. 메모리 업종 낙폭 확대."),
        ("유가 2% 급등, 에너지 섹터 강세", "중동 공급 우려가 재부각되며 WTI가 $69선 회복. 정유·시추 업종 상승.")]
STATE = {"near": ("🔔", "매수선 근접", "warn"), "hit": ("✅", "매수선 도달", "ok"), "break": ("⚠️", "매수선 이탈", "bad")}

CSS = """
:root{--bg:#0d111c;--panel:#171e2f;--line:#28324a;--txt:#f0f4fa;--mut:#8a96ac;--acc:#60a5fa;--up:#2ecc71;--dn:#ff5c5c;--warn:#f5b942;color-scheme:dark}
@media(prefers-color-scheme:light){:root{--bg:#f3f5fa;--panel:#fff;--line:#dfe4ef;--txt:#141a29;--mut:#66728a;--acc:#2563eb;--up:#16a34a;--dn:#dc2626;--warn:#d97706;color-scheme:light}}
*{box-sizing:border-box;margin:0}html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--txt);font:15px/1.5 -apple-system,"Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic",sans-serif;padding-bottom:40px}
.wrap{max-width:560px;margin:0 auto;padding:0 16px}
header{padding:28px 0 12px}.eyebrow{font-size:12px;letter-spacing:.12em;color:var(--acc);font-weight:700}
h1{font-size:26px;margin:4px 0 2px}.sub{color:var(--mut);font-size:13px}
.mock{display:inline-block;margin-top:10px;font-size:11px;padding:3px 9px;border-radius:99px;border:1px dashed var(--warn);color:var(--warn)}
nav{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);margin:0 -16px 8px;padding:8px 16px;display:flex;gap:8px;overflow-x:auto;scrollbar-width:none}
nav a{flex:none;color:var(--mut);text-decoration:none;font-size:13px;padding:6px 12px;border-radius:99px;border:1px solid var(--line);background:var(--panel)}
nav a:active{color:var(--txt)}
section{margin-top:26px;scroll-margin-top:56px}h2{font-size:18px;margin-bottom:4px}.hint{color:var(--mut);font-size:12.5px;margin-bottom:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:14px 16px}.stack{display:grid;gap:10px}
.up{color:var(--up)}.dn{color:var(--dn)}.mut{color:var(--mut)}.num{font-variant-numeric:tabular-nums;font-weight:700}
.row{display:flex;align-items:center;justify-content:space-between;gap:10px}
.idx{display:grid;grid-template-columns:1fr 96px auto;align-items:center;gap:10px;padding:12px 16px}.idx b{font-size:15px}.idx .r{text-align:right}.idx .r div:first-child{font-size:16px}
.badge{font-size:12px;font-weight:700;padding:3px 10px;border-radius:99px;white-space:nowrap}
.warn{background:color-mix(in srgb,var(--warn) 18%,transparent);color:var(--warn)}.ok{background:color-mix(in srgb,var(--up) 18%,transparent);color:var(--up)}.bad{background:color-mix(in srgb,var(--dn) 18%,transparent);color:var(--dn)}
.tk{font-size:11px;color:var(--mut);border:1px solid var(--line);border-radius:6px;padding:1px 6px;margin-left:6px;vertical-align:middle}
.price{font-size:24px;margin:8px 0 2px}.track{position:relative;height:8px;border-radius:9px;background:var(--line);margin:14px 0 6px}
.track i{position:absolute;top:-4px;width:4px;height:16px;border-radius:3px;background:var(--acc)}.track em{position:absolute;top:-3px;width:14px;height:14px;border-radius:50%;border:3px solid var(--bg);transform:translateX(-50%)}
.meta{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px;padding-top:12px;border-top:1px dashed var(--line)}.meta div{font-size:11.5px;color:var(--mut)}.meta b{display:block;color:var(--txt);font-size:14px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 8px}.tag{font-size:12px;padding:3px 10px;border-radius:99px;background:color-mix(in srgb,var(--acc) 16%,transparent);color:var(--acc);font-weight:600}
.score{display:flex;gap:4px;align-items:center}.score span{width:22px;height:6px;border-radius:4px;background:var(--line)}.score span.on{background:var(--acc)}.note{font-size:13.5px;color:var(--mut);margin-top:8px}
.sec{display:grid;grid-template-columns:104px 1fr 62px;align-items:center;gap:10px;font-size:13.5px;padding:7px 0}.bar{height:14px;position:relative;background:transparent}
.bar::before{content:"";position:absolute;left:50%;top:-4px;bottom:-4px;width:1px;background:var(--line)}.bar span{position:absolute;top:0;height:14px;border-radius:6px}.sec .p{text-align:right;font-weight:700}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}.mc{padding:12px 14px}.mc .n{font-size:12px;color:var(--mut)}.mc .v{font-size:18px;font-weight:700;margin:2px 0}.mc .row{align-items:flex-end}.mc .row .num{font-size:13px;white-space:nowrap}
.ev{display:grid;grid-template-columns:70px 1fr auto;gap:8px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line);font-size:14px}.ev:last-child{border:0}.ev time{color:var(--mut);font-size:12.5px}
.dot{width:8px;height:8px;border-radius:50%}.high{background:var(--dn)}.mid{background:var(--warn)}.low{background:var(--mut)}
.news{padding:14px 16px}.news b{display:block;margin-bottom:4px;font-size:15px}.news p{font-size:13.5px;color:var(--mut)}.news .no{color:var(--acc);font-weight:700;font-size:12px}
footer{margin-top:34px;color:var(--mut);font-size:12px;text-align:center;line-height:1.7}
"""


def idx_row(n, v, p, h):
    return f'<div class="card idx"><b>{escape(n)}</b>{spark(h)}<div class="r"><div class="num">{v:,.2f}</div><div class="num {cls(p)}">{"▲" if p >= 0 else "▼"} {fp(p)}</div></div></div>'


def taesan_card(t):
    code, name, st, px, chg, buy, ma, vol, tm, hist = t
    ico, label, k = STATE[st]
    gap = (px / buy - 1) * 100
    lo, hi = min(px, buy, ma) * 0.985, max(px, buy, ma) * 1.015
    pos = lambda v: (v - lo) / (hi - lo) * 100
    f = (lambda v: f"{v:,.0f}") if px > 1000 else (lambda v: f"{v:,.1f}")
    return f'''<article class="card"><div class="row"><div><b>{escape(name)}</b><span class="tk">{code}</span></div><span class="badge {k}">{ico} {label}</span></div>
<div class="row"><div class="price num">{f(px)} <small class="num {cls(chg)}" style="font-size:14px">{fp(chg)}</small></div>{spark(hist)}</div>
<div class="track"><i style="left:{pos(buy):.1f}%" title="매수선"></i><em style="left:{pos(px):.1f}%;background:var(--{'up' if chg >= 0 else 'dn'})"></em></div>
<div class="row mut" style="font-size:12px"><span>매수선 {f(buy)}</span><span>이격 <b class="{cls(gap)}">{fp(gap)}</b></span></div>
<div class="meta"><div>20일선<b>{f(ma)}</b></div><div>거래량<b>{vol:.1f}배</b></div><div>알림시각<b>{tm}</b></div></div></article>'''


def signal_card(s):
    code, name, tags, score, note, px, chg, hist = s
    dots = "".join(f'<span class="{"on" if i < score else ""}"></span>' for i in range(5))
    return f'''<article class="card"><div class="row"><div><b>{escape(name)}</b><span class="tk">{code}</span></div><div class="num">{px} <small class="{cls(chg)}">{fp(chg)}</small></div></div>
<div class="tags">{"".join(f'<span class="tag">{escape(t)}</span>' for t in tags)}</div>
<div class="row"><div class="score" title="신호 강도">{dots}</div>{spark(hist)}</div><p class="note">{escape(note)}</p></article>'''


def sector_row(n, p):
    mx = 2.0
    w = min(abs(p) / mx, 1) * 50
    st = f"left:50%;width:{w:.1f}%;background:var(--up)" if p >= 0 else f"left:{50 - w:.1f}%;width:{w:.1f}%;background:var(--dn)"
    return f'<div class="sec"><span>{escape(n)}</span><div class="bar"><span style="{st}"></span></div><span class="p {cls(p)}">{fp(p)}</span></div>'


def build():
    nav = "".join(f'<a href="#{i}">{t}</a>' for i, t in [("idx", "지수"), ("ts", "태산 알람"), ("sg", "S 알림"), ("sec", "섹터"), ("mac", "매크로"), ("ev", "일정·뉴스")])
    macro = "".join(f'<div class="card mc"><div class="n">{n}</div><div class="v num">{v}</div><div class="row"><span class="num {cls(p)}">{"▲" if p >= 0 else "▼"} {fp(p)}</span>{spark(h, 56, 26)}</div></div>' for n, v, p, h in MACRO)
    events = "".join(f'<div class="ev"><time>{t}</time><span>{escape(e)}</span><i class="dot {l}"></i></div>' for t, e, l in EVENTS)
    news = "".join(f'<div class="card news"><span class="no">NEWS {i}</span><b>{escape(t)}</b><p>{escape(d)}</p></div>' for i, (t, d) in enumerate(NEWS, 1))
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>모닝 브리핑 {DATE}</title><meta name="robots" content="noindex"><style>{CSS}</style></head><body><div class="wrap">
<header><div class="eyebrow">MORNING BRIEF</div><h1>모닝 브리핑</h1><div class="sub">{DATE} · {US_DATE}</div><span class="mock">목업 · 샘플 데이터 (실제 시세 아님)</span></header>
<nav>{nav}</nav>
<section id="idx"><h2>시장 지수</h2><div class="hint">선은 최근 5거래일 종가 흐름</div><div class="stack">{"".join(idx_row(*i) for i in INDICES)}</div></section>
<section id="ts"><h2>🔔 태산 알람 종목</h2><div class="hint">매수선 대비 위치 · 파란 막대 = 매수선, 점 = 현재가</div><div class="stack">{"".join(taesan_card(t) for t in TAESAN)}</div></section>
<section id="sg"><h2>⭐ S 알림 종목</h2><div class="hint">신호 강도 5점 만점 · 오늘 새로 포착된 종목</div><div class="stack">{"".join(signal_card(s) for s in SIGNALS)}</div></section>
<section id="sec"><h2>섹터 등락률</h2><div class="hint">미국 섹터 ETF 11개 기준</div><div class="card">{"".join(sector_row(n, p) for n, p in SECTORS)}</div></section>
<section id="mac"><h2>매크로 지표</h2><div class="hint">금·은·원유는 선물, 나머지는 24시간 시세</div><div class="grid2">{macro}</div></section>
<section id="ev"><h2>오늘의 일정</h2><div class="hint">한국시간 · 🔴 중요 🟠 보통</div><div class="card">{events}</div>
<h2 style="margin-top:26px">주요 뉴스 3선</h2><div class="hint">시장을 움직인 순서</div><div class="stack">{news}</div></section>
<footer>본 페이지의 모든 수치는 목업용 샘플입니다.<br>투자 권유가 아니며 판단과 책임은 본인에게 있습니다.</footer></div></body></html>'''


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "mockup")
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(build(), encoding="utf-8")
    print("wrote", out / "index.html")
