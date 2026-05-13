#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
암호화폐 실시간 모니터 실행 래퍼
에러 로깅 기능 포함
"""
import sys
import os
import traceback
from datetime import datetime

# 현재 디렉토리를 omg로 설정
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 로그 파일 경로
LOG_FILE = "crypto_monitor_error.log"

def log_error(message):
    """에러를 파일과 화면에 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}\n"

    # 화면 출력
    print(log_message, end='')

    # 파일 출력
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message)

try:
    print("=" * 80)
    print("암호화폐 실시간 모니터 시작")
    print("=" * 80)
    print()

    # crypto_realtime_monitor 임포트 및 실행
    import crypto_realtime_monitor

    print("모니터 초기화 중...")
    monitor = crypto_realtime_monitor.CryptoRealtimeMonitor()

    print("모니터링 시작...")
    monitor.start_monitoring()

except KeyboardInterrupt:
    print("\n\n사용자에 의해 중단되었습니다.")
    log_error("사용자에 의해 중단됨")
    sys.exit(0)

except Exception as e:
    error_msg = f"실행 중 오류 발생: {str(e)}"
    log_error(error_msg)
    log_error(traceback.format_exc())

    print("\n" + "=" * 80)
    print("⚠️ 오류가 발생했습니다")
    print("=" * 80)
    print(f"오류: {e}")
    print(f"\n자세한 내용은 {LOG_FILE} 파일을 확인하세요.")
    print("=" * 80)

    input("\nEnter 키를 눌러 종료하세요...")
    sys.exit(1)
