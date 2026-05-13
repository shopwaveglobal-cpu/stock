@echo off
REM Trading Signal System Batch File (20:10 Auto Execution)
REM Called by Windows Task Scheduler

cd /d "%~dp0"

set LOG_FILE=%~dp0logs\s12_daily_%date:~0,4%%date:~5,2%%date:~8,2%.log
if not exist "%~dp0logs" mkdir "%~dp0logs"

echo ======================================== >> "%LOG_FILE%"
echo S12 Trading System - Daily Run (20:10) >> "%LOG_FILE%"
echo Start Time: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

echo ========================================
echo S12 Trading System - Daily Run (20:10)
echo Start Time: %date% %time%
echo ========================================
echo.

REM Step 0: Get token (shared by Step 1 and 2)
echo [Token] Acquiring API token... >> "%LOG_FILE%"
C:\Python314\python.exe get_token_once.py IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs > "%TEMP%\kiwoom_token.txt" 2>> "%LOG_FILE%"
set /p KIWOOM_TOKEN=< "%TEMP%\kiwoom_token.txt"
if "%KIWOOM_TOKEN%"=="" (
    echo ERROR: Token acquisition failed! >> "%LOG_FILE%"
    echo ERROR: Token acquisition failed!
    goto :error_exit
)
echo [Token] Token acquired successfully >> "%LOG_FILE%"

REM Step 1: Daily Turnover Tracking
echo [1/2] Daily Turnover Tracking...
echo ========================================
echo [1/2] Daily Turnover Tracking... >> "%LOG_FILE%"

C:\Python314\python.exe Daily_Turnover_Tracker.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% neq 0 (
    echo ERROR: Daily Turnover Tracker failed! >> "%LOG_FILE%"
    echo ERROR: Daily Turnover Tracker failed!
    goto :error_exit
)

echo Step 1 completed successfully >> "%LOG_FILE%"
echo.

REM Step 2: Trading Signal Generation
echo [2/2] Trading Signal Generation...
echo ========================================
echo [2/2] Trading Signal Generation... >> "%LOG_FILE%"

C:\Python314\python.exe Trading_Signal_System.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --alert-threshold 10.0 >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% neq 0 (
    echo ERROR: Trading Signal System failed! >> "%LOG_FILE%"
    echo ERROR: Trading Signal System failed!
    goto :error_exit
)

echo Step 2 completed successfully >> "%LOG_FILE%"

echo.
echo ========================================
echo Completion Time: %date% %time%
echo ========================================
echo Completion Time: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo SUCCESS: All steps completed successfully >> "%LOG_FILE%"
exit /b 0

:error_exit
echo ========================================
echo ERROR: Process failed at %date% %time%
echo ========================================
echo ERROR: Process failed at %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
exit /b 1
