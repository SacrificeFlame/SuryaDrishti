# SuryaDrishti Setup Script for Windows
# This script sets up the entire project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SuryaDrishti Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "[2/6] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Node.js not found. Frontend setup will be skipped." -ForegroundColor Yellow
    Write-Host "   Install Node.js from https://nodejs.org/ to enable frontend" -ForegroundColor Yellow
    $skipFrontend = $true
}

# Create virtual environment
Write-Host "[3/6] Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists. Skipping creation." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "[4/6] Installing Python dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r backend\requirements.txt
Write-Host "✅ Python dependencies installed" -ForegroundColor Green

# Setup database
Write-Host "[5/6] Setting up database..." -ForegroundColor Yellow
python scripts\setup_database.py
Write-Host "✅ Database initialized" -ForegroundColor Green

# Setup frontend (if Node.js is available)
if (-not $skipFrontend) {
    Write-Host "[6/6] Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "[6/6] Skipping frontend setup (Node.js not found)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Generate training data: python scripts\generate_sample_data.py" -ForegroundColor White
Write-Host "2. Train models: python train_models.py" -ForegroundColor White
Write-Host "3. Test system: python test_system.py" -ForegroundColor White
Write-Host "4. Start backend: cd backend && python -m uvicorn app.main:app --reload" -ForegroundColor White
if (-not $skipFrontend) {
    Write-Host "5. Start frontend: cd frontend && npm run dev" -ForegroundColor White
}
Write-Host ""

