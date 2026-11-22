@echo off
REM Jalankan Device Monitor (tray + panel http://localhost:4173)
cd /d "%~dp0scripts"
start "" "C:\Users\Daffa\AppData\Local\Python\pythoncore-3.14-64\pythonw.exe" start_monitor.pyw
