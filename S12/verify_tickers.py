import requests
from datetime import datetime

body = {'grant_type':'client_credentials','appkey':'IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU','secretkey':'eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs'}
r = requests.post('https://api.kiwoom.com/oauth2/token', headers={'Content-Type':'application/json;charset=UTF-8'}, json=body, timeout=20)
TOKEN = r.json()['token']
print('토큰 발급 완료')

candidates = [
    ('한화투자증권','003530',5600),
    ('현대힘스','321820',13820),
    ('포스코인터내셔널','047050',56000),
    ('HPSP','403870',41450),
    ('흥구석유','024060',11260),
    ('대한해운','005880',1930),
    ('후성','093370',9760),
    ('HD현대일렉트릭','267260',947000),
    ('미래에셋증권','006800',55100),
    ('LIG디펜스앤에어로스페이스','079550',679000),
    ('HD현대에너지솔루션','322000',154800),
    ('한미반도체','042700',268000),
    ('삼양식품','003230',1035000),
    ('HD현대건설기계','267270',132200),
    ('실리콘투','257760',31400),
    ('쿠콘','294570',20800),
    ('한국석유','004090',10960),
    ('한화','000880',108200),
    ('풍산','103140',69400),
    ('성우하이텍','015260',6450),
    ('RFHIC','218410',77800),
    ('셀바스AI','108860',8950),
    ('펄어비스','263750',38100),
    ('한화시스템','272210',86400),
    ('쏠리드','050890',13160),
    ('현대건설','000720',119800),
    ('대주전자재료','078600',117400),
    ('고영','098460',30000),
    ('리노공업','058470',83400),
    ('한국항공우주','047810',130900),
    ('필옵틱스','161580',40100),
    ('한화에어로스페이스','012450',995000),
    ('SFA반도체','036540',6820),
    ('엘앤에프','066970',134200),
    ('POSCO홀딩스','005490',364500),
    ('LS ELECTRIC','010120',218500),
    ('두산에너빌리티','034020',91000),
]

today = datetime.now().strftime('%Y%m%d')
headers = {
    'authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json;charset=UTF-8',
    'api-id': 'ka10081', 'cont-yn': 'N', 'next-key': ''
}

print(f"{'종목명':<24} {'티커':<8} {'검증가':>10} {'현재가':>10} {'차이%':>7} {'결과'}")
print('-'*70)
mismatches = []
for name, ticker, ref_price in candidates:
    try:
        b = {'stk_cd': f'{ticker}_AL', 'base_dt': today, 'upd_stkpc_tp': '1', 'stex_tp': '3'}
        rr = requests.post('https://api.kiwoom.com/api/dostk/chart', headers=headers, json=b, timeout=10)
        data = rr.json().get('stk_dt_pole_chart_qry', [])
        if data:
            cur = abs(int(str(data[0]['cur_prc']).replace(',','')))
            ratio = abs(cur - ref_price) / ref_price * 100
            ok = 'OK' if ratio < 5 else f'X({ratio:.0f}%차)'
            print(f"{name:<24} {ticker:<8} {ref_price:>10,} {cur:>10,} {ratio:>6.1f}% {ok}")
            if ratio >= 5:
                mismatches.append((name, ticker, ref_price, cur))
        else:
            print(f"{name:<24} {ticker:<8} {ref_price:>10,} {'데이터없음':>10}       ?")
            mismatches.append((name, ticker, ref_price, 0))
    except Exception as e:
        print(f"{name:<24} {ticker:<8} 오류: {e}")

print()
print(f'불일치/미확인: {len(mismatches)}개')
for m in mismatches:
    print(f'  {m[0]} ({m[1]}): 검증가 {m[2]:,} / API {m[3]:,}')
