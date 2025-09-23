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
- `GET /api/v1/health` - Health check endpoint
- `GET /` - Root endpoint with basic info

### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `POST /auth/validate` - Validate JWT token

### Marketplaces
- `GET /api/v1/marketplaces/mirakl/orders` - Get orders from Mirakl
- `POST /api/v1/marketplaces/mirakl/orders` - Create order in Mirakl
- `PUT /api/v1/marketplaces/mirakl/orders/{order_id}` - Update order in Mirakl
- `POST /api/v1/marketplaces/mirakl/tracking` - Update tracking in Mirakl

### Carriers
- `GET /api/v1/carriers/tipsa/shipments` - Get shipments from TIPSA
- `POST /api/v1/carriers/tipsa/shipments` - Create shipment in TIPSA
- `GET /api/v1/carriers/tipsa/shipments/{shipment_id}` - Get specific shipment
- `POST /api/v1/carriers/tipsa/webhook` - TIPSA webhook endpoint

### Orchestrator (Main Workflow)
- `POST /api/v1/orchestrator/fetch-orders` - Fetch orders from Mirakl
- `POST /api/v1/orchestrator/post-to-carrier` - Post orders to carrier
- `POST /api/v1/orchestrator/push-tracking-to-mirakl` - Push tracking to Mirakl
- `GET /api/v1/orchestrator/orders-view` - Get orders view

### Logs & Exports
- `GET /api/v1/logs/operations` - Get operations logs
- `GET /api/v1/logs/orders-view` - Get orders view logs
- `GET /api/v1/logs/exports/operations.csv` - Export operations CSV
- `GET /api/v1/logs/exports/orders-view.csv` - Export orders view CSV
- `GET /api/v1/logs/stats` - Get logs statistics

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
  "password": "password123"
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

### POST /api/v1/carriers/tipsa/webhook
TIPSA webhook endpoint for tracking updates.

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
curl -X POST "http://localhost:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Fetch Orders
```bash
curl -X POST "http://localhost:8080/api/v1/orchestrator/fetch-orders" \
  -H "Authorization: Bearer <your-token>"
```

### Export CSV
```bash
curl -X GET "http://localhost:8080/api/v1/logs/exports/operations.csv" \
  -H "Authorization: Bearer <your-token>" \
  -o operations.csv
```
