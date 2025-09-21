# Mirakl-TIPSA Orchestrator

Sistema completo de orquestación entre Mirakl marketplace y transportistas (TIPSA, OnTime, SEUR, Correos Express) con dashboard web, extensión Chrome MV3 y mocks para testing.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chrome Ext    │    │   Dashboard     │    │   Backend API   │
│   (MV3)         │    │   (React+MUI)   │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TIPSA Mock    │    │  Mirakl Mock    │    │   Real APIs     │
│   (Port 3001)   │    │  (Port 3002)    │    │   (Production)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Inicio Rápido

### 1. Levantar Sistema Completo

```bash
# Levantar todos los servicios
docker compose up -d

# Ver logs
docker compose logs -f

# Verificar sistema
powershell -ExecutionPolicy Bypass -File scripts/verify-complete-system.ps1
```

### 2. URLs Disponibles

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **TIPSA Mock**: http://localhost:3001
- **Mirakl Mock**: http://localhost:3002

### 3. Cargar Extensión Chrome

1. Abrir Chrome → `chrome://extensions/`
2. Activar "Modo de desarrollador"
3. Clic en "Cargar extensión sin empaquetar"
4. Seleccionar carpeta `extension/dist/`

## 📋 Funcionalidades

### Backend API (FastAPI)

#### Endpoints Principales

- **Autenticación**: `POST /api/v1/auth/login`
- **Carriers**: `POST /api/v1/carriers/{carrier}/shipments`
- **Webhooks**: `POST /api/v1/carriers/webhooks/{carrier}`
- **Orquestador**: `POST /api/v1/orchestrator/fetch-orders`
- **Logs**: `GET /api/v1/logs/operations`

#### Carriers Soportados

- **TIPSA** (Real + Mock)
- **OnTime** (Mock)
- **SEUR** (Mock)
- **Correos Express** (Mock)

#### APIs de Mirakl

- **OR12**: `GET /api/orders` - Obtener pedidos
- **OR23**: `PUT /api/orders/{id}/tracking` - Actualizar tracking
- **OR24**: `PUT /api/orders/{id}/ship` - Marcar como enviado
- **ST23**: `POST /api/shipments/tracking` - Tracking batch

### Frontend Dashboard (React + MUI)

#### Páginas

- **Dashboard**: Vista de pedidos con filtros y estadísticas
- **Configuración**: Ajustes del sistema
- **Método de Pago**: Gestión de suscripciones
- **Integraciones**: Configuración de APIs (próximamente)

#### Características

- Tema blanco/azul (MUI)
- Autenticación JWT
- Tabla de pedidos con filtros
- Exportación CSV
- Actualización en tiempo real
- Responsive design

### Extensión Chrome (MV3)

#### Funcionalidades

- **3 Botones**: Cargar Pedidos, Crear Envíos, Subir Tracking
- **Sentinels**: Verificación de build y versión
- **Logging**: FrontLogger para acciones del usuario
- **Export CSV**: Descarga de logs en formato CSV

#### Archivos

- `manifest.json` - Manifest MV3 con versioning
- `background.js` - Service worker
- `popup.html/js` - Interfaz del popup
- `content/index.js` - Content script

### Servidores Mock

#### TIPSA Mock (Puerto 3001)

- Simula API de TIPSA
- Webhooks automáticos
- Idempotencia con `Idempotency-Key`
- Progresión de estados automática

#### Mirakl Mock (Puerto 3002)

- Simula APIs de Mirakl (OR12, OR23, OR24, ST23)
- Pedidos de prueba
- Respuestas realistas
- Manejo de códigos de estado

## 🔧 Desarrollo

### Estructura del Proyecto

```
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── adapters/       # Adaptadores de APIs
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configuración y utilidades
│   │   └── rules/          # Motor de reglas
│   └── logs/               # Logs CSV y JSON
├── frontend/               # Dashboard React
│   ├── src/
│   │   ├── pages/          # Páginas del dashboard
│   │   ├── hooks/          # Hooks personalizados
│   │   └── components/     # Componentes reutilizables
│   └── dist/               # Build del frontend
├── extension/              # Extensión Chrome
│   ├── src/
│   │   ├── popup/          # Popup de la extensión
│   │   ├── background/     # Service worker
│   │   └── content/        # Content script
│   └── dist/               # Build de la extensión
├── mocks/                  # Servidores mock
│   ├── tipsa-mock.py       # Mock de TIPSA
│   ├── mirakl-mock.py      # Mock de Mirakl
│   └── run-mocks.py        # Script para ejecutar mocks
└── scripts/                # Scripts de utilidad
    ├── verify-complete-system.ps1
    └── build-all.ps1
```

### Comandos de Desarrollo

```bash
# Backend
cd backend
docker compose up backend

# Frontend
cd frontend
npm install
npm run dev

# Extensión
cd extension
npm install
npm run build

# Mocks
cd mocks
python run-mocks.py
```

### Testing

```bash
# Tests unitarios (extensión)
cd extension
npm run test:unit

# Tests E2E (extensión)
npm run test:e2e

# Verificar sistema completo
powershell -ExecutionPolicy Bypass -File scripts/verify-complete-system.ps1
```

## 📊 Logging y Monitoreo

### Logs CSV

- **operations.csv**: Logs de operaciones del backend
- **orders_view.csv**: Vista unificada de pedidos (Mirakl + Carrier + Interno)

### Logs JSON

- **dumps/**: Dumps de requests/responses para debugging

### Endpoints de Logs

- `GET /api/v1/logs/operations` - Logs de operaciones
- `GET /api/v1/logs/orders-view` - Vista de pedidos
- `GET /api/v1/logs/exports/*.csv` - Descarga de CSVs
- `GET /api/v1/logs/stats` - Estadísticas

## 🔐 Seguridad

### Autenticación

- JWT tokens con expiración configurable
- Headers de autorización en todas las peticiones
- Tokens especiales para extensión Chrome

### Webhooks

- Validación HMAC con secretos por carrier
- Protección contra replay attacks (timestamp)
- Idempotencia con event IDs

### CORS

- Configurado para desarrollo local
- Headers apropiados para APIs

## 🚀 Despliegue

### Docker Compose

```bash
# Producción
docker compose -f docker-compose.prod.yml up -d

# Desarrollo
docker compose up -d
```

### Variables de Entorno

```bash
# Backend
MIRAKL_API_KEY=your_key
TIPSA_API_KEY=your_key
SECRET_KEY=your_secret

# Carriers
ONTIME_API_KEY=your_key
SEUR_API_KEY=your_key
CORREOSEX_API_KEY=your_key
```

## 📚 Documentación

- **AUDIT.md**: Auditoría del repositorio y estado actual
- **MOCKS.md**: Documentación de servidores mock
- **API Docs**: http://localhost:8080/docs (Swagger)

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte o preguntas:

1. Revisar documentación en `AUDIT.md` y `MOCKS.md`
2. Verificar logs en `backend/logs/`
3. Ejecutar script de verificación: `scripts/verify-complete-system.ps1`
4. Crear issue en el repositorio

---

**Desarrollado con ❤️ para la orquestación eficiente de pedidos Mirakl-TIPSA**