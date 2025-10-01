# Simple verification script
Write-Host "=== MIRAKL-TIPSA SYSTEM CHECK ===" -ForegroundColor Cyan

# Check services
Write-Host "`n1. Docker Services:" -ForegroundColor Yellow
docker compose ps

# Check Backend
Write-Host "`n2. Backend Health:" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/health" -UseBasicParsing
    Write-Host "Backend is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check Frontend
Write-Host "`n3. Frontend:" -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    Write-Host "Frontend responding: $($frontend.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Frontend error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check Extension
Write-Host "`n4. Extension:" -ForegroundColor Yellow
if (Test-Path "extension/dist/manifest.json") {
    Write-Host "Extension generated successfully" -ForegroundColor Green
    $files = Get-ChildItem extension/dist/
    Write-Host "Files: $($files.Count)" -ForegroundColor White
} else {
    Write-Host "Extension not found" -ForegroundColor Red
}

# Check Logs
Write-Host "`n5. Logs:" -ForegroundColor Yellow
if (Test-Path "backend/logs") {
    $logFiles = Get-ChildItem "backend/logs/run-*.log" -ErrorAction SilentlyContinue
    Write-Host "Log files: $($logFiles.Count)" -ForegroundColor Green
} else {
    Write-Host "No logs directory" -ForegroundColor Yellow
}

Write-Host "`n=== CHECK COMPLETE ===" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend: http://localhost:8080" -ForegroundColor White
Write-Host "Extension: extension/dist/" -ForegroundColor White







