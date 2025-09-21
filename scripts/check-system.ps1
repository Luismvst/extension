# Check system status
Write-Host "Checking Mirakl-TIPSA System..." -ForegroundColor Cyan

# Check Backend
Write-Host "`n1. Backend (port 8080)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/health" -UseBasicParsing
    Write-Host "OK - Backend running" -ForegroundColor Green
} catch {
    Write-Host "ERROR - Backend not responding" -ForegroundColor Red
}

# Check Frontend
Write-Host "`n2. Frontend (port 3000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    Write-Host "OK - Frontend running" -ForegroundColor Green
} catch {
    Write-Host "ERROR - Frontend not responding" -ForegroundColor Red
}

# Check TIPSA Mock
Write-Host "`n3. TIPSA Mock (port 3001)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/docs" -UseBasicParsing
    Write-Host "OK - TIPSA Mock running" -ForegroundColor Green
} catch {
    Write-Host "ERROR - TIPSA Mock not responding" -ForegroundColor Red
}

# Check Mirakl Mock
Write-Host "`n4. Mirakl Mock (port 3002)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3002/docs" -UseBasicParsing
    Write-Host "OK - Mirakl Mock running" -ForegroundColor Green
} catch {
    Write-Host "ERROR - Mirakl Mock not responding" -ForegroundColor Red
}

# Check Extension
Write-Host "`n5. Extension..." -ForegroundColor Yellow
if (Test-Path "extension/dist/manifest.json") {
    Write-Host "OK - Extension generated" -ForegroundColor Green
} else {
    Write-Host "ERROR - Extension not generated" -ForegroundColor Red
}

Write-Host "`nSystem Status:" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8080" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "TIPSA Mock: http://localhost:3001" -ForegroundColor White
Write-Host "Mirakl Mock: http://localhost:3002" -ForegroundColor White
Write-Host "Extension: extension/dist/" -ForegroundColor White
