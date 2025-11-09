# View Backend Logs
# This script helps you view backend logs

Write-Host "=== Backend Log Viewer ===" -ForegroundColor Cyan
Write-Host ""

# Check if backend is running
$backendProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*app.main*"
}

if ($backendProcess) {
    Write-Host "✅ Backend is running (PID: $($backendProcess.Id))" -ForegroundColor Green
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "1. Find the PowerShell window where you started the backend" -ForegroundColor White
    Write-Host "2. Look for messages like:" -ForegroundColor White
    Write-Host "   - 'INFO:     Uvicorn running on http://0.0.0.0:8000'" -ForegroundColor Cyan
    Write-Host "   - 'Fetching forecast schedule for microgrid...'" -ForegroundColor Cyan
    Write-Host "   - 'Successfully generated schedule...'" -ForegroundColor Green
    Write-Host ""
    Write-Host "3. If you want to save logs to a file, restart backend with:" -ForegroundColor Yellow
    Write-Host "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 2>&1 | Tee-Object -FilePath backend.log" -ForegroundColor White
} else {
    Write-Host "❌ Backend is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Start the backend with:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
}

Write-Host ""
Write-Host "=== Quick Test ===" -ForegroundColor Cyan
Write-Host "Test the forecast endpoint:" -ForegroundColor Yellow
Write-Host "   Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/forecast/schedule?forecast_hours=12' -Method POST | Select-Object StatusCode" -ForegroundColor White

