$startup = [Environment]::GetFolderPath('Startup')
$lnk = Join-Path $startup 'Device Monitor.lnk'
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($lnk)
$s.TargetPath = 'C:\Users\Daffa\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe'
$s.Arguments = '"C:\Hermes\Output\device-monitor\scripts\start_monitor.pyw"'
$s.WorkingDirectory = 'C:\Hermes\Output\device-monitor\scripts'
$s.Description = 'Device Monitor tray - VXE R1 SE+ / EarFun Air Pro 4'
$s.Save()
Write-Output $lnk
