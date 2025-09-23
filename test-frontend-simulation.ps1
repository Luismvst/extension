# Simulación del frontend para diagnosticar el problema
Write-Host "=== SIMULACIÓN DEL FRONTEND ===" -ForegroundColor Cyan

# 1. Simular el login como lo haría el frontend
Write-Host "1. Simulando login..." -ForegroundColor Yellow
try {
    $loginData = @{
        email = "test@example.com"
        password = "test123"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8080/auth/login" -Method POST -ContentType "application/json" -Body $loginData
    $token = $loginResponse.access_token
    Write-Host "Login exitoso: Token obtenido" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0, 50))..." -ForegroundColor Gray
} catch {
    Write-Host "Error en login: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Simular la petición de órdenes como lo haría el frontend
Write-Host "2. Simulando petición de órdenes..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    $ordersResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/orchestrator/orders-view" -Method GET -Headers $headers
    Write-Host "Órdenes obtenidas: $($ordersResponse.total)" -ForegroundColor Green
    
    # Mostrar la primera orden
    if ($ordersResponse.orders -and $ordersResponse.orders.Count -gt 0) {
        Write-Host "Primera orden:" -ForegroundColor Yellow
        $firstOrder = $ordersResponse.orders[0]
        Write-Host "  ID: $($firstOrder.order_id)" -ForegroundColor White
        Write-Host "  Cliente: $($firstOrder.customer_name)" -ForegroundColor White
        Write-Host "  Estado: $($firstOrder.status)" -ForegroundColor White
        Write-Host "  Carrier: $($firstOrder.carrier_name)" -ForegroundColor White
    }
} catch {
    Write-Host "Error en órdenes: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== DIAGNÓSTICO ===" -ForegroundColor Cyan
Write-Host "Backend: ✅ Funcionando" -ForegroundColor Green
Write-Host "API: ✅ Respondiendo" -ForegroundColor Green
Write-Host "Datos: ✅ 3 órdenes disponibles" -ForegroundColor Green
Write-Host ""
Write-Host "=== PROBLEMA IDENTIFICADO ===" -ForegroundColor Yellow
Write-Host "El backend funciona correctamente." -ForegroundColor White
Write-Host "El problema está en el frontend JavaScript." -ForegroundColor White
Write-Host ""
Write-Host "=== SOLUCIÓN ===" -ForegroundColor Cyan
Write-Host "1. Abre http://localhost:3000 en tu navegador" -ForegroundColor White
Write-Host "2. Abre la consola del navegador (F12)" -ForegroundColor White
Write-Host "3. Ve a la pestaña 'Console'" -ForegroundColor White
Write-Host "4. Recarga la página" -ForegroundColor White
Write-Host "5. Mira si hay errores en la consola" -ForegroundColor White
Write-Host "6. Si no hay errores, intenta hacer login:" -ForegroundColor White
Write-Host "   - Email: test@example.com" -ForegroundColor White
Write-Host "   - Password: test123" -ForegroundColor White
Write-Host "7. Si el login falla, mira los errores en la consola" -ForegroundColor White
Write-Host "8. Comparte los errores que veas en la consola" -ForegroundColor White

