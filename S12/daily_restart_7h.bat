@echo off
chcp 65001 >nul
REM S1 + S12 실시간 모니터 일일 재시작 (07:00, 토큰 갱신)

REM ── S1 kill ──
powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\Users\log\Desktop\Code\S1\S1_restart_monitor.ps1"
timeout /t 3 /nobreak >nul

REM ── S1 start ──
wscript //nologo "C:\Users\log\Desktop\Code\S1\S1_start_monitor.vbs"
timeout /t 5 /nobreak >nul

REM ── S12 kill ──
powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "C:\Users\log\Desktop\Code\S12\S12_restart_monitor.ps1"
timeout /t 3 /nobreak >nul

REM ── S12 start ──
wscript //nologo "C:\Users\log\Desktop\Code\S12\S12_start_monitor.vbs"

exit /b 0
