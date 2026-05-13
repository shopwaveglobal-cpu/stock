@echo off
cd /d "C:\Users\log\Desktop\Code\S12"

:loop
"C:\Python314\python.exe" Real_Time_Monitor.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --interval 60 --signal-file output/trading_signals.xlsx
timeout /t 5 /nobreak >nul
goto loop
