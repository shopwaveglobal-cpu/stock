# S1 스마트 재시작: 07:xx에만 강제 kill+restart, 그 외에는 이미 실행 중이면 스킵

# ── 뮤텍스: 동시 실행 방지 ──────────────────────────────────────
$mutexFile = "C:\Users\log\Desktop\Code\S1\smart_restart.mutex"
if (Test-Path $mutexFile) {
    $age = (Get-Date) - (Get-Item $mutexFile).LastWriteTime
    if ($age.TotalSeconds -lt 300) { exit 0 }
}
New-Item $mutexFile -Force -ItemType File | Out-Null

try {
    $h = (Get-Date).Hour

    $loop = Get-WmiObject Win32_Process | Where-Object {
        $_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S1_self_restart*"
    }

    if ($h -eq 7 -or -not $loop) {
        # kill 기존 프로세스 (taskkill /F 사용)
        $targets = Get-WmiObject Win32_Process | Where-Object {
            ($_.Name -eq "python.exe" -and $_.CommandLine -like "*Real_Time_Monitor*" -and $_.CommandLine -like "*--label S1*") -or
            ($_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S1_self_restart*")
        }
        foreach ($p in $targets) {
            taskkill /F /PID $p.ProcessId /T 2>$null
        }
        # 락 파일 제거
        $lockFile = "C:\Users\log\Desktop\Code\S1\realtime_monitor.lock"
        if (Test-Path $lockFile) { Remove-Item $lockFile -Force }
        Start-Sleep -Seconds 3
        # 새로 시작
        Start-Process -FilePath "wscript" -ArgumentList "//nologo C:\Users\log\Desktop\Code\S1\S1_start_monitor.vbs" -WindowStyle Hidden
    }
} finally {
    Remove-Item $mutexFile -Force -ErrorAction SilentlyContinue
}
