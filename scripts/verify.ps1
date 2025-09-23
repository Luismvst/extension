# Verify script for Mirakl-TIPSA system
Write-Host "🔍 Verifying Mirakl-TIPSA System..." -ForegroundColor Cyan

# Check backend health
Write-Host "1. Checking backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/health" -UseBasicParsing
    if ($response.status -eq "healthy") {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend is not healthy" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Backend is not responding" -ForegroundColor Red
    exit 1
}

# Check frontend
Write-Host "2. Checking frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is responding" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Frontend status != 200 (check manually)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Frontend not responding" -ForegroundColor Yellow
}

# Check TIPSA mock
Write-Host "3. Checking TIPSA mock..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/docs" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ TIPSA mock is responding" -ForegroundColor Green
    } else {
        Write-Host "⚠️ TIPSA mock not responding" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ TIPSA mock not responding" -ForegroundColor Yellow
}

# Check Mirakl mock
Write-Host "4. Checking Mirakl mock..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3002/docs" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Mirakl mock is responding" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Mirakl mock not responding" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Mirakl mock not responding" -ForegroundColor Yellow
}

# Check log files
Write-Host "5. Checking log files..." -ForegroundColor Yellow
if (Test-Path "backend/logs") {
    $logFiles = Get-ChildItem "backend/logs/run-*.log" -ErrorAction SilentlyContinue
    if ($logFiles) {
        Write-Host "✅ Found $($logFiles.Count) log file(s)" -ForegroundColor Green
        Write-Host "📋 Latest log file:" -ForegroundColor Blue
        $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Format-Table Name, Length, LastWriteTime
    } else {
        Write-Host "⚠️ No log files found" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Log directory not found" -ForegroundColor Yellow
}

# Check orders CSV
Write-Host "6. Checking orders CSV..." -ForegroundColor Yellow
if (Test-Path "backend/logs/orders_view.csv") {
    Write-Host "✅ Orders CSV exists" -ForegroundColor Green
    Write-Host "📊 CSV info:" -ForegroundColor Blue
    $lineCount = (Get-Content "backend/logs/orders_view.csv" | Measure-Object -Line).Lines
    Write-Host "Lines: $lineCount" -ForegroundColor White
} else {
    Write-Host "ℹ️ Orders CSV not found (will be created on first use)" -ForegroundColor Blue
}

Write-Host ""
Write-Host "🎉 System verification completed!" -ForegroundColor Green
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "🔧 Backend: http://localhost:8080" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8080/docs" -ForegroundColor White

