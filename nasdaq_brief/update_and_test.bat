@echo off
chcp 65001 >nul
setlocal

set DEST=C:\Users\log\Documents\NasdaqBriefing
set SRC=%~dp0

echo Copying updated files to %DEST%...
copy /y "%SRC%src\data_fetcher.py"         "%DEST%\src\data_fetcher.py"    >nul
copy /y "%SRC%src\card_renderer.py"         "%DEST%\src\card_renderer.py"   >nul
copy /y "%SRC%src\checkpoint_generator.py"  "%DEST%\src\checkpoint_generator.py" >nul
copy /y "%SRC%src\slack_sender.py"          "%DEST%\src\slack_sender.py"    >nul
copy /y "%SRC%src\main.py"                 "%DEST%\src\main.py"            >nul
copy /y "%SRC%templates\market_card.html"   "%DEST%\templates\market_card.html" >nul
echo Done.

echo.
echo Running test...
python "%DEST%\src\main.py"

echo.
echo Output folder: %DEST%\output\
pause
endlocal
