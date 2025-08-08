@echo off
title PDF Processing Libraries Installer
color 0E

echo ====================================================
echo  📄 PDF PROCESSING LIBRARIES INSTALLER
echo ====================================================
echo.

cd /d "%~dp0"

echo [1/4] Activating Virtual Environment...
if exist "venv_enhanced\Scripts\activate.bat" (
    call "venv_enhanced\Scripts\activate.bat"
    echo ✅ Virtual environment activated
) else (
    echo ❌ Virtual environment not found. Please run ULTIMATE_STARTUP.bat first.
    pause
    exit /b 1
)
echo.

echo [2/4] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [3/4] Installing PDF processing libraries with verbose output...
echo Installing pdfplumber...
pip install --upgrade pdfplumber==0.9.0 --verbose
echo.
echo Installing PyPDF2...
pip install --upgrade PyPDF2==3.0.1 --verbose
echo.

echo [4/4] Testing PDF processing installation...
echo Testing pdfplumber...
python -c "import pdfplumber; print('✅ pdfplumber imported successfully')" || echo "❌ pdfplumber import failed"

echo Testing PyPDF2...
python -c "import PyPDF2; print('✅ PyPDF2 imported successfully')" || echo "❌ PyPDF2 import failed"

echo Testing PDF functionality...
python -c "
import pdfplumber, PyPDF2
print('✅ Both PDF libraries working')
print('pdfplumber version:', getattr(pdfplumber, '__version__', 'unknown'))
print('PyPDF2 version:', getattr(PyPDF2, '__version__', 'unknown'))
" || echo "❌ PDF libraries test failed"

echo.
echo ====================================================
echo PDF Processing Setup Complete!
echo You can now run ULTIMATE_STARTUP.bat
echo ====================================================
pause
