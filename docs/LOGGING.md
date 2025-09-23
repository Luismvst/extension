# Logging System Documentation

This document describes the comprehensive logging system implemented in the Mirakl-TIPSA Orchestrator.

## Overview

The logging system consists of two main components:
1. **Operations CSV Logger** - Tracks all operations and API calls
2. **Unified Order Logger** - Maintains the "truth table" of order states

## Operations CSV Logger

### Location
- File: `backend/logs/operations.csv`
- Path: `backend/app/utils/csv_ops_logger.py`

### Headers
The operations CSV uses standardized headers:
```
timestamp_iso,scope,action,order_id,carrier,marketplace,status,message,duration_ms,meta_json
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp_iso` | ISO 8601 UTC | Operation timestamp | `2025-01-01T12:00:00Z` |
| `scope` | String | Operation scope | `mirakl`, `carrier`, `orchestrator` |
| `action` | String | Action performed | `fetch_order`, `create_shipment` |
| `order_id` | String | Order identifier | `MIR-001` |
| `carrier` | String | Carrier name | `tipsa`, `ontime`, `seur` |
| `marketplace` | String | Marketplace name | `mirakl` |
| `status` | String | Operation status | `OK`, `ERROR`, `WARNING` |
| `message` | String | Additional message | `Order fetched successfully` |
| `duration_ms` | Integer | Operation duration | `150` |
| `meta_json` | JSON | Additional metadata | `{"order_data": {...}}` |

### Usage Example

```python
from app.utils.csv_ops_logger import csv_ops_logger

# Log a successful operation
await csv_ops_logger.log(
    scope="mirakl",
    action="fetch_order",
    order_id="MIR-001",
    marketplace="mirakl",
    status="OK",
    message="Order fetched successfully",
    duration_ms=150,
    meta={"order_data": order_data}
)

# Log an error
await csv_ops_logger.log(
    scope="carrier",
    action="create_shipment",
    order_id="MIR-002",
    carrier="tipsa",
    status="ERROR",
    message="Failed to create shipment",
    meta={"error": "Invalid address"}
)
```

## Unified Order Logger

### Location
- File: `backend/logs/orders_view.csv`
- Path: `backend/app/core/unified_order_logger.py`

### Headers
The orders view CSV contains comprehensive order information:
```
order_id,marketplace,buyer_email,buyer_name,total_amount,currency,shipping_address,
carrier_code,carrier_name,tracking_number,label_url,internal_state,created_at,updated_at,
error_message,retry_count,mirakl_tracking_updated,mirakl_ship_updated,reference,
consignee_name,consignee_address,consignee_city,consignee_postal_code,consignee_country,
consignee_contact,consignee_phone,packages,weight_kg,volume,shipping_cost,product_type,
cod_amount,delayed_date,observations,destination_email,package_type,client_department,
return_conform,order_date,consignee_nif,client_name,return_flag,client_code,multi_reference
```

### Field Descriptions

#### Core Order Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `order_id` | String | Unique order identifier | `MIR-001` |
| `marketplace` | String | Source marketplace | `mirakl` |
| `buyer_email` | String | Customer email | `customer@example.com` |
| `buyer_name` | String | Customer name | `Juan Pérez` |
| `total_amount` | Decimal | Order total amount | `45.99` |
| `currency` | String | Currency code | `EUR` |
| `shipping_address` | JSON | Shipping address | `{"street": "Calle Test 123"}` |

#### Carrier Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `carrier_code` | String | Carrier identifier | `tipsa` |
| `carrier_name` | String | Carrier display name | `TIPSA` |
| `tracking_number` | String | Tracking number | `TRK123456789` |
| `label_url` | String | Shipping label URL | `https://example.com/label.pdf` |

#### State Tracking Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `internal_state` | String | Current order state | `PENDING_POST`, `POSTED`, `TRACKED` |
| `created_at` | ISO 8601 | Order creation timestamp | `2025-01-01T10:00:00Z` |
| `updated_at` | ISO 8601 | Last update timestamp | `2025-01-01T12:00:00Z` |
| `error_message` | String | Error details if any | `Invalid address format` |
| `retry_count` | Integer | Number of retry attempts | `2` |

#### Detailed Shipping Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `reference` | String | Order reference | `MIR-001` |
| `consignee_name` | String | Recipient name | `Juan Pérez` |
| `consignee_address` | JSON | Recipient address | `{"street": "Calle Test 123"}` |
| `consignee_city` | String | Recipient city | `Madrid` |
| `consignee_postal_code` | String | Postal code | `28001` |
| `consignee_country` | String | Country code | `ES` |
| `consignee_contact` | String | Contact person | `Juan Pérez` |
| `consignee_phone` | String | Phone number | `+34612345678` |
| `packages` | Integer | Number of packages | `1` |
| `weight_kg` | Decimal | Package weight | `1.5` |
| `volume` | Decimal | Package volume | `0.001` |
| `shipping_cost` | Decimal | Shipping cost | `5.99` |
| `product_type` | String | Product type | `electronics` |
| `cod_amount` | Decimal | Cash on delivery amount | `0.00` |
| `delayed_date` | Date | Delayed delivery date | `2025-01-05` |
| `observations` | String | Special instructions | `Handle with care` |
| `destination_email` | String | Delivery email | `customer@example.com` |
| `package_type` | String | Package type | `box` |
| `client_department` | String | Client department | `sales` |
| `return_conform` | Boolean | Return confirmation | `true` |
| `order_date` | Date | Order date | `2025-01-01` |
| `consignee_nif` | String | Tax ID | `12345678A` |
| `client_name` | String | Client name | `Company ABC` |
| `return_flag` | Boolean | Return flag | `false` |
| `client_code` | String | Client code | `CLI001` |
| `multi_reference` | String | Multi-reference | `REF-001-002` |

