@echo off
title TEST - AI Insurance Query System
color 0E

echo ========================================
echo  🧪 STEP-BY-STEP DIAGNOSTIC TEST
echo ========================================
echo.

cd /d "%~dp0"

echo [STEP 1] Testing PDF Processing Libraries...
cd backend
call ..\venv_enhanced\Scripts\activate.bat
python test_pdf_processing.py
if errorlevel 1 (
    echo.
    echo ❌ PDF processing test FAILED
    echo Please check error messages above
    pause
    exit /b 1
)

echo.
echo [STEP 2] Starting server in test mode...
echo ⚠️  This will start the server - check the output!
echo.
echo Look for:
echo   ✅ Documents loaded: X
echo   📋 Available Documents: (list should appear)
echo.
echo Press Ctrl+C to stop server when ready
echo.
pause

python main_intelligent_fuzzy.py

echo.
echo Server stopped. Check the output above for document loading status.
pause
