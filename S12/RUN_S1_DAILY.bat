@echo off
REM Compatibility wrapper for the existing S1_Daily_Trading_Signal task.
REM The real S1 flow uses Daily_MarketCap_Tracker.py in the S1 directory.

call "%~dp0..\S1\RUN_S1_DAILY.bat"
exit /b %ERRORLEVEL%











