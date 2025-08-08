@echo off
echo 🎯 Starting Dynamic AI Insurance Query System
echo ========================================

REM Navigate to backend directory
cd /d "C:\Users\harsh\OneDrive\Desktop\Making Experimental Changes to Bajaj_V3\bajaj_V3\backend"

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call "C:\Users\harsh\OneDrive\Desktop\Making Experimental Changes to Bajaj_V3\.venv\Scripts\activate.bat"

REM Verify Python path
echo 🐍 Python path:
where python

REM Install any missing dependencies
echo 📦 Checking dependencies...
pip install flask flask-cors rapidfuzz pdfplumber PyPDF2 requests

REM Start the server
echo 🚀 Starting server...
python main_intelligent_fuzzy.py

pause
