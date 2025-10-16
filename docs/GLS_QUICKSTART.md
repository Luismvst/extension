# GLS ShipIT - Quick Start Guide

## 🚀 Inicio Rápido (5 minutos)

### 1. Configurar Variables de Entorno

Edita `backend/.env`:

```bash
# Para testing (sin conectar a GLS real)
GLS_BASE_URL=https://api-sandbox.gls-group.net/shipit-farm/v1/backend
GLS_USERNAME=test_user
GLS_PASSWORD=test_pass
GLS_CONTACT_ID=test_contact
GLS_MOCK_MODE=true

# Para producción
# GLS_MOCK_MODE=false
# GLS_BASE_URL=https://api.gls-group.net/shipit-farm/v1/backend
```

### 2. Iniciar el Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 3. Obtener Token JWT

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Guarda el token:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Ejecutar Flujo Completo Mirakl → GLS

```bash
# Obtener pedidos de Mirakl, crear envíos en GLS y actualizar Mirakl
curl -X POST "http://localhost:8000/api/v1/orchestrator/mirakl-to-gls?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Procesadas 5 órdenes de Mirakl; creados 5 envíos en GLS; 5 actualizaciones a Mirakl",
  "orders_processed": 5,
  "shipments_created": 5,
  "mirakl_updates": [...],
  "shipments": [...]
}
```

### 5. Iniciar Tracking Poller

```bash
# Inicia polling automático cada 5 minutos
curl -X POST "http://localhost:8000/api/v1/orchestrator/gls/tracking-poller/start" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Verificar Estado

```bash
# Estado del poller
curl "http://localhost:8000/api/v1/orchestrator/gls/tracking-poller/status" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🧪 Test Completo

Ejecuta el script de prueba:

```bash
cd backend
python test_gls_integration.py
```

**Output:**
```
✓ GLS Adapter inicializado (mock_mode: True)
✓ Mirakl Adapter inicializado (mock_mode: True)
✓ Obtenidos 5 pedidos de Mirakl
✓ Validación exitosa
✓ 5 envíos creados exitosamente
✓ Tracking actualizado en Mirakl
✓ Orden marcada como enviada (OR24)
✓ INTEGRACIÓN GLS COMPLETADA EXITOSAMENTE
```

---

## 📊 Verificar Resultados

### Logs

```bash
# Ver operaciones registradas
cat backend/logs/operations.csv

# Ver resultados del test
cat backend/logs/gls_test_results.json
```

### Unified Order Logger

```bash
# Ver todas las órdenes
cat backend/logs/orders_view.csv
```

---

## 🎯 Endpoints Principales

| Endpoint | Descripción |
|----------|-------------|
| `POST /orchestrator/mirakl-to-gls` | Flujo completo MVP |
| `POST /orchestrator/test-gls-direct` | Test directo GLS |
| `POST /orchestrator/gls/tracking-poller/start` | Iniciar poller |
| `GET /orchestrator/gls/tracking-poller/status` | Estado poller |
| `POST /orchestrator/gls/tracking-poller/poll-once` | Polling manual |

---

## 🔍 Troubleshooting

### "No orders found to process"
- Verifica que `MIRAKL_MOCK_MODE=true` en `.env`
- Verifica que el adapter de Mirakl tiene pedidos mock en estado SHIPPING

### "GLS timeout"
- Verifica conectividad con GLS API
- Verifica credenciales (username/password)
- Usa `GLS_MOCK_MODE=true` para testing sin conectar

### "Missing required fields"
- Verifica que los pedidos de Mirakl tienen todos los campos necesarios
- Ver `_transform_order_to_gls_request()` en `gls.py`

---

## 📚 Documentación Completa

- **Guía Completa:** `docs/GLS_INTEGRATION.md`
- **Resumen de Implementación:** `docs/GLS_IMPLEMENTATION_SUMMARY.md`
- **OpenAPI Spec:** `docs/gls-shipit-farm.yaml`

---

## ✅ Checklist de Verificación

- [ ] Variables de entorno configuradas
- [ ] Backend iniciado correctamente
- [ ] Token JWT obtenido
- [ ] Flujo Mirakl → GLS ejecutado exitosamente
- [ ] Tracking poller iniciado
- [ ] Script de test ejecutado sin errores
- [ ] Logs verificados

---

**¡Listo! La integración GLS está funcionando. 🎉**

Para más detalles, consulta `docs/GLS_INTEGRATION.md`

