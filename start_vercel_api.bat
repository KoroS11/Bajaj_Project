@echo off
echo ========================================
echo Starting Vercel-Compatible API Server
echo ========================================
echo.
echo This API works WITHOUT a database!
echo - Processes PDFs in memory
echo - Uses session storage
echo - Perfect for Vercel deployment
echo.
echo Starting server on http://localhost:5000
echo Press Ctrl+C to stop
echo.
python api/vercel_index.py
pause
