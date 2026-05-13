$procs = Get-WmiObject Win32_Process | Where-Object {
    ($_.Name -eq "python.exe" -and $_.CommandLine -like "*Real_Time_Monitor*") -or
    ($_.Name -eq "cmd.exe" -and ($_.CommandLine -like "*S1_self_restart*" -or $_.CommandLine -like "*S12_self_restart*"))
}
if ($procs.Count -eq 0) {
    Write-Host "NO MONITORS RUNNING"
} else {
    foreach ($proc in $procs) {
        $start = $proc.ConvertToDateTime($proc.CreationDate)
        $cmd = if ($proc.CommandLine.Length -gt 100) { $proc.CommandLine.Substring(0,100) } else { $proc.CommandLine }
        Write-Host "PID=$($proc.ProcessId) Name=$($proc.Name) Start=$start"
        Write-Host "  CMD=$cmd"
    }
}
