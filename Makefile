# Mirakl-TIPSA Orchestrator Makefile

.PHONY: help build up down logs clean test install-extension

# Default target
help:
	@echo "Mirakl-TIPSA Orchestrator - Comandos disponibles:"
	@echo ""
	@echo "  make up              - Levantar todos los servicios"
	@echo "  make down            - Parar todos los servicios"
	@echo "  make build           - Construir todas las imágenes"
	@echo "  make logs             - Ver logs de todos los servicios"
	@echo "  make clean            - Limpiar contenedores e imágenes"
	@echo "  make test             - Ejecutar tests"
	@echo "  make test-e2e         - Ejecutar tests E2E con Playwright"
	@echo "  make install-extension - Instalar dependencias de la extensión"
	@echo "  make build-extension  - Construir la extensión"
	@echo "  make backend-only     - Solo backend"
	@echo "  make demo-only        - Solo sitios de demostración"
	@echo "  make ci               - Ejecutar pipeline CI completo"
	@echo ""

# Levantar todos los servicios
up:
	@echo "🚀 Levantando Mirakl-TIPSA Orchestrator..."
	docker-compose up -d
	@echo "✅ Servicios levantados:"
	@echo "   - Backend API: http://localhost:8080"
	@echo "   - TIPSA Demo: http://localhost:3001"
	@echo "   - Mirakl Demo: http://localhost:3002"
	@echo "   - API Docs: http://localhost:8080/docs"

# Parar todos los servicios
down:
	@echo "🛑 Parando servicios..."
	docker-compose down
	@echo "✅ Servicios parados"

# Construir todas las imágenes
build:
	@echo "🔨 Construyendo imágenes..."
	docker-compose build
	@echo "✅ Imágenes construidas"

# Ver logs
logs:
	@echo "📋 Mostrando logs..."
	docker-compose logs -f

# Limpiar contenedores e imágenes
clean:
	@echo "🧹 Limpiando..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Limpieza completada"

# Solo backend
backend-only:
	@echo "🚀 Levantando solo el backend..."
	docker-compose up -d backend
	@echo "✅ Backend levantado en http://localhost:8080"

# Solo demos
demo-only:
	@echo "🚀 Levantando sitios de demostración..."
	docker-compose up -d tipsa-demo mirakl-demo
	@echo "✅ Demos levantados:"
	@echo "   - TIPSA Demo: http://localhost:3001"
	@echo "   - Mirakl Demo: http://localhost:3002"

# Instalar dependencias de la extensión
install-extension:
	@echo "📦 Instalando dependencias de la extensión..."
	cd extension && npm install
	@echo "✅ Dependencias instaladas"

# Construir la extensión
build-extension: install-extension
	@echo "🔨 Construyendo extensión..."
	cd extension && npm run build
	@echo "✅ Extensión construida en extension/dist/"

# Ejecutar tests
test:
	@echo "🧪 Ejecutando tests..."
	@echo "Backend tests:"
	cd backend && python -m pytest tests/ -v
	@echo "Extension tests:"
	cd extension && npm test
	@echo "✅ Tests completados"

# Desarrollo completo
dev: build up install-extension build-extension
	@echo "🎉 Entorno de desarrollo listo!"
	@echo ""
	@echo "Próximos pasos:"
	@echo "1. Cargar la extensión en Chrome desde extension/dist/"
	@echo "2. Visitar http://localhost:3001 para probar TIPSA"
	@echo "3. Visitar http://localhost:3002 para probar Mirakl"
	@echo "4. Usar http://localhost:8080/docs para la API"

# Verificar estado
status:
	@echo "📊 Estado de los servicios:"
	docker-compose ps

# Reiniciar servicios
restart:
	@echo "🔄 Reiniciando servicios..."
	docker-compose restart
	@echo "✅ Servicios reiniciados"

# Backup de logs
backup-logs:
	@echo "💾 Creando backup de logs..."
	mkdir -p backups
	tar -czf backups/logs-$(shell date +%Y%m%d-%H%M%S).tar.gz logs/
	@echo "✅ Backup creado en backups/"

# Actualizar dependencias
update-deps:
	@echo "🔄 Actualizando dependencias..."
	cd backend && pip install --upgrade pip && pip install -e .[dev]
	cd extension && npm update
	@echo "✅ Dependencias actualizadas"

# Verificar salud
health:
	@echo "🏥 Verificando salud de los servicios..."
	@echo "Backend:"
	@curl -s http://localhost:8080/api/v1/health/ | jq . || echo "❌ Backend no disponible"
	@echo "TIPSA Demo:"
	@curl -s http://localhost:3001/api/status | jq . || echo "❌ TIPSA Demo no disponible"
	@echo "Mirakl Demo:"
	@curl -s http://localhost:3002/api/orders | jq . || echo "❌ Mirakl Demo no disponible"

# Tests E2E con Playwright
test-e2e:
	@echo "🧪 Ejecutando tests E2E..."
	docker-compose up -d
	@sleep 30
	cd tests && npm install && npx playwright install && npx playwright test
	docker-compose down
	@echo "✅ Tests E2E completados"

# Pipeline CI completo
ci:
	@echo "🔄 Ejecutando pipeline CI completo..."
	@echo "1. Construyendo imágenes..."
	docker-compose build
	@echo "2. Levantando servicios..."
	docker-compose up -d
	@sleep 30
	@echo "3. Ejecutando tests E2E..."
	cd tests && npm install && npx playwright install && npx playwright test
	@echo "4. Parando servicios..."
	docker-compose down
	@echo "✅ Pipeline CI completado"