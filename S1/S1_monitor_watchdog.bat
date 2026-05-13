@echo off
chcp 65001 >nul

REM ================================================
REM S1 실시간 모니터 재시작 스크립트
REM - 기존 프로세스 종료 후 새로 시작 (토큰 매일 갱신)
REM ================================================

cd /d "C:\Users\log\Desktop\Code\S1"

REM 1. 기존 S1 프로세스 종료
powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\Users\log\Desktop\Code\S1\S1_restart_monitor.ps1"

REM 2. 잠시 대기
timeout /t 3 /nobreak >nul

REM 3. VBScript로 분리된 프로세스 시작 (창 없음)
wscript //nologo "C:\Users\log\Desktop\Code\S1\S1_start_monitor.vbs"

exit /b 0
