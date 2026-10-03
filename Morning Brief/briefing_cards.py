# -*- coding: utf-8 -*-
"""Morning Briefing 카드 1(시장)·2(뉴스) 생성. 사용: python3 briefing_cards.py day_input.json
스키마 예시는 day_input_example.json 참고. 출력: cards/card1_market_<date>.png, card2_news_<date>.png"""
import json, os, sys, datetime, subprocess, glob
BASE=os.path.dirname(os.path.abspath(__file__))
try: import koreanize_matplotlib
except ImportError:
    subprocess.run([sys.executable,"-m","pip","install","--quiet","--break-system-packages","koreanize-matplotlib","pillow"]); import koreanize_matplotlib
from PIL import Image, ImageDraw, ImageFont
FD=os.path.dirname(koreanize_matplotlib.__file__)+"/fonts/"
def F(sz,w="Regular"):
    n={"Regular":"NanumGothic.ttf","Bold":"NanumGothicBold.ttf","XBold":"NanumGothicExtraBold.ttf"}[w]
    return ImageFont.truetype(FD+n,sz)
W=840
BG=(8,12,10);PANEL=(16,22,19);BORDER=(42,54,47)
GREEN=(74,222,128);RED=(248,113,113);BLUE=(96,165,250);YELLOW=(250,204,21);ORANGE=(250,160,70)
TXT=(232,237,233);DIM=(148,158,152);DIM2=(110,120,114)
C={"green":GREEN,"red":RED,"blue":BLUE,"yellow":YELLOW,"orange":ORANGE,"dim":DIM}
def lerp(a,b,t): return tuple(int(x+(y-x)*t) for x,y in zip(a,b))
J=json.load(open(sys.argv[1]))
DATE=datetime.date.fromisoformat(J["date"]); WD="월화수목금토일"[DATE.weekday()]
DSTR=f"{DATE.year}년 {DATE.month:02d}월 {DATE.day:02d}일 ({WD})"
def canvas(): img=Image.new("RGB",(W,2600),BG); return img,ImageDraw.Draw(img)
def panel(d,x0,y0,x1,y1,fill=PANEL,outline=BORDER,r=14): d.rounded_rectangle([x0,y0,x1,y1],radius=r,fill=fill,outline=outline,width=2)
def header(d,y,part,sub):
    d.rounded_rectangle([40,y,238,y+44],radius=22,fill=(12,38,24),outline=(30,90,55),width=2)
    d.ellipse([58,y+15,72,y+29],fill=GREEN)
    d.text((82,y+22),"LIVE SIGNAL",font=F(19,"XBold"),fill=GREEN,anchor="lm")
    d.text((W-40,y+22),f"DATE {DATE.isoformat()}",font=F(19,"Bold"),fill=DIM,anchor="rm")
    y+=78
    d.text((40,y),"Morning Briefing",font=F(42,"XBold"),fill=GREEN,anchor="lt")
    d.text((40+d.textlength("Morning Briefing",font=F(42,"XBold"))+16,y+10),part,font=F(26,"Bold"),fill=TXT,anchor="lt")
    y+=62; d.text((40,y),sub,font=F(21),fill=DIM,anchor="lt")
    y+=44; d.line([40,y,W-40,y],fill=BORDER,width=2); return y+28
def section(d,y,label):
    d.text((40,y),label,font=F(23,"Bold"),fill=DIM,anchor="lt")
    d.line([40+d.textlength(label,font=F(23,"Bold"))+14,y+13,W-40,y+13],fill=BORDER,width=1); return y+44
