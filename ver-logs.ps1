# Script para ver logs del sistema
Write-Host "=== VISOR DE LOGS DEL SISTEMA ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. LOGS DEL BACKEND (ultimas 20 lineas):" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
docker logs extension-backend-1 --tail=20

Write-Host ""
Write-Host "2. LOGS DEL FRONTEND (ultimas 10 lineas):" -ForegroundColor Yellow
Write-Host "------------------------------------------" -ForegroundColor Gray
docker logs extension-frontend-1 --tail=10

Write-Host ""
Write-Host "3. LOGS DE TIPSA MOCK (ultimas 10 lineas):" -ForegroundColor Yellow
Write-Host "--------------------------------------------" -ForegroundColor Gray
docker logs extension-tipsa-mock-1 --tail=10

Write-Host ""
Write-Host "4. LOGS DE MIRAKL MOCK (ultimas 10 lineas):" -ForegroundColor Yellow
Write-Host "---------------------------------------------" -ForegroundColor Gray
docker logs extension-mirakl-mock-1 --tail=10

Write-Host ""
Write-Host "5. ARCHIVO DE LOGS DEL BACKEND:" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Gray
if (Test-Path "backend/logs") {
    $logFiles = Get-ChildItem "backend/logs" -Filter "*.log" | Sort-Object LastWriteTime -Descending
    if ($logFiles.Count -gt 0) {
        Write-Host "Archivo mas reciente: $($logFiles[0].Name)" -ForegroundColor Green
        Write-Host "Tamaño: $([math]::Round($logFiles[0].Length / 1KB, 2)) KB" -ForegroundColor Green
        Write-Host "Ultima modificacion: $($logFiles[0].LastWriteTime)" -ForegroundColor Green
    } else {
        Write-Host "No hay archivos de log" -ForegroundColor Red
    }
} else {
    Write-Host "Directorio de logs no existe" -ForegroundColor Red
}

Write-Host ""
Write-Host "6. ARCHIVO CSV DE ORDENES:" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Gray
if (Test-Path "backend/logs/orders_view.csv") {
    $csvFile = Get-Item "backend/logs/orders_view.csv"
    Write-Host "Archivo: $($csvFile.Name)" -ForegroundColor Green
    Write-Host "Tamaño: $([math]::Round($csvFile.Length / 1KB, 2)) KB" -ForegroundColor Green
    Write-Host "Ultima modificacion: $($csvFile.LastWriteTime)" -ForegroundColor Green
    
    # Mostrar primeras 5 lineas del CSV
    Write-Host ""
    Write-Host "Primeras 5 lineas del CSV:" -ForegroundColor Cyan
    Get-Content "backend/logs/orders_view.csv" | Select-Object -First 5 | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
} else {
    Write-Host "Archivo CSV no existe" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== COMANDOS UTILES ===" -ForegroundColor Cyan
Write-Host "Ver logs en tiempo real del backend: docker logs -f extension-backend-1" -ForegroundColor White
Write-Host "Ver logs en tiempo real del frontend: docker logs -f extension-frontend-1" -ForegroundColor White
Write-Host "Ver archivo de log completo: Get-Content backend/logs/*.log" -ForegroundColor White
Write-Host "Ver CSV de ordenes: Get-Content backend/logs/orders_view.csv" -ForegroundColor White

