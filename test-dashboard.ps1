# Test del dashboard para verificar que las ordenes se muestran
Write-Host "=== TEST DEL DASHBOARD ===" -ForegroundColor Cyan

# 1. Verificar backend
Write-Host "1. Verificando backend..." -ForegroundColor Yellow
try {
    $body = @{email="test@example.com"; password="test123"} | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "http://localhost:8080/auth/login" -Method POST -ContentType "application/json" -Body $body
    $token = $login.access_token
    $headers = @{Authorization="Bearer $token"}
    $orders = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/orchestrator/orders-view" -Headers $headers -UseBasicParsing
    Write-Host "Backend OK: $($orders.total) ordenes" -ForegroundColor Green
} catch {
    Write-Host "Backend Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Verificar frontend
Write-Host "2. Verificando frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    Write-Host "Frontend OK: Status $($frontend.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Frontend Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== INSTRUCCIONES ===" -ForegroundColor Cyan
Write-Host "1. Abre http://localhost:3000 en tu navegador" -ForegroundColor White
Write-Host "2. Haz login con test@example.com / test123" -ForegroundColor White
Write-Host "3. Deberias ver 3 ordenes en el dashboard:" -ForegroundColor White
Write-Host "   - MIR-001: Juan Perez (TIPSA - SHIPPED)" -ForegroundColor White
Write-Host "   - MIR-002: Maria Garcia (SEUR - IN_TRANSIT)" -ForegroundColor White
Write-Host "   - MIR-003: Carlos Lopez (OnTime - DELIVERED)" -ForegroundColor White
Write-Host ""
Write-Host "Si no ves las ordenes, revisa la consola del navegador (F12)" -ForegroundColor Yellow

