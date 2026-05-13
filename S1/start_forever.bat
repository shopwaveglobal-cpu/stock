@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 중복 실행 방지
tasklist /FI "WINDOWTITLE eq S1_Monitor_Forever" 2>nul | find /I /N "cmd.exe">nul
if "%ERRORLEVEL%"=="0" (
    echo S1 모니터가 이미 실행 중입니다.
    timeout /t 3
    exit
)

title S1_Monitor_Forever

echo ========================================================
echo 🔍 [S1] 24시간 실시간 주식 모니터링 (거래시간만 작동)
echo ========================================================
echo.
echo 모니터링 설정:
echo   - 거래일 08:00~20:00만 API 호출
echo   - 비거래시간은 대기 상태
echo   - 프로그램 종료 안 함 (재부팅 전까지 계속 실행)
echo.
echo 종료하려면 이 창을 닫으세요.
echo ========================================================
echo.

:RESTART
python Real_Time_Monitor_S1.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --interval 60

echo.
echo [오류] 프로그램이 종료되었습니다. 10초 후 재시작합니다...
timeout /t 10
goto RESTART
