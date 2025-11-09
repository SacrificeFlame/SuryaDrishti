# Quick test script to check if backend is running
Write-Host "Testing backend connection..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "Backend is running!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Backend is NOT running!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start the backend, run:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Cyan
    Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Cyan
}
