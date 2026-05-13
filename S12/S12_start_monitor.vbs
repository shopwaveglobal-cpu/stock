Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "C:\Users\log\Desktop\Code\S12"
objShell.Run "cmd /c C:\Users\log\Desktop\Code\S12\S12_self_restart.bat", 0, False
