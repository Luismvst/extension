# Mirakl Multi-Carrier Orchestrator

Un orquestador modular para gestionar pedidos entre marketplaces Mirakl y múltiples transportistas (TIPSA, OnTime, DHL, UPS), con una extensión de Chrome que proporciona una interfaz intuitiva tipo Sendcloud.

## 🚀 Características Principales

- **Extensión Chrome MV3** con Material Design
- **Backend FastAPI** modular y extensible
- **Soporte multi-transportista** (TIPSA, OnTime, DHL, UPS)
- **Motor de reglas inteligente** para selección automática de transportista
- **Adapters configurables** para marketplaces y transportistas
- **Logging CSV** completo con dumps de operaciones
- **Modo Mock** para testing sin APIs reales
- **Docker** para fácil despliegue
- **Trazabilidad completa** de extremo a extremo

## 📋 Flujo de Trabajo

1. **Cargar pedidos de Mirakl** - La extensión obtiene pedidos pendientes desde Mirakl
2. **Selección automática de transportista** - El motor de reglas elige el mejor transportista
3. **Crear envíos multi-transportista** - Genera envíos automáticamente con el transportista apropiado
4. **Subir tracking a Mirakl** - Actualiza el estado de seguimiento en Mirakl con datos reales

## 🏗️ Arquitectura

```
mirakl-tipsa-orchestrator/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── core/              # Configuración, logging, auth
│   │   ├── api/               # Endpoints REST
│   │   ├── adapters/          # Conectores modulares
│   │   │   ├── interfaces/    # MarketplaceAdapter, CarrierAdapter
│   │   │   ├── marketplaces/  # Mirakl, Amazon, etc.
│   │   │   └── carriers/      # TIPSA, DHL, etc.
│   │   ├── rules/             # Motor de reglas de negocio
│   │   └── utils/             # CSV logger, dumps
│   └── tests/
├── extension/                  # Extensión Chrome MV3
│   ├── src/
│   │   ├── content/           # Script para sitios TIPSA
│   │   ├── popup/             # Interfaz principal
│   │   ├── options/           # Configuración
│   │   └── lib/               # API client, utils
│   └── dist/                  # Build output
├── demo/                      # Sitios web de demostración
└── docs/                      # Documentación
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo de la extensión)
- Python 3.11+ (para desarrollo del backend)

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd mirakl-tipsa-orchestrator
   ```

2. **Configurar variables de entorno**
   ```bash
   cp backend/env.example backend/.env
   # Editar backend/.env con tus configuraciones
   ```

3. **Levantar el backend**
   ```bash
   docker-compose up -d backend
   ```

4. **Construir la extensión**
   ```bash
   cd extension
   npm install
   npm run build
   ```

5. **Cargar la extensión en Chrome**
   - Abrir `chrome://extensions/`
   - Activar "Modo desarrollador"
   - Hacer clic en "Cargar extensión sin empaquetar"
   - Seleccionar la carpeta `extension/dist`

### Uso

1. **Abrir el portal de demostración**
   ```bash
   docker-compose up -d
   # TIPSA Demo: http://localhost:3001
   # Mirakl Demo: http://localhost:3002
   ```

2. **Probar la extensión**
   - Navegar a http://localhost:3001 (TIPSA)
   - La extensión debería mostrar un overlay automáticamente
   - Usar los botones para cargar pedidos y crear envíos

## 🔧 Configuración

### Backend

Variables de entorno principales:

```env
# Autenticación
JWT_SECRET=your-super-secret-jwt-key

# Mirakl
MIRAKL_BASE_URL=https://your-tenant.mirakl.net
MIRAKL_API_KEY=your-api-key
MIRAKL_MODE=mock  # o 'live'

# TIPSA
TIPSA_BASE_URL=https://api.tip-sa.com
TIPSA_API_KEY=your-api-key
TIPSA_MODE=mock  # o 'live'

# OnTime
ONTIME_BASE_URL=https://api.ontime.com
ONTIME_API_KEY=your-api-key
ONTIME_MODE=mock  # o 'live'

# DHL
DHL_BASE_URL=https://api-eu.dhl.com
DHL_API_KEY=your-api-key
DHL_API_SECRET=your-api-secret
DHL_ACCOUNT=your-account
DHL_MODE=mock  # o 'live'

# UPS
UPS_BASE_URL=https://onlinetools.ups.com
UPS_ACCESS_KEY=your-access-key
UPS_USERNAME=your-username
UPS_PASSWORD=your-password
UPS_ACCOUNT_NUMBER=your-account
UPS_MODE=mock  # o 'live'
```

### Extensión

Configuración disponible en la página de opciones:
- URL del backend API
- Modo de funcionamiento (mock/live)
- Configuraciones de comportamiento

