@echo off
chcp 65001 > nul
set DESKTOP=%USERPROFILE%\Desktop
set S12=%~dp0

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\스케줄러_등록.lnk'); $s.TargetPath = '%S12%setup_scheduler.bat'; $s.WorkingDirectory = '%S12%'; $s.Save()"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\중간점검_즉시실행.lnk'); $s.TargetPath = '%S12%run_midday_report_now.bat'; $s.WorkingDirectory = '%S12%'; $s.Save()"

echo 바탕화면에 단축키 2개가 생성됐습니다.
pause
