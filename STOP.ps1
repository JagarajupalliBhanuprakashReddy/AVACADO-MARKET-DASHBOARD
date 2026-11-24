# Agricultural Market Pricing & Sales Dashboard - PowerShell Shutdown
$ErrorActionPreference = "SilentlyContinue"

Write-Host "==============================================================================" -ForegroundColor Yellow
Write-Host "       AGRICULTURAL MARKET PRICING & SALES DASHBOARD - SHUTDOWN" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Yellow
Write-Host ""

Set-Location $PSScriptRoot

Write-Host "[INFO] Finding active dashboard processes..." -ForegroundColor Cyan

# Find processes listening on 8501
$conns = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
if ($conns) {
    foreach ($c in $conns) {
        $pId = $c.OwningProcess
        Write-Host "[INFO] Stopping process ID $pId on port 8501..." -ForegroundColor Cyan
        Stop-Process -Id $pId -Force -ErrorAction SilentlyContinue
    }
}

# Find any python processes running app.py
Get-CimInstance Win32_Process -Filter "Name LIKE 'python%'" | Where-Object { 
    $_.CommandLine -match 'streamlit' -and $_.CommandLine -match 'app.py' 
} | ForEach-Object {
    Write-Host "[INFO] Stopping background server worker (PID: $($_.ProcessId))..." -ForegroundColor Cyan
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " Application has been shut down cleanly." -ForegroundColor Green
Write-Host " To start the dashboard again, run: START.bat or START.ps1" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Start-Sleep -Seconds 3
