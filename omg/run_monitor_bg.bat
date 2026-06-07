@echo off
cd /d "%~dp0"
C:\Python314\python.exe crypto_realtime_monitor.py >> logs\monitor_stdout.log 2>&1
