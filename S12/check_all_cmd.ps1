Write-Host "=== 모든 cmd.exe 프로세스 (S1/S12 관련) ==="
Get-WmiObject Win32_Process | Where-Object { $_.Name -eq "cmd.exe" } | ForEach-Object {
    if ($_.CommandLine -like "*Code*" -or $_.CommandLine -like "*monitor*" -or $_.CommandLine -like "*restart*") {
        $start = $_.ConvertToDateTime($_.CreationDate)
        Write-Host ("PID={0} Start={1}" -f $_.ProcessId, $start)
        Write-Host ("  {0}" -f $_.CommandLine)
    }
}
Write-Host ""
Write-Host "=== python PID 1748 정보 ==="
$p = Get-WmiObject Win32_Process | Where-Object { $_.ProcessId -eq 1748 }
if ($p) {
    Write-Host ("CMD={0}" -f $p.CommandLine)
    Write-Host ("ParentPID={0}" -f $p.ParentProcessId)
}
