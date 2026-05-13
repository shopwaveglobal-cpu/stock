$all = @(Get-WmiObject Win32_Process | Where-Object { $_.Name -eq "python.exe" -and $_.CommandLine -match "Real_Time_Monitor_S1" })
Write-Host "Found: $($all.Count) processes"
foreach ($p in $all) {
    Write-Host "Killing PID $($p.ProcessId)"
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1
$remaining = @(Get-WmiObject Win32_Process | Where-Object { $_.Name -eq "python.exe" -and $_.CommandLine -match "Real_Time_Monitor_S1" })
Write-Host "Remaining: $($remaining.Count)"
