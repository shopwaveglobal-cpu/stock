@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM S12 모니터링 시작 (백그라운드 실행 - 콘솔 창 숨김)
start "" /min python Real_Time_Monitor.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --interval 60 --signal-file output/trading_signals.xlsx


