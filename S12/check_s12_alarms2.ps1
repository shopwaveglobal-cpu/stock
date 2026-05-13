$log = "C:\Users\log\Desktop\Code\S12\realtime_monitor_20260325.log"

Write-Host "=== 최근 사이클 완료 메시지 ==="
Get-Content $log | Where-Object { $_ -match "OK" -or $_ -match "0.." } | Select-Object -Last 10 | ForEach-Object { Write-Host $_ }

Write-Host ""
Write-Host "=== 오늘 로그 마지막 50줄 ==="
Get-Content $log -Tail 50 | ForEach-Object { Write-Host $_ }
