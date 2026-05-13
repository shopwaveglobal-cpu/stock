# S12 Monitor Watchdog 작업 스케줄러 등록 스크립트

$taskName1 = "S12_Monitor_Watchdog_Logon"
$taskName2 = "S12_Monitor_Watchdog_Daily"
$watchdogPath = "C:\Users\log\Desktop\Code\S12\S12_monitor_watchdog.bat"
$workDir = "C:\Users\log\Desktop\Code\S12"

# 기존 작업 삭제
Unregister-ScheduledTask -TaskName $taskName1 -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $taskName2 -Confirm:$false -ErrorAction SilentlyContinue

# 공통 설정
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable

$action = New-ScheduledTaskAction `
    -Execute $watchdogPath `
    -WorkingDirectory $workDir

$principal = New-ScheduledTaskPrincipal `
    -UserId "log" `
    -LogonType Interactive `
    -RunLevel Limited

# --- 작업 1: 로그인 시 자동 실행 (1분 지연 - 시스템 안정화 후 실행) ---
$triggerLogon = New-ScheduledTaskTrigger -AtLogOn -User "log"
$triggerLogon.Delay = "PT1M"  # 1분 지연

Register-ScheduledTask `
    -TaskName $taskName1 `
    -Action $action `
    -Trigger $triggerLogon `
    -Settings $settings `
    -Principal $principal `
    -Description "S12 실시간 모니터 감시자 - 로그인 시 실행" `
    -Force

Write-Host "[$taskName1] 등록 완료"

# --- 작업 2: 평일 08:00 + 14:00 반복 실행 ---
$trigger0800 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "08:00"
$trigger1400 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "14:00"

Register-ScheduledTask `
    -TaskName $taskName2 `
    -Action $action `
    -Trigger @($trigger0800, $trigger1400) `
    -Settings $settings `
    -Principal $principal `
    -Description "S12 실시간 모니터 감시자 - 평일 08:00/14:00 실행" `
    -Force

Write-Host "[$taskName2] 등록 완료 (평일 08:00, 14:00)"
Write-Host ""
Write-Host "=== 등록된 작업 확인 ==="
Get-ScheduledTask -TaskName "S12_Monitor_Watchdog*" | Format-Table TaskName, State -AutoSize
