# Complete system startup script
Write-Host "=== MIRAKL-TIPSA SYSTEM STARTUP ===" -ForegroundColor Cyan

# Set run timestamp
$RUN_TS = Get-Date -Format "yyyyMMdd-HHmmss"
$env:RUN_TS = $RUN_TS
Write-Host "Run timestamp: $RUN_TS" -ForegroundColor Yellow

# Clean up previous containers
Write-Host "`n1. Cleaning up previous containers..." -ForegroundColor Yellow
docker compose down -v --remove-orphans

# Build and start services
Write-Host "`n2. Building and starting services..." -ForegroundColor Yellow
docker compose build --no-cache
docker compose up -d

# Wait for services to be ready
Write-Host "`n3. Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Verify system
Write-Host "`n4. Verifying system..." -ForegroundColor Yellow
.\scripts\check-all.ps1

Write-Host "`n=== SYSTEM STARTUP COMPLETE ===" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend: http://localhost:8080" -ForegroundColor White
Write-Host "Extension: extension/dist/" -ForegroundColor White
Write-Host "`nTo check system status: .\scripts\check-all.ps1" -ForegroundColor Cyan



