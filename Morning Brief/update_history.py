# -*- coding: utf-8 -*-
"""당일 종가 1줄 추가. 사용: python3 update_history.py '{"date":"2026-06-10","gold":4275.0,"silver":66.1,"btc":62100,"eth":1655.2,"usd":1521.4,"eur":1755.0,"jpy":9.51}'
jpy는 1엔당 원화(예: 9.51). 일부 지표만 줘도 됨. 같은 날짜는 덮어씀."""
import json, sys, os
BASE=os.path.dirname(os.path.abspath(__file__))
P=os.path.join(BASE,"data","market_history.json")
h=json.load(open(P))
new=json.loads(sys.argv[1]); date=new.pop("date")
for k,v in new.items():
    if k in h: h[k]["data"][date]=v
json.dump(h,open(P,"w"),ensure_ascii=False)
print("updated",date,list(new.keys()))
