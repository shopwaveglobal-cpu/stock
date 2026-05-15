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
    Write-Log "OMG 크립토 미실행 감지"

    # 재시작 카운터 파일
    $restartLog = "C:\Users\log\Desktop\Code\omg\omg_restart_count.json"
    # .env 파일에서 SLACK_WEBHOOK_URL 로드
    $envFile = "C:\Users\log\Desktop\Code\S12\.env"
    $webhookUrl = ""
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match "^SLACK_WEBHOOK_URL=(.+)$") { $webhookUrl = $Matches[1].Trim() }
        }
    }
    $now = Get-Date

    # 카운터 로드
    $restartData = @{ timestamps = @() }
    if (Test-Path $restartLog) {
        try { $restartData = Get-Content $restartLog -Raw | ConvertFrom-Json } catch {}
    }

    # 1시간 이내 재시작 횟수 계산
    $cutoff = $now.AddHours(-1)
    $recentRestarts = @($restartData.timestamps | Where-Object { [datetime]$_ -gt $cutoff })

    if ($recentRestarts.Count -ge 3) {
        # 크래시 루프 감지 → 재시작 중단 + 슬랙 알림
        Write-Log "OMG 크래시 루프 감지 ($($recentRestarts.Count)회/1h) -> 재시작 중단"
        $msg = ":rotating_light: *OMG 크립토 모니터 크래시 루프*`n1시간 내 $($recentRestarts.Count)회 재시작 감지. 수동 확인 필요.`nlogs/omg_monitor_error.log 확인하세요."
        $body = @{ text = $msg } | ConvertTo-Json
        try { Invoke-RestMethod -Uri $webhookUrl -Method Post -Body $body -ContentType "application/json" } catch {}
    } else {
        # 정상 재시작
        $recentRestarts += $now.ToString("o")
        $restartData = @{ timestamps = $recentRestarts }
        $restartData | ConvertTo-Json | Set-Content $restartLog -Encoding UTF8

        $lockFile = "C:\Users\log\Desktop\Code\omg\crypto_monitor.lock"
        if (Test-Path $lockFile) {
            Remove-Item $lockFile -Force
            Write-Log "OMG 락 파일 삭제"
        }

        $ts = (Get-Date).ToString("yyyyMMdd")
        $stdoutLog = "C:\Users\log\Desktop\Code\omg\logs\monitor_${ts}_out.log"
        $stderrLog = "C:\Users\log\Desktop\Code\omg\logs\monitor_${ts}_err.log"
        Write-Log "OMG 재시작 ($($recentRestarts.Count)회/1h)"
        Start-Process -FilePath "C:\Python314\python.exe" `
                      -ArgumentList "crypto_realtime_monitor.py" `
                      -WorkingDirectory "C:\Users\log\Desktop\Code\omg" `
                      -WindowStyle Hidden `
                      -RedirectStandardOutput $stdoutLog `
                      -RedirectStandardError $stderrLog
    }
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
