@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo 🔍 S12 실시간 주식 모니터링 시작
echo ========================================================
echo.
echo 현재 시간 확인 중...
python -c "from datetime import datetime; print(datetime.now().strftime('%%Y-%%m-%%d %%H:%%M:%%S'))"
echo.
echo ⚠️ 모니터링 시간: 거래일 08:00 ~ 20:00
echo ⚠️ 현재 시간이 모니터링 시간이 아니면 대기합니다.
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo ========================================================
echo.

start /B pythonw Real_Time_Monitor.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --interval 60

echo.
echo ========================================================
echo 모니터링이 백그라운드에서 시작되었습니다!
echo 콘솔 창 없이 실행 중입니다.
echo.
echo 종료하려면 작업 관리자에서 pythonw.exe를 종료하세요.
echo ========================================================

