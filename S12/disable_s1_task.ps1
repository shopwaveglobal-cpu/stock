$result = & schtasks.exe /Change /TN "S1_Daily_Trading_Signal" /DISABLE
Write-Host $result
$result2 = & schtasks.exe /Query /TN "S1_Daily_Trading_Signal" /FO LIST
Write-Host $result2
