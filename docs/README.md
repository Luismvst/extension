# Mirakl CSV Extension MVP

Chrome extension (MV3) que intercepta exportaciones CSV de marketplaces Mirakl (Carrefour/Leroy/Adeo), normaliza pedidos y genera un archivo listo para transportistas (TIPSA / OnTime).

## 🎯 Objetivo

Extensión de Chrome (MV3) que intercepta exportaciones CSV de marketplaces Mirakl, normaliza pedidos y genera un archivo listo para transportistas (TIPSA / OnTime). Fase 2: API-first Mirakl + backend FastAPI para colas, logs, etiquetas y tracking.

## 🏗️ Arquitectura

- **Frontend**: Chrome Extension MV3 + React + TypeScript + Tailwind + Zod
- **Backend**: FastAPI + Pydantic + Uvicorn (opcional en MVP)
- **Tests**: Playwright E2E + Jest unitarios
- **Deploy**: Docker + GitHub Actions CI/CD

## 🚀 Inicio Rápido

### Prerrequisitos

- Node.js 18+
- Python 3.12+
- Docker & Docker Compose
- Chrome/Chromium

### Instalación

1. **Clonar repositorio**
```bash
git clone https://github.com/Luismvst/extension.git
cd extension
```

2. **Instalar dependencias**
```bash
# Extension
cd extension
pnpm install

# Backend (opcional)
cd ../backend
pip install -e .
```

3. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

### Desarrollo

#### Extension

```bash
cd extension
pnpm dev          # Desarrollo con hot reload
pnpm build        # Build para producción
pnpm test:e2e     # Tests E2E con Playwright
```

#### Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8080
```

#### Docker

```bash
# Levantar todos los servicios
docker-compose -f docker/docker-compose.yml up --build

# Solo backend
docker-compose -f docker/docker-compose.yml up backend

# Solo build de extensión
docker-compose -f docker/docker-compose.yml up extension_build
```

### Cargar Extensión en Chrome

1. Build de la extensión:
```bash
cd extension
pnpm build
```

2. Abrir Chrome → `chrome://extensions/`
3. Activar "Modo de desarrollador"
4. Clic "Cargar extensión sin empaquetar"
5. Seleccionar carpeta `extension/dist`

## 🧪 Testing

### Tests Unitarios

```bash
# Backend
cd backend
pytest

# Extension
cd extension
pnpm test
```

### Tests E2E

```bash
cd tests
pnpm test:e2e
```

### Portal de Pruebas

El proyecto incluye un portal fake para testing:

```bash
cd tests
pnpm dev:portal
# Abrir http://localhost:3000
```

## 📁 Estructura del Proyecto

```
extension/                 # Chrome MV3 + React + TS + Tailwind + Zod
  src/
    background/            # service worker (cola, mensajería)
    content/               # hook de exportación CSV + UI/acciones in-portal
    popup/                 # interfaz minimal (lista + generar CSV TIPSA)
    options/               # credenciales/config en storage
    common/                # mensajes, tipos, esquemas Zod
    lib/                   # csv utils, storage, cola
    mappers/               # tipsa.ts (CSV), ontime.ts (placeholder)
    styles/
  public/                  # iconos
  manifest.ts
  vite.config.ts
  package.json

backend/                   # FastAPI + Pydantic + Uvicorn
  app/
    api/                   # routers: health, map, ship, tracking
    core/                  # settings, logging, errors
    models/                # pydantic models (OrderStandard, Carrier payloads)
    services/              # adapters TIPSA/OnTime (stubs)
    utils/                 # parse/normalize helpers
    main.py
  tests/
    unit/
    e2e/
  pyproject.toml
  Dockerfile

tests/                     # Playwright (portal fake) + fixtures de CSV
  playwright/
    e2e.spec.ts
    fixtures/
      carrefour_sample.csv
      leroy_sample.csv

docs/
  README.md                # guía general (top-level)
  ARCHITECTURE.md
  MVP_PLAN.md
  CHANGELOG.md

docker/
  docker-compose.yml       # backend + builder de extensión
  extension.Dockerfile     # build dist
  backend.Dockerfile       # slim Python
```

## 🔧 Scripts Disponibles

### Extension
- `pnpm dev` - Desarrollo con hot reload
- `pnpm build` - Build para producción
- `pnpm test` - Tests unitarios
- `pnpm test:e2e` - Tests E2E con Playwright
- `pnpm lint` - Linting
- `pnpm type-check` - Verificación de tipos

### Backend
- `uvicorn app.main:app --reload` - Servidor de desarrollo
- `pytest` - Tests unitarios
- `pytest --cov` - Tests con cobertura

### Docker
- `make up` - Levantar todos los servicios
- `make build-ext` - Build solo de extensión
- `make test` - Ejecutar todos los tests

## 📋 Criterios de Aceptación MVP

- [x] Captura CSV en Carrefour/Leroy demo → pedidos aparecen en popup
- [x] Generación CSV TIPSA válido (cabeceras + filas correctas)
- [x] Tests unitarios/verdes; e2e básico ok
- [x] Build en Docker y CI ok
- [x] Repo sincronizado en GitHub

## 🛣️ Roadmap

### Fase 2 (Post-MVP)
- API Mirakl (OR11/12/21/23), aceptación y tracking
- Integración TIPSA/OnTime con etiqueta PDF/ZPL
- Reglas de servicio (peso, provincias, horarios)
- Onboarding UX + Stripe
- Telemetría (consent) y alertas de fallos

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## 📞 Contacto

Luis Miguel Vázquez - [@luismvst](https://github.com/luismvst)

Link del Proyecto: [https://github.com/Luismvst/extension](https://github.com/Luismvst/extension)
