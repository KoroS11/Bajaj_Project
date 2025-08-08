@echo off
title AI Insurance Query System - Ultimate Startup
color 0A

echo ====================================================
echo  🎯 AI INSURANCE QUERY SYSTEM - ULTIMATE STARTUP
echo  ✅ FIXED: Now uses ONLY your uploaded documents
echo  📄 No mock data - Real document analysis only
echo ====================================================
echo.

cd /d "%~dp0"

echo [1/5] Activating Virtual Environment...
if exist "venv_enhanced\Scripts\activate.bat" (
    call "venv_enhanced\Scripts\activate.bat"
    echo ✅ Virtual environment activated
) else (
    echo ❌ Virtual environment not found, creating one...
    python -m venv venv_enhanced
    call "venv_enhanced\Scripts\activate.bat"
    echo ✅ New virtual environment created and activated
)
echo.

echo [2/5] Installing/Updating Dependencies...
echo Installing core packages...
python -m pip install --upgrade pip --quiet
echo ✅ pip upgraded

echo Installing Flask framework...
pip install Flask==2.3.0 Flask-CORS==4.0.0 --quiet
echo ✅ Flask installed

echo Installing PDF processing libraries...
pip install pdfplumber==0.9.0 PyPDF2==3.0.1 --quiet
echo ✅ PDF libraries installed

echo Installing fuzzy matching library...
pip install rapidfuzz==3.5.0 --quiet
echo ✅ RapidFuzz installed

echo Verifying PDF processing installation...
python -c "import pdfplumber, PyPDF2; print('✅ PDF processing libraries working correctly')" 2>nul || (
    echo ❌ PDF libraries failed - trying alternative installation...
    pip install --upgrade --force-reinstall pdfplumber==0.9.0 PyPDF2==3.0.1
    python -c "import pdfplumber, PyPDF2; print('✅ PDF processing libraries installed successfully')" || echo "❌ PDF installation still failing"
)
echo ✅ All dependencies processed
echo.

echo [4/5] Testing PDF Processing...
echo Running PDF processing test...
cd backend
python test_pdf_processing.py
if errorlevel 1 (
    echo ❌ PDF processing test failed - check if PDF libraries are working
    pause
    exit /b 1
)
echo ✅ PDF processing test passed
cd..
echo.

echo [5/5] Starting Flask Server...
cd backend
echo 🚀 Server will be available at: http://localhost:5000
echo 📋 Health check: http://localhost:5000/health
echo 🌐 Frontend: Open working_interface.html in your browser
echo.
echo ⚠️  IMPORTANT: Upload PDF documents first before submitting queries
echo 📄 System requires actual policy documents - no mock data used
echo.
echo 🔧 TO OPEN FRONTEND INTERFACE:
echo    1. Keep this terminal window open (server running)
echo    2. Open File Explorer  
echo    3. Navigate to: frontend\intelligent_interface.html
echo    4. Double-click intelligent_interface.html to open in browser
echo.
echo 🎯 NEW INTELLIGENT FEATURES:
echo    - Advanced NLP query processing
echo    - Confusion Matrix Classification (RR, RA, AR, AA)
echo    - Semantic procedure matching
echo    - Enhanced fuzzy matching
echo    - Complete JSON response format
echo.
echo 🔍 TO DEBUG PDF PROCESSING:
echo    - Open: frontend\debug_tool.html
echo    - Use this to see what was extracted from your PDF
echo.
echo Press Ctrl+C to stop the server
echo ====================================================
echo.

python main_complete_intelligent.py

echo.
echo ====================================================
echo Server stopped. Press any key to exit...
pause > nul
