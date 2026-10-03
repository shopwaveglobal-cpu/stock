# -*- coding: utf-8 -*-
"""Morning Briefing 카드 3 (세계 주요 지표 120거래일) 생성.
data/market_history.json을 읽어 cards/card3_global_YYYY-MM-DD.png 저장."""
import json, os, datetime, subprocess, sys, glob

BASE=os.path.dirname(os.path.abspath(__file__))
try:
    import koreanize_matplotlib
except ImportError:
    subprocess.run([sys.executable,"-m","pip","install","--quiet","--break-system-packages","koreanize-matplotlib","pillow"])
    import koreanize_matplotlib
from PIL import Image, ImageDraw, ImageFont

FD=glob.glob(os.path.dirname(koreanize_matplotlib.__file__)+"/fonts/")[0]
def F(sz,w="Regular"):
    n={"Regular":"NanumGothic.ttf","Bold":"NanumGothicBold.ttf","XBold":"NanumGothicExtraBold.ttf"}[w]
    return ImageFont.truetype(FD+n,sz)

W=840
BG=(8,12,10);PANEL=(16,22,19);BORDER=(42,54,47)
GREEN=(74,222,128);RED=(248,113,113);YELLOW=(250,204,21)
TXT=(232,237,233);DIM=(148,158,152);DIM2=(110,120,114)

today=datetime.date.today()
WD="월화수목금토일"[today.weekday()]
N_DAYS=120

H=json.load(open(os.path.join(BASE,"data","market_history.json")))
def series(k,n=N_DAYS):
    items=sorted(H[k]["data"].items())[-n if k not in("btc","eth") else -int(n*1.48):]
    return [d for d,_ in items],[v for _,v in items]

img=Image.new("RGB",(W,2200),BG); d=ImageDraw.Draw(img)
y=36
d.rounded_rectangle([40,y,238,y+44],radius=22,fill=(12,38,24),outline=(30,90,55),width=2)
d.ellipse([58,y+15,72,y+29],fill=GREEN)
d.text((82,y+22),"LIVE SIGNAL",font=F(19,"XBold"),fill=GREEN,anchor="lm")
d.text((W-40,y+22),f"DATE {today.isoformat()}",font=F(19,"Bold"),fill=DIM,anchor="rm")
y+=78
d.text((40,y),"Morning Briefing",font=F(42,"XBold"),fill=GREEN,anchor="lt")
tw=d.textlength("Morning Briefing",font=F(42,"XBold"))
d.text((40+tw+16,y+10),"(3/3)",font=F(26,"Bold"),fill=TXT,anchor="lt")
y+=62
d.text((40,y),f"{today.year}년 {today.month:02d}월 {today.day:02d}일 ({WD}) · 세계 주요 지표 {N_DAYS}거래일 추이",font=F(21),fill=DIM,anchor="lt")
y+=44; d.line([40,y,W-40,y],fill=BORDER,width=2); y+=28

dts,_=series("usd")
lbl=f"세계 주요 지표  ({dts[0]} ~ {dts[-1]} 종가 · Yahoo Finance)"
d.text((40,y),lbl,font=F(23,"Bold"),fill=DIM,anchor="lt")
d.line([40+d.textlength(lbl,font=F(23,"Bold"))+14,y+13,W-40,y+13],fill=BORDER,width=1)
y+=44

def fmt(v,kind):
    return f"${v:,.0f}" if kind=="usd_big" else (f"${v:,.1f}" if kind=="usd_1" else f"{v:,.1f}원")
rows=[("금","XAU/USD ($/oz)","gold","usd_big",1),("은","XAG/USD ($/oz)","silver","usd_1",1),
      ("비트코인","BTC/USD","btc","usd_big",1),("이더리움","ETH/USD","eth","usd_big",1),
      ("달러","USD/KRW","usd","krw",1),("유로","EUR/KRW","eur","krw",1),("엔화","JPY/KRW (100엔)","jpy","krw",100)]
rh=171; sx0,sx1=268,556
for name,code,key,kind,mult in rows:
    _,s=series(key); s=[v*mult for v in s]
    chg=(s[-1]/s[0]-1)*100; hi,lo=max(s),min(s)
    d.rounded_rectangle([40,y,W-40,y+rh],radius=14,fill=PANEL,outline=BORDER,width=2)
    d.text((66,y+50),name,font=F(22,"XBold"),fill=TXT,anchor="lm")
    d.text((66,y+82),code,font=F(15),fill=DIM2,anchor="lm")
    sy0,sy1=y+26,y+rh-24; rng=(hi-lo) or 1; n=len(s)
    pts=[(sx0+i*(sx1-sx0)/(n-1), sy1-(v-lo)/rng*(sy1-sy0)) for i,v in enumerate(s)]
    col=RED if chg<0 else GREEN
    d.line(pts,fill=col,width=2,joint="curve")
    p=pts[-1]; d.ellipse([p[0]-4,p[1]-4,p[0]+4,p[1]+4],fill=col)
    d.text((W-66,y+50),fmt(s[-1],kind),font=F(23,"XBold"),fill=TXT,anchor="rm")
    d.text((W-66,y+92),f"{chg:+.1f}%",font=F(19,"XBold"),fill=col,anchor="rm")
    hf=f"{hi:,.1f}" if hi<1000 else f"{hi:,.0f}"; lf=f"{lo:,.1f}" if lo<1000 else f"{lo:,.0f}"
    d.text((W-66,y+138),f"고 {hf} · 저 {lf}",font=F(13),fill=DIM2,anchor="rm")
    y+=rh+12
m0=datetime.date.fromisoformat(dts[0]); m1=datetime.date.fromisoformat(dts[-1])
mons=[]; c=m0.replace(day=1)
while c<=m1: mons.append(f"{c.month}월"); c=(c.replace(day=28)+datetime.timedelta(days=4)).replace(day=1)
for mi,m in enumerate(mons):
    d.text((sx0+mi*(sx1-sx0)/max(len(mons)-1,1), y+4),m,font=F(14),fill=DIM2,anchor="mt")
y+=30
d.text((40,y),"Yahoo Finance 일별 종가 (암호화폐는 매일) · 변화율 = 기간 시작 종가 대비",font=F(15),fill=DIM2,anchor="lt")
y+=35; d.line([40,y,W-40,y],fill=BORDER,width=1); y+=22
d.text((W//2,y),"DATA · Yahoo Finance   ·   07:00 KST",font=F(17),fill=DIM2,anchor="mt")
y+=44
os.makedirs(os.path.join(BASE,"cards"),exist_ok=True)
out=os.path.join(BASE,"cards",f"card3_global_{today.isoformat()}.png")
img.crop((0,0,W,y)).save(out)
print(out)
