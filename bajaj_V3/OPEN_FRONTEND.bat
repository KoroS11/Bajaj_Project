@echo off
title Open Frontend Interface
echo 🌐 Opening AI Insurance Query System Frontend...

:: Check if working_interface.html exists
if exist "frontend\working_interface.html" (
    echo ✅ Found frontend interface
    echo 🚀 Opening in default browser...
    start "" "frontend\working_interface.html"
    echo ✅ Frontend interface opened!
    echo.
    echo 📋 Interface should now be open in your browser
    echo 🔧 Make sure the server is running (ULTIMATE_STARTUP.bat)
) else (
    echo ❌ Frontend interface not found!
    echo 📁 Looking for: frontend\working_interface.html
    echo 💡 Make sure you're in the correct directory
)

echo.
echo Press any key to close...
pause > nul
