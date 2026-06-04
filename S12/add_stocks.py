"""
37개 신규 종목을 turnover_universe.xlsx + trading_signals.xlsx Summary 탭에 추가
"""
import pandas as pd
import requests
import math
import time
from datetime import datetime
from pathlib import Path

# ── 토큰 ──────────────────────────────────────────────────────────
body = {'grant_type':'client_credentials',
        'appkey':'IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU',
        'secretkey':'eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs'}
TOKEN = requests.post('https://api.kiwoom.com/oauth2/token',
    headers={'Content-Type':'application/json;charset=UTF-8'},
    json=body, timeout=20).json()['token']
HEADERS = {'authorization':f'Bearer {TOKEN}',
    'Content-Type':'application/json;charset=UTF-8',
    'api-id':'ka10081','cont-yn':'N','next-key':''}

# ── 호가/매수선 계산 ──────────────────────────────────────────────
def get_tick(p):
    if p<1000: return 1
    if p<5000: return 5
    if p<10000: return 10
    if p<50000: return 50
    if p<100000: return 100
    if p<500000: return 500
    return 1000

def ceil_tick(p):
    t = get_tick(p); return math.ceil(p/t)*t

def calc_buy1(S19):
    p = ceil_tick(S19/24.0)
    while True:
        d = get_tick(p)
        if p < (S19+25.0*d)/24.0: return int(p)
        p += d

def calc_buy2(b1): return ceil_tick(b1*0.90)
def calc_buy3(b2): return ceil_tick(b2*0.90)

# ── 37개 종목 ─────────────────────────────────────────────────────
NEW_STOCKS = [
    ('한화투자증권', '003530'),
    ('현대힘스',     '460930'),
    ('포스코인터내셔널','047050'),
    ('HPSP',        '403870'),
    ('흥구석유',     '024060'),
    ('대한해운',     '005880'),
    ('후성',         '093370'),
    ('HD현대일렉트릭','267260'),
    ('미래에셋증권', '006800'),
    ('LIG디펜스앤에어로스페이스','079550'),
    ('HD현대에너지솔루션','322000'),
    ('한미반도체',   '042700'),
    ('삼양식품',     '003230'),
    ('HD현대건설기계','267270'),
    ('실리콘투',     '257720'),
    ('쿠콘',         '294570'),
    ('한국석유',     '004090'),
    ('한화',         '000880'),
    ('풍산',         '103140'),
    ('성우하이텍',   '015750'),
    ('RFHIC',        '218410'),
    ('셀바스AI',     '108860'),
    ('펄어비스',     '263750'),
    ('한화시스템',   '272210'),
    ('쏠리드',       '050890'),
    ('현대건설',     '000720'),
    ('대주전자재료', '078600'),
    ('고영',         '098460'),
    ('리노공업',     '058470'),
    ('한국항공우주', '047810'),
    ('필옵틱스',     '161580'),
    ('한화에어로스페이스','012450'),
    ('SFA반도체',    '036540'),
    ('엘앤에프',     '066970'),
    ('POSCO홀딩스',  '005490'),
    ('LS ELECTRIC',  '010120'),
    ('두산에너빌리티','034020'),
]

today_str = datetime.now().strftime('%Y%m%d')
today_dt  = datetime.now().date()

# ── 매수선 계산 ───────────────────────────────────────────────────
print("매수선 계산 중...")
results = []
for name, ticker in NEW_STOCKS:
    try:
        b = {'stk_cd':f'{ticker}_AL','base_dt':today_str,'upd_stkpc_tp':'1','stex_tp':'3'}
        data = requests.post('https://api.kiwoom.com/api/dostk/chart',
            headers=HEADERS, json=b, timeout=10).json().get('stk_dt_pole_chart_qry',[])

        # data[1:21]: 오늘 장중가 제외, 확정 종가만 사용 (장중 실행 시 정확도 유지)
        closes = []
        for d in data[1:21]:
            raw = str(d.get('cur_prc','')).replace(',','').strip()
            if raw: closes.append(abs(int(raw)))
        closes.reverse()

        if len(closes) < 20:
            print(f"  ⚠ {name} ({ticker}): 데이터 부족 ({len(closes)}일)")
            results.append({'name':name,'ticker':ticker,'ok':False})
            time.sleep(0.3); continue

        S20 = sum(closes); ma20 = S20/20
        S19 = S20 - closes[0]
        cur = abs(int(str(data[0].get('cur_prc',data[1].get('cur_prc',0))).replace(',','')))
        b1 = calc_buy1(S19); b2 = calc_buy2(b1); b3 = calc_buy3(b2)
        high = abs(int(str(data[0].get('high_pric',cur)).replace(',','')))
        low  = abs(int(str(data[0].get('low_pric', cur)).replace(',','')))

        print(f"  ✓ {name:<24} 1차={b1:>9,}  2차={b2:>9,}  3차={b3:>9,}  (현재가 {cur:,})")
        results.append({'name':name,'ticker':ticker,'ok':True,
            'cur':cur,'high':high,'low':low,'ma20':ma20,
            'b1':b1,'b2':b2,'b3':b3})
        time.sleep(0.3)
    except Exception as e:
        print(f"  ✗ {name} ({ticker}): {e}")
        results.append({'name':name,'ticker':ticker,'ok':False})

