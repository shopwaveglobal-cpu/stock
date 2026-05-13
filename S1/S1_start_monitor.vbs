Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "C:\Users\log\Desktop\Code\S1"
objShell.Run "cmd /c C:\Users\log\Desktop\Code\S1\S1_self_restart.bat", 0, False
