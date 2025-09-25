# Script de pruebas para todos los endpoints de la API
# Este script contiene ejemplos pre-rellenados que se pueden ejecutar directamente

# Configuración
$baseUrl = "http://localhost:8080"
$token = ""

Write-Host "=== PRUEBAS DE ENDPOINTS DE LA API MIRAKL-TIPSA ORCHESTRATOR ===" -ForegroundColor Green
Write-Host ""

# Función para hacer requests con manejo de errores
function Invoke-APIRequest {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [string]$ContentType = "application/json"
    )
    
    try {
        $params = @{
            Uri = $Uri
            Method = $Method
            Headers = $Headers
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = $ContentType
        }
        
        $response = Invoke-WebRequest @params
        Write-Host "✅ $Method $Uri - Status: $($response.StatusCode)" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Host "❌ $Method $Uri - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# 1. HEALTH & STATUS ENDPOINTS
Write-Host "=== 1. HEALTH & STATUS ENDPOINTS ===" -ForegroundColor Yellow

Write-Host "`n1.1. Health Check"
Invoke-APIRequest -Uri "$baseUrl/api/v1/health"

Write-Host "`n1.2. Root Endpoint"
Invoke-APIRequest -Uri "$baseUrl/"

# 2. AUTHENTICATION ENDPOINTS
Write-Host "`n=== 2. AUTHENTICATION ENDPOINTS ===" -ForegroundColor Yellow

Write-Host "`n2.1. Login"
$loginBody = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$loginResponse = Invoke-APIRequest -Uri "$baseUrl/auth/login" -Method POST -Body $loginBody
if ($loginResponse) {
    $token = ($loginResponse.Content | ConvertFrom-Json).access_token
    Write-Host "Token obtenido: $($token.Substring(0, 20))..." -ForegroundColor Cyan
}

if ($token) {
    $authHeaders = @{"Authorization" = "Bearer $token"}
    
    Write-Host "`n2.2. Get Current User"
    Invoke-APIRequest -Uri "$baseUrl/auth/me" -Headers $authHeaders
    
    Write-Host "`n2.3. Validate Token"
    Invoke-APIRequest -Uri "$baseUrl/auth/validate" -Method POST -Headers $authHeaders
}

# 3. CARRIER ENDPOINTS
Write-Host "`n=== 3. CARRIER ENDPOINTS ===" -ForegroundColor Yellow

if ($token) {
    Write-Host "`n3.1. Carrier Health (TIPSA)"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/carriers/tipsa/health" -Headers $authHeaders
    
    Write-Host "`n3.2. All Carriers Health"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/carriers/health" -Headers $authHeaders
    
    Write-Host "`n3.3. Create Shipment"
    $shipmentBody = @{
        orders = @(
            @{
                order_id = "MIR-001"
                created_at = "2025-01-01T10:00:00"
                status = "PENDING"
                items = @(
                    @{
                        sku = "SKU001"
                        name = "Producto Test"
                        qty = 1
                        unit_price = 45.99
                    }
                )
                buyer = @{
                    name = "Juan Perez"
                    email = "juan@example.com"
                }
                shipping = @{
                    name = "Juan Perez"
                    address1 = "Calle Mayor 123"
                    city = "Madrid"
                    postcode = "28001"
                    country = "ES"
                }
                totals = @{
                    goods = 45.99
                    shipping = 0
                }
            }
        )
        carrier = "tipsa"
        service = "ESTANDAR"
    } | ConvertTo-Json -Depth 10
    
    $shipmentResponse = Invoke-APIRequest -Uri "$baseUrl/api/v1/carriers/tipsa/shipments" -Method POST -Headers $authHeaders -Body $shipmentBody
    
    if ($shipmentResponse) {
        $expeditionId = ($shipmentResponse.Content | ConvertFrom-Json).jobs[0].expedition_id
        Write-Host "Expedition ID obtenido: $expeditionId" -ForegroundColor Cyan
        
        Write-Host "`n3.4. Get Shipment Status"
        Invoke-APIRequest -Uri "$baseUrl/api/v1/carriers/tipsa/shipments/$expeditionId" -Headers $authHeaders
    }
}

# 4. WEBHOOK ENDPOINTS
Write-Host "`n=== 4. WEBHOOK ENDPOINTS ===" -ForegroundColor Yellow

Write-Host "`n4.1. TIPSA Webhook"
$webhookBody = @{
    event_type = "shipment_update"
    expedition_id = "TIPSA-MIR-0013852"
    tracking_number = "1Z-0013852"
    status = "IN_TRANSIT"
    timestamp = "2025-01-01T12:00:00Z"
    location = "Madrid, Spain"
    description = "Package in transit"
} | ConvertTo-Json

Invoke-APIRequest -Uri "$baseUrl/api/v1/carriers/webhooks/tipsa" -Method POST -Body $webhookBody

# 5. ORCHESTRATOR ENDPOINTS
Write-Host "`n=== 5. ORCHESTRATOR ENDPOINTS ===" -ForegroundColor Yellow

if ($token) {
    Write-Host "`n5.1. Fetch Orders from Mirakl"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/orchestrator/fetch-orders" -Method POST -Headers $authHeaders
    
    Write-Host "`n5.2. Post Orders to Carrier"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/orchestrator/post-to-carrier?carrier=tipsa" -Method POST -Headers $authHeaders
    
    Write-Host "`n5.3. Push Tracking to Mirakl"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/orchestrator/push-tracking-to-mirakl" -Method POST -Headers $authHeaders
    
    Write-Host "`n5.4. Get Orders View"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/orchestrator/orders-view" -Headers $authHeaders
}

# 6. LOGS & EXPORTS ENDPOINTS
Write-Host "`n=== 6. LOGS & EXPORTS ENDPOINTS ===" -ForegroundColor Yellow

if ($token) {
    Write-Host "`n6.1. Get Operations Logs"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/logs/operations" -Headers $authHeaders
    
    Write-Host "`n6.2. Get Orders View Logs"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/logs/orders-view" -Headers $authHeaders
    
    Write-Host "`n6.3. Export Operations CSV"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/logs/exports/operations.csv" -Headers $authHeaders
    
    Write-Host "`n6.4. Export Orders View CSV"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/logs/exports/orders-view.csv" -Headers $authHeaders
    
    Write-Host "`n6.5. Get Logs Statistics"
    Invoke-APIRequest -Uri "$baseUrl/api/v1/logs/stats" -Headers $authHeaders
}

Write-Host "`n=== PRUEBAS COMPLETADAS ===" -ForegroundColor Green
Write-Host "Todos los endpoints han sido probados. Revisa los resultados arriba." -ForegroundColor Cyan