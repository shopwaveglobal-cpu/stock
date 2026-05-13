Write-Host "=== Kiwoom 관련 프로세스 ==="
Get-WmiObject Win32_Process | Where-Object {
    $_.Name -like "*kiwoom*" -or $_.Name -like "*Kiwoom*" -or $_.Name -like "*kwi*"
} | ForEach-Object {
    Write-Host ("PID={0} Name={1} Start={2}" -f $_.ProcessId, $_.Name, $_.ConvertToDateTime($_.CreationDate))
}
Write-Host "=== 완료 ==="
