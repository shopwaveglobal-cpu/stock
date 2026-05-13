#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""시트 이름 자동 감지 테스트"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Daily_Turnover_Tracker import read_existing_data, get_last_update_date

EXCEL_PATH = "output/turnover_universe.xlsx"

print("=" * 60)
print("시트 이름 자동 감지 테스트")
print("=" * 60)

# 1. 데이터 읽기 테스트
print("\n[1] read_existing_data() 테스트")
df = read_existing_data(EXCEL_PATH)
print(f"  - 읽은 종목 수: {len(df)}개")
print(f"  - 컬럼: {df.columns.tolist()}")

# 2. 최근주도주 확인
print("\n[2] 최근주도주 확인")
recent_dates = df['최근주도주'].value_counts().sort_index().tail(5)
print(recent_dates)

# 3. 업데이트 날짜 읽기 테스트
print("\n[3] get_last_update_date() 테스트")
last_update = get_last_update_date(EXCEL_PATH)
print(f"  - 최종 업데이트: {last_update}")

print("\n" + "=" * 60)
print("테스트 완료!")
print("=" * 60)
