"""
신규 종목 20일선 매수선 계산 + 검증가 비교
"""
import requests
import math
from datetime import datetime

# ── 토큰 ──────────────────────────────────────────────────────────
body = {'grant_type':'client_credentials',
        'appkey':'IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU',
        'secretkey':'eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs'}
r = requests.post('https://api.kiwoom.com/oauth2/token',
                  headers={'Content-Type':'application/json;charset=UTF-8'},
                  json=body, timeout=20)
TOKEN = r.json()['token']
HEADERS = {
    'authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json;charset=UTF-8',
    'api-id': 'ka10081', 'cont-yn': 'N', 'next-key': ''
}

# ── 호가 단위 ─────────────────────────────────────────────────────
def get_tick(price):
    if price < 1000:    return 1
    if price < 5000:    return 5
    if price < 10000:   return 10
    if price < 50000:   return 50
    if price < 100000:  return 100
    if price < 500000:  return 500
    return 1000

def ceil_tick(price):
    t = get_tick(price)
    return math.ceil(price / t) * t

def floor_tick(price):
    t = get_tick(price)
    return math.floor(price / t) * t

# ── 매수선 계산 (Trading_Signal_System과 동일) ──────────────────────
def calc_buy1(S19_next):
    x_star = S19_next / 24.0
    p = ceil_tick(x_star)
    while True:
        delta = get_tick(p)
        upper = (S19_next + 25.0 * delta) / 24.0
        if p < upper:
            return int(p)
        p += delta

def calc_buy2(buy1):
    return ceil_tick(buy1 * 0.90)

def calc_buy3(buy2):
    return ceil_tick(buy2 * 0.90)

# ── 차트 데이터 취득 ──────────────────────────────────────────────
def get_chart(ticker):
    today = datetime.now().strftime('%Y%m%d')
    b = {'stk_cd': f'{ticker}_AL', 'base_dt': today, 'upd_stkpc_tp': '1', 'stex_tp': '3'}
    r = requests.post('https://api.kiwoom.com/api/dostk/chart',
                      headers=HEADERS, json=b, timeout=10)
    return r.json().get('stk_dt_pole_chart_qry', [])

# ── 종목 리스트 (이름, 티커, 검증가) ────────────────────────────────
stocks = [
    ('한화투자증권',    '003530',  5600),
    ('현대힘스',        'TBD',    13820),   # 티커 확인 필요
    ('포스코인터내셔널','047050', 56000),
    ('HPSP',           '403870', 41450),
    ('흥구석유',        '024060', 11260),
    ('대한해운',        '005880',  1930),
    ('후성',            '093370',  9760),
    ('HD현대일렉트릭',  '267260',947000),
    ('미래에셋증권',    '006800', 55100),
    ('LIG디펜스앤에어로스페이스','079550',679000),
    ('HD현대에너지솔루션','322000',154800),
    ('한미반도체',      '042700',268000),
    ('삼양식품',        '003230',1035000),
    ('HD현대건설기계',  '267270',132200),
    ('실리콘투',        '257760', 31400),
    ('쿠콘',            '294570', 20800),
    ('한국석유',        '004090', 10960),
    ('한화',            '000880',108200),
    ('풍산',            '103140', 69400),
    ('성우하이텍',      'TBD',    6450),   # 티커 확인 필요
    ('RFHIC',           '218410', 77800),
    ('셀바스AI',        '108860',  8950),
    ('펄어비스',        '263750', 38100),
    ('한화시스템',      '272210', 86400),
    ('쏠리드',          '050890', 13160),
    ('현대건설',        '000720',119800),
    ('대주전자재료',    '078600',117400),
    ('고영',            '098460', 30000),
    ('리노공업',        '058470', 83400),
    ('한국항공우주',    '047810',130900),
    ('필옵틱스',        '161580', 40100),
    ('한화에어로스페이스','012450',995000),
    ('SFA반도체',       '036540',  6820),
    ('엘앤에프',        '066970',134200),
    ('POSCO홀딩스',     '005490',364500),
    ('LS ELECTRIC',     '010120',218500),
    ('두산에너빌리티',  '034020', 91000),
]

# 티커 미확인 종목은 일단 스킵
print(f"{'종목명':<24} {'티커':<8} {'검증가':>10} {'현재가':>10} {'MA20':>10} {'1차매수선':>10} {'2차매수선':>10} {'3차매수선':>10} {'이격도1차':>9}")
print('-'*105)

results = []
ticker_errors = []

for name, ticker, ref_price in stocks:
    if ticker == 'TBD':
        print(f"{name:<24} {'??':<8} {ref_price:>10,} {'티커미확인':>10}")
        ticker_errors.append(name)
        continue

    try:
        data = get_chart(ticker)
        if not data or len(data) < 20:
            print(f"{name:<24} {ticker:<8} {ref_price:>10,} {'데이터부족':>10}")
            continue

        # 현재가 (오늘 첫 번째 항목)
        cur_prc_raw = str(data[0].get('cur_prc', '')).replace(',', '')
        if not cur_prc_raw:
            print(f"{name:<24} {ticker:<8} {ref_price:>10,} {'가격없음':>10}")
            continue
        cur_price = abs(int(cur_prc_raw))

        # 종가 리스트 (최신순 → 역순으로 오래된 것부터)
        closes = []
        for d in data[:20]:
            cp = str(d.get('cur_prc', '')).replace(',', '')
            if cp:
                closes.append(abs(int(cp)))
        closes.reverse()  # 오래된 것 → 최신

        if len(closes) < 20:
            print(f"{name:<24} {ticker:<8} {ref_price:>10,} {'20일데이터부족':>10}")
            continue

        # MA20 계산
        S20 = sum(closes)
        ma20 = S20 / 20

        # S19_next: 익일 기준 (가장 오래된 종가 제외)
        Close_D_19 = closes[0]   # 가장 오래된 종가 (D-19일)
        S19_next = S20 - Close_D_19

        # 매수선 계산
        buy1 = calc_buy1(S19_next)
        buy2 = calc_buy2(buy1)
        buy3 = calc_buy3(buy2)

        # 현재가 대비 1차 매수선 이격도
        dist1 = (cur_price - buy1) / buy1 * 100

        print(f"{name:<24} {ticker:<8} {ref_price:>10,} {cur_price:>10,} {ma20:>10,.0f} {buy1:>10,} {buy2:>10,} {buy3:>10,} {dist1:>+8.1f}%")

        results.append({
            '티커': ticker, '종목명': name,
            '검증가': ref_price, '현재가': cur_price,
            'MA20': ma20, '1차매수선': buy1, '2차매수선': buy2, '3차매수선': buy3,
            '이격도(%)': dist1
        })

    except Exception as e:
        print(f"{name:<24} {ticker:<8} 오류: {e}")

print()
print(f"계산 완료: {len(results)}개 / 티커 미확인: {len(ticker_errors)}개 ({', '.join(ticker_errors)})")
