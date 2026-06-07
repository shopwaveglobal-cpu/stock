import json
import pandas as pd

with open('alert_history.json', encoding='utf-8-sig') as f:
    data = json.load(f)

alerts = data.get('alerts', {})
print(f"날짜: {data.get('date','?')}")
print(f"알람 기록 종목 수: {len(alerts)}개\n")

# Summary에서 종목명 매핑
df = pd.read_excel('output/trading_signals.xlsx', sheet_name='Summary', dtype={'티커':str})
name_map = dict(zip(df['티커'].astype(str).str.zfill(6), df['종목명']))

print("오늘 발송된 알람:")
for ticker, flags in sorted(alerts.items()):
    sent = [k for k,v in flags.items() if v]
    if sent:
        name = name_map.get(ticker, ticker)
        print(f"  {name} ({ticker}): {', '.join(sent)}")
