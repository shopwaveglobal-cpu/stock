$all = @(Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like "*Real_Time_Monitor_S1*" })
Write-Host "Count: $($all.Count)"
foreach ($p in $all) {
    Write-Host "PID=$($p.ProcessId) Created=$($p.CreationDate)"
    Write-Host "CMD=$($p.CommandLine)"
    Write-Host ""
}
