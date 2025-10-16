# Guía de Testing - GLS ShipIT Integration

## 📋 Resumen

Esta guía te ayudará a probar la integración de GLS ShipIT paso a paso, tanto en modo mock como con el sandbox real de GLS.

---

## 🚀 Opción 1: Testing Rápido (Mock Mode)

Si solo quieres verificar que la integración funciona sin conectar a GLS:

### 1. Configurar `.env`

```bash
# En backend/.env
GLS_MOCK_MODE=true
GLS_BASE_URL=https://api-sandbox.gls-group.net/shipit-farm/v1/backend
GLS_CONTACT_ID=276002471
```

### 2. Ejecutar Test

```powershell
cd backend
python test_gls_standalone.py
```

**Resultado Esperado:**
```
[OK] TODOS LOS TESTS DISPONIBLES PASARON
  - Create Shipment (mock): ✓
  - Get Tracking (mock): ✓
```

---

## 🔐 Opción 2: Testing con GLS Sandbox (OAuth2)

Para probar con la API real de GLS en sandbox:

### Paso 1: Obtener Credenciales

**Contactar con GLS** para obtener:
- `client_id` (OAuth2)
- `client_secret` (OAuth2)
- `ContactID` (ID de tu cuenta de remitente)

### Paso 2: Configurar `.env`

```bash
# Copiar el archivo de ejemplo
cp backend/.env.gls-sandbox backend/.env

# Editar y añadir tus credenciales
GLS_CLIENT_ID=tu_client_id_aqui
GLS_CLIENT_SECRET=tu_client_secret_aqui
GLS_CONTACT_ID=tu_contact_id_aqui
GLS_MOCK_MODE=false
```

### Paso 3: Ejecutar Test

```powershell
cd backend
python test_gls_standalone.py
```

**Resultado Esperado:**
```
TEST STANDALONE DE GLS SHIPIT API
================================================================================

CONFIGURACIÓN:
  Base URL: https://api-sandbox.gls-group.net/shipit-farm/v1/backend
  Auth URL: https://api-sandbox.gls-group.net/oauth2/v2/token
  Client ID: abc123...
  Use OAuth: True
  Mock Mode: False

================================================================================
TEST 1: OAuth2 Token
================================================================================
✓ Token OAuth2 obtenido exitosamente
  Token (primeros 50 chars): eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
  Expira en: 2025-01-15 15:30:00

================================================================================
TEST 2: Validar Envío
================================================================================
✓ Envío válido
  Sin errores de validación

================================================================================
TEST 3: Servicios Permitidos
================================================================================
✓ Servicios permitidos obtenidos: 4
  - Producto: PARCEL
  - Producto: EXPRESS
  - Servicio: service_cash
  - Servicio: service_flexdelivery

...

[OK] TODOS LOS TESTS DISPONIBLES PASARON
```

---

## 🌐 Opción 3: Testing via API HTTP

### Paso 1: Iniciar el Servidor

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Paso 2: Obtener Token JWT

```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method Post `
  -Body '{"username":"admin","password":"admin"}' `
  -ContentType "application/json"

$token = $response.access_token
Write-Host "Token: $token"
```

### Paso 3: Probar Endpoint de GLS

**Test Directo:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/orchestrator/test-gls-direct" `
  -Method Post `
  -Headers @{Authorization="Bearer $token"} `
  | ConvertTo-Json -Depth 10
```

**Flujo Completo Mirakl → GLS:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/orchestrator/mirakl-to-gls?limit=3" `
  -Method Post `
  -Headers @{Authorization="Bearer $token"} `
  | ConvertTo-Json -Depth 10
```

**Respuesta Esperada:**
```json
{
  "success": true,
  "message": "Procesadas 3 órdenes de Mirakl; creados 3 envíos en GLS; 3 actualizaciones a Mirakl",
  "orders_processed": 3,
  "shipments_created": 3,
  "mirakl_updates": [
    {
      "order_id": "70268248-A",
      "tracking_number": "GLS1234567",
      "status": "updated"
    }
  ],
  "shipments": [
    {
      "shipment_id": "GLS1234567",
      "track_id": "GLS1234567",
      "status": "CREATED",
      "carrier": "gls",
      "label": {
        "format": "PDF",
        "bytes_b64": "JVBERi0xLjQK..."
      }
    }
  ]
}
```

---

## 🔍 Testing Manual con curl

### 1. Obtener Token OAuth2 de GLS

```bash
curl -X POST "https://api-sandbox.gls-group.net/oauth2/v2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=TU_CLIENT_ID" \
  -d "client_secret=TU_CLIENT_SECRET"
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 2. Validar Envío

