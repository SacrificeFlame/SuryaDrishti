# Start both Backend and Frontend servers
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting SuryaDrishti - All Services" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend Server
Write-Host "Starting Backend Server (port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn app.main:app --reload --port 8000" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host "Starting Frontend Server (port 3000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Both servers are starting!" -ForegroundColor Green
Write-Host "Backend: http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")