ok_results = [r for r in results if r.get('ok')]
print(f"\n성공: {len(ok_results)}/{len(NEW_STOCKS)}개")

# ── 1. turnover_universe.xlsx 업데이트 ───────────────────────────
UNIVERSE_FILE = 'output/turnover_universe.xlsx'
print(f"\n[1] {UNIVERSE_FILE} 업데이트...")

df_uni = pd.read_excel(UNIVERSE_FILE, dtype={'티커':str})
existing_tickers = set(df_uni['티커'].astype(str).str.zfill(6).tolist())

new_rows = []
for r in ok_results:
    t = str(r['ticker']).zfill(6)
    if t not in existing_tickers:
        new_rows.append({
            '첫거래날짜': today_dt,
            '최근거래날짜': today_dt,
            '티커': t,
            '종목명': r['name'],
            '거래량평균(일)': 0,
            '거래횟수': 0,
        })

if new_rows:
    df_new = pd.DataFrame(new_rows)
    # 기존 컬럼에 맞춰 병합
    df_uni = pd.concat([df_uni, df_new[df_uni.columns.intersection(df_new.columns)]], ignore_index=True)
    df_uni.to_excel(UNIVERSE_FILE, index=False)
    print(f"  ✓ {len(new_rows)}개 신규 추가 (기존 {len(existing_tickers)}개 → 총 {len(df_uni)}개)")
else:
    print("  ℹ 추가할 신규 종목 없음 (이미 모두 등록됨)")

# ── 2. trading_signals.xlsx Summary 탭 업데이트 (즉시 감시용) ────
SIGNAL_FILE = 'output/trading_signals.xlsx'
print(f"\n[2] {SIGNAL_FILE} Summary 탭 업데이트...")

df_sum = pd.read_excel(SIGNAL_FILE, sheet_name='Summary', dtype={'티커':str})
df_hist = pd.read_excel(SIGNAL_FILE, sheet_name='History', dtype={'티커':str})
existing_sum = set(df_sum['티커'].astype(str).str.zfill(6).tolist())

added = 0
for r in ok_results:
    t = str(r['ticker']).zfill(6)
    if t in existing_sum:
        # 이미 있는 종목은 건드리지 않음 (기존 매수선 유지)
        print(f"  — {r['name']} ({t}): 이미 존재, 스킵")
        continue

    # 신규 행 추가 (기존 Summary 컬럼 구조 그대로)
    new_row = {col: None for col in df_sum.columns}
    new_row.update({
        '티커': t,
        '종목명': r['name'],
        '매수상태': 'NONE',
        '알람상태': 'WATCHING',
        '종가': r['cur'],
        '고가': r['high'],
        '저가': r['low'],
        '20일선(당일)': r['ma20'],
        '20일선(익일)': r['ma20'],
        '-20%엔벨로프(당일)': r['ma20']*0.80,
        '-20%엔벨로프(익일)': r['ma20']*0.80,
        '1차매수선(당일)': r['b1'],
        '1차매수선(익일)': r['b1'],
        '2차매수선(당일)': r['b2'],
        '2차매수선(익일)': r['b2'],
        '3차매수선(당일)': r['b3'],
        '3차매수선(익일)': r['b3'],
        '최근감시일': today_dt,
    })
    df_sum = pd.concat([df_sum, pd.DataFrame([new_row])], ignore_index=True)
    added += 1

# 저장
with pd.ExcelWriter(SIGNAL_FILE, engine='openpyxl') as writer:
    df_sum.to_excel(writer, sheet_name='Summary', index=False)
    df_hist.to_excel(writer, sheet_name='History', index=False)

print(f"  ✓ {added}개 신규 추가 / 기존 종목 매수선 갱신 (총 {len(df_sum)}개)")
print(f"\n완료! 모니터가 다음 사이클(최대 60초)에 자동으로 반영합니다.")
