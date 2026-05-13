# S12 중복 프로세스 정리 - 가장 최신 것(오늘 07:00)만 남기고 나머지 kill
Write-Host "=== S12 프로세스 현황 ==="
$procs = Get-WmiObject Win32_Process | Where-Object {
    ($_.Name -eq "python.exe" -and $_.CommandLine -like "*Real_Time_Monitor.py*" -and $_.CommandLine -notlike "*S1*") -or
    ($_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S12_self_restart*")
}
foreach ($p in $procs) {
    Write-Host ("PID={0} {1} Start={2}" -f $p.ProcessId, $p.Name, $p.ConvertToDateTime($p.CreationDate))
}

# 오늘(03-27) 07:00 이후 시작한 것만 남기고 나머지 kill
$today = (Get-Date).Date
$keepPids = @()
$killPids = @()

foreach ($p in $procs) {
    $start = $p.ConvertToDateTime($p.CreationDate)
    if ($start.Date -eq $today) {
        $keepPids += $p.ProcessId
    } else {
        $killPids += $p.ProcessId
    }
}

Write-Host ""
Write-Host "유지할 PID: $keepPids"
Write-Host "종료할 PID: $killPids"

foreach ($pidVal in $killPids) {
    Write-Host "taskkill /F /PID $pidVal"
    & taskkill /F /PID $pidVal 2>&1
}
Write-Host "=== 완료 ==="
