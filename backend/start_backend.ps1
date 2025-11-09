# Start Backend Server
Write-Host "Starting SuryaDrishti Backend Server..." -ForegroundColor Green
Set-Location "$PSScriptRoot"
python -m uvicorn app.main:app --reload --port 8000



