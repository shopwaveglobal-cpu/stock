import requests, time

body = {'grant_type':'client_credentials','appkey':'IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU','secretkey':'eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs'}
r = requests.post('https://api.kiwoom.com/oauth2/token', headers={'Content-Type':'application/json;charset=UTF-8'}, json=body, timeout=20)
TOKEN = r.json()['token']
hdrs = {'authorization': f'Bearer {TOKEN}','Content-Type':'application/json;charset=UTF-8','api-id':'ka10081','cont-yn':'N','next-key':''}
today = '20260604'

def check(ticker, ref):
    try:
        b = {'stk_cd':f'{ticker}_AL','base_dt':today,'upd_stkpc_tp':'1','stex_tp':'3'}
        r = requests.post('https://api.kiwoom.com/api/dostk/chart', headers=hdrs, json=b, timeout=10)
        d = r.json().get('stk_dt_pole_chart_qry',[])
        if d:
            raw = str(d[0].get('cur_prc','')).replace(',','').strip()
            if not raw: return None
            cur = abs(int(raw))
            diff = abs(cur-ref)/ref*100
            ok = '<<< OK' if diff < 8 else ''
            print(f'  {ticker} = {cur:>8,}  (diff {diff:.0f}%) {ok}')
            return cur
        else:
            print(f'  {ticker} = 데이터없음')
            return None
    except Exception as e:
        print(f'  {ticker} = 오류: {e}')
        return None
    finally:
        time.sleep(0.3)

print('=== 현대힘스 (검증가 13,820) ===')
for t in ['100230','192820','321820','307260','238490','320000','063570','007340','014990','238500','011700','011760','011610','024890','024900','025440','025450','025460','025500','025540','025560']:
    check(t, 13820)

print()
print('=== 성우하이텍 (검증가 6,450) ===')
for t in ['015260','045300','062900','097800','268280','041510','015280','006830','030000','030520','041620','046210','048410','049800','050760','054090','054120','060380','062070','064130']:
    check(t, 6450)

print()
print('=== 실리콘투 257720 확인 ===')
check('257720', 31400)
