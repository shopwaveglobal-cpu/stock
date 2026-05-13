# watchdog_monitors.ps1
# S1/S12/OMG 실시간 모니터 감시 - 루프 프로세스가 없으면 자동 재시작
# Task Scheduler에서 평일 15분마다 실행

$now = Get-Date
$hour = $now.Hour
$dow = $now.DayOfWeek
$logFile = "C:\Users\log\Desktop\Code\S12\watchdog_monitors.log"

function Write-Log {
    param($msg)
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$ts] $msg"
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

# ── OMG 크립토 체크: 24/7 (시간/요일 제한 없음) ────────────
$omgPython = Get-WmiObject Win32_Process | Where-Object {
    $_.Name -eq "python.exe" -and $_.CommandLine -like "*crypto_realtime_monitor*"
}

if (-not $omgPython) {
    Write-Log "OMG 크립토 미실행 감지 -> 재시작"
    $lockFile = "C:\Users\log\Desktop\Code\omg\crypto_monitor.lock"
    if (Test-Path $lockFile) {
        Remove-Item $lockFile -Force
        Write-Log "OMG 락 파일 삭제"
    }
    Start-Process -FilePath "C:\Python314\python.exe" `
                  -ArgumentList "crypto_realtime_monitor.py" `
                  -WorkingDirectory "C:\Users\log\Desktop\Code\omg" `
                  -WindowStyle Normal
}

# 평일(월~금) + 07:00~20:00 사이에만 동작
if ($dow -eq 'Saturday' -or $dow -eq 'Sunday') { exit 0 }
if ($hour -lt 7 -or $hour -ge 20) { exit 0 }

# ── S1 체크: cmd.exe S1_self_restart.bat 프로세스 확인 ────
$s1Loop = Get-WmiObject Win32_Process | Where-Object {
    $_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S1_self_restart*"
}

if (-not $s1Loop) {
    # python 직접 실행 중인지도 확인 (루프 이전 방식 호환)
    $s1Python = Get-WmiObject Win32_Process | Where-Object {
        $_.Name -eq "python.exe" -and $_.CommandLine -like "*Real_Time_Monitor_S1.py*"
    }
    if (-not $s1Python) {
        Write-Log "S1 미실행 감지 -> 재시작"
        Start-Process -FilePath "C:\Users\log\Desktop\Code\S1\run_s1_realtime.bat" `
                      -WorkingDirectory "C:\Users\log\Desktop\Code\S1" `
                      -WindowStyle Hidden
    }
}

# ── S12 체크: cmd.exe S12_self_restart.bat 프로세스 확인 ──
$s12Loop = Get-WmiObject Win32_Process | Where-Object {
    $_.Name -eq "cmd.exe" -and $_.CommandLine -like "*S12_self_restart*"
}

if (-not $s12Loop) {
    # python 직접 실행 중인지도 확인 (루프 이전 방식 호환)
    $s12Python = Get-WmiObject Win32_Process | Where-Object {
        $_.Name -eq "python.exe" -and
        $_.CommandLine -like "*Real_Time_Monitor.py*" -and
        $_.CommandLine -notlike "*Real_Time_Monitor_S1.py*"
    }
    if (-not $s12Python) {
        Write-Log "S12 미실행 감지 -> 재시작"
        Start-Process -FilePath "C:\Users\log\Desktop\Code\S12\S12_monitor_watchdog.bat" `
                      -WorkingDirectory "C:\Users\log\Desktop\Code\S12" `
                      -WindowStyle Hidden
    }
}
