# Start script for Mirakl-TIPSA system
Write-Host "🚀 Starting Mirakl-TIPSA System..." -ForegroundColor Cyan

# Set run timestamp
$RUN_TS = Get-Date -Format "yyyyMMdd-HHmmss"
$env:RUN_TS = $RUN_TS
Write-Host "RUN_TS=$RUN_TS" -ForegroundColor Yellow

# Clean up previous containers
Write-Host "🧹 Cleaning up previous containers..." -ForegroundColor Yellow
docker compose down -v --remove-orphans

# Build and start services
Write-Host "🔨 Building and starting services..." -ForegroundColor Yellow
docker compose build --no-cache
docker compose up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show service status
Write-Host "📊 Service status:" -ForegroundColor Green
docker compose ps

# Show backend logs
Write-Host "📋 Backend logs (last 20 lines):" -ForegroundColor Green
docker compose logs --tail=20 backend

Write-Host "✅ System started successfully!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "🔧 Backend API: http://localhost:8080" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8080/docs" -ForegroundColor White
Write-Host "📝 Logs: Get-Content backend/logs/run-*.log -Wait" -ForegroundColor White

