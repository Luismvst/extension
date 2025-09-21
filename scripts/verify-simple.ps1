# Script de verificación simple del sistema
Write-Host "🔍 VERIFICANDO SISTEMA MIRAKL-TIPSA" -ForegroundColor Cyan

# Verificar Backend
Write-Host "`n1. Backend (puerto 8080)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/health" -UseBasicParsing
    Write-Host "✅ Backend: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend: Error" -ForegroundColor Red
}

# Verificar Frontend
Write-Host "`n2. Frontend (puerto 3000)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    Write-Host "✅ Frontend: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend: Error" -ForegroundColor Red
}

# Verificar TIPSA Mock
Write-Host "`n3. TIPSA Mock (puerto 3001)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/docs" -UseBasicParsing
    Write-Host "✅ TIPSA Mock: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ TIPSA Mock: Error" -ForegroundColor Red
}

# Verificar Mirakl Mock
Write-Host "`n4. Mirakl Mock (puerto 3002)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3002/docs" -UseBasicParsing
    Write-Host "✅ Mirakl Mock: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Mirakl Mock: Error" -ForegroundColor Red
}

# Verificar Extensión
Write-Host "`n5. Extensión..." -ForegroundColor Yellow
if (Test-Path "extension/dist/manifest.json") {
    Write-Host "✅ Extensión: Generada correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ Extensión: No generada" -ForegroundColor Red
}

Write-Host "`n🎉 SISTEMA LISTO" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8080" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "TIPSA Mock: http://localhost:3001" -ForegroundColor White
Write-Host "Mirakl Mock: http://localhost:3002" -ForegroundColor White
Write-Host "Extensión: extension/dist/" -ForegroundColor White
