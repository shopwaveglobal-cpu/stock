@echo off
REM 11:30 중간 점검 리포트 (S12 + S1 순차 실행)
REM Called by Windows Task Scheduler at 11:30 on trading days

cd /d "%~dp0"

set LOG_FILE=%~dp0logs\midday_%date:~0,4%%date:~5,2%%date:~8,2%.log
if not exist "%~dp0logs" mkdir "%~dp0logs"

echo ======================================== >> "%LOG_FILE%"
echo Midday Report - %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

echo [1/2] S12 중간 점검...
echo [1/2] S12 중간 점검... >> "%LOG_FILE%"

C:\Python314\python.exe midday_report.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --label S12 --signal output/trading_signals.xlsx >> "%LOG_FILE%" 2>&1

echo [2/2] S1 중간 점검...
echo [2/2] S1 중간 점검... >> "%LOG_FILE%"

C:\Python314\python.exe ..\S1\midday_report.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --label S1 --signal ..\S1\output\trading_signals_s1.xlsx >> "%LOG_FILE%" 2>&1

echo Done: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
exit /b 0
