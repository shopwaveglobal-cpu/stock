Write-Host "=== S12 관련 모든 cmd/python 프로세스 ==="
Get-WmiObject Win32_Process | Where-Object {
    $_.CommandLine -like "*S12*" -or
    ($_.Name -eq "python.exe" -and $_.CommandLine -like "*Real_Time_Monitor*" -and $_.CommandLine -notlike "*S1*")
} | ForEach-Object {
    $start = $_.ConvertToDateTime($_.CreationDate)
    Write-Host ("PID={0} {1} Start={2}" -f $_.ProcessId, $_.Name, $start)
    Write-Host ("  {0}" -f $_.CommandLine)
}

Write-Host ""
Write-Host "=== PID 13928 부모 프로세스 확인 ==="
$p13928 = Get-WmiObject Win32_Process | Where-Object { $_.ProcessId -eq 13928 }
if ($p13928) {
    $parent = Get-WmiObject Win32_Process | Where-Object { $_.ProcessId -eq $p13928.ParentProcessId }
    Write-Host ("부모 PID={0} Name={1}" -f $p13928.ParentProcessId, $parent.Name)
    Write-Host ("부모 CMD={0}" -f $parent.CommandLine)
}
