:loop
:: 1. 杀掉所有 Python 进程
taskkill /f /im python.exe /t >nul 2>&1
taskkill /F /IM "League of Legends.exe"
taskkill /F /IM "Client.exe"
taskkill /F /IM League*
taskkill /F /IM Riot*

:: 2. 杀掉旧的 PowerShell 进程（匹配特定命令行）
for /f "tokens=2 delims=," %%A in (
    'tasklist /v /fo csv ^| findstr /i "main.pyw"'
) do (
    taskkill /pid %%~A /f >nul 2>&1
)

:: 3. 启动新的 PowerShell 并运行 Python
start "" powershell -NoExit -Command "cd \""%~dp0\"\"; python.exe .\main.pyw"

:: 4. 等待 3600 秒
timeout /t 7200 /nobreak >nul

goto loop