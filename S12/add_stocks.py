"""
S12 신규 종목 추가 스크립트

사용법:
    python add_stocks.py                   # 신규 종목만 추가 (기존 종목 절대 불변)
    python add_stocks.py --update          # 기존 종목 매수선도 갱신 (의도적일 때만)
    python add_stocks.py --dry-run         # 실제 저장 없이 미리보기만

주의: --update 없이 실행하면 기존 종목의 매수선은 절대 변경되지 않습니다.
"""
import sys
import argparse
import pandas as pd
import requests
import math
import time
from datetime import datetime

# ── 인자 파싱 ──────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description='S12 신규 종목 추가')
parser.add_argument('--update', action='store_true',
                    help='기존 종목 매수선 갱신 (기본값: 기존 종목 스킵)')
parser.add_argument('--dry-run', action='store_true',
                    help='실제 저장 없이 결과만 미리보기')
args = parser.parse_args()

if args.update:
    print("=" * 60)
    print("⚠  --update 모드: 기존 종목 매수선도 갱신됩니다.")
    print("   기존 알람 히스토리가 있는 종목에 알람이 재발생할 수 있습니다.")
    print("=" * 60)
    confirm = input("계속하시겠습니까? (yes 입력): ").strip().lower()
    if confirm != 'yes':
        print("취소됨.")
        sys.exit(0)

if args.dry_run:
    print("=" * 60)
    print("ℹ  DRY-RUN 모드: 파일 저장 없이 미리보기만 합니다.")
    print("=" * 60)

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

# ── 추가할 종목 목록 ─────────────────────────────────────────────
# 형식: ('종목명', '티커')
# 티커 모를 경우 verify_tickers.py 또는 find_tickers.py로 먼저 확인
NEW_STOCKS = [
    # 여기에 추가할 종목을 입력하세요
    # ('삼성전자', '005930'),
    # ('SK하이닉스', '000660'),
]

if not NEW_STOCKS:
    print("추가할 종목이 없습니다. NEW_STOCKS 리스트를 채워주세요.")
    sys.exit(0)

# ── 매수선 계산 ───────────────────────────────────────────────────
today_str = datetime.now().strftime('%Y%m%d')
today_dt  = datetime.now().date()

print(f"\n매수선 계산 중... (총 {len(NEW_STOCKS)}개)")
print("-" * 70)
results = []
for name, ticker in NEW_STOCKS:
    try:
        b = {'stk_cd':f'{ticker}_AL','base_dt':today_str,'upd_stkpc_tp':'1','stex_tp':'3'}
        data = requests.post('https://api.kiwoom.com/api/dostk/chart',
            headers=HEADERS, json=b, timeout=10).json().get('stk_dt_pole_chart_qry',[])

        # data[1:21]: 오늘 장중가 제외, 확정 종가만 사용
        closes = []
        for d in data[1:21]:
            raw = str(d.get('cur_prc','')).replace(',','').strip()
            if raw: closes.append(abs(int(raw)))
        closes.reverse()

        if len(closes) < 20:
            print(f"  SKIP  {name} ({ticker}): 데이터 부족 ({len(closes)}일)")
            time.sleep(0.3); continue

        S20 = sum(closes); ma20 = S20/20; S19 = S20 - closes[0]
        raw_cur = str(data[0].get('cur_prc', data[1].get('cur_prc',0))).replace(',','')
        cur = abs(int(raw_cur)) if raw_cur else 0
        high = abs(int(str(data[0].get('high_pric',cur)).replace(',','')))
        low  = abs(int(str(data[0].get('low_pric', cur)).replace(',','')))

        b1 = calc_buy1(S19); b2 = calc_buy2(b1); b3 = calc_buy3(b2)

        print(f"  OK    {name:<22} 1차={b1:>9,}  2차={b2:>9,}  3차={b3:>9,}  (현재가 {cur:,})")
        results.append({'name':name,'ticker':ticker,'ok':True,
            'cur':cur,'high':high,'low':low,'ma20':ma20,
            'b1':b1,'b2':b2,'b3':b3})
        time.sleep(0.3)
    except Exception as e:
        print(f"  ERROR {name} ({ticker}): {e}")

ok_results = [r for r in results if r.get('ok')]
print(f"\n계산 완료: {len(ok_results)}/{len(NEW_STOCKS)}개\n")

if not ok_results:
    print("추가 가능한 종목이 없습니다.")
    sys.exit(0)

# ── 기존 데이터 로드 ──────────────────────────────────────────────
UNIVERSE_FILE = 'output/turnover_universe.xlsx'
SIGNAL_FILE   = 'output/trading_signals.xlsx'

df_uni = pd.read_excel(UNIVERSE_FILE, dtype={'티커':str})
df_sum = pd.read_excel(SIGNAL_FILE, sheet_name='Summary', dtype={'티커':str})
df_hist= pd.read_excel(SIGNAL_FILE, sheet_name='History', dtype={'티커':str})

existing_uni = set(df_uni['티커'].astype(str).str.zfill(6).tolist())
existing_sum = set(df_sum['티커'].astype(str).str.zfill(6).tolist())

