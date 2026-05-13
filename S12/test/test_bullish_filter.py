#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
양봉 필터 기능 테스트
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Daily_Turnover_Tracker import get_access_token, fetch_today_candle, is_bullish_candle

APPKEY = "IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU"
SECRET = "eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs"

# 테스트 종목 (11/7 실제 데이터 기준)
TEST_STOCKS = [
    ("005930", "삼성전자"),  # 시가 97,800 / 종가 97,500 → 음봉
    ("000660", "SK하이닉스"),  # 시가/종가 확인 필요
]

print("=" * 80)
print("양봉 필터 기능 테스트")
print("=" * 80)

# 토큰 획득
print("\n[1] 토큰 획득 중...")
token = get_access_token(APPKEY, SECRET)
print("  [OK] 토큰 획득 완료")

# 종목별 테스트
print("\n[2] 종목별 양봉 체크:")
for ticker, name in TEST_STOCKS:
    print(f"\n  {name} ({ticker}):")

    # 캔들 데이터 조회
    candle = fetch_today_candle(token, ticker)

    if candle:
        open_price = candle['open']
        close_price = candle['close']
        is_bullish = open_price < close_price

        print(f"    시가: {open_price:,.0f}원")
        print(f"    종가: {close_price:,.0f}원")
        print(f"    결과: {'양봉' if is_bullish else '음봉'}")
    else:
        print(f"    [ERROR] 캔들 데이터 조회 실패")

    # is_bullish_candle 함수 테스트
    bullish_result = is_bullish_candle(token, ticker)
    print(f"    is_bullish_candle(): {bullish_result}")

print("\n" + "=" * 80)
print("테스트 완료")
print("=" * 80)
