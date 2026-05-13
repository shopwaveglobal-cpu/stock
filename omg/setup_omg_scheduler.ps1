# Windows 작업 스케줄러 자동 설정 스크립트
# OMG 암호화폐 실시간 모니터링 시스템용

# 인코딩 설정 (한글 출력을 위해)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# PowerShell 관리자 권한 체크 (경고만 표시, 계속 진행)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  관리자 권한이 없습니다. 현재 사용자 권한으로 시도합니다." -ForegroundColor Yellow
    Write-Host "   만약 작업 등록에 실패하면, 관리자 권한으로 PowerShell을 실행해주세요." -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 2
}

# 현재 스크립트 위치
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile = Join-Path $scriptDir "run_realtime_monitor.bat"
$pythonScript = Join-Path $scriptDir "crypto_realtime_monitor.py"

# 배치 파일 존재 확인
if (-not (Test-Path $batFile)) {
    Write-Host "❌ 배치 파일을 찾을 수 없습니다: $batFile" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Windows 작업 스케줄러 설정 시작 (OMG)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 작업 스케줄러 서비스 체크
try {
    $schedule = New-Object -ComObject Schedule.Service
    $schedule.Connect()
} catch {
    Write-Host "❌ 작업 스케줄러에 연결할 수 없습니다." -ForegroundColor Red
    exit 1
}

# 기존 작업 삭제 (있다면)
$taskName = "OMG_Crypto_Realtime_Monitor"
try {
    $schedule.GetFolder("\").DeleteTask($taskName, 0)
    Write-Host "✓ 기존 작업 삭제: $taskName" -ForegroundColor Yellow
} catch {
    # 작업이 없으면 에러 무시
}

# 작업 생성: 컴퓨터 시작 시 자동 실행
Write-Host "`n작업 생성 중... (컴퓨터 시작 시 자동 실행)" -ForegroundColor Green

$action = New-ScheduledTaskAction -Execute $batFile -WorkingDirectory $scriptDir
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0)  # 무제한 실행

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

$task = Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "OMG 암호화폐 실시간 모니터링 시스템 (24/7 실행)" `
    -Force

# 표시 모드로 설정 (로그를 볼 수 있도록)
$task.Settings.Hidden = $false
$task | Set-ScheduledTask | Out-Null

Write-Host "✓ 작업 생성 완료: $taskName" -ForegroundColor Green
Write-Host "  - 트리거: 컴퓨터 시작 시 자동 실행" -ForegroundColor White
Write-Host "  - 모드: 표시 모드 (로그 확인 가능)" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ 작업 스케줄러 설정 완료! (OMG)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "생성된 작업:" -ForegroundColor Yellow
Write-Host "  - $taskName" -ForegroundColor White
Write-Host "    → 컴퓨터 시작 시 자동 실행" -ForegroundColor Gray
Write-Host "    → 터미널을 닫아도 계속 실행됨" -ForegroundColor Gray
Write-Host "    → 재부팅 후 자동으로 다시 시작" -ForegroundColor Gray

Write-Host "`n테스트 방법:" -ForegroundColor Yellow
Write-Host "  1. 작업 스케줄러 열기: Win+R → taskschd.msc" -ForegroundColor White
Write-Host "  2. 작업 목록에서 '$taskName' 우클릭 → '실행'" -ForegroundColor White
Write-Host "  3. 새 창이 열리며 모니터링이 시작됩니다" -ForegroundColor White

Write-Host "`n중요:" -ForegroundColor Yellow
Write-Host "  - 작업 스케줄러에 등록되면 터미널을 닫아도 계속 실행됩니다" -ForegroundColor White
Write-Host "  - 컴퓨터를 재부팅하면 자동으로 다시 시작됩니다" -ForegroundColor White
Write-Host "  - 작업을 중지하려면 작업 스케줄러에서 작업을 중지하세요" -ForegroundColor White

Write-Host "`n지금 바로 실행하시겠습니까? (Y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "`n작업 실행 중..." -ForegroundColor Green
    Start-ScheduledTask -TaskName $taskName
    Write-Host "✓ 작업이 실행되었습니다!" -ForegroundColor Green
    Write-Host "  모니터링 창이 열리며 로그가 표시됩니다." -ForegroundColor White
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Gray
Read-Host | Out-Null

