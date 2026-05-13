Set-Location "C:\Users\log\Desktop\Code\S1"

# S1 python 프로세스 종료
$procs = @(Get-WmiObject Win32_Process | Where-Object { $_.Name -eq "python.exe" -and $_.CommandLine -match "Real_Time_Monitor_S1" })
foreach ($proc in $procs) {
    (Get-WmiObject Win32_Process -Filter "ProcessId='$($proc.ProcessId)'").Terminate() | Out-Null
}

# S1 루프 bat (S1_self_restart.bat) CMD 프로세스 종료
$cmdProcs = @(Get-WmiObject Win32_Process | Where-Object {
    $_.Name -eq "cmd.exe" -and (
        $_.CommandLine -match "run_s1_realtime" -or
        $_.CommandLine -match "S1_self_restart"
    )
})
foreach ($proc in $cmdProcs) {
    (Get-WmiObject Win32_Process -Filter "ProcessId='$($proc.ProcessId)'").Terminate() | Out-Null
}
