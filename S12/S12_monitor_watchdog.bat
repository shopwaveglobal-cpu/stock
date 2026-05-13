@echo off
chcp 65001 >nul

REM ================================================
REM S12 실시간 모니터 재시작 스크립트
REM - 07:xx : 항상 kill+restart (토큰 갱신)
REM - 그 외 : 프로세스 없을 때만 시작
REM ================================================

cd /d "C:\Users\log\Desktop\Code\S12"

powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\Users\log\Desktop\Code\S12\S12_smart_restart.ps1"

exit /b 0
