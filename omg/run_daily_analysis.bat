@echo off
chcp 65001 > nul
REM ========================================
REM OMG Daily Update (00:00 Auto Run)
REM ========================================
REM daily_update.py 실행
REM - Debug 파일 생성 (auto_debug_builder.py)
REM - Analysis Excel 생성 (coin_analysis_excel.py)
REM ========================================

cd /d "%~dp0"

REM 로그 파일 설정
set LOG_FILE=logs\omg_daily_%date:~0,4%%date:~5,2%%date:~8,2%.log
if not exist "logs" mkdir "logs"

echo ======================================== >> "%LOG_FILE%"
echo OMG Daily Update - %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

echo ========================================
echo OMG Daily Update - %date% %time%
echo ========================================
echo.

REM ===== daily_update.py 실행 =====
echo Running daily_update.py...
echo ========================================
echo daily_update.py 실행 중... >> "%LOG_FILE%"

python daily_update.py >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% neq 0 (
    echo ERROR: daily_update.py failed! >> "%LOG_FILE%"
    echo ERROR: 일일 업데이트 실패!
    goto :error_exit
)

echo.
echo ========================================
echo 완료: %date% %time%
echo ========================================
echo 완료: %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

echo SUCCESS: Daily update completed >> "%LOG_FILE%"
echo.
echo 생성된 파일:
echo   - debug/*.csv (Top 100 coins)
echo   - output/coin_analysis_*.xlsx
echo.
echo NEXT: 실시간 모니터링은 crypto_realtime_monitor.py에서 자동 재로드됨 (00:05)
echo.
exit /b 0

:error_exit
echo ========================================
echo ERROR: 작업 실패 at %date% %time%
echo ========================================
echo ERROR: 작업 실패 at %date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
exit /b 1
