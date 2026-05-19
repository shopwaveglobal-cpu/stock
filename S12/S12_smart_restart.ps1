# S12 스마트 재시작: 07:xx에만 강제 kill+restart, 그 외에는 이미 실행 중이면 스킵

# ── 뮤텍스: 동시 실행 방지 ──────────────────────────────────────
# 여러 트리거(로그인/08:00/14:00/15분 워치독)가 동시에 실행될 때 레이스 컨디션 방지
$mutexFile = "C:\Users\log\Desktop\Code\S12\smart_restart.mutex"
if (Test-Path $mutexFile) {
    # 5분(300초) 이상 된 뮤텍스는 좀비로 간주하고 무시
    $age = (Get-Date) - (Get-Item $mutexFile).LastWriteTime
    if ($age.TotalSeconds -lt 300) { exit 0 }
}
New-Item $mutexFile -Force -ItemType File | Out-Null

try {
    $h = (Get-Date).Hour

    $loop = Get-WmiObject Win32_Process | Where-Object {
        $_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S12_self_restart*"
    }

    if ($h -eq 7 -or -not $loop) {
        # kill 기존 프로세스 (taskkill /F 사용 - WMI Terminate보다 확실)
        $targets = Get-WmiObject Win32_Process | Where-Object {
            ($_.Name -eq "python.exe" -and $_.CommandLine -like "*Real_Time_Monitor.py*" -and $_.CommandLine -notlike "*Real_Time_Monitor_S1*") -or
            ($_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S12_self_restart*")
        }
        foreach ($p in $targets) {
            taskkill /F /PID $p.ProcessId /T 2>$null
        }
        # 락 파일도 확실히 제거
        $lockFile = "C:\Users\log\Desktop\Code\S12\realtime_monitor.lock"
        if (Test-Path $lockFile) { Remove-Item $lockFile -Force }
        Start-Sleep -Seconds 3
        # 새로 시작
        Start-Process -FilePath "wscript" -ArgumentList "//nologo C:\Users\log\Desktop\Code\S12\S12_start_monitor.vbs" -WindowStyle Hidden
    }
} finally {
    # 뮤텍스 해제
    Remove-Item $mutexFile -Force -ErrorAction SilentlyContinue
}