```bash
curl -X POST "https://api-sandbox.gls-group.net/shipit-farm/v1/backend/rs/shipments/validate" \
  -H "Authorization: Bearer TU_TOKEN_OAUTH" \
  -H "Content-Type: application/glsVersion1+json" \
  -H "Accept: application/glsVersion1+json" \
  -d '{
    "Shipment": {
      "Product": "PARCEL",
      "Consignee": {
        "Address": {
          "Name1": "Juan Pérez",
          "CountryCode": "ES",
          "ZIPCode": "28001",
          "City": "Madrid",
          "Street": "Calle Test 123"
        }
      },
      "Shipper": {
        "ContactID": "276002471"
      },
      "ShipmentUnit": [
        {
          "Weight": 2.5
        }
      ]
    }
  }'
```

### 3. Crear Envío

```bash
curl -X POST "https://api-sandbox.gls-group.net/shipit-farm/v1/backend/rs/shipments" \
  -H "Authorization: Bearer TU_TOKEN_OAUTH" \
  -H "Content-Type: application/glsVersion1+json" \
  -d '{
    "Shipment": {
      "Product": "PARCEL",
      "Consignee": {
        "Address": {
          "Name1": "Juan Pérez",
          "CountryCode": "ES",
          "ZIPCode": "28001",
          "City": "Madrid",
          "Street": "Calle Test 123",
          "eMail": "test@example.com"
        }
      },
      "Shipper": {
        "ContactID": "276002471"
      },
      "ShipmentUnit": [
        {
          "Weight": 2.5
        }
      ]
    },
    "PrintingOptions": {
      "ReturnLabels": {
        "TemplateSet": "NONE",
        "LabelFormat": "PDF"
      }
    }
  }'
```

### 4. Consultar Tracking

```bash
curl -X POST "https://api-sandbox.gls-group.net/shipit-farm/v1/backend/rs/tracking/parceldetails" \
  -H "Authorization: Bearer TU_TOKEN_OAUTH" \
  -H "Content-Type: application/glsVersion1+json" \
  -d '{
    "TrackID": "GLS1234567"
  }'
```

---

## 📊 Verificar Resultados

### Logs

```powershell
# Ver operaciones registradas
Get-Content backend\logs\operations.csv -Tail 20

# Ver resultados del test
Get-Content backend\logs\gls_standalone_test_results.json | ConvertFrom-Json
```

### Base de Datos

```powershell
# Ver órdenes en unified logger
Get-Content backend\logs\orders_view.csv -Tail 10
```

---

## ❌ Troubleshooting

### Error: "Failed to obtain OAuth2 token"

**Causa:** Credenciales incorrectas o no configuradas.

**Solución:**
1. Verificar que `GLS_CLIENT_ID` y `GLS_CLIENT_SECRET` están en `.env`
2. Contactar con GLS para verificar credenciales
3. Verificar que usas el URL correcto de sandbox

### Error: "Missing required fields"

**Causa:** Datos incompletos en la solicitud.

**Solución:**
- Revisar que el pedido tiene todos los campos obligatorios:
  - `customer_name`
  - `weight`
  - `shipping_address.country`
  - `shipping_address.postal_code`
  - `shipping_address.city`
  - `shipping_address.address1`

### Error: "Invalid ContactID"

**Causa:** ContactID no válido o no pertenece a tu cuenta.

**Solución:**
- Verificar el ContactID con GLS
- Usar el ContactID que te proporcionaron en el onboarding

### Mock Mode no funciona

**Causa:** Configuración incorrecta.

**Solución:**
```bash
# En .env
GLS_MOCK_MODE=true
```

---

## 📚 Siguientes Pasos

Una vez que los tests pasen:

1. **Integrar con Mirakl Real**
   - Cambiar `MIRAKL_MOCK_MODE=false`
   - Configurar credenciales de Mirakl

2. **Probar Tracking Poller**
   ```powershell
   curl -X POST "http://localhost:8000/api/v1/orchestrator/gls/tracking-poller/start" \
     -H "Authorization: Bearer $token"
   ```

3. **Configurar Producción**
   - Cambiar URLs a producción
   - Usar credenciales de producción
   - Realizar pruebas exhaustivas

---

## 📞 Soporte

- **Documentación GLS:** https://shipit-download.gls-group.eu/documentation/
- **OpenAPI Spec:** `docs/gls-shipit-farm.yaml`
- **Guía Completa:** `docs/GLS_INTEGRATION.md`
- **Quick Start:** `docs/GLS_QUICKSTART.md`

---

**Última Actualización:** 2025-01-15  
**Versión:** 1.0 MVP

