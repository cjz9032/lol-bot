@echo off
:loop
taskkill /f /im python.exe /t
start "" python.exe "./main.pyw"
timeout /t 36 /nobreak
goto loop