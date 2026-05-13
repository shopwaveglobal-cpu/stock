$all = @(Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like "*Real_Time_Monitor_S1*" })
Write-Host "S1 Count: $($all.Count)"
foreach ($p in $all) {
    $ppid = $p.ParentProcessId
    $par = @(Get-WmiObject Win32_Process | Where-Object { $_.ProcessId -eq $ppid })
    $parName = if ($par.Count -gt 0) { $par[0].Name } else { "(gone)" }
    $parCmd = if ($par.Count -gt 0) { $par[0].CommandLine } else { "" }
    Write-Host "PID=$($p.ProcessId) PPID=$ppid ParentName=$parName"
    Write-Host "  ParentCmd=$parCmd"
}
