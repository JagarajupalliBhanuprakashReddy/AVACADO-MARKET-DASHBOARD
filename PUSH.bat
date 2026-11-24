@echo off
title Push to GitHub - Avocado Market Dashboard
color 0A
echo =====================================================================
echo  Agricultural Market Pricing ^& Sales Dashboard - Git Push
echo =====================================================================
echo.
echo Pushing repository to:
echo https://github.com/JagarajupalliBhanuprakashReddy/AVACADO-MARKET-DASHBOARD.git
echo.
echo If prompted, please authenticate via your web browser or enter
echo your GitHub username and Personal Access Token (PAT).
echo.
git push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo =====================================================================
    echo  SUCCESS: Repository successfully pushed to GitHub!
    echo =====================================================================
) else (
    echo =====================================================================
    echo  Push failed or was cancelled. Please check your GitHub credentials.
    echo =====================================================================
)
echo.
pause
