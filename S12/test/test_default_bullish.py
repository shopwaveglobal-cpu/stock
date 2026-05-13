#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기본값 양봉 필터 테스트
"""

import sys
import argparse

# argparse 동작 테스트
parser = argparse.ArgumentParser()
parser.add_argument("--no-filter-bullish", action="store_true")
args = parser.parse_args([])  # 빈 인자

filter_bullish = not args.no_filter_bullish

print("=" * 60)
print("기본값 양봉 필터 테스트")
print("=" * 60)
print(f"\n인자 없음:")
print(f"  args.no_filter_bullish = {args.no_filter_bullish}")
print(f"  filter_bullish = {filter_bullish}")
print(f"  결과: {'양봉 필터 활성화 ✓' if filter_bullish else '양봉 필터 비활성화'}")

# --no-filter-bullish 있을 때
args2 = parser.parse_args(["--no-filter-bullish"])
filter_bullish2 = not args2.no_filter_bullish

print(f"\n--no-filter-bullish 플래그 사용:")
print(f"  args.no_filter_bullish = {args2.no_filter_bullish}")
print(f"  filter_bullish = {filter_bullish2}")
print(f"  결과: {'양봉 필터 활성화' if filter_bullish2 else '양봉 필터 비활성화 ✓'}")

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)
