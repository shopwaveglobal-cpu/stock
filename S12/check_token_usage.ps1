Write-Host "=== S12 Real_Time_Monitor.py 토큰 관련 ==="
$lines = Get-Content "C:\Users\log\Desktop\Code\S12\Real_Time_Monitor.py"
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match "token|Token|KIWOOM_TOKEN|get_access") {
        Write-Host ("L{0}: {1}" -f ($i+1), $lines[$i].Trim())
    }
}

Write-Host ""
Write-Host "=== S1 Real_Time_Monitor_S1.py 토큰 관련 ==="
$lines2 = Get-Content "C:\Users\log\Desktop\Code\S1\Real_Time_Monitor_S1.py"
for ($i = 0; $i -lt $lines2.Count; $i++) {
    if ($lines2[$i] -match "token|Token|KIWOOM_TOKEN|get_access") {
        Write-Host ("L{0}: {1}" -f ($i+1), $lines2[$i].Trim())
    }
}

Write-Host ""
Write-Host "=== Trading_Signal_System.py 토큰 관련 ==="
$lines3 = Get-Content "C:\Users\log\Desktop\Code\S12\Trading_Signal_System.py"
for ($i = 0; $i -lt $lines3.Count; $i++) {
    if ($lines3[$i] -match "token|Token|KIWOOM_TOKEN|get_access") {
        Write-Host ("L{0}: {1}" -f ($i+1), $lines3[$i].Trim())
    }
}
