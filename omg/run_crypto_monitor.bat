@echo off
REM 암호화폐 실시간 모니터 실행 스크립트
REM OMG Phase 1.5 매수목표 접근 알림 시스템

cd /d C:\Users\log\Desktop\Code\omg

echo ========================================
echo 암호화폐 실시간 모니터 시작
echo ========================================
echo.

REM Python 경로 (환경에 맞게 수정)
set PYTHON_EXE=python

REM 실행
%PYTHON_EXE% crypto_realtime_monitor.py

pause
