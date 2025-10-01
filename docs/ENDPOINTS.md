# API Endpoints Documentation

This document provides comprehensive documentation for all available API endpoints in the Mirakl-TIPSA Orchestrator.

## Base URL
- Development: `http://localhost:8080`
- Production: `https://api.mirakl-tipsa.com`

## Authentication
Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints Overview

### Health & Status
- `GET /api/v1/health` - Health check endpoint ✅
- `GET /` - Root endpoint with basic info ✅

### Authentication
- `POST /auth/login` - User login ✅
- `GET /auth/me` - Get current user info ✅
- `POST /auth/validate` - Validate JWT token ✅

### Marketplaces
- `GET /api/v1/marketplaces/mirakl/orders` - Get orders from Mirakl ✅
- `POST /api/v1/marketplaces/mirakl/orders` - Create order in Mirakl ✅
- `PUT /api/v1/marketplaces/mirakl/orders/{order_id}` - Update order in Mirakl ✅
- `POST /api/v1/marketplaces/mirakl/tracking` - Update tracking in Mirakl ✅

### Carriers (Dynamic Routes)
- `POST /api/v1/carriers/{carrier}/shipments` - Create shipments for any carrier ✅
- `GET /api/v1/carriers/{carrier}/shipments/{expedition_id}` - Get shipment status ✅
- `POST /api/v1/carriers/webhooks/{carrier}` - Carrier webhook endpoint ✅
- `GET /api/v1/carriers/{carrier}/health` - Get carrier health status ✅
- `GET /api/v1/carriers/health` - Get all carriers health status ✅

**Available carriers**: `tipsa`, `ontime`, `seur`, `correosex`

**✅ Note**: The `/shipments` endpoint now works correctly with proper JSON format and ASCII characters.

**Important Requirements**:
- Use ASCII characters only (no special characters like "é", "ñ", "ü")
- Date format: ISO 8601 without "Z" (e.g., "2025-01-01T10:00:00")
- Status must be one of: PENDING, ACCEPTED, SHIPPED, DELIVERED, CANCELLED
- Totals must use `goods` and `shipping` fields, not `subtotal`, `tax`, `total`

**Example Request Body**:
```json
{
  "orders": [
    {
      "order_id": "MIR-001",
      "created_at": "2025-01-01T10:00:00",
      "status": "PENDING",
      "items": [
        {
          "sku": "SKU001",
          "name": "Producto Test",
          "qty": 1,
          "unit_price": 45.99
        }
      ],
      "buyer": {
        "name": "Juan Perez",
        "email": "juan@example.com"
      },
      "shipping": {
        "name": "Juan Perez",
        "address1": "Calle Mayor 123",
        "city": "Madrid",
        "postcode": "28001",
        "country": "ES"
      },
      "totals": {
        "goods": 45.99,
        "shipping": 0
      }
    }
  ],
  "carrier": "tipsa",
  "service": "ESTANDAR"
}
```

### Orchestrator (Main Workflow)
- `POST /api/v1/orchestrator/fetch-orders` - Fetch orders from Mirakl ✅
- `POST /api/v1/orchestrator/post-to-carrier` - Post orders to carrier ✅
- `POST /api/v1/orchestrator/push-tracking-to-mirakl` - Push tracking to Mirakl ✅
- `GET /api/v1/orchestrator/orders-view` - Get orders view ✅

### Logs & Exports
- `GET /api/v1/logs/operations` - Get operations logs ✅
- `GET /api/v1/logs/orders-view` - Get orders view logs ✅
- `GET /api/v1/logs/exports/operations.csv` - Export operations CSV ✅
- `GET /api/v1/logs/exports/orders-view.csv` - Export orders view CSV ✅
- `GET /api/v1/logs/stats` - Get logs statistics ✅

---

## Detailed Endpoint Documentation

### Health & Status

