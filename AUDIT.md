# AUDIT.md - Auditoría del Repositorio Mirakl-TIPSA Orchestrator

## Estado Actual del Repositorio

### 1. Arquitectura General
- **Backend**: FastAPI con estructura modular (adapters, rules, core)
- **Frontend**: Chrome Extension MV3 con Vite/React/TypeScript
- **Docker**: Multi-container con docker-compose
- **Logging**: CSV + JSON dumps en `/app/logs`

### 2. Flujo Actual de Datos

#### GET Mirakl (OR12)
- **Ubicación**: `backend/app/adapters/marketplaces/mirakl.py`
- **Método**: `get_orders(status, limit, offset)`
- **Mock**: Implementado con datos de prueba
- **Real**: Configurado para `https://marketplace.mirakl.net`

#### POST TIPSA
- **Ubicación**: `backend/app/adapters/carriers/tipsa.py`
- **Método**: `create_shipment()` y `create_shipments_bulk()`
- **Mock**: Implementado con respuestas simuladas
- **Real**: Configurado para `https://api.tipsa.com`

#### Update Tracking (OR23/OR24)
- **Ubicación**: `backend/app/adapters/marketplaces/mirakl.py`
- **Métodos**: `update_order_tracking()` y `update_order_status()`
- **OR23**: PUT `/api/orders/{order_id}/tracking`
- **OR24**: PUT `/api/orders/{order_id}/ship` (no implementado aún)

#### Validación de Envío
- **Ubicación**: `backend/app/rules/selector.py`
- **Método**: `select_carrier()` - selecciona transportista basado en reglas
- **Carriers**: TIPSA, OnTime, DHL, UPS (todos en mock)

### 3. Generación de Logs

#### CSV Logs
- **Ubicación**: `backend/app/core/logging.py` - clase `CSVLogger`
- **Archivo**: `/app/logs/operations.csv`
- **Columnas**: timestamp, operation, order_id, status, details, duration_ms
- **Volumen**: Mapeado en Docker como `./backend/logs:/app/logs`

#### JSON Dumps
- **Ubicación**: `backend/app/core/logging.py` - clase `JSONDumper`
- **Directorio**: `/app/logs/dumps/`
- **Formato**: `{operation}_{order_id}_{timestamp}.json`
- **Contenido**: request/response completos

### 4. Extensión Chrome

#### Overlay 3 Botones
- **Ubicación**: `extension/src/popup/App.tsx`
- **Botones**: "Cargar Pedidos", "Crear Envíos", "Subir Tracking"
- **Rutas Backend**:
  - `POST /api/v1/orchestrator/load-orders`
  - `POST /api/v1/orchestrator/upload-tracking`
  - `GET /api/v1/orchestrator/status`

#### Problemas Identificados
- **require('fs')**: Encontrado en `check-types.js`, `create-icons.cjs`, `fix-paths.cjs` (scripts de build, no afecta MV3)
- **No hay require('fs') en frontend**: ✅ Correcto para MV3

### 5. Configuración Docker

#### Puertos
- **Backend**: 8080:8080
- **Extension**: Solo build, no runtime

#### Volúmenes
- **Logs**: `./backend/logs:/app/logs` ✅
- **Extension**: `./extension/dist:/app/dist` ✅

#### Variables de Entorno
- **MIRAKL_MODE**: mock
- **TIPSA_MODE**: mock
- **LOG_DIR**: /app/logs

### 6. Problemas Identificados

#### Faltantes Críticos
1. **OR24 (Ship)**: No implementado en Mirakl adapter
2. **ST23 (Shipments Tracking)**: No implementado
3. **Webhooks**: No implementados para carriers
4. **HMAC Validation**: No implementado
5. **Dashboard Web**: No existe
6. **Auth JWT**: Básico, no implementado completamente
7. **Mocks TIPSA/Mirakl**: No hay servidores mock independientes

#### Mejoras Necesarias
1. **Idempotencia**: No implementada en carriers
2. **Retry Logic**: No implementado
3. **Rate Limiting**: No implementado
4. **Error Handling**: Básico
5. **Monitoring**: No implementado

### 7. Estructura de Archivos

```
backend/
├── app/
│   ├── adapters/
│   │   ├── carriers/
│   │   │   ├── tipsa.py ✅
│   │   │   ├── ontime.py ✅ (mock)
│   │   │   ├── dhl.py ✅ (mock)
│   │   │   └── ups.py ✅ (mock)
│   │   └── marketplaces/
│   │       └── mirakl.py ✅ (parcial)
│   ├── api/
│   │   ├── orchestrator.py ✅
│   │   ├── marketplaces.py ✅
│   │   ├── carriers.py ✅
│   │   ├── health.py ✅
│   │   └── auth.py ✅ (básico)
│   ├── core/
│   │   ├── settings.py ✅
│   │   ├── logging.py ✅
│   │   └── auth.py ✅ (básico)
│   └── rules/
│       ├── engine.py ✅
│       └── selector.py ✅
├── logs/ ✅ (mapeado en Docker)
└── requirements.txt ✅

extension/
├── src/
│   ├── popup/ ✅
│   ├── background/ ✅
│   ├── content/ ✅
│   └── options/ ✅
├── dist/ ✅ (generado)
└── package.json ✅
```

### 8. Próximos Pasos

1. **Implementar OR24 y ST23** en Mirakl adapter
2. **Crear servidores mock** TIPSA (3001) y Mirakl (3002)
3. **Implementar webhooks** con HMAC validation
4. **Crear dashboard web** con Vite+React+MUI
5. **Completar auth JWT** con guards
6. **Implementar idempotencia** en carriers
7. **Añadir retry logic** y rate limiting
8. **Crear tests** unitarios y E2E

### 9. Comandos de Verificación

```bash
# Ver logs del backend
docker compose logs -f backend

# Ver CSVs generados
docker compose exec backend ls -lah /app/logs

# Ver JSON dumps
docker compose exec backend ls -lah /app/logs/dumps

# Verificar extensión
ls -la extension/dist/
```

### 10. Conclusión

El repositorio tiene una base sólida pero necesita completar:
- APIs de Mirakl (OR24, ST23)
- Webhooks seguros
- Dashboard web
- Mocks independientes
- Tests completos

La arquitectura es correcta y extensible. Los logs están bien implementados y mapeados correctamente en Docker.
