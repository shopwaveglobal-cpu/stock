Write-Host "=== S1_Daily_Trading_Signal 트리거 상세 ==="
$svc = New-Object -ComObject "Schedule.Service"
$svc.Connect()
$folder = $svc.GetFolder("\")
$task = $folder.GetTask("S1_Daily_Trading_Signal")
Write-Host ("LastRunTime: {0}" -f $task.LastRunTime)
Write-Host ("NextRunTime: {0}" -f $task.NextRunTime)
Write-Host ("LastTaskResult: {0}" -f $task.LastTaskResult)
Write-Host ""
Write-Host "XML Definition (Triggers 부분):"
$xml = $task.Definition.XmlText
$xml -split "`n" | Where-Object { $_ -match "Trigger|StartBoundary|Repetition|Interval|Duration|EndBoundary" } | ForEach-Object { Write-Host $_ }
