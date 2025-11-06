# SuryaDrishti - Complete Setup and Run Script
# This script sets up and runs the entire system

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SuryaDrishti - Complete Setup & Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/8] Checking Python..." -ForegroundColor Yellow
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
    $pythonVersion = python --version
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
    $pythonVersion = py --version
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Or install from Microsoft Store" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
Write-Host "[2/8] Checking Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "✅ Found: $nodeVersion" -ForegroundColor Green
    $hasNode = $true
} else {
    Write-Host "⚠️  Node.js not found - Frontend will be skipped" -ForegroundColor Yellow
    Write-Host "Install from https://nodejs.org/ to enable dashboard" -ForegroundColor Yellow
    $hasNode = $false
}

# Create virtual environment
Write-Host "[3/8] Setting up Python environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment exists, using it" -ForegroundColor Yellow
} else {
    & $pythonCmd -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate and install dependencies
Write-Host "[4/8] Installing Python dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
& $pythonCmd -m pip install --upgrade pip --quiet
& $pythonCmd -m pip install -r backend\requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Setup database
Write-Host "[5/8] Setting up database..." -ForegroundColor Yellow
& $pythonCmd scripts\setup_database.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Database setup failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Database initialized" -ForegroundColor Green

# Check if models exist, if not train them
Write-Host "[6/8] Checking ML models..." -ForegroundColor Yellow
if (-not (Test-Path "data\models\cloud_seg_v1.pth") -or -not (Test-Path "data\models\irradiance_v1.pth")) {
    Write-Host "⚠️  Models not found, training models (this may take a while)..." -ForegroundColor Yellow
    & $pythonCmd train_models.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Model training had issues, but continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Models trained" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Models found" -ForegroundColor Green
}

# Test system
Write-Host "[7/8] Running system tests..." -ForegroundColor Yellow
& $pythonCmd test_system.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some tests failed, but continuing..." -ForegroundColor Yellow
} else {
    Write-Host "✅ System tests passed" -ForegroundColor Green
}

# Setup frontend
if ($hasNode) {
    Write-Host "[8/8] Setting up frontend..." -ForegroundColor Yellow
    Set-Location frontend
    if (Test-Path "node_modules") {
        Write-Host "⚠️  node_modules exists, skipping install" -ForegroundColor Yellow
    } else {
        npm install
        Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
    }
    Set-Location ..
} else {
    Write-Host "[8/8] Skipping frontend (Node.js not found)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start backend in background
Write-Host "Starting backend server on http://localhost:8000..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Wait a bit for backend to start
Start-Sleep -Seconds 5

# Start frontend if Node.js is available
if ($hasNode) {
    Write-Host "Starting frontend dashboard on http://localhost:3000..." -ForegroundColor Green
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        Set-Location frontend
        npm run dev
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Services Running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
if ($hasNode) {
    Write-Host "Frontend Dashboard: http://localhost:3000" -ForegroundColor White
}
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Keep script running and show logs
try {
    while ($true) {
        Start-Sleep -Seconds 1
        # Check if jobs are still running
        $backendStatus = Get-Job -Id $backendJob.Id | Select-Object -ExpandProperty State
        if ($backendStatus -eq "Failed" -or $backendStatus -eq "Completed") {
            Write-Host "Backend stopped!" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    if ($hasNode) {
        Stop-Job $frontendJob -ErrorAction SilentlyContinue
        Remove-Job $frontendJob -ErrorAction SilentlyContinue
    }
    Write-Host "Services stopped." -ForegroundColor Green
}

