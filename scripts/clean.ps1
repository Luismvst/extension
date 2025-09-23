# Clean script for Mirakl-TIPSA system
Write-Host "🧹 Cleaning Mirakl-TIPSA System..." -ForegroundColor Yellow

# Stop and remove containers, volumes, and networks
Write-Host "🛑 Stopping and removing containers..." -ForegroundColor Yellow
docker compose down -v --remove-orphans

# Clean up Docker system
Write-Host "🗑️ Cleaning Docker system..." -ForegroundColor Yellow
docker system prune -f

# Clean up old log files (keep last 10)
Write-Host "📝 Cleaning old log files (keeping last 10)..." -ForegroundColor Yellow
if (Test-Path "backend/logs") {
    $logFiles = Get-ChildItem "backend/logs/run-*.log" | Sort-Object LastWriteTime -Descending
    if ($logFiles.Count -gt 10) {
        $logFiles | Select-Object -Skip 10 | Remove-Item -Force
        Write-Host "✅ Old log files cleaned" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ No old log files to clean" -ForegroundColor Blue
    }
} else {
    Write-Host "ℹ️ No log directory found" -ForegroundColor Blue
}

# Clean up build artifacts
Write-Host "🔨 Cleaning build artifacts..." -ForegroundColor Yellow
if (Test-Path "frontend/dist") { Remove-Item -Recurse -Force "frontend/dist" }
if (Test-Path "extension/dist") { Remove-Item -Recurse -Force "extension/dist" }
if (Test-Path "extension/out") { Remove-Item -Recurse -Force "extension/out" }

Write-Host "✅ System cleaned successfully!" -ForegroundColor Green

