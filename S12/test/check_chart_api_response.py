#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
차트 API 응답 구조 확인 (시가 필드 찾기)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import requests
import json
import argparse
from datetime import datetime

# API 설정
API_BASE_URL = "https://api.kiwoom.com"
API_CHART_ENDPOINT = "/api/dostk/chart"
API_CHART_ID = "ka10081"

def get_token(appkey, secret):
    """OAuth2 토큰 획득"""

    url = f"{API_BASE_URL}/oauth2/token"
    body = {
        "grant_type": "client_credentials",
        "appkey": appkey,
        "secretkey": secret
    }

    response = requests.post(url, json=body)
    response.raise_for_status()
    result = response.json()
    return result["token"]

def fetch_chart_raw(token: str, ticker: str):
    """차트 데이터 조회 (원본 응답 출력)"""
    # 통합 종목코드 (티커 + _AL)
    integrated_ticker = f"{ticker}_AL"

    headers = {
        "authorization": f"Bearer {token}",
        "Content-Type": "application/json;charset=UTF-8",
        "api-id": API_CHART_ID,
        "cont-yn": "N",
        "next-key": ""
    }

    body = {
        "stk_cd": integrated_ticker,
        "base_dt": datetime.now().strftime("%Y%m%d"),
        "upd_stkpc_tp": "1",  # 수정주가
        "stex_tp": "3"  # 통합
    }

    url = API_BASE_URL + API_CHART_ENDPOINT
    response = requests.post(url, headers=headers, json=body, timeout=20)
    response.raise_for_status()

    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--appkey", required=True)
    parser.add_argument("--secret", required=True)
    args = parser.parse_args()

    print("=" * 80)
    print("차트 API 응답 구조 확인")
    print("=" * 80)

    # 토큰 획득
    print("\n[1] 토큰 획득 중...")
    token = get_token(args.appkey, args.secret)
    print("  [OK] 토큰 획득 완료")

    # 삼성전자 차트 조회
    print("\n[2] 삼성전자(005930) 차트 조회...")
    result = fetch_chart_raw(token, "005930")

    # 첫 번째 레코드만 상세 출력
    print("\n[3] API 응답 구조:")
    print(f"  응답 키: {list(result.keys())}")

    # 데이터 배열 찾기
    records = None
    for key, value in result.items():
        if isinstance(value, list) and len(value) > 0:
            records = value
            print(f"  데이터 배열 키: {key}")
            print(f"  총 레코드 수: {len(records)}")
            break

    if records:
        print("\n[4] 첫 번째 레코드 필드:")
        first_record = records[0]
        for key in sorted(first_record.keys()):
            value = first_record[key]
            print(f"  {key}: {value}")

        print("\n[5] 시가 필드 검색:")
        open_candidates = [k for k in first_record.keys() if 'open' in k.lower() or 'oprc' in k.lower() or 'OPEN' in k or 'OPRC' in k or 'STRT' in k or 'strt' in k]
        if open_candidates:
            print(f"  [OK] 시가 후보 필드: {open_candidates}")
            for field in open_candidates:
                print(f"    {field} = {first_record[field]}")
        else:
            print("  [WARN] 시가 필드를 찾을 수 없습니다!")
            print("  모든 필드:")
            print(f"  {list(first_record.keys())}")

    print("\n" + "=" * 80)
    print("확인 완료")
    print("=" * 80)
