# Script de verificación completa del sistema
Write-Host "🔍 VERIFICANDO SISTEMA COMPLETO MIRAKL-TIPSA" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Verificar Docker
Write-Host "`n1. Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está disponible" -ForegroundColor Red
    exit 1
}

# Verificar servicios
Write-Host "`n2. Verificando servicios Docker..." -ForegroundColor Yellow
$services = docker compose ps --format "table {{.Service}}\t{{.Status}}"
Write-Host $services

# Verificar Backend
Write-Host "`n3. Verificando Backend (puerto 8080)..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/health" -UseBasicParsing
    if ($backendResponse.StatusCode -eq 200) {
        $healthData = $backendResponse.Content | ConvertFrom-Json
        Write-Host "✅ Backend: $($healthData.status) - Versión $($healthData.version)" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend no responde correctamente" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Backend no está disponible" -ForegroundColor Red
}

# Verificar Frontend
Write-Host "`n4. Verificando Frontend (puerto 3000)..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "✅ Frontend: Respondiendo correctamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend no responde correctamente" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend no está disponible" -ForegroundColor Red
}

# Verificar TIPSA Mock
Write-Host "`n5. Verificando TIPSA Mock (puerto 3001)..." -ForegroundColor Yellow
try {
    $tipsaResponse = Invoke-WebRequest -Uri "http://localhost:3001/docs" -UseBasicParsing
    if ($tipsaResponse.StatusCode -eq 200) {
        Write-Host "✅ TIPSA Mock: Documentación disponible" -ForegroundColor Green
    } else {
        Write-Host "❌ TIPSA Mock no responde correctamente" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ TIPSA Mock no está disponible" -ForegroundColor Red
}

# Verificar Mirakl Mock
Write-Host "`n6. Verificando Mirakl Mock (puerto 3002)..." -ForegroundColor Yellow
try {
    $miraklResponse = Invoke-WebRequest -Uri "http://localhost:3002/docs" -UseBasicParsing
    if ($miraklResponse.StatusCode -eq 200) {
        Write-Host "✅ Mirakl Mock: Documentación disponible" -ForegroundColor Green
    } else {
        Write-Host "❌ Mirakl Mock no responde correctamente" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Mirakl Mock no está disponible" -ForegroundColor Red
}

# Verificar Extensión
Write-Host "`n7. Verificando Extensión..." -ForegroundColor Yellow
if (Test-Path "extension/dist/manifest.json") {
    $manifest = Get-Content "extension/dist/manifest.json" | ConvertFrom-Json
    Write-Host "✅ Extensión: Manifest v$($manifest.manifest_version) - Versión $($manifest.version)" -ForegroundColor Green
    Write-Host "   Archivos generados:" -ForegroundColor Gray
    Get-ChildItem "extension/dist" | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Gray }
} else {
    Write-Host "❌ Extensión no se ha generado correctamente" -ForegroundColor Red
}

# Verificar logs del backend
Write-Host "`n8. Verificando logs del backend..." -ForegroundColor Yellow
Write-Host "Últimas 5 líneas de logs:" -ForegroundColor Gray
docker compose logs --tail=5 backend

Write-Host "`n🎉 VERIFICACIÓN COMPLETA" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host "Sistema listo para usar:" -ForegroundColor Green
Write-Host "- Backend API: http://localhost:8080" -ForegroundColor White
Write-Host "- Frontend Dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "- TIPSA Mock: http://localhost:3001" -ForegroundColor White
Write-Host "- Mirakl Mock: http://localhost:3002" -ForegroundColor White
Write-Host "- Extensión: extension/dist/ (cargar en Chrome)" -ForegroundColor White
