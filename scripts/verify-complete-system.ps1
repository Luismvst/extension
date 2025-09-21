# Script de verificación del sistema completo
Write-Host "🚀 VERIFICACIÓN DEL SISTEMA COMPLETO MIRAKL-TIPSA" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Verificar Docker
Write-Host "`n1. Verificando Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker está funcionando" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está disponible" -ForegroundColor Red
    exit 1
}

# Verificar servicios
Write-Host "`n2. Verificando servicios..." -ForegroundColor Yellow
$services = @("backend", "frontend", "tipsa-mock", "mirakl-mock")
foreach ($service in $services) {
    try {
        $status = docker compose ps --services --filter "status=running" | Select-String $service
        if ($status) {
            Write-Host "✅ $service está ejecutándose" -ForegroundColor Green
        } else {
            Write-Host "❌ $service no está ejecutándose" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error verificando $service" -ForegroundColor Red
    }
}

# Verificar endpoints del backend
Write-Host "`n3. Verificando endpoints del backend..." -ForegroundColor Yellow
$backendEndpoints = @(
    "http://localhost:8080/",
    "http://localhost:8080/docs",
    "http://localhost:8080/api/v1/carriers/health",
    "http://localhost:8080/api/v1/logs/stats"
)

foreach ($endpoint in $backendEndpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint -Method GET -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $endpoint - OK" -ForegroundColor Green
        } else {
            Write-Host "❌ $endpoint - Status: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ $endpoint - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Verificar mocks
Write-Host "`n4. Verificando servidores mock..." -ForegroundColor Yellow
$mockEndpoints = @(
    "http://localhost:3001/",
    "http://localhost:3002/"
)

foreach ($endpoint in $mockEndpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint -Method GET -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $endpoint - OK" -ForegroundColor Green
        } else {
            Write-Host "❌ $endpoint - Status: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ $endpoint - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Verificar frontend
Write-Host "`n5. Verificando frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/" -Method GET -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend está funcionando" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend - Status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend - Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Verificar extensión
Write-Host "`n6. Verificando extensión..." -ForegroundColor Yellow
if (Test-Path "extension/dist/manifest.json") {
    Write-Host "✅ Extensión construida en extension/dist/" -ForegroundColor Green
    
    # Verificar archivos de la extensión
    $extensionFiles = @("manifest.json", "background.js", "popup.html", "popup.js")
    foreach ($file in $extensionFiles) {
        if (Test-Path "extension/dist/$file") {
            Write-Host "  ✅ $file existe" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $file no existe" -ForegroundColor Red
        }
    }
} else {
    Write-Host "❌ Extensión no construida" -ForegroundColor Red
}

# Verificar logs
Write-Host "`n7. Verificando logs..." -ForegroundColor Yellow
if (Test-Path "backend/logs/operations.csv") {
    Write-Host "✅ Logs CSV generados" -ForegroundColor Green
    $logContent = Get-Content "backend/logs/operations.csv" | Measure-Object -Line
    Write-Host "  📊 Líneas en operations.csv: $($logContent.Lines)" -ForegroundColor Cyan
} else {
    Write-Host "❌ No se encontraron logs CSV" -ForegroundColor Red
}

# Test de integración
Write-Host "`n8. Ejecutando test de integración..." -ForegroundColor Yellow
try {
    # Test de login
    $loginData = @{
        email = "test@example.com"
        password = "test123"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/json" -TimeoutSec 10
    
    if ($loginResponse.StatusCode -eq 200) {
        Write-Host "✅ Login funciona correctamente" -ForegroundColor Green
        
        $token = ($loginResponse.Content | ConvertFrom-Json).access_token
        
        # Test de carriers health
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        
        $healthResponse = Invoke-WebRequest -Uri "http://localhost:8080/api/v1/carriers/health" -Method GET -Headers $headers -TimeoutSec 5
        
        if ($healthResponse.StatusCode -eq 200) {
            Write-Host "✅ API de carriers funciona correctamente" -ForegroundColor Green
        } else {
            Write-Host "❌ API de carriers - Status: $($healthResponse.StatusCode)" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Login falló - Status: $($loginResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Test de integración falló: $($_.Exception.Message)" -ForegroundColor Red
}

# Resumen final
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "📋 RESUMEN DE VERIFICACIÓN" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "`n🌐 URLs Disponibles:" -ForegroundColor Yellow
Write-Host "  • Backend API: http://localhost:8080" -ForegroundColor White
Write-Host "  • API Docs: http://localhost:8080/docs" -ForegroundColor White
Write-Host "  • Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  • TIPSA Mock: http://localhost:3001" -ForegroundColor White
Write-Host "  • Mirakl Mock: http://localhost:3002" -ForegroundColor White

Write-Host "`n📁 Archivos Importantes:" -ForegroundColor Yellow
Write-Host "  • Extensión: extension/dist/" -ForegroundColor White
Write-Host "  • Logs: backend/logs/" -ForegroundColor White
Write-Host "  • Documentación: AUDIT.md, MOCKS.md" -ForegroundColor White

Write-Host "`n🚀 Próximos Pasos:" -ForegroundColor Yellow
Write-Host "  1. Cargar extensión en Chrome desde extension/dist/" -ForegroundColor White
Write-Host "  2. Abrir frontend en http://localhost:3000" -ForegroundColor White
Write-Host "  3. Probar flujo completo con mocks" -ForegroundColor White
Write-Host "  4. Verificar logs en backend/logs/" -ForegroundColor White

Write-Host "`n✅ Verificación completada!" -ForegroundColor Green
