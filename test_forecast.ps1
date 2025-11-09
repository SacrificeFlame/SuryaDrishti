# Test Forecast Endpoint and View Logs
Write-Host "`n=== Testing Forecast Endpoint ===" -ForegroundColor Cyan
Write-Host "This will trigger the forecast API and you should see logs in the backend window`n" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/forecast/schedule?forecast_hours=12" -Method POST -ContentType "application/json"
    
    Write-Host "✅ Request successful! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "`nResponse preview:" -ForegroundColor Yellow
    $data = $response.Content | ConvertFrom-Json
    Write-Host "  Status: $($data.status)" -ForegroundColor White
    if ($data.data) {
        Write-Host "  Source: $($data.data.meta.source)" -ForegroundColor White
        Write-Host "  Schedule items: $($data.data.schedule.Count)" -ForegroundColor White
        Write-Host "  Forecast points: $($data.data.forecast_kW.Count)" -ForegroundColor White
        
        if ($data.data.meta.source -like "*mock*") {
            Write-Host "`n⚠️  WARNING: Using mock data!" -ForegroundColor Red
            Write-Host "   Check backend logs for errors" -ForegroundColor Yellow
        } else {
            Write-Host "`n✅ Using real forecast data!" -ForegroundColor Green
        }
    }
    
    Write-Host "`n📋 Check the backend PowerShell window for detailed logs" -ForegroundColor Cyan
    Write-Host "   Look for: 'Fetching forecast schedule for microgrid...'" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure the backend is running on port 8000" -ForegroundColor Yellow
}

