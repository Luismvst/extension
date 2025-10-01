# Runbook - Operations Guide

This document provides step-by-step instructions for operating the Mirakl-TIPSA Orchestrator system.

## Quick Start

### Prerequisites
- Docker Desktop running
- Node.js 18+ (for extension development)
- Python 3.11+ (for backend development)

### Start Complete System
```bash
# Start all services
.\scripts\start-system.ps1

# Verify system
.\scripts\verify-system.ps1
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **TIPSA Mock**: http://localhost:3001
- **Mirakl Mock**: http://localhost:3002

## Development Setup

### Backend Development
```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Frontend Development
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Extension Development
```bash
# Navigate to extension
cd extension

# Install dependencies
npm install

# Build extension
npm run build

# Load in Chrome
# 1. Go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the 'dist' folder
```

## Service Management

### Start Services
```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d backend
docker compose up -d frontend
docker compose up -d tipsa-mock
docker compose up -d mirakl-mock
```

### Stop Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Stop specific service
docker compose stop backend
```

### View Logs
```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs backend
docker compose logs frontend

# Follow logs in real-time
docker compose logs -f backend
```

### Restart Services
```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
```

## Testing

### Backend Tests
```bash
# Run all tests
cd backend
python -m pytest

# Run specific test file
python -m pytest tests/test_csv_logging.py

# Run with coverage
python -m pytest --cov=app tests/

# Run with verbose output
python -m pytest -v
```

### Frontend Tests
```bash
# Run type check
cd frontend
npm run type-check

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix
```

### Extension Tests
```bash
# Run type check
cd extension
npm run typecheck

# Run linting
npm run lint

# Run unit tests
npm run test:unit

# Run e2e tests
npm run test:e2e
```

## Data Management

### Export CSV Files
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

### View Log Statistics
```bash
# Get logs statistics
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/stats"
```

### Filter Logs
```bash
# Get operations by scope
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/operations?scope=mirakl"

# Get orders by state
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/orders-view?state=POSTED"

# Get orders by carrier
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/logs/orders-view?carrier=tipsa"
```

## Workflow Operations

### Fetch Orders from Mirakl
```bash
# Fetch orders
curl -X POST -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/orchestrator/fetch-orders"
```

### Post Orders to Carrier
```bash
# Post to TIPSA
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"carrier": "tipsa"}' \
  "http://localhost:8080/api/v1/orchestrator/post-to-carrier"

# Post to OnTime
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"carrier": "ontime"}' \
  "http://localhost:8080/api/v1/orchestrator/post-to-carrier"
```

### Push Tracking to Mirakl
```bash
# Push tracking updates
curl -X POST -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/orchestrator/push-tracking-to-mirakl"
```

### Get Orders View
```bash
# Get all orders
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/orchestrator/orders-view"

# Get orders with filters
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/api/v1/orchestrator/orders-view?state=POSTED&carrier=tipsa"
```

## Authentication

### Login
```bash
# Login and get token
curl -X POST -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "test123"}' \
  "http://localhost:8080/auth/login"
```

### Validate Token
```bash
# Validate token
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/auth/validate"
```

### Get User Info
```bash
# Get current user
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8080/auth/me"
```

## Monitoring

### Health Checks
```bash
# Check basic system health
curl "http://localhost:8080/api/v1/health/"

# Check detailed health (includes all services)
curl "http://localhost:8080/api/v1/health/detailed"
```

### System Status
```bash
# Check Docker services
docker compose ps

# Check service logs
docker compose logs --tail=10 backend
docker compose logs --tail=10 frontend
```

### Resource Usage
```bash
# Check Docker resource usage
docker stats

# Check disk usage
docker system df

# Clean up unused resources
docker system prune
```

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker status
docker --version
docker compose --version

# Check if ports are available
netstat -an | findstr :8080
netstat -an | findstr :3000

# Check Docker logs
docker compose logs
```

#### Authentication Issues
```bash
# Check auth endpoint
curl "http://localhost:8080/auth/login" -v

# Check token format
echo "Bearer <token>" | base64 -d
```

#### CSV File Issues
```bash
# Check CSV file permissions
ls -la backend/logs/

# Check CSV file content
head -5 backend/logs/operations.csv
head -5 backend/logs/orders_view.csv

# Check file size
wc -l backend/logs/operations.csv
wc -l backend/logs/orders_view.csv
```

#### Frontend Issues
```bash
# Check frontend build
cd frontend
npm run build

# Check TypeScript errors
npm run type-check

# Check linting issues
npm run lint
```

#### Extension Issues
```bash
# Check extension build
cd extension
npm run build

# Check manifest
cat dist/manifest.json

# Check console errors in Chrome
# 1. Open chrome://extensions/
# 2. Click "Details" on extension
# 3. Click "Inspect views: popup"
# 4. Check Console tab for errors
```

### Debug Commands

#### Backend Debug
```bash
# Check Python environment
python --version
pip list

# Check FastAPI docs
curl "http://localhost:8080/docs"

# Check OpenAPI spec
curl "http://localhost:8080/openapi.json"
```

#### Frontend Debug
```bash
# Check Node environment
node --version
npm --version

# Check build output
cd frontend
npm run build
ls -la dist/
```

#### Extension Debug
```bash
# Check extension files
cd extension
ls -la dist/

# Check manifest
cat dist/manifest.json | jq '.'

# Check popup
cat dist/popup.html
```

## Maintenance

### Regular Tasks

#### Daily
- Check system health
- Monitor error rates
- Review failed operations
- Check CSV file sizes

#### Weekly
- Export CSV backups
- Clean up old log files
- Update dependencies
- Review performance metrics

#### Monthly
- Full system backup
- Security updates
- Performance optimization
- Documentation updates

### Backup Procedures
```bash
# Backup CSV files
cp backend/logs/operations.csv backups/operations_$(date +%Y%m%d).csv
cp backend/logs/orders_view.csv backups/orders_view_$(date +%Y%m%d).csv

# Backup Docker volumes
docker compose down
docker run --rm -v extension_postgres_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_$(date +%Y%m%d).tar.gz -C /data .
docker compose up -d
```

### Update Procedures
```bash
# Update backend dependencies
cd backend
pip install -r requirements.txt --upgrade

# Update frontend dependencies
cd frontend
npm update

# Update extension dependencies
cd extension
npm update

# Rebuild services
docker compose build --no-cache
docker compose up -d
```

## Security

### Access Control
- Use strong passwords
- Rotate JWT tokens regularly
- Limit API access by IP
- Monitor failed login attempts

### Data Protection
- Encrypt sensitive data
- Use HTTPS in production
- Implement rate limiting
- Regular security audits

### Backup Security
- Encrypt backup files
- Store backups securely
- Test restore procedures
- Document access controls

## Performance Tuning

### Backend Optimization
- Increase worker processes
- Optimize database queries
- Implement caching
- Monitor memory usage

### Frontend Optimization
- Enable compression
- Optimize bundle size
- Implement lazy loading
- Use CDN for assets

### Database Optimization
- Index frequently queried fields
- Optimize query patterns
- Monitor query performance
- Regular maintenance

## Emergency Procedures

### Service Outage
1. Check system health
2. Review error logs
3. Restart affected services
4. Escalate if needed

### Data Corruption
1. Stop all services
2. Restore from backup
3. Verify data integrity
4. Restart services

### Security Incident
1. Isolate affected systems
2. Preserve evidence
3. Notify stakeholders
4. Implement fixes

### Performance Degradation
1. Monitor resource usage
2. Identify bottlenecks
3. Implement optimizations
4. Scale resources if needed
