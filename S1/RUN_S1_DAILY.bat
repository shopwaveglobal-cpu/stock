@echo off
REM Trading Signal System Batch File (20:15 Auto Execution)
REM Called by Windows Task Scheduler
REM Can run in screensaver/locked state

REM Set working directory
cd /d "%~dp0"

REM Set log file
set LOG_FILE=%~dp0logs\s1_daily_%date:~0,4%%date:~5,2%%date:~8,2%.log
if not exist "%~dp0logs" mkdir "%~dp0logs"

REM Start logging
echo ======================================== >> "%LOG_FILE%"
echo S1 Trading System - Daily Run (20:15) >> "%LOG_FILE%"
echo Start Time: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

echo ========================================
echo S1 Trading System - Daily Run (20:15)
echo Start Time: %date% %time%
echo ========================================
echo.

REM ===== Step 1: Daily Market Cap Tracking =====
echo [1/2] Daily Market Cap Tracking...
echo ========================================
echo [1/2] Daily Market Cap Tracking... >> "%LOG_FILE%"

python Daily_MarketCap_Tracker.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% neq 0 (
    echo ERROR: Daily Market Cap Tracker failed! >> "%LOG_FILE%"
    echo ERROR: Daily Market Cap Tracker failed!
    goto :error_exit
)

echo Step 1 completed successfully >> "%LOG_FILE%"
echo.

REM ===== Step 2: Trading Signal Generation =====
echo [2/2] Trading Signal Generation...
echo ========================================
echo [2/2] Trading Signal Generation... >> "%LOG_FILE%"

python Trading_Signal_System.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --alert-threshold 10.0 --label S1 --universe output/marketcap_universe.xlsx --signal output/trading_signals_s1.xlsx >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% neq 0 (
    echo ERROR: Trading Signal System S1 failed! >> "%LOG_FILE%"
    echo ERROR: Trading Signal System S1 failed!
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
