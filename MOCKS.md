# MOCKS.md - Documentación de Servidores Mock

## Servidores Mock Disponibles

### TIPSA Mock (Puerto 3001)

**URL Base**: `http://localhost:3001`

#### Endpoints

- `GET /` - Información del API
- `POST /api/shipments` - Crear envíos (batch)
- `GET /api/shipments/{expedition_id}` - Estado del envío
- `POST /webhook` - Recibir webhooks (para testing)
- `GET /api/shipments` - Listar todos los envíos (debug)

#### Ejemplo de Uso

```bash
# Crear envío
curl -X POST http://localhost:3001/api/shipments \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-123" \
  -d '[
    {
      "order_id": "MIR-001",
      "weight": 2.5,
      "value": 45.99,
      "currency": "EUR",
      "recipient": {
        "name": "Juan Pérez",
        "email": "juan@email.com",
        "address": {
          "street": "Calle Mayor 123",
          "city": "Madrid",
          "postal_code": "28001",
          "country": "ES"
        }
      },
      "service": "STANDARD"
    }
  ]'

# Ver estado del envío
curl http://localhost:3001/api/shipments/TIPSA-MIR0011234
```

#### Simulación de Webhooks

El mock TIPSA simula automáticamente webhooks después de crear envíos:

1. **LABELED** - 2 segundos después de crear
2. **IN_TRANSIT** - 30 minutos después
3. **OUT_FOR_DELIVERY** - 60 minutos después  
4. **DELIVERED** - 90 minutos después

### Mirakl Mock (Puerto 3002)

**URL Base**: `http://localhost:3002`

#### Endpoints

- `GET /` - Información del API
- `GET /api/orders` - Obtener pedidos (OR12)
- `PUT /api/orders/{order_id}/tracking` - Actualizar tracking (OR23)
- `PUT /api/orders/{order_id}/ship` - Marcar como enviado (OR24)
- `POST /api/shipments/tracking` - Tracking batch (ST23)
- `GET /api/orders/{order_id}` - Detalles del pedido
- `GET /api/orders/{order_id}/status` - Estado del pedido

#### Ejemplo de Uso

```bash
# Obtener pedidos
curl "http://localhost:3002/api/orders?status=PENDING&limit=10"

# Actualizar tracking (OR23)
curl -X PUT http://localhost:3002/api/orders/MIR-001/tracking \
  -H "Content-Type: application/json" \
  -d '{
    "carrier_code": "tipsa",
    "carrier_name": "TIPSA",
    "tracking_number": "1Z123456789"
  }'

# Marcar como enviado (OR24)
curl -X PUT http://localhost:3002/api/orders/MIR-001/ship \
  -H "Content-Type: application/json" \
  -d '{
    "carrier_code": "tipsa",
    "carrier_name": "TIPSA", 
    "tracking_number": "1Z123456789",
    "shipped_at": "2025-09-21T12:00:00Z"
  }'
```

## Configuración de Respuestas Mock

### TIPSA Mock

Para cambiar respuestas, editar `mocks/tipsa-mock.py`:

```python
# Cambiar costos
"cost": 15.50 + (shipment.weight * 2.0)  # Línea 89

# Cambiar tiempos de entrega
"estimated_delivery": (datetime.utcnow() + timedelta(days=2)).isoformat()  # Línea 90

# Cambiar progresión de estados
if elapsed_minutes > 10 and status_index < 1:  # Línea 120
```

### Mirakl Mock

Para cambiar respuestas, editar `mocks/mirakl-mock.py`:

```python
# Cambiar pedidos mock
mock_orders = [  # Línea 45
    {
        "order_id": "MIR-001",
        "status": "PENDING",
        # ... más campos
    }
]

# Cambiar respuestas de tracking
return {  # Línea 95
    "order_id": order_id,
    "status": "success",
    # ... más campos
}
```

## Ejecutar Mocks

### Opción 1: Docker Compose

```bash
# Levantar todos los servicios incluyendo mocks
docker compose up -d

# Ver logs de mocks
docker compose logs -f tipsa-mock
docker compose logs -f mirakl-mock
```

### Opción 2: Ejecución Directa

```bash
# Instalar dependencias
cd mocks
pip install -r requirements.txt

# Ejecutar ambos mocks
python run-mocks.py

# O ejecutar individualmente
python tipsa-mock.py    # Puerto 3001
python mirakl-mock.py   # Puerto 3002
```

## Testing de Webhooks

### Enviar Webhook Manual a TIPSA

```bash
curl -X POST http://localhost:3001/webhook \
  -H "Content-Type: application/json" \
  -H "X-Signature: $(echo -n '{"event_type":"LABELED","expedition_id":"TIPSA-123"}' | openssl dgst -sha256 -hmac 'tipsa_webhook_secret_2025' -binary | base64)" \
  -H "X-Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -d '{
    "event_id": "evt_123",
    "event_type": "LABELED",
    "expedition_id": "TIPSA-123",
    "status": "LABELED",
    "tracking_number": "1Z123456789",
    "label_url": "https://mock.tipsa.com/labels/TIPSA-123",
    "timestamp": "2025-09-21T12:00:00Z"
  }'
```

### Verificar Webhooks en Backend

```bash
# Ver logs del backend
docker compose logs -f backend | grep webhook

# Verificar procesamiento
curl http://localhost:8080/api/v1/logs/operations | jq '.logs[] | select(.operation | contains("webhook"))'
```

## Debugging

### Ver Estado de Mocks

```bash
# TIPSA - Listar envíos
curl http://localhost:3001/api/shipments

# Mirakl - Listar pedidos  
curl http://localhost:3002/api/orders
```

### Logs Detallados

```bash
# Ver logs de mocks con debug
docker compose logs -f tipsa-mock mirakl-mock

# Ver logs del backend
docker compose logs -f backend
```

## Notas Importantes

1. **Idempotencia**: TIPSA mock respeta `Idempotency-Key` header
2. **Webhooks**: Se envían automáticamente después de crear envíos
3. **Estados**: Los estados progresan automáticamente basado en tiempo
4. **Persistencia**: Los datos se mantienen en memoria (se pierden al reiniciar)
5. **CORS**: Ambos mocks tienen CORS habilitado para desarrollo
