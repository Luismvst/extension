# Test simple del flujo de autenticación
Write-Host "=== TEST SIMPLE DEL FLUJO DE AUTENTICACIÓN ===" -ForegroundColor Cyan

# 1. Verificar backend
Write-Host "1. Verificando backend..." -ForegroundColor Yellow
try {
    $body = @{email="test@example.com"; password="test123"} | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "http://localhost:8080/auth/login" -Method POST -ContentType "application/json" -Body $body
    Write-Host "Backend OK: Token obtenido" -ForegroundColor Green
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
Write-Host "2. Abre la consola del navegador (F12)" -ForegroundColor White
Write-Host "3. Ve a la pestaña 'Console'" -ForegroundColor White
Write-Host "4. Recarga la página" -ForegroundColor White
Write-Host "5. Mira si hay errores en la consola" -ForegroundColor White
Write-Host "6. Si no hay errores, intenta hacer login:" -ForegroundColor White
Write-Host "   - Email: test@example.com" -ForegroundColor White
Write-Host "   - Password: test123" -ForegroundColor White
Write-Host "7. Si el login falla, mira los errores en la consola" -ForegroundColor White

