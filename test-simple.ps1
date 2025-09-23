# Test simple del sistema
Write-Host "=== TEST DEL SISTEMA MIRAKL-TIPSA ===" -ForegroundColor Cyan

# 1. Verificar servicios
Write-Host "1. Verificando servicios..." -ForegroundColor Yellow
docker compose ps

# 2. Test Backend
Write-Host "2. Testeando Backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/health" -UseBasicParsing
    Write-Host "Backend OK: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Test Login
Write-Host "3. Testeando Login..." -ForegroundColor Yellow
try {
    $body = @{email="test@example.com"; password="test123"} | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "http://localhost:8080/auth/login" -Method POST -ContentType "application/json" -Body $body
    Write-Host "Login OK: Token generado" -ForegroundColor Green
    $global:token = $login.access_token
} catch {
    Write-Host "Login Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Test Dashboard
Write-Host "4. Testeando Dashboard..." -ForegroundColor Yellow
try {
    $headers = @{Authorization="Bearer $global:token"}
    $orders = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/orchestrator/orders-view" -Headers $headers -UseBasicParsing
    Write-Host "Dashboard OK: $($orders.total) ordenes" -ForegroundColor Green
} catch {
    Write-Host "Dashboard Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Test Frontend
Write-Host "5. Testeando Frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    Write-Host "Frontend OK: Status $($frontend.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Frontend Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== RESUMEN ===" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Login: test@example.com / test123" -ForegroundColor Yellow
Write-Host "Extension: extension/dist/" -ForegroundColor Yellow

