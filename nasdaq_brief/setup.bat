@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================
echo   NASDAQ BRIEFING CARD - SETUP
echo ============================================
echo.

set DEST=C:\Users\log\Documents\NasdaqBriefing
set SRC=%~dp0

echo [1/6] Creating directory structure...
mkdir "%DEST%\src"        2>nul
mkdir "%DEST%\templates"  2>nul
mkdir "%DEST%\data"       2>nul
mkdir "%DEST%\output"     2>nul
echo     OK: %DEST%

echo.
echo [2/6] Copying files...
copy /y "%SRC%requirements.txt"          "%DEST%\requirements.txt"       >nul
copy /y "%SRC%src\data_fetcher.py"       "%DEST%\src\data_fetcher.py"    >nul
copy /y "%SRC%src\checkpoint_generator.py" "%DEST%\src\checkpoint_generator.py" >nul
copy /y "%SRC%src\card_renderer.py"      "%DEST%\src\card_renderer.py"   >nul
copy /y "%SRC%src\slack_sender.py"       "%DEST%\src\slack_sender.py"    >nul
copy /y "%SRC%src\main.py"              "%DEST%\src\main.py"            >nul
copy /y "%SRC%templates\market_card.html" "%DEST%\templates\market_card.html" >nul
echo     OK: All source files copied

echo.
echo [3/6] Installing Python packages...
python -m pip install -r "%DEST%\requirements.txt" --quiet
if errorlevel 1 (
    echo     ERROR: pip install failed. Check Python is in PATH.
    pause
    exit /b 1
)
echo     OK: Packages installed

echo.
echo [4/6] Installing Playwright Chromium...
python -m playwright install chromium
if errorlevel 1 (
    echo     ERROR: Playwright install failed.
    pause
    exit /b 1
)
echo     OK: Chromium ready

echo.
echo [5/6] Slack Bot Token setup...
echo.
echo   Please enter your Slack Bot Token (starts with xoxb-):
set /p USER_TOKEN="  Token: "
if "!USER_TOKEN!"=="" (
    echo     SKIP: Token not entered. Set SLACK_BOT_TOKEN manually later.
) else (
    setx SLACK_BOT_TOKEN "!USER_TOKEN!" >nul
    echo     OK: SLACK_BOT_TOKEN saved as system environment variable
    echo     NOTE: Restart terminal/Task Scheduler after setup to apply.
)

echo.
echo [6/6] Registering Windows Task Scheduler (Tue-Sat 07:00 KST)...
schtasks /delete /tn "NasdaqBriefingCard" /f >nul 2>&1
schtasks /create /tn "NasdaqBriefingCard" /tr "python \"%DEST%\src\main.py\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 07:00 /f >nul
if errorlevel 1 (
    echo     ERROR: Task Scheduler registration failed. Run as Administrator.
    pause
    exit /b 1
)
echo     OK: Task 'NasdaqBriefingCard' registered (Tue-Sat 07:00)

echo.
echo ============================================
echo   SETUP COMPLETE
echo ============================================
echo.
echo   Install path : %DEST%
echo   Schedule     : Tue-Sat 07:00 KST
echo   Task name    : NasdaqBriefingCard
echo.

set /p RUN_TEST="  Run test now? (Y/N): "
if /i "!RUN_TEST!"=="Y" (
    echo.
    echo   Running test...
    python "%DEST%\src\main.py"
    echo.
    echo   Check output folder: %DEST%\output\
)

echo.
pause
endlocal