## 📊 API Endpoints

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/me` - Información del usuario
- `POST /api/v1/auth/validate` - Validar token

### Marketplaces
- `GET /api/v1/marketplaces/mirakl/orders` - Obtener pedidos
- `GET /api/v1/marketplaces/mirakl/orders/{id}` - Obtener pedido específico
- `PUT /api/v1/marketplaces/mirakl/orders/{id}/tracking` - Subir tracking

### Transportistas
- `POST /api/v1/carriers/tipsa/shipments` - Crear envío TIPSA
- `POST /api/v1/carriers/tipsa/shipments/bulk` - Crear múltiples envíos TIPSA
- `POST /api/v1/carriers/ontime/shipments` - Crear envío OnTime
- `POST /api/v1/carriers/ontime/shipments/bulk` - Crear múltiples envíos OnTime
- `POST /api/v1/carriers/dhl/shipments` - Crear envío DHL
- `POST /api/v1/carriers/dhl/shipments/bulk` - Crear múltiples envíos DHL
- `POST /api/v1/carriers/ups/shipments` - Crear envío UPS
- `POST /api/v1/carriers/ups/shipments/bulk` - Crear múltiples envíos UPS

### Orquestador
- `POST /api/v1/orchestrator/load-orders` - Cargar pedidos y crear envíos automáticamente
- `POST /api/v1/orchestrator/upload-tracking` - Subir tracking a Mirakl
- `GET /api/v1/orchestrator/status` - Estado del orquestador y transportistas

### Salud
- `GET /api/v1/health/` - Estado básico
- `GET /api/v1/health/detailed` - Estado detallado
- `GET /api/v1/health/logs` - Información de logs

## 🧪 Testing

### Backend
```bash
cd backend
pip install -e .[dev]
pytest
```

### Extensión
```bash
cd extension
npm test
```

### E2E
```bash
# Levantar servicios de demo
docker-compose up -d

# Ejecutar tests E2E
npm run test:e2e
```

## 📝 Logging

El sistema genera logs detallados en formato CSV:

- **Operaciones**: `logs/operations.csv`
- **Dumps**: `logs/dumps/` (JSON con payloads completos)

Cada operación incluye:
- Timestamp
- Acción realizada
- ID del pedido
- Marketplace/Transportista
- Hash del request
- Status de respuesta
- Resultado y mensaje

## 🔌 Adapters

### MarketplaceAdapter

Interfaz común para todos los marketplaces:

```python
class MarketplaceAdapter(ABC):
    async def fetch_orders(self, **filters) -> List[Order]
    async def get_order(self, order_id: str) -> Optional[Order]
    async def upload_tracking(self, order_id: str, tracking: str, ...) -> bool
    async def test_connection(self) -> bool
```

### CarrierAdapter

Interfaz común para todos los transportistas:

```python
class CarrierAdapter(ABC):
    async def create_shipment(self, request: ShipmentRequest) -> ShipmentResult
    async def create_shipments(self, requests: List[ShipmentRequest]) -> List[ShipmentResult]
    async def track_shipment(self, tracking_number: str) -> Optional[TrackingResult]
    async def get_label(self, shipment_id: str) -> Optional[bytes]
```

## ⚙️ Motor de Reglas de Negocio

El motor de reglas determina automáticamente qué transportista usar basándose en las características del pedido:

### Reglas de Selección

1. **Paquetes pesados (>20kg)** → **TIPSA** (maneja paquetes pesados)
2. **Pago contra reembolso (COD)** → **TIPSA** (soporte COD)
3. **Servicio express** → **DHL** (entrega rápida)
4. **Pedidos internacionales** → **DHL** (cobertura mundial)
5. **Por defecto** → **TIPSA** (envío estándar doméstico)

### Transportistas Soportados

| Transportista | Fortalezas | Peso Máx | Países | Servicios |
|---------------|------------|----------|--------|-----------|
| **TIPSA** | Paquetes pesados, COD, Doméstico | 30kg | ES | Estándar, Express |
| **DHL** | Internacional, Express, Confiabilidad | 70kg | Mundial | Express, Internacional |
| **OnTime** | Económico, Doméstico, Confiabilidad | 25kg | ES | Estándar |
| **UPS** | Internacional, Paquetes pesados, Tracking | 70kg | Mundial | Ground, Express, Internacional |

### Configuración de Reglas

Las reglas se pueden personalizar modificando `backend/app/rules/selector.py`:

```python
def select_carrier(order: Dict[str, Any]) -> str:
    # Regla 1: Paquetes pesados
    if order.get("weight", 0) > 20:
        return "tipsa"
    
    # Regla 2: Pago contra reembolso
    if order.get("payment_method") == "COD":
        return "tipsa"
    
    # Regla 3: Servicio express
    if order.get("shipping_speed") == "EXPRESS":
        return "dhl"
    
    # Regla 4: Internacional
    if order.get("shipping_address", {}).get("country") != "ES":
        return "dhl"
    
    # Por defecto
    return "tipsa"
```

## 🐳 Docker

### Desarrollo
```bash
# Solo backend
docker-compose up backend

# Con demos
docker-compose up
```

### Producción
```bash
# Backend con persistencia
docker-compose -f docker-compose.prod.yml up -d
```

## 📚 Documentación Adicional

- [Arquitectura](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Guía de Desarrollo](docs/DEVELOPMENT.md)
- [Despliegue](docs/DEPLOYMENT.md)

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Para soporte y preguntas:
- Crear un issue en GitHub
- Revisar la documentación
- Contactar al equipo de desarrollo

---

**Nota**: Este es un MVP (Minimum Viable Product) diseñado para demostrar la funcionalidad básica. Para uso en producción, se requieren configuraciones adicionales de seguridad y optimizaciones de rendimiento.