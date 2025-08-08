# PowerShell script to start the Dynamic AI Insurance Query System
Write-Host "🎯 Starting Dynamic AI Insurance Query System..." -ForegroundColor Green

# Navigate to the backend directory
Set-Location "C:\Users\harsh\OneDrive\Desktop\Making Experimental Changes to Bajaj_V3\bajaj_V3\backend"

# Start the server using the virtual environment
& "C:\Users\harsh\OneDrive\Desktop\Making Experimental Changes to Bajaj_V3\.venv\Scripts\python.exe" main_intelligent_fuzzy.py

Write-Host "Press any key to continue..." -ForegroundColor Yellow
Read-Host
