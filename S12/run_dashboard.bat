@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Real-time Monitor Dashboard
echo ========================================
echo.

python monitor_dashboard.py

if errorlevel 1 (
    echo.
    echo Error: Dashboard execution failed
    pause
)
