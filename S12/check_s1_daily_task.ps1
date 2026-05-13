Write-Host "=== S1_Daily_Trading_Signal 작업 상세 ==="
$task = Get-ScheduledTask -TaskName "S1_Daily_Trading_Signal" -ErrorAction SilentlyContinue
if ($task) {
    Write-Host "Action:"
    foreach ($a in $task.Actions) {
        Write-Host ("  Execute: {0}" -f $a.Execute)
        Write-Host ("  Arguments: {0}" -f $a.Arguments)
        Write-Host ("  WorkingDir: {0}" -f $a.WorkingDirectory)
    }
    Write-Host "Triggers:"
    foreach ($t in $task.Triggers) {
        Write-Host ("  {0}" -f $t)
    }
}

Write-Host ""
Write-Host "=== RUN_S1_DAILY.bat 확인 ==="
if (Test-Path "C:\Users\log\Desktop\Code\S1\RUN_S1_DAILY.bat") {
    Get-Content "C:\Users\log\Desktop\Code\S1\RUN_S1_DAILY.bat"
} else {
    Write-Host "파일 없음: C:\Users\log\Desktop\Code\S1\RUN_S1_DAILY.bat"
    Write-Host ""
    Write-Host "S1 폴더 bat 파일 목록:"
    Get-ChildItem "C:\Users\log\Desktop\Code\S1\" -Filter "*.bat" | ForEach-Object { Write-Host ("  {0}" -f $_.Name) }
}
