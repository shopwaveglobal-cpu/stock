Set objWMI = GetObject("winmgmts:\\.\root\cimv2")
Set procs = objWMI.ExecQuery("SELECT * FROM Win32_Process WHERE CommandLine LIKE '%Real_Time_Monitor_S1%'")
For Each proc In procs
    proc.Terminate
Next
