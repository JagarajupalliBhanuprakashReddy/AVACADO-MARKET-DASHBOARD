@echo off
title Agricultural Market Pricing ^& Sales Dashboard - Shutdown
color 0C

echo ==============================================================================
echo        AGRICULTURAL MARKET PRICING ^& SALES DASHBOARD - SHUTDOWN
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [INFO] Searching for running dashboard processes on port 8501...

:: Find PID listening on port 8501
set "FOUND_PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501 " ^| findstr "LISTENING"') do (
    set "FOUND_PID=%%a"
)

if not "%FOUND_PID%"=="" (
    echo [INFO] Stopping process ID %FOUND_PID% on port 8501...
    taskkill /F /PID %FOUND_PID% >nul 2>&1
    echo [OK] Dashboard server stopped successfully.
) else (
    echo [INFO] No server process found listening on port 8501.
)

:: Terminate any lingering python processes running app.py
powershell -Command "Get-CimInstance Win32_Process -Filter \"Name LIKE 'python%%'\" | Where-Object { $_.CommandLine -match 'streamlit' -and $_.CommandLine -match 'app.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1

echo.
echo ==============================================================================
echo  Application has been shut down cleanly.
echo  To start the dashboard again, double-click: START.bat
echo ==============================================================================
echo.
ping 127.0.0.1 -n 3 >nul