#### GET /api/v1/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.2.0",
  "timestamp": "2025-01-01T12:00:00Z",
  "services": {
    "mirakl": "connected",
    "tipsa": "connected",
    "database": "connected"
  }
}
```

#### GET /
Root endpoint with basic information.

**Response:**
```json
{
  "message": "Mirakl-TIPSA Orchestrator Backend",
  "version": "0.2.0",
  "status": "running",
  "docs": "/docs"
}
```

### Authentication

#### POST /auth/login
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "test123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "user123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin"
}
```

#### POST /auth/validate
Validate JWT token.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "valid": true,
  "user_id": "user123",
  "expires_at": "2025-01-01T13:00:00Z"
}
```

### Carriers (Dynamic Routes)

**Available carriers**: `tipsa`, `ontime`, `seur`, `correosex`

#### POST /api/v1/carriers/{carrier}/shipments
Create shipments for any carrier.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `carrier`: Carrier code (tipsa, ontime, seur, correosex)

**Request Body:**
```json
{
  "orders": [
    {
      "order_id": "MIR-001",
      "customer_name": "Juan Pérez",
      "customer_email": "juan@example.com",
      "shipping_address": {
        "street": "Calle Mayor 123",
        "city": "Madrid",
        "postal_code": "28001",
        "country": "ES"
      },
      "weight": 2.5,
      "total_amount": 45.99,
      "currency": "EUR"
    }
  ],
  "service": "ESTANDAR",
  "carrier": "tipsa"
}
```

**Response:**
```json
{
  "success": true,
  "carrier": "tipsa",
  "total_orders": 1,
  "successful_shipments": 1,
  "failed_shipments": 0,
  "jobs": [
    {
      "order_id": "MIR-001",
      "expedition_id": "TIPSA-MIR-001-12345",
      "status": "CREATED",
      "carrier": "tipsa",
      "created_at": "2025-01-15T10:00:00"
    }
  ]
}
```

#### GET /api/v1/carriers/{carrier}/shipments/{expedition_id}
Get shipment status for a specific expedition.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `carrier`: Carrier code
- `expedition_id`: Expedition identifier

**Response:**
```json
{
  "success": true,
  "expedition_id": "EXP001",
  "status": "IN_TRANSIT",
  "tracking_number": "TRK123456789",
  "carrier": "tipsa",
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z",
  "events": [
    {
      "timestamp": "2025-01-01T10:00:00Z",
      "status": "CREATED",
      "description": "Shipment created"
    },
    {
      "timestamp": "2025-01-01T12:00:00Z",
      "status": "IN_TRANSIT",
      "description": "Package in transit"
    }
  ]
}
```

#### POST /api/v1/carriers/webhooks/{carrier}
Receive webhook notifications from carriers.

**⚠️ Note:** This endpoint does NOT require authentication (webhooks come from external carriers).

**Path Parameters:**
- `carrier`: Carrier code

**Headers:**
- `Content-Type: application/json`
- `X-Webhook-Signature`: Webhook signature for verification

**Request Body:**
```json
{
  "expedition_id": "EXP001",
  "tracking_number": "TRK123456789",
  "status": "DELIVERED",
  "timestamp": "2025-01-01T14:00:00Z",
  "location": "Madrid, Spain",
  "description": "Package delivered successfully"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Webhook processed successfully",
  "expedition_id": "EXP001",
  "status_updated": true
}
```

#### GET /api/v1/carriers/{carrier}/health
Get health status for a specific carrier.

**Headers:** `Authorization: Bearer <token>`

**Path Parameters:**
- `carrier`: Carrier code

**Response:**
```json
{
  "carrier": "tipsa",
  "status": "healthy",
  "last_check": "2025-01-01T12:00:00Z",
  "api_available": true,
  "response_time_ms": 150,
  "version": "1.0.0"
}
```

#### GET /api/v1/carriers/health
Get health status for all carriers.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "overall_status": "healthy",
  "last_check": "2025-01-01T12:00:00Z",
  "carriers": {
    "tipsa": {
      "status": "healthy",
      "api_available": true,
      "response_time_ms": 150
    },
    "ontime": {
      "status": "healthy",
      "api_available": true,
      "response_time_ms": 200
    },
    "seur": {
      "status": "degraded",
      "api_available": false,
      "response_time_ms": null,
      "error": "API timeout"
    }
  }
}
```

