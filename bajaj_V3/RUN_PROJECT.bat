@echo off
title AI Insurance Query System
echo.
echo ========================================
echo   AI Insurance Query System Setup
echo ========================================
echo.

REM Navigate to project directory
cd /d "C:\Users\harsh\OneDrive\Desktop\Making Experimental Changes to Bajaj_V3\bajaj_V3\backend"
echo 📂 Current directory: %CD%

REM Check if virtual environment exists
if not exist "..\venv_enhanced\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Creating new virtual environment...
    cd ..
    python -m venv venv_enhanced
    cd backend
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call "..\venv_enhanced\Scripts\activate.bat"

REM Install required packages
echo 📦 Installing dependencies...
pip install flask flask-cors rapidfuzz pdfplumber PyPDF2 requests

REM Check Python version
echo 🐍 Python version:
python --version

REM Start the server
echo.
echo 🚀 Starting AI Insurance Query System...
echo 🌐 Server will be available at: http://localhost:5000
echo.
python main_intelligent_fuzzy.py

echo.
echo ⚠️ Server stopped. Press any key to exit...
pause > nul
