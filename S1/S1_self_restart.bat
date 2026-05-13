@echo off
cd /d "C:\Users\log\Desktop\Code\S1"

:loop
"C:\Python314\python.exe" Real_Time_Monitor_S1.py --appkey IweTdkYa8JWDUOa8NohVSVeOiJ1THDGd_2x050A8XcU --secret eazu-jPNJpAsIVkaUTh3_88gUvXrCMJCwGF2AYRtBJs --interval 60
timeout /t 5 /nobreak >nul
goto loop
