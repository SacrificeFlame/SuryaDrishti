# SuryaDrishti - Complete Setup Script
# Run this AFTER installing Python 3.11+

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SuryaDrishti Setup & Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} else {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = & $pythonCmd --version
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Step 1: Virtual Environment
Write-Host "[1/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment exists" -ForegroundColor Yellow
} else {
    & $pythonCmd -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Step 2: Activate and install dependencies
Write-Host "[2/6] Installing dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
& $pythonCmd -m pip install --upgrade pip --quiet
& $pythonCmd -m pip install -r backend\requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Step 3: Setup database
Write-Host "[3/6] Setting up database..." -ForegroundColor Yellow
& $pythonCmd scripts\setup_database.py
Write-Host "✅ Database initialized" -ForegroundColor Green

# Step 4: Check models
Write-Host "[4/6] Checking ML models..." -ForegroundColor Yellow
if (-not (Test-Path "data\models\cloud_seg_v1.pth")) {
    Write-Host "⚠️  Models not found - training models (this will take several minutes)..." -ForegroundColor Yellow
    Write-Host "You can skip this and train later with: python train_models.py" -ForegroundColor Yellow
    $train = Read-Host "Train models now? (y/n)"
    if ($train -eq "y" -or $train -eq "Y") {
        & $pythonCmd train_models.py
    }
} else {
    Write-Host "✅ Models found" -ForegroundColor Green
}

# Step 5: Test system
Write-Host "[5/6] Testing system..." -ForegroundColor Yellow
& $pythonCmd test_system.py
Write-Host "✅ System ready" -ForegroundColor Green

# Step 6: Start backend
Write-Host "[6/6] Starting backend server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Backend Starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start backend
Set-Location backend
& $pythonCmd -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

