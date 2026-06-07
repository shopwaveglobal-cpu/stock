import pandas as pd
df = pd.read_excel('output/trading_signals.xlsx', sheet_name='Summary', dtype={'티커':str})
lig = df[df['티커']=='079550'].iloc[0]
col1 = '1차매수선(익일)'
col2 = '2차매수선(익일)'
col3 = '3차매수선(익일)'
print(f'LIG넥스원 갱신 확인:')
print(f'  1차: {lig[col1]:,.0f}  (목표: 679,000)')
print(f'  2차: {lig[col2]:,.0f}')
print(f'  3차: {lig[col3]:,.0f}')