### Usage Example

```python
from app.core.unified_order_logger import unified_order_logger

# Create/update an order
unified_order_logger.upsert_order("MIR-001", {
    'marketplace': 'mirakl',
    'buyer_email': 'customer@example.com',
    'buyer_name': 'Juan Pérez',
    'total_amount': 45.99,
    'currency': 'EUR',
    'internal_state': 'PENDING_POST',
    'reference': 'MIR-001',
    'consignee_name': 'Juan Pérez',
    'consignee_address': '{"street": "Calle Test 123", "city": "Madrid"}',
    'weight_kg': 1.5,
    'order_date': '2025-01-01',
    'client_name': 'Juan Pérez',
    'destination_email': 'customer@example.com'
})

# Get an order
order = unified_order_logger.get_order("MIR-001")

# Get orders by state
pending_orders = unified_order_logger.get_orders_by_state('PENDING_POST')

# Get all orders
all_orders = unified_order_logger.get_all_orders()
```

## Order State Flow

The order states follow this progression:

1. **PENDING_POST** - Order fetched from Mirakl, ready to be sent to carrier
2. **POSTED** - Order successfully sent to carrier
3. **AWAITING_TRACKING** - Waiting for tracking information from carrier
4. **TRACKED** - Tracking information received from carrier
5. **MIRAKL_OK** - Tracking information successfully pushed to Mirakl

### Error States
- **FAILED_FETCH** - Failed to fetch order from Mirakl
- **FAILED_POST** - Failed to post order to carrier
- **FAILED_TRACKING** - Failed to receive tracking from carrier
- **FAILED_PUSH** - Failed to push tracking to Mirakl

## Integration Points

### Mirakl Operations
- `fetch_order` - When fetching orders from Mirakl
- `update_tracking` - When updating tracking in Mirakl

### Carrier Operations
- `create_shipment` - When creating shipment with carrier
- `webhook_received` - When receiving webhook from carrier

### Orchestrator Operations
- `fetch_orders_from_mirakl` - Overall fetch operation
- `post_to_carrier` - Overall post operation
- `push_tracking_to_mirakl` - Overall push operation

## Data Integrity Guarantees

### Atomic Writes
- All CSV writes are atomic using file locks
- Headers are written only once when file is created
- Concurrent access is handled safely

### Idempotency
- Operations can be safely retried
- Duplicate operations are logged but don't cause corruption
- State transitions are idempotent

### Error Handling
- Failed operations are logged with ERROR status
- Retry counts are tracked
- Error messages are preserved for debugging

## Export and Analysis

### CSV Export
```bash
# Export operations CSV
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/exports/operations.csv" \
  -o operations.csv

# Export orders view CSV
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/exports/orders-view.csv" \
  -o orders_view.csv
```

### Statistics
```bash
# Get logging statistics
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/stats"
```

### Filtering
```bash
# Get operations by scope
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/operations?scope=mirakl"

# Get orders by state
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/orders-view?state=POSTED"
```

## Monitoring and Alerts

### Key Metrics
- Operations success rate
- Order processing time
- Error frequency by operation type
- Carrier performance metrics

### Alert Conditions
- Success rate below 95%
- Processing time above 5 minutes
- More than 10 errors in 1 hour
- Carrier webhook failures

## Troubleshooting

### Common Issues

#### CSV File Not Found
- Check file permissions
- Ensure log directory exists
- Verify environment variables

#### Concurrent Access Errors
- Check for file locks
- Ensure single instance running
- Check disk space

#### Data Corruption
- Verify CSV headers
- Check for incomplete writes
- Restore from backup if needed

### Debug Commands
```bash
# Check CSV file integrity
head -5 backend/logs/operations.csv
head -5 backend/logs/orders_view.csv

# Count operations
wc -l backend/logs/operations.csv

# Check recent operations
tail -10 backend/logs/operations.csv

# Verify JSON in meta_json field
jq '.' backend/logs/operations.csv | head -20
```

## Performance Considerations

### File Size Management
- Operations CSV grows continuously
- Orders CSV grows with order volume
- Consider log rotation for production

### Query Performance
- Use filters to limit data retrieval
- Index frequently queried fields
- Consider database migration for large volumes

### Memory Usage
- CSV operations are memory-efficient
- Large exports may require streaming
- Monitor memory usage during bulk operations