### Orchestrator (Main Workflow)

#### POST /api/v1/orchestrator/fetch-orders
Fetch orders from Mirakl and save to unified CSV.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Fetched 5 orders from Mirakl",
  "orders_fetched": 5,
  "orders": [
    {
      "order_id": "MIR-001",
      "customer_name": "Juan Pérez",
      "customer_email": "juan@example.com",
      "total_amount": 45.99,
      "currency": "EUR",
      "status": "PENDING"
    }
  ]
}
```

#### POST /api/v1/orchestrator/post-to-carrier
Post pending orders to specified carrier.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "carrier": "tipsa"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully posted 3 orders to tipsa",
  "orders_processed": 3,
  "shipments_created": 3,
  "shipments": [
    {
      "order_id": "MIR-001",
      "expedition_id": "EXP-001",
      "tracking_number": "TRK123456789",
      "status": "CREATED",
      "label_url": "https://example.com/label.pdf"
    }
  ]
}
```

#### POST /api/v1/orchestrator/push-tracking-to-mirakl
Push tracking information to Mirakl.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Successfully updated 2 orders in Mirakl",
  "orders_updated": 2,
  "updated_orders": [
    {
      "order_id": "MIR-001",
      "tracking_number": "TRK123456789",
      "status": "SHIPPED"
    }
  ]
}
```

#### GET /api/v1/orchestrator/orders-view
Get orders view with filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `state` (optional): Filter by internal state (PENDING_POST, POSTED, AWAITING_TRACKING, TRACKED, MIRAKL_OK)
- `carrier` (optional): Filter by carrier code (tipsa, ontime, seur, correosex)
- `limit` (optional): Maximum number of orders (default: 100)
- `offset` (optional): Number of orders to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "orders": [
    {
      "order_id": "MIR-001",
      "marketplace": "mirakl",
      "buyer_name": "Juan Pérez",
      "buyer_email": "juan@example.com",
      "total_amount": 45.99,
      "currency": "EUR",
      "carrier_code": "tipsa",
      "carrier_name": "TIPSA",
      "tracking_number": "TRK123456789",
      "internal_state": "POSTED",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0,
  "has_more": false
}
```

### Logs & Exports