# ── 미리보기 출력 ─────────────────────────────────────────────────
print("=" * 60)
print("변경 예정 내역:")
print("-" * 60)
new_in_uni = 0
new_in_sum = 0
skip_sum   = 0
update_sum = 0

for r in ok_results:
    t = str(r['ticker']).zfill(6)
    uni_status = "NEW" if t not in existing_uni else "SKIP"
    if t not in existing_sum:
        sum_status = "NEW"
        new_in_sum += 1
    elif args.update:
        sum_status = "UPDATE (--update)"
        update_sum += 1
    else:
        sum_status = "SKIP (기존유지)"
        skip_sum += 1
    if uni_status == "NEW": new_in_uni += 1
    print(f"  {r['name']:<22} Universe:{uni_status:<5}  Summary:{sum_status}")

print("-" * 60)
print(f"  Universe: 신규 {new_in_uni}개 추가 예정")
print(f"  Summary:  신규 {new_in_sum}개 추가 예정"
      + (f" / {update_sum}개 매수선 갱신" if update_sum else "")
      + (f" / {skip_sum}개 스킵" if skip_sum else ""))
print("=" * 60)

if args.dry_run:
    print("\nDRY-RUN 완료. 실제 저장하려면 --dry-run 없이 실행하세요.")
    sys.exit(0)

if new_in_uni == 0 and new_in_sum == 0 and update_sum == 0:
    print("\n추가/변경할 내용이 없습니다.")
    sys.exit(0)

# ── 1. turnover_universe.xlsx 업데이트 ───────────────────────────
print(f"\n[1] {UNIVERSE_FILE} 업데이트...")
uni_rows = []
for r in ok_results:
    t = str(r['ticker']).zfill(6)
    if t not in existing_uni:
        uni_rows.append({
            '첫거래날짜': today_dt, '최근거래날짜': today_dt,
            '티커': t, '종목명': r['name'],
            '거래량평균(일)': 0, '거래횟수': 0,
        })

if uni_rows:
    df_add = pd.DataFrame(uni_rows)
    df_uni = pd.concat([df_uni, df_add[df_uni.columns.intersection(df_add.columns)]], ignore_index=True)
    if not args.dry_run:
        df_uni.to_excel(UNIVERSE_FILE, index=False)
    print(f"  {len(uni_rows)}개 신규 추가 (총 {len(df_uni)}개)")
else:
    print("  추가할 신규 종목 없음")

# ── 2. trading_signals.xlsx Summary 탭 업데이트 ──────────────────
print(f"\n[2] {SIGNAL_FILE} Summary 탭 업데이트...")
added = 0; updated = 0

for r in ok_results:
    t = str(r['ticker']).zfill(6)

    if t in existing_sum:
        if args.update:
            # --update 플래그가 있을 때만 기존 종목 갱신
            idx = df_sum[df_sum['티커'].astype(str).str.zfill(6) == t].index
            if len(idx):
                df_sum.loc[idx[0], '1차매수선(익일)'] = r['b1']
                df_sum.loc[idx[0], '2차매수선(익일)'] = r['b2']
                df_sum.loc[idx[0], '3차매수선(익일)'] = r['b3']
                df_sum.loc[idx[0], '20일선(익일)']   = r['ma20']
                print(f"  UPDATE {r['name']} ({t}): 1차={r['b1']:,} / 2차={r['b2']:,} / 3차={r['b3']:,}")
                updated += 1
        else:
            # 기존 종목은 건드리지 않음 (기본 동작)
            print(f"  SKIP   {r['name']} ({t}): 기존 매수선 유지")
        continue

    # 신규 행 추가
    new_row = {col: None for col in df_sum.columns}
    new_row.update({
        '티커': t, '종목명': r['name'], '매수상태': 'NONE', '알람상태': 'WATCHING',
        '종가': r['cur'], '고가': r['high'], '저가': r['low'],
        '20일선(당일)': r['ma20'], '20일선(익일)': r['ma20'],
        '-20%엔벨로프(당일)': r['ma20']*0.80, '-20%엔벨로프(익일)': r['ma20']*0.80,
        '1차매수선(당일)': r['b1'], '1차매수선(익일)': r['b1'],
        '2차매수선(당일)': r['b2'], '2차매수선(익일)': r['b2'],
        '3차매수선(당일)': r['b3'], '3차매수선(익일)': r['b3'],
        '최근감시일': today_dt,
    })
    df_sum = pd.concat([df_sum, pd.DataFrame([new_row])], ignore_index=True)
    print(f"  ADD    {r['name']} ({t}): 1차={r['b1']:,} / 2차={r['b2']:,} / 3차={r['b3']:,}")
    added += 1

if added > 0 or updated > 0:
    if not args.dry_run:
        with pd.ExcelWriter(SIGNAL_FILE, engine='openpyxl') as writer:
            df_sum.to_excel(writer, sheet_name='Summary', index=False)
            df_hist.to_excel(writer, sheet_name='History', index=False)
    print(f"\n  신규 추가: {added}개 / 매수선 갱신: {updated}개 (총 {len(df_sum)}개)")
else:
    print("\n  변경 없음")

print("\n완료! 모니터가 다음 사이클(최대 60초)에 자동으로 반영합니다.")
if args.dry_run:
    print("(DRY-RUN: 실제 파일은 변경되지 않았습니다)")
