Start-Process -FilePath "C:\Windows\System32\cmd.exe" `
    -ArgumentList "/c `"C:\Users\log\Desktop\Code\S12\S12_self_restart.bat`"" `
    -WorkingDirectory "C:\Users\log\Desktop\Code\S12" `
    -WindowStyle Hidden
Start-Sleep -Seconds 3
Write-Host "S12 루프 시작 완료"
