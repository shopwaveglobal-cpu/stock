$log = "C:\Users\log\Desktop\Code\S12\realtime_monitor_20260325.log"

# 사이클 완료 요약 라인
Write-Host "=== 최근 사이클 요약 ==="
Get-Content $log | Select-String "사이클 완료|전송 알람|알람.*개|OK.*완료" | Select-Object -Last 10 | ForEach-Object { Write-Host $_.Line }

Write-Host ""
Write-Host "=== 5% 이내 이격도 종목 확인 (오늘 전체) ==="
Get-Content $log | Select-String "이격도.*[0-4]\." | Select-Object -Last 20 | ForEach-Object { Write-Host $_.Line }

Write-Host ""
Write-Host "=== 알람/ALERT 발송 기록 ==="
Get-Content $log | Select-String "알람|ALERT|텔레그램|발송" | Select-Object -Last 20 | ForEach-Object { Write-Host $_.Line }
