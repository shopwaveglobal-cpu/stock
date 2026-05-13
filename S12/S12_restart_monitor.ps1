# S12 Real_Time_Monitor 기존 프로세스 종료 스크립트
# (프로세스 시작은 watchdog.bat에서 처리)

Set-Location "C:\Users\log\Desktop\Code\S12"

# 기존 S12 프로세스 찾아서 종료 (S1 제외)
$procs = Get-WmiObject Win32_Process | Where-Object {
    $_.CommandLine -like "*Real_Time_Monitor.py*" -and
    $_.CommandLine -like "*trading_signals.xlsx*" -and
    $_.CommandLine -notlike "*trading_signals_s1*"
}

foreach ($proc in $procs) {
    (Get-WmiObject Win32_Process -Filter "ProcessId='$($proc.ProcessId)'").Terminate() | Out-Null
}

# S12 루프 bat (S12_self_restart.bat) 및 기존 CMD 프로세스 종료
$cmdProcs = Get-WmiObject Win32_Process | Where-Object {
    $_.Name -eq "cmd.exe" -and (
        $_.CommandLine -like "*S12_Monitor_Forever*" -or
        $_.CommandLine -like "*S12_self_restart*"
    )
}
foreach ($proc in $cmdProcs) {
    (Get-WmiObject Win32_Process -Filter "ProcessId='$($proc.ProcessId)'").Terminate() | Out-Null
}
