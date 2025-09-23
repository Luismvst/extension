# Stop script for Mirakl-TIPSA system
Write-Host "🛑 Stopping Mirakl-TIPSA System..." -ForegroundColor Red

# Stop all services
docker compose down

Write-Host "✅ System stopped successfully!" -ForegroundColor Green

