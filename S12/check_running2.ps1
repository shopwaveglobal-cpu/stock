Write-Host "=== S1/S12 관련 모든 프로세스 ==="
$procs = Get-WmiObject Win32_Process | Where-Object {
    ($_.Name -eq "python.exe" -and $_.CommandLine -like "*Real_Time_Monitor*") -or
    ($_.Name -eq "cmd.exe" -and ($_.CommandLine -like "*S1_self_restart*" -or $_.CommandLine -like "*S12_self_restart*" -or $_.CommandLine -like "*S12*"))
}
foreach ($proc in $procs) {
    $start = $proc.ConvertToDateTime($proc.CreationDate)
    Write-Host ("PID={0} {1} Start={2}" -f $proc.ProcessId, $proc.Name, $start)
    Write-Host ("  {0}" -f $proc.CommandLine)
}
Write-Host ""
Write-Host "=== 총 S1 python 수: $(($procs | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*S1*' }).Count)"
Write-Host "=== 총 S12 python 수: $(($procs | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -notlike '*S1*' }).Count)"
