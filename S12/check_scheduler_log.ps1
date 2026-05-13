Write-Host "=== 최근 Task Scheduler 실행 기록 (오늘) ==="
$tasks = @("S1_S12_Daily_Restart_7h", "Monitor_Watchdog_15min", "S12_Monitor_Watchdog", "S1_Realtime_Monitor", "S1_Daily_Trading_Signal", "S12_Trading_Signal_Daily")
foreach ($taskName in $tasks) {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) {
        $info = Get-ScheduledTaskInfo -TaskName $taskName -ErrorAction SilentlyContinue
        Write-Host ("[$taskName]")
        Write-Host ("  마지막실행: {0}" -f $info.LastRunTime)
        Write-Host ("  결과코드:   {0}" -f $info.LastTaskResult)
        Write-Host ("  다음실행:   {0}" -f $info.NextRunTime)
    }
}

Write-Host ""
Write-Host "=== 오늘 오전 Task Scheduler 이벤트 로그 ==="
Get-WinEvent -FilterHashtable @{
    LogName = 'Microsoft-Windows-TaskScheduler/Operational'
    StartTime = (Get-Date).Date
} -ErrorAction SilentlyContinue |
Where-Object { $_.Message -match "S1|S12|Watchdog|Restart|failed|실패|오류" } |
Select-Object -Last 20 |
ForEach-Object {
    Write-Host ("[{0}] {1}" -f $_.TimeCreated.ToString("HH:mm:ss"), $_.Message.Substring(0, [Math]::Min(120, $_.Message.Length)))
}
