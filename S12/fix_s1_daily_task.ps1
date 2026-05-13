# S1_Daily_Trading_Signal 작업 수정 - 20:15 평일, 반복 없음
$svc = New-Object -ComObject "Schedule.Service"
$svc.Connect()
$folder = $svc.GetFolder("\")

$folder.DeleteTask("S1_Daily_Trading_Signal", 0)
Write-Host "기존 작업 삭제"

$taskDef = $svc.NewTask(0)
$taskDef.RegistrationInfo.Description = "S1 Daily Trading Signal - 평일 20:15"
$taskDef.Settings.Enabled = $true
$taskDef.Settings.Hidden = $true
$taskDef.Settings.StopIfGoingOnBatteries = $false
$taskDef.Settings.DisallowStartIfOnBatteries = $false

$trigger = $taskDef.Triggers.Create(2)
$trigger.StartBoundary = "2025-11-02T20:15:00"
$trigger.DaysInterval = 1
$trigger.Enabled = $true

$action = $taskDef.Actions.Create(0)
$action.Path = "C:\Users\log\Desktop\Code\S1\RUN_S1_DAILY.bat"
$action.WorkingDirectory = "C:\Users\log\Desktop\Code\S1"

$folder.RegisterTaskDefinition("S1_Daily_Trading_Signal", $taskDef, 6, $null, $null, 3) | Out-Null
Write-Host "재생성 완료"

$info = Get-ScheduledTaskInfo -TaskName "S1_Daily_Trading_Signal" -ErrorAction SilentlyContinue
Write-Host ("다음 실행: {0}" -f $info.NextRunTime)
