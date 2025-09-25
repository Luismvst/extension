# Frontend Environment Setup

Este directorio contiene un entorno virtual Python para el desarrollo del frontend de la extensión.

## Configuración Inicial

### Opción 1: Script Automático (Recomendado)
```powershell
npm run setup:env
```

### Opción 2: Manual
```powershell
# Crear entorno virtual
python -m venv frontend-env

# Activar entorno virtual
frontend-env\Scripts\activate

# Instalar dependencias Python
pip install -r requirements-frontend.txt

# Instalar dependencias Node.js
npm install
```

## Uso del Entorno Virtual

### Activar el entorno virtual
```powershell
npm run activate:env
```

### Comandos con entorno virtual
```powershell
# Desarrollo
npm run dev:env

# Build
npm run build:env

# Tests
npm run test:env
```

### Activar manualmente
```powershell
frontend-env\Scripts\activate
```

## Estructura

```
extension/
├── frontend-env/              # Entorno virtual Python
├── requirements-frontend.txt  # Dependencias Python
├── scripts/
│   ├── setup-frontend-env.ps1
│   └── activate-frontend-env.ps1
└── env.example               # Variables de entorno de ejemplo
```

## Dependencias Python

- `nodeenv`: Herramientas para Node.js
- `watchdog`: Monitoreo de archivos
- `python-dotenv`: Variables de entorno
- `requests`: HTTP requests

## Variables de Entorno

Copia `env.example` a `.env` y configura:

- `VITE_API_URL`: URL del backend API
- `VITE_DEBUG`: Modo debug
- `VITE_LOG_LEVEL`: Nivel de logging

## Notas

- El entorno virtual está excluido del control de versiones
- Usa PowerShell para los scripts de activación
- El entorno virtual se crea automáticamente en la carpeta `frontend-env/`
