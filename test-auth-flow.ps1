# Test completo del flujo de autenticación
Write-Host "=== TEST COMPLETO DEL FLUJO DE AUTENTICACIÓN ===" -ForegroundColor Cyan

# 1. Verificar que el backend esté funcionando
Write-Host "1. Verificando backend..." -ForegroundColor Yellow
try {
    $body = @{email="test@example.com"; password="test123"} | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "http://localhost:8080/auth/login" -Method POST -ContentType "application/json" -Body $body
    $token = $login.access_token
    Write-Host "Backend OK: Token obtenido" -ForegroundColor Green
} catch {
    Write-Host "Backend Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Verificar que el frontend esté sirviendo el HTML
Write-Host "2. Verificando frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    Write-Host "Frontend OK: Status $($frontend.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Frontend Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. Verificar que el endpoint de órdenes funcione con el token
Write-Host "3. Verificando endpoint de órdenes..." -ForegroundColor Yellow
try {
    $headers = @{Authorization="Bearer $token"}
    $orders = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/orchestrator/orders-view" -Headers $headers -UseBasicParsing
    Write-Host "Órdenes OK: $($orders.total) ordenes encontradas" -ForegroundColor Green
} catch {
    Write-Host "Órdenes Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== DIAGNÓSTICO ===" -ForegroundColor Cyan
Write-Host "Backend: ✅ Funcionando" -ForegroundColor Green
Write-Host "Frontend: ✅ Sirviendo HTML" -ForegroundColor Green
Write-Host "API: ✅ Respondiendo" -ForegroundColor Green
Write-Host ""
Write-Host "=== INSTRUCCIONES PARA DEBUGGING ===" -ForegroundColor Cyan
Write-Host "1. Abre http://localhost:3000 en tu navegador" -ForegroundColor White
Write-Host "2. Abre la consola del navegador (F12)" -ForegroundColor White
Write-Host "3. Ve a la pestaña 'Console'" -ForegroundColor White
Write-Host "4. Recarga la página" -ForegroundColor White
Write-Host "5. Mira si hay errores en la consola" -ForegroundColor White
Write-Host "6. Si no hay errores, intenta hacer login:" -ForegroundColor White
Write-Host "   - Email: test@example.com" -ForegroundColor White
Write-Host "   - Password: test123" -ForegroundColor White
Write-Host "7. Si el login falla, mira los errores en la consola" -ForegroundColor White
Write-Host ""
Write-Host "=== POSIBLES PROBLEMAS ===" -ForegroundColor Yellow
Write-Host "- CORS: El frontend no puede hacer peticiones al backend" -ForegroundColor White
Write-Host "- API URL: El frontend está usando la URL incorrecta" -ForegroundColor White
Write-Host "- Token: El token no se está guardando en localStorage" -ForegroundColor White
Write-Host "- Redirección: El router no está funcionando correctamente" -ForegroundColor White

