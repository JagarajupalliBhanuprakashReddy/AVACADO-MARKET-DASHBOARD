# Agricultural Market Pricing & Sales Dashboard - PowerShell Launcher
$ErrorActionPreference = "SilentlyContinue"

Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "       AGRICULTURAL MARKET PRICING & SALES DASHBOARD - LAUNCHER" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host ""

$workDir = $PSScriptRoot
if (-not $workDir) { $workDir = (Get-Location).Path }
Set-Location $workDir

# Locate Python
$pythonExe = ""
if (Test-Path "C:\venvs\agricultural_market_env\Scripts\python.exe") {
    $pythonExe = "C:\venvs\agricultural_market_env\Scripts\python.exe"
} elseif (Test-Path "$workDir\.venv\Scripts\python.exe") {
    $pythonExe = "$workDir\.venv\Scripts\python.exe"
} elseif (Test-Path "$workDir\venv\Scripts\python.exe") {
    $pythonExe = "$workDir\venv\Scripts\python.exe"
} else {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { $pythonExe = "python" }
}

if (-not $pythonExe) {
    Write-Host "[ERROR] Python was not found on your system!" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ or configure your virtual environment."
    pause
    exit 1
}

Write-Host "[OK] Using Python: $pythonExe" -ForegroundColor Cyan

# Check if already running on port 8501
$activeConn = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
if ($activeConn) {
    Write-Host "[INFO] Dashboard is already active at http://localhost:8501" -ForegroundColor Yellow
    Write-Host "Opening your web browser now..."
    Start-Process "http://localhost:8501"
    Start-Sleep -Seconds 3
    exit 0
}

Write-Host "[INFO] Starting application server on http://localhost:8501 ..." -ForegroundColor Cyan
Start-Process -FilePath $pythonExe -ArgumentList "-m streamlit run app.py --server.port 8501 --server.headless true" -WorkingDirectory $workDir

Write-Host "[INFO] Initializing engine and loading database views..." -ForegroundColor Cyan
Start-Sleep -Seconds 4

Write-Host "[INFO] Opening dashboard in your default browser..." -ForegroundColor Green
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " Dashboard is active at: http://localhost:8501" -ForegroundColor Green
Write-Host " To stop the application at any time, run: STOP.bat or STOP.ps1" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Start-Sleep -Seconds 3