#### GET /api/v1/logs/operations
Get operations logs with filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `scope` (optional): Filter by scope (mirakl, carrier, orchestrator)
- `action` (optional): Filter by action (fetch_order, create_shipment, etc.)
- `status` (optional): Filter by status (OK, ERROR, WARNING)
- `limit` (optional): Maximum number of logs (default: 100)
- `offset` (optional): Number of logs to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "timestamp_iso": "2025-01-01T12:00:00Z",
      "scope": "mirakl",
      "action": "fetch_order",
      "order_id": "MIR-001",
      "carrier": "",
      "marketplace": "mirakl",
      "status": "OK",
      "message": "Order fetched successfully",
      "duration_ms": 150,
      "meta_json": "{\"order_data\": {...}}"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0,
  "has_more": false
}
```

#### GET /api/v1/logs/orders-view
Get orders view logs with filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `state` (optional): Filter by internal state
- `carrier` (optional): Filter by carrier code
- `limit` (optional): Maximum number of orders (default: 100)
- `offset` (optional): Number of orders to skip (default: 0)

**Response:**
```json
{
  "success": true,
  "orders": [
    {
      "order_id": "MIR-001",
      "marketplace": "mirakl",
      "buyer_name": "Juan Pérez",
      "buyer_email": "juan@example.com",
      "total_amount": 45.99,
      "currency": "EUR",
      "carrier_code": "tipsa",
      "carrier_name": "TIPSA",
      "tracking_number": "TRK123456789",
      "internal_state": "POSTED",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0,
  "has_more": false
}
```

#### GET /api/v1/logs/exports/operations.csv
Export operations logs as CSV file.

**Headers:** `Authorization: Bearer <token>`

**Response:** CSV file download
```
timestamp_iso,scope,action,order_id,carrier,marketplace,status,message,duration_ms,meta_json
2025-01-01T12:00:00Z,mirakl,fetch_order,MIR-001,,mirakl,OK,Order fetched successfully,150,"{""order_data"":{...}}"
```

#### GET /api/v1/logs/exports/orders-view.csv
Export orders view as CSV file.

**Headers:** `Authorization: Bearer <token>`

**Response:** CSV file download
```
order_id,marketplace,buyer_email,buyer_name,total_amount,currency,carrier_code,carrier_name,tracking_number,internal_state,created_at,updated_at,...
MIR-001,mirakl,juan@example.com,Juan Pérez,45.99,EUR,tipsa,TIPSA,TRK123456789,POSTED,2025-01-01T10:00:00Z,2025-01-01T12:00:00Z,...
```

#### GET /api/v1/logs/stats
Get logs statistics and metrics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "stats": {
    "operations": {
      "total_logs": 150,
      "success_rate": 95.5,
      "error_rate": 4.5,
      "operations_count": {
        "fetch_order": 50,
        "create_shipment": 45,
        "update_tracking": 30,
        "webhook_received": 25
      }
    },
    "orders": {
      "total_orders": 75,
      "by_state": {
        "PENDING_POST": 10,
        "POSTED": 25,
        "AWAITING_TRACKING": 20,
        "TRACKED": 15,
        "MIRAKL_OK": 5
      },
      "by_carrier": {
        "tipsa": 40,
        "ontime": 20,
        "seur": 10,
        "correosex": 5
      }
    },
    "files": {
      "operations_csv_size": 1024000,
      "orders_view_csv_size": 512000,
      "json_dumps_count": 25
    }
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Unsupported carrier: invalid_carrier"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Order not found"
}
```

### 422 Validation Error
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "loc": ["body", "carrier"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

- **Authentication endpoints**: 10 requests per minute
- **Orchestrator endpoints**: 100 requests per minute
- **Logs endpoints**: 50 requests per minute
- **Export endpoints**: 10 requests per minute

---

## CORS Configuration

The API supports CORS for the following origins:
- `http://localhost:3000` (Frontend development)
- `https://dashboard.mirakl-tipsa.com` (Frontend production)
- `chrome-extension://*` (Chrome extension)

---

## Webhook Endpoints

### POST /api/v1/carriers/webhooks/{carrier}
Carrier webhook endpoint for tracking updates from any carrier (TIPSA, OnTime, SEUR, Correos Express).

**Request Body:**
```json
{
  "expedition_id": "EXP-001",
  "tracking_number": "TRK123456789",
  "status": "IN_TRANSIT",
  "timestamp": "2025-01-01T12:00:00Z",
  "location": "Madrid, Spain",
  "description": "Package in transit"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Webhook processed successfully",
  "order_id": "MIR-001",
  "updated": true
}
```

---

## Testing

### Health Check
```bash
curl -X GET "http://localhost:8080/api/v1/health"
```

### Authentication
```bash
# Login
curl -X POST "http://localhost:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Get current user (replace <token> with actual token)
curl -X GET "http://localhost:8080/auth/me" \
  -H "Authorization: Bearer <token>"

# Validate token
curl -X POST "http://localhost:8080/auth/validate" \
  -H "Authorization: Bearer <token>"
```

### Carrier Operations
```bash
# Create shipment
curl -X POST "http://localhost:8080/api/v1/carriers/tipsa/shipments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "orders": [{
      "order_id": "MIR-001",
      "created_at": "2025-01-01T10:00:00",
      "status": "PENDING",
      "items": [{
        "sku": "SKU001",
        "name": "Producto Test",
        "qty": 1,
        "unit_price": 45.99
      }],
      "buyer": {
        "name": "Juan Perez",
        "email": "juan@example.com"
      },
      "shipping": {
        "name": "Juan Perez",
        "address1": "Calle Mayor 123",
        "city": "Madrid",
        "postcode": "28001",
        "country": "ES"
      },
      "totals": {
        "goods": 45.99,
        "shipping": 0
      }
    }],
    "carrier": "tipsa",
    "service": "ESTANDAR"
  }'

# Get shipment status (replace <expedition_id> with actual ID)
curl -X GET "http://localhost:8080/api/v1/carriers/tipsa/shipments/<expedition_id>" \
  -H "Authorization: Bearer <token>"

# Carrier health
curl -X GET "http://localhost:8080/api/v1/carriers/tipsa/health" \
  -H "Authorization: Bearer <token>"
```

### Webhook Testing
```bash
# TIPSA webhook (with signature validation)
curl -X POST "http://localhost:8080/api/v1/carriers/webhooks/tipsa" \
  -H "Content-Type: application/json" \
  -H "X-Signature: generated_hmac_signature" \
  -H "X-Timestamp: 2025-01-01T12:00:00Z" \
  -d '{
    "event_type": "shipment_update",
    "expedition_id": "TIPSA-MIR-0013852",
    "tracking_number": "1Z-0013852",
    "status": "IN_TRANSIT",
    "timestamp": "2025-01-01T12:00:00Z",
    "location": "Madrid, Spain",
    "description": "Package in transit"
  }'

# OnTime webhook
curl -X POST "http://localhost:8080/api/v1/carriers/webhooks/ontime" \
  -H "Content-Type: application/json" \
  -H "X-Signature: generated_hmac_signature" \
  -H "X-Timestamp: 2025-01-01T12:00:00Z" \
  -d '{
    "event_type": "shipment_update",
    "expedition_id": "ONTIME-MIR-001-12345",
    "status": "DELIVERED"
  }'
```

### Orchestrator Operations
```bash
# Fetch orders from Mirakl
curl -X POST "http://localhost:8080/api/v1/orchestrator/fetch-orders" \
  -H "Authorization: Bearer <token>"

# Post orders to carrier
curl -X POST "http://localhost:8080/api/v1/orchestrator/post-to-carrier?carrier=tipsa" \
  -H "Authorization: Bearer <token>"

# Push tracking to Mirakl
curl -X POST "http://localhost:8080/api/v1/orchestrator/push-tracking-to-mirakl" \
  -H "Authorization: Bearer <token>"

# Get orders view
curl -X GET "http://localhost:8080/api/v1/orchestrator/orders-view" \
  -H "Authorization: Bearer <token>"
```

### Logs & Exports
```bash
# Get operations logs
curl -X GET "http://localhost:8080/api/v1/logs/operations" \
  -H "Authorization: Bearer <token>"

# Get orders view logs
curl -X GET "http://localhost:8080/api/v1/logs/orders-view" \
  -H "Authorization: Bearer <token>"

# Export operations CSV
curl -X GET "http://localhost:8080/api/v1/logs/exports/operations.csv" \
  -H "Authorization: Bearer <token>" \
  -o operations.csv

# Export orders view CSV
curl -X GET "http://localhost:8080/api/v1/logs/exports/orders-view.csv" \
  -H "Authorization: Bearer <token>" \
  -o orders_view.csv

# Get logs statistics
curl -X GET "http://localhost:8080/api/v1/logs/stats" \
  -H "Authorization: Bearer <token>"
```

### PowerShell Script (Windows)
Para Windows, también puedes usar el script de PowerShell incluido:
```powershell
# Ejecutar el script completo de pruebas
.\test_endpoints.ps1
```

Este script contiene todos los ejemplos pre-rellenados y se puede ejecutar directamente para probar todos los endpoints.
