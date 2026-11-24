@echo off
title Agricultural Market Pricing ^& Sales Dashboard - Launcher
color 0A

echo ==============================================================================
echo        AGRICULTURAL MARKET PRICING ^& SALES DASHBOARD - LAUNCHER
echo ==============================================================================
echo.

:: Change directory to current folder
cd /d "%~dp0"

:: 1. Locate Python executable
set "PYTHON_EXE="

if exist "C:\venvs\agricultural_market_env\Scripts\python.exe" (
    set "PYTHON_EXE=C:\venvs\agricultural_market_env\Scripts\python.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
) else (
    for /f "delims=" %%i in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)

if "%PYTHON_EXE%"=="" (
    color 0C
    echo [ERROR] Python was not found on your system!
    echo Please install Python 3.10+ or configure your virtual environment.
    echo.
    pause
    exit /b 1
)

echo [OK] Using Python: %PYTHON_EXE%

:: 2. Check if application is already running on port 8501
netstat -ano | findstr ":8501 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Dashboard server is already active on http://localhost:8501
    echo Opening your web browser now...
    start http://localhost:8501
    ping 127.0.0.1 -n 3 >nul
    exit /b 0
)

:: 3. Launch Streamlit server
echo [INFO] Starting application server on http://localhost:8501 ...
start "Agri Market Dashboard Server" "%PYTHON_EXE%" -m streamlit run app.py --server.port 8501 --server.headless true

:: 4. Wait for server to bind port and launch browser
echo [INFO] Initializing engine and loading database views...
ping 127.0.0.1 -n 5 >nul

echo [INFO] Opening dashboard in your default browser...
start http://localhost:8501

echo.
echo ==============================================================================
echo  Dashboard is active at: http://localhost:8501
echo  To stop the application at any time, double-click: STOP.bat
echo ==============================================================================
echo.
ping 127.0.0.1 -n 4 >nul
