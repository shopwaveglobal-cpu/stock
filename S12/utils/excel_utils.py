#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 읽기 공통 유틸리티
시트 이름 자동 감지 기능 제공

사용 예시:
    from utils.excel_utils import read_turnover_universe

    # turnover_universe.xlsx 읽기 (시트 이름 자동 감지)
    df = read_turnover_universe()

    # 또는 커스텀 경로
    df = read_turnover_universe("path/to/file.xlsx")

    # 일반 Excel 파일 읽기 (시트 이름 자동 감지)
    from utils.excel_utils import read_excel_auto_sheet
    df = read_excel_auto_sheet("file.xlsx", preferred_sheet="Sheet1")
"""

import pandas as pd
from typing import Optional


def read_excel_auto_sheet(file_path: str, preferred_sheet: str = "universe", **kwargs) -> pd.DataFrame:
    """
    시트 이름 자동 감지하여 Excel 파일 읽기

    Args:
        file_path: Excel 파일 경로
        preferred_sheet: 우선적으로 찾을 시트 이름 (기본값: "universe")
        **kwargs: pd.read_excel()에 전달할 추가 인자

    Returns:
        pd.DataFrame: 읽은 데이터
    """
    try:
        # 우선 지정된 시트 이름으로 시도
        return pd.read_excel(file_path, sheet_name=preferred_sheet, **kwargs)
    except ValueError as e:
        if "Worksheet" in str(e) and "not found" in str(e):
            # 시트가 없으면 첫 번째 시트 읽기
            return pd.read_excel(file_path, sheet_name=0, **kwargs)
        else:
            raise


def read_turnover_universe(file_path: str = "output/turnover_universe.xlsx") -> pd.DataFrame:
    """
    turnover_universe.xlsx 읽기 (시트 이름 자동 감지 + 불필요한 컬럼 제거)

    Args:
        file_path: Excel 파일 경로 (기본값: "output/turnover_universe.xlsx")

    Returns:
        pd.DataFrame: 유니버스 데이터 (정제됨)
    """
    df = read_excel_auto_sheet(file_path, preferred_sheet="universe", dtype={"티커": str})

    # Unnamed 컬럼 및 업데이트 관련 컬럼 제거
    cols_to_drop = [col for col in df.columns if "Unnamed" in str(col) or "업데이트" in str(col) or "최종" in str(col)]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    return df


if __name__ == "__main__":
    # 테스트
    df = read_turnover_universe()
    print(f"총 {len(df)}개 종목 읽기 성공")
    print(f"컬럼: {df.columns.tolist()}")
