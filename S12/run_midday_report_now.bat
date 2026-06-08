@echo off
REM 11:30 중간 점검 리포트 즉시 실행 (비거래일/수동 실행용, --force 포함)

cd /d "%~dp0"

set LOG_FILE=%~dp0logs\midday_force_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.log
if not exist "%~dp0logs" mkdir "%~dp0logs"

echo ======================================== >> "%LOG_FILE%"
echo Midday Report (FORCE) - %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

echo [1/2] S12 중간 점검 (강제 실행)...
C:\Python314\python.exe midday_report.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --label S12 --signal output/trading_signals.xlsx --force >> "%LOG_FILE%" 2>&1

echo [2/2] S1 중간 점검 (강제 실행)...
C:\Python314\python.exe ..\S1\midday_report.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --label S1 --signal ..\S1\output\trading_signals_s1.xlsx --force >> "%LOG_FILE%" 2>&1

echo Done: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

echo.
echo 완료! 슬랙 확인하세요.
pause
