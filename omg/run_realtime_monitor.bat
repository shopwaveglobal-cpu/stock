@echo off
chcp 949 > nul
cd /d "%~dp0"

REM ========================================================
REM OMG Realtime Monitoring Start (Duplicate Prevention)
REM ========================================================

REM Check and kill existing process
echo Checking existing process...
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /C:"python.exe"') do (
    wmic process where "ProcessId=%%i AND CommandLine LIKE '%%crypto_realtime_monitor%%'" get ProcessId 2>nul | findstr /R "^[0-9]" >nul
    if not errorlevel 1 (
        echo Found existing process (PID: %%i), terminating...
        taskkill /PID %%i /F >nul 2>&1
    )
)

timeout /t 2 /nobreak >nul

echo ========================================================
echo OMG Crypto Realtime Monitor Starting
echo ========================================================
echo.
echo Monitoring Settings:
echo   - Target: Top 100 coins (based on Analysis Excel)
echo   - Interval: Check every 5 minutes
echo   - Alert Condition: Within 5%% of buy level
echo   - Duplicate Prevention: Once per coin/level per day
echo.
echo Initialization:
echo   - Load existing Analysis Excel (no file generation)
echo   - Auto reload data at 00:05 daily
echo   - Daily update is handled by daily_update.py at 00:00
echo.
echo Press Ctrl+C to stop.
echo ========================================================
echo.

python crypto_realtime_monitor.py

REM Clean up lock file on process exit
if exist "crypto_monitor.lock" del "crypto_monitor.lock"

pause
