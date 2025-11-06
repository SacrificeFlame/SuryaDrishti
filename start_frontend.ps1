# Frontend Setup Script
# Run this AFTER installing Node.js from https://nodejs.org/

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SuryaDrishti Frontend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not found!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

$nodeVersion = node --version
Write-Host "✅ Found Node.js: $nodeVersion" -ForegroundColor Green
Write-Host ""

Write-Host "[1/2] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Write-Host "✅ Dependencies installed" -ForegroundColor Green

Write-Host "[2/2] Starting frontend dev server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Frontend Starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

npm run dev

