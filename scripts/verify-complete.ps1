# Complete verification script for Mirakl-TIPSA system
Write-Host "=== MIRAKL-TIPSA SYSTEM VERIFICATION ===" -ForegroundColor Cyan

# Check Docker services
Write-Host "`n1. Checking Docker services..." -ForegroundColor Yellow
$services = docker compose ps --format "table {{.Name}}\t{{.Status}}"
Write-Host $services

# Check Backend Health
Write-Host "`n2. Checking Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/health" -UseBasicParsing
    Write-Host "✅ Backend is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check Frontend
Write-Host "`n3. Checking Frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    if ($frontend.StatusCode -eq 200) {
        Write-Host "✅ Frontend is responding (Status: $($frontend.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Frontend status: $($frontend.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Frontend not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Check TIPSA Mock
Write-Host "`n4. Checking TIPSA Mock..." -ForegroundColor Yellow
try {
    $tipsa = Invoke-WebRequest -Uri "http://localhost:3001/docs" -UseBasicParsing
    Write-Host "✅ TIPSA Mock is responding (Status: $($tipsa.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⚠️ TIPSA Mock not responding: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Check Mirakl Mock
Write-Host "`n5. Checking Mirakl Mock..." -ForegroundColor Yellow
try {
    $mirakl = Invoke-WebRequest -Uri "http://localhost:3002/docs" -UseBasicParsing
    Write-Host "✅ Mirakl Mock is responding (Status: $($mirakl.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Mirakl Mock not responding: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Check Extension
Write-Host "`n6. Checking Extension..." -ForegroundColor Yellow
if (Test-Path "extension/dist/manifest.json") {
    $manifest = Get-Content "extension/dist/manifest.json" | ConvertFrom-Json
    Write-Host "✅ Extension generated (Version: $($manifest.version))" -ForegroundColor Green
    Write-Host "   Files: $(Get-ChildItem extension/dist/ | Measure-Object).Count files" -ForegroundColor White
} else {
    Write-Host "❌ Extension not generated" -ForegroundColor Red
}

# Check Logs
Write-Host "`n7. Checking Logs..." -ForegroundColor Yellow
if (Test-Path "backend/logs") {
    $logFiles = Get-ChildItem "backend/logs/run-*.log" -ErrorAction SilentlyContinue
    if ($logFiles) {
        Write-Host "Log files found: $($logFiles.Count)" -ForegroundColor Green
        $latestLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        Write-Host "   Latest: $($latestLog.Name) ($(Get-Date $latestLog.LastWriteTime -Format 'HH:mm:ss'))" -ForegroundColor White
    } else {
        Write-Host "No log files found" -ForegroundColor Yellow
    }
} else {
    Write-Host "Log directory not found" -ForegroundColor Yellow
}

# Check Orders CSV
Write-Host "`n8. Checking Orders CSV..." -ForegroundColor Yellow
if (Test-Path "backend/logs/orders_view.csv") {
    $csvLines = (Get-Content "backend/logs/orders_view.csv" | Measure-Object -Line).Lines
    Write-Host "✅ Orders CSV exists ($csvLines lines)" -ForegroundColor Green
} else {
    Write-Host "ℹ️ Orders CSV not found (will be created on first use)" -ForegroundColor Blue
}

# Test Login
Write-Host "`n9. Testing Login..." -ForegroundColor Yellow
try {
    $loginBody = @{email="test@example.com"; password="test123"} | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "http://localhost:8080/auth/login" -Method POST -ContentType "application/json" -Body $loginBody
    if ($login.access_token) {
        Write-Host "✅ Login successful (Token length: $($login.access_token.Length))" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Login response unexpected" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== VERIFICATION COMPLETE ===" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "🔧 Backend: http://localhost:8080" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8080/docs" -ForegroundColor White
Write-Host "📦 Extension: extension/dist/" -ForegroundColor White