def footer(d,y):
    d.line([40,y,W-40,y],fill=BORDER,width=1); y+=22
    d.text((W//2,y),"DATA · Yahoo Finance | CNN Fear&Greed   ·   07:00 KST",font=F(17),fill=DIM2,anchor="mt"); return y+44
# ---------------- CARD 1 ----------------
img,d=canvas(); y=header(d,36,"(1/3)",DSTR+" · 미국 전일 시장 데이터")
y=section(d,y,"미국 전일 시장")
bw=(W-80-32)//3
for i,(n,v,c,cl) in enumerate(J["indices"]):
    x0=40+i*(bw+16); panel(d,x0,y,x0+bw,y+118)
    d.text((x0+20,y+24),n,font=F(19,"Bold"),fill=DIM,anchor="lm")
    d.text((x0+20,y+58),v,font=F(30,"XBold"),fill=TXT,anchor="lm")
    d.text((x0+20,y+92),c,font=F(18,"Bold"),fill=C[cl],anchor="lm")
y+=148
fd=J["five_day"]; days=fd["days"]; nas=fd["nasdaq"]; kos=fd["kospi"]
y=section(d,y,f"5일 지수 흐름 비교  (시작일 {days[0]} = 100)")
ch=460; panel(d,40,y,W-40,y+ch)
nasN=[v/nas[0]*100 for v in nas]; kosN=[v/kos[0]*100 for v in kos]
d.line([66,y+34,98,y+34],fill=GREEN,width=5); d.text((108,y+34),"NASDAQ",font=F(19,"Bold"),fill=TXT,anchor="lm")
d.line([240,y+34,272,y+34],fill=BLUE,width=5); d.text((282,y+34),"KOSPI",font=F(19,"Bold"),fill=TXT,anchor="lm")
allv=nasN+kosN; ymin=int(min(allv))-2; ymax=int(max(allv))+2
px0,px1=120,W-110; py0,py1=y+86,y+ch-106
def Y(v): return py1-(v-ymin)/(ymax-ymin)*(py1-py0)
def X(i): return px0+i*(px1-px0)/(len(days)-1)
import math
for g in range(ymin,ymax+1,5):
    d.line([px0-34,Y(g),px1+24,Y(g)],fill=(30,40,35),width=1)
    d.text((px0-42,Y(g)),str(g),font=F(15),fill=DIM2,anchor="rm")
for series,col in [(nasN,GREEN),(kosN,BLUE)]:
    pts=[(X(i),Y(v)) for i,v in enumerate(series)]
    d.line(pts,fill=col,width=5,joint="curve")
    for p in pts: d.ellipse([p[0]-5,p[1]-5,p[0]+5,p[1]+5],fill=col)
for i in range(len(days)):
    d.text((X(i),Y(nasN[i])-18),f"{nas[i]:,.0f}",font=F(16,"Bold"),fill=(150,235,170),anchor="mb")
    d.text((X(i),Y(kosN[i])+16),f"{kos[i]:,.0f}",font=F(16,"Bold"),fill=(150,190,250),anchor="mt")
    d.text((X(i),py1+52),days[i],font=F(16),fill=DIM,anchor="mt")
if fd.get("marker"):
    mi=fd["marker"]["idx"]; d.text((X(mi),Y(kosN[mi])+44),fd["marker"]["text"],font=F(15,"Bold"),fill=BLUE,anchor="mt")
if fd.get("note"): d.text((60,y+ch-26),fd["note"],font=F(15),fill=DIM2,anchor="lm")
y+=ch+30
y=section(d,y,"미국 섹터 히트맵 (전일 등락률)")
tw_=(W-80-32)//3; th=86
for i,(n,p) in enumerate(J["sectors"]):
    r_,c_=divmod(i,3); x0=40+c_*(tw_+16); y0=y+r_*(th+14)
    t=min(abs(p)/2.2,1.0)
    fill=lerp((20,42,30),(28,118,62),t) if p>=0 else lerp((46,26,26),(132,44,44),t)
    panel(d,x0,y0,x0+tw_,y0+th,fill=fill,outline=lerp(BORDER,fill,0.5),r=10)
    d.text((x0+tw_//2,y0+28),n,font=F(20,"Bold"),fill=TXT,anchor="mm")
    d.text((x0+tw_//2,y0+60),f"{p:+.1f}%",font=F(22,"XBold"),fill=(220,255,230) if p>=0 else (255,215,215),anchor="mm")
y+=((len(J["sectors"])+2)//3)*(th+14)+16
fg=J["fear"]; y=section(d,y,"공포·탐욕 지수 (CNN 공식 · 전일 기준)")
panel(d,40,y,W-40,y+130)
fv=fg["value"]; fcol=ORANGE if fv<45 else (YELLOW if fv<55 else GREEN)
if fv<25: fcol=RED
d.text((120,y+52),str(fv),font=F(52,"XBold"),fill=fcol,anchor="mm")
d.text((120,y+96),f"{fg['label']} · {fg['vix']}",font=F(18,"Bold"),fill=DIM,anchor="mm")
gx0,gx1,gy=230,W-80,y+58
for i in range(gx1-gx0):
    t=i/(gx1-gx0)
    if t<0.25: c=lerp((200,60,60),(235,140,60),t/0.25)
    elif t<0.5: c=lerp((235,140,60),(245,205,80),(t-0.25)/0.25)
    elif t<0.75: c=lerp((245,205,80),(140,210,110),(t-0.5)/0.25)
    else: c=lerp((140,210,110),(60,180,90),(t-0.75)/0.25)
    d.line([gx0+i,gy-9,gx0+i,gy+9],fill=c)
kx=gx0+int((gx1-gx0)*fv/100)
d.ellipse([kx-13,gy-13,kx+13,gy+13],fill=(245,248,246),outline=(60,70,64),width=3)
for lab,t in [("극공포",0.04),("중립",0.5),("극탐욕",0.96)]:
    d.text((gx0+(gx1-gx0)*t,gy+30),lab,font=F(15),fill=DIM2,anchor="mm")
y+=160; y=footer(d,y)
os.makedirs(BASE+"/cards",exist_ok=True)
img.crop((0,0,W,y)).save(f"{BASE}/cards/card1_market_{DATE.isoformat()}.png")
# ---------------- CARD 2 ----------------
img,d=canvas(); y=header(d,36,"(2/3)",DSTR+" · 금주 일정 & 주요 뉴스")
y=section(d,y,"금주 일정  (KST)")
rh=96
for day,ev,note,today_ in J["calendar"]:
    fill=(14,30,22) if today_ else PANEL; outline=(35,95,60) if today_ else BORDER
    panel(d,40,y,W-40,y+rh,fill=fill,outline=outline,r=12)
    d.text((68,y+rh//2),day,font=F(19,"XBold"),fill=GREEN if today_ else DIM,anchor="lm")
    d.text((236,y+rh//2),ev,font=F(20,"Bold"),fill=TXT,anchor="lm")
    d.text((W-68,y+rh//2),note,font=F(17),fill=DIM,anchor="rm")
    if today_:
        d.rounded_rectangle([168,y+rh//2-13,222,y+rh//2+13],radius=7,fill=(20,70,40))
        d.text((195,y+rh//2),"오늘",font=F(15,"Bold"),fill=GREEN,anchor="mm")
    y+=rh+12
y+=20
y=section(d,y,"주요 뉴스 3선  (전일 시장을 움직인 뉴스 · AI 선별)")
nh=298
for i,nw in enumerate(J["news"]):
    panel(d,40,y,W-40,y+nh)
    d.rounded_rectangle([62,y+32,96,y+70],radius=8,fill=(12,38,24),outline=(30,90,55),width=2)
    d.text((79,y+51),str(i+1),font=F(21,"XBold"),fill=GREEN,anchor="mm")
    d.text((114,y+51),nw["h"],font=F(23,"Bold"),fill=TXT,anchor="lm")
    d.text((114,y+112),nw["lines"][0],font=F(19),fill=DIM,anchor="lm")
    if len(nw["lines"])>1: d.text((114,y+155),nw["lines"][1],font=F(19),fill=DIM,anchor="lm")
    x=114; d.text((x,y+218),"관련",font=F(16,"Bold"),fill=DIM2,anchor="lm"); x+=52
    for j,(t,cl) in enumerate(nw["tags"]):
        if j: d.text((x,y+218),"·",font=F(17,"Bold"),fill=DIM2,anchor="lm"); x+=18
        d.text((x,y+218),t,font=F(18,"Bold"),fill=C[cl],anchor="lm"); x+=d.textlength(t,font=F(18,"Bold"))+14
    y+=nh+16
y+=16; y=footer(d,y)
img.crop((0,0,W,y)).save(f"{BASE}/cards/card2_news_{DATE.isoformat()}.png")
print("cards saved:", DATE.isoformat())
