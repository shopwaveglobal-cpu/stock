import requests, math

body = {'grant_type':'client_credentials','appkey':'IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU','secretkey':'eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs'}
TOKEN = requests.post('https://api.kiwoom.com/oauth2/token', headers={'Content-Type':'application/json;charset=UTF-8'}, json=body, timeout=20).json()['token']
H = {'authorization':f'Bearer {TOKEN}','Content-Type':'application/json;charset=UTF-8','api-id':'ka10081','cont-yn':'N','next-key':''}

def get_tick(p):
    if p<1000: return 1
    if p<5000: return 5
    if p<10000: return 10
    if p<50000: return 50
    if p<100000: return 100
    if p<500000: return 500
    return 1000
def ceil_tick(p):
    t=get_tick(p); return math.ceil(p/t)*t
def calc_buy1(S19):
    p=ceil_tick(S19/24.0)
    while True:
        d=get_tick(p)
        if p<(S19+25.0*d)/24.0: return int(p)
        p+=d
def calc_buy2(b1): return ceil_tick(b1*0.90)
def calc_buy3(b2): return ceil_tick(b2*0.90)

b={'stk_cd':'079550_AL','base_dt':'20260604','upd_stkpc_tp':'1','stex_tp':'3'}
data=requests.post('https://api.kiwoom.com/api/dostk/chart',headers=H,json=b,timeout=10).json().get('stk_dt_pole_chart_qry',[])

print('최근 5일 raw 데이터:')
for i, d in enumerate(data[:5]):
    print(f'  [{i}] dt={d.get("dt")} cur_prc={d.get("cur_prc")}')

print()

# 방법 A: data[0:20] - 오늘 장중가 포함 (우리 스크립트 현재 방식)
closesA = [abs(int(str(d.get('cur_prc','')).replace(',','').strip())) for d in data[:20] if str(d.get('cur_prc','')).strip()]
closesA.reverse()
S20A = sum(closesA); S19A = S20A - closesA[0]
buy1A = calc_buy1(S19A); buy2A = calc_buy2(buy1A); buy3A = calc_buy3(buy2A)
print(f'방법A (오늘 현재가 포함 data[0:20]):  MA20={S20A/20:,.0f}  1차={buy1A:,}  2차={buy2A:,}  3차={buy3A:,}')

# 방법 B: data[1:21] - 어제까지의 확정 종가만 사용 (정확한 익일 기준)
closesB = [abs(int(str(d.get('cur_prc','')).replace(',','').strip())) for d in data[1:21] if str(d.get('cur_prc','')).strip()]
closesB.reverse()
S20B = sum(closesB); S19B = S20B - closesB[0]
buy1B = calc_buy1(S19B); buy2B = calc_buy2(buy1B); buy3B = calc_buy3(buy2B)
print(f'방법B (확정종가만 data[1:21]):         MA20={S20B/20:,.0f}  1차={buy1B:,}  2차={buy2B:,}  3차={buy3B:,}')

print()
print(f'사용자 기준: 679,000')
print(f'  방법A 차이: {buy1A-679000:+,}  ({(buy1A-679000)/679000*100:+.1f}%)')
print(f'  방법B 차이: {buy1B-679000:+,}  ({(buy1B-679000)/679000*100:+.1f}%)')
