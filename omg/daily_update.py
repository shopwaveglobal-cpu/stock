#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
암호화폐 일일 업데이트 시스템 (00:00 실행)

기능:
1. 00:00에 DEBUG 파일 생성 (auto_debug_builder.py)
2. 00:00에 ANALYSIS 파일 생성 (coin_analysis_excel.py)
3. 생성된 파일 정보 출력

이 파일은 crypto_realtime_monitor.py에서 분리되었습니다.
실시간 모니터링과 일일 업데이트를 명확히 분리하기 위함입니다.
"""

import os
import sys
import subprocess
import pathlib
from datetime import datetime


class DailyUpdateSystem:
    def __init__(self):
        self.omg_dir = pathlib.Path(__file__).parent  # 현재 스크립트 위치

    def run_daily_update(self):
        """00:00에 실행되는 일일 업데이트"""
        print(f"[{datetime.now()}] 일일 업데이트 시작...")

        try:
            # OMG 디렉토리로 이동
            os.chdir(self.omg_dir)

            # DEBUG 파일 생성
            print("=" * 60)
            print("Step 1: DEBUG 파일 생성 중...")
            print("=" * 60)
            result = subprocess.run([
                "python", "auto_debug_builder.py", "--limit-days", "1200"
            ], capture_output=True, text=True, encoding='cp949')

            if result.returncode != 0:
                print(f"[ERROR] DEBUG 파일 생성 실패: {result.stderr}")
                return False

            print("[OK] DEBUG 파일 생성 완료")
            print(result.stdout)

            # ANALYSIS 파일 생성
            print("\n" + "=" * 60)
            print("Step 2: ANALYSIS 파일 생성 중...")
            print("=" * 60)
            result = subprocess.run([
                "python", "coin_analysis_excel.py"
            ], capture_output=True, text=True, encoding='cp949')

            if result.returncode != 0:
                print(f"[ERROR] ANALYSIS 파일 생성 실패: {result.stderr}")
                return False

            print("[OK] ANALYSIS 파일 생성 완료")
            print(result.stdout)

            # 최신 ANALYSIS 파일 확인
            output_dir = self.omg_dir / "output"
            analysis_files = list(output_dir.glob("coin_analysis_*.xlsx"))
            if analysis_files:
                latest_file = max(analysis_files, key=os.path.getctime)
                print(f"\n[INFO] 최신 ANALYSIS 파일: {latest_file.name}")

            # DEBUG 파일 개수 확인
            debug_dir = self.omg_dir / "debug"
            debug_files = list(debug_dir.glob("*_debug.csv"))
            print(f"[INFO] DEBUG 파일 개수: {len(debug_files)}개")

            print("\n" + "=" * 60)
            print(f"[SUCCESS] 일일 업데이트 완료! [{datetime.now()}]")
            print("=" * 60)

            return True

        except Exception as e:
            print(f"[ERROR] 일일 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 원래 디렉토리로 복귀
            os.chdir(self.omg_dir)


def main():
    """메인 실행 함수"""
    print("\n" + "=" * 60)
    print("암호화폐 일일 업데이트 시스템")
    print("=" * 60)
    print(f"실행 시각: {datetime.now()}")
    print("=" * 60)

    updater = DailyUpdateSystem()
    success = updater.run_daily_update()

    if success:
        print("\n[SUCCESS] 모든 작업이 성공적으로 완료되었습니다.")
        sys.exit(0)
    else:
        print("\n[ERROR] 작업 중 오류가 발생했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
