Write-Host "🔧 QUICK DIAGNOSIS TOOL" -ForegroundColor Green
Write-Host "Testing AI Insurance Query System" -ForegroundColor Yellow
Write-Host ""

# Change to correct directory
Set-Location "c:\Users\harsh\OneDrive\Desktop\Making Experimental Changes to Bajaj_V3\bajaj_V3"

# Test 1: Check if Python is available
Write-Host "[TEST 1] Checking Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found" -ForegroundColor Red
    exit 1
}

# Test 2: Check if virtual environment exists
Write-Host "[TEST 2] Checking Virtual Environment..." -ForegroundColor Cyan
if (Test-Path "venv_enhanced\Scripts\activate.bat") {
    Write-Host "✅ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found" -ForegroundColor Red
}

# Test 3: Check backend files
Write-Host "[TEST 3] Checking Backend Files..." -ForegroundColor Cyan
if (Test-Path "backend\main_intelligent_fuzzy.py") {
    Write-Host "✅ Main backend file exists" -ForegroundColor Green
} else {
    Write-Host "❌ Main backend file missing" -ForegroundColor Red
}

# Test 4: Check PDF files
Write-Host "[TEST 4] Checking PDF Files..." -ForegroundColor Cyan
$pdfCount = (Get-ChildItem -Path "backend\uploads" -Filter "*.pdf" -ErrorAction SilentlyContinue).Count
if ($pdfCount -gt 0) {
    Write-Host "✅ Found $pdfCount PDF files in uploads" -ForegroundColor Green
} else {
    Write-Host "⚠️ No PDF files found in uploads" -ForegroundColor Yellow
}

# Test 5: Activate environment and check dependencies
Write-Host "[TEST 5] Testing Dependencies..." -ForegroundColor Cyan
try {
    & "venv_enhanced\Scripts\activate.bat"
    
    # Test PDF libraries
    $testResult = python -c "import pdfplumber, PyPDF2; print('PDF libraries OK')" 2>&1
    if ($testResult -match "PDF libraries OK") {
        Write-Host "✅ PDF processing libraries working" -ForegroundColor Green
    } else {
        Write-Host "❌ PDF libraries failed: $testResult" -ForegroundColor Red
    }
    
    # Test Flask
    $flaskTest = python -c "import flask; print('Flask OK')" 2>&1
    if ($flaskTest -match "Flask OK") {
        Write-Host "✅ Flask working" -ForegroundColor Green
    } else {
        Write-Host "❌ Flask failed: $flaskTest" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Environment activation failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "🚀 READY TO START SERVER" -ForegroundColor Green
Write-Host "Run: .\ULTIMATE_STARTUP.bat" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue"
