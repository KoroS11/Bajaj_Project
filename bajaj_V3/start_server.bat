@echo off
echo 🎯 Starting Dynamic AI Insurance Backend Server...
echo.

cd /d "C:\Users\harsh\OneDrive\Desktop\Making Experimental Changes to Bajaj_V3\bajaj_V3\backend"

echo Activating virtual environment...
call "C:\Users\harsh\OneDrive\Desktop\Making Experimental Changes to Bajaj_V3\.venv\Scripts\activate.bat"

echo.
echo Starting server...
python main_intelligent_fuzzy.py

pause
