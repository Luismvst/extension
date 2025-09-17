# Mirakl CSV Backend

FastAPI backend for the Mirakl CSV Extension, providing TIPSA mapping and carrier integration services.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- pip or poetry

### Installation

1. **Clone and install dependencies**
```bash
git clone https://github.com/Luismvst/extension.git
cd extension/backend
pip install -e .
```

2. **Set environment variables**
```bash
cp ../env.example .env
# Edit .env with your configuration
```

3. **Run the server**
```bash
uvicorn app.main:app --reload --port 8080
```

### Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Lint code
black .
isort .
flake8 .
mypy app/

# Run server
uvicorn app.main:app --reload
```

## 📁 Project Structure

```
app/
├── api/                # API routers
│   ├── health.py      # Health check endpoints
│   ├── map_router.py  # Mapping endpoints
│   ├── ship_router.py # Shipping endpoints
│   └── tracking_router.py # Tracking endpoints
├── core/              # Core configuration
│   ├── settings.py    # Application settings
│   └── logging.py     # Logging configuration
├── models/            # Pydantic models
│   └── order.py       # Order and related models
├── services/          # Business logic
│   └── tipsa.py       # TIPSA mapping service
└── main.py           # FastAPI application
```

## 🔧 Configuration

Environment variables:

```bash
# Application
APP_NAME=Mirakl CSV Backend
VERSION=0.1.0
ENVIRONMENT=development
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8080

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","chrome-extension://*"]

# External APIs (future)
TIPSATOKEN=
ONTIMETOKEN=
MIRAKLTOKEN=
```

## 📚 API Documentation

### Health Endpoints

- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system information
- `GET /api/v1/health/ready` - Readiness check
- `GET /api/v1/health/live` - Liveness check

### Mapping Endpoints

- `POST /api/v1/map/tipsa` - Map orders to TIPSA format
- `POST /api/v1/map/tipsa/csv` - Get TIPSA CSV file
- `POST /api/v1/map/tipsa/validate` - Validate orders for TIPSA
- `GET /api/v1/map/tipsa/schema` - Get TIPSA CSV schema

### Shipping Endpoints

- `POST /api/v1/ship/tipsa` - Create TIPSA shipment (stub)
- `POST /api/v1/ship/ontime` - Create OnTime shipment (stub)
- `GET /api/v1/ship/tipsa/{job_id}/status` - Get shipment status
- `GET /api/v1/ship/carriers` - List available carriers

### Tracking Endpoints

- `POST /api/v1/tracking/mirakl` - Update Mirakl tracking (stub)
- `GET /api/v1/tracking/mirakl/{order_id}` - Get tracking info
- `POST /api/v1/tracking/bulk` - Bulk tracking update
- `GET /api/v1/tracking/statuses` - Available statuses

## 🧪 Testing

### Unit Tests
```bash
pytest
```

### Tests with Coverage
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Test Structure
```
tests/
├── unit/              # Unit tests
│   ├── test_models.py
│   └── test_tipsa_mapping.py
└── conftest.py        # Test configuration
```

## 🐳 Docker

### Build Image
```bash
docker build -f docker/backend.Dockerfile -t mirakl-backend .
```

### Run Container
```bash
docker run -p 8080:8080 mirakl-backend
```

### Docker Compose
```bash
docker-compose -f docker/docker-compose.yml up backend
```

## 📊 Monitoring

### Health Checks

The application provides comprehensive health checks:

- **Basic**: Application status and version
- **Detailed**: System resources and configuration
- **Readiness**: Service availability for load balancers
- **Liveness**: Container orchestration health

### Logging

Structured JSON logging with configurable levels:

```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "level": "INFO",
  "message": "Order mapped successfully",
  "order_id": "ORD-001",
  "marketplace": "carrefour",
  "duration_ms": 150
}
```

### Metrics

Key metrics tracked:

- Request count and duration
- Error rates by endpoint
- Order processing statistics
- System resource usage

## 🔒 Security

### Input Validation

All inputs validated with Pydantic models:

- Order data validation
- CSV format validation
- API parameter validation
- File upload validation

### Error Handling

Comprehensive error handling:

- Validation errors (400)
- Authentication errors (401)
- Authorization errors (403)
- Not found errors (404)
- Server errors (500)

### CORS Configuration

Configurable CORS for different environments:

- Development: All origins allowed
- Production: Restricted to known domains
- Extension: Chrome extension origins

## 🚀 Deployment

### Environment Setup

1. **Production Environment**
```bash
export ENVIRONMENT=production
export LOG_LEVEL=WARNING
export ALLOWED_ORIGINS=["https://yourdomain.com"]
```

2. **Database Setup** (future)
```bash
# PostgreSQL setup
createdb mirakl_csv
python -m alembic upgrade head
```

3. **External APIs** (future)
```bash
export TIPSATOKEN=your_tipsa_token
export ONTIMETOKEN=your_ontime_token
export MIRAKLTOKEN=your_mirakl_token
```

### Docker Deployment

```bash
# Build production image
docker build -f docker/backend.Dockerfile -t mirakl-backend:latest .

# Run with environment
docker run -d \
  --name mirakl-backend \
  -p 8080:8080 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=INFO \
  mirakl-backend:latest
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mirakl-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mirakl-backend
  template:
    metadata:
      labels:
        app: mirakl-backend
    spec:
      containers:
      - name: backend
        image: mirakl-backend:latest
        ports:
        - containerPort: 8080
        env:
        - name: ENVIRONMENT
          value: "production"
```

## 🔄 API Integration

### TIPSA Integration (Future)

```python
# Example TIPSA API integration
from app.services.tipsa import TIPSAClient

client = TIPSAClient(api_token="your_token")
shipment = await client.create_shipment(orders)
tracking = await client.track_shipment(shipment.tracking_number)
```

### OnTime Integration (Future)

```python
# Example OnTime API integration
from app.services.ontime import OnTimeClient

client = OnTimeClient(api_token="your_token")
shipment = await client.create_shipment(orders)
label = await client.generate_label(shipment.id)
```

### Mirakl Integration (Future)

```python
# Example Mirakl API integration
from app.services.mirakl import MiraklClient

client = MiraklClient(api_token="your_token")
orders = await client.get_orders(status="PENDING")
await client.update_tracking(order_id, tracking_number)
```

## 📈 Performance

### Optimization

- **Async Processing**: All I/O operations are async
- **Connection Pooling**: HTTP client connection pooling
- **Caching**: Response caching for static data
- **Compression**: Gzip compression for responses

### Monitoring

- **Response Times**: Track endpoint performance
- **Memory Usage**: Monitor memory consumption
- **Error Rates**: Track error frequencies
- **Throughput**: Measure requests per second

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

## 🔗 Links

- [Main Documentation](../docs/README.md)
- [Architecture Guide](../docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8080/docs)
- [Changelog](../CHANGELOG.md)
