@echo off
echo ========================================
echo    VERCEL DEPLOYMENT QUICK START
echo ========================================
echo.
echo This script will help you deploy your
echo Insurance Query Engine to Vercel!
echo.
pause

echo.
echo Step 1: Checking if Node.js is installed...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please download and install from: https://nodejs.org/
    echo After installing, run this script again.
    pause
    exit /b 1
)
echo [OK] Node.js is installed

echo.
echo Step 2: Checking if Vercel CLI is installed...
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Vercel CLI not found. Installing now...
    npm install -g vercel
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install Vercel CLI
        pause
        exit /b 1
    )
)
echo [OK] Vercel CLI is installed

echo.
echo Step 3: Checking project files...
if not exist "vercel.json" (
    echo [ERROR] vercel.json not found!
    pause
    exit /b 1
)
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)
if not exist "api\vercel_index.py" (
    if not exist "api\index.py" (
        echo [ERROR] API files not found!
        pause
        exit /b 1
    )
)
echo [OK] All required files found

echo.
echo ========================================
echo    READY TO DEPLOY!
echo ========================================
echo.
echo Next steps:
echo 1. The Vercel login page will open
echo 2. Login with your Vercel account
echo 3. Return to this window
echo 4. Follow the deployment prompts
echo.
pause

echo.
echo Logging in to Vercel...
vercel login

echo.
echo Starting deployment...
echo.
echo When prompted:
echo - Project name: bajaj-insurance-engine
echo - Directory: ./ (just press Enter)
echo - Modify settings: N
echo.
vercel

echo.
echo ========================================
echo    DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your app should now be available at:
echo https://bajaj-insurance-engine.vercel.app
echo.
echo To deploy to production, run:
echo vercel --prod
echo.
pause
