# S1 스마트 재시작: 07:xx에만 강제 kill+restart, 그 외에는 이미 실행 중이면 스킵
$h = (Get-Date).Hour

$loop = Get-WmiObject Win32_Process | Where-Object {
    $_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S1_self_restart*"
}

if ($h -eq 7 -or -not $loop) {
    # kill 기존 프로세스
    Get-WmiObject Win32_Process | Where-Object {
        ($_.Name -eq "python.exe" -and $_.CommandLine -like "*Real_Time_Monitor_S1*") -or
        ($_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S1_self_restart*")
    } | ForEach-Object {
        (Get-WmiObject Win32_Process -Filter "ProcessId='$($_.ProcessId)'").Terminate() | Out-Null
    }
    Start-Sleep -Seconds 3
    # 새로 시작
    Start-Process -FilePath "wscript" -ArgumentList "//nologo C:\Users\log\Desktop\Code\S1\S1_start_monitor.vbs" -WindowStyle Hidden
}
