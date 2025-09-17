# Mirakl CSV Extension - Makefile

.PHONY: help install build test clean up down logs shell

# Default target
help:
	@echo "Mirakl CSV Extension - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install all dependencies"
	@echo "  build       - Build all components"
	@echo "  test        - Run all tests"
	@echo "  clean       - Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  up          - Start all services"
	@echo "  up-dev      - Start development services"
	@echo "  down        - Stop all services"
	@echo "  logs        - Show logs"
	@echo "  shell       - Open shell in backend container"
	@echo ""
	@echo "Extension:"
	@echo "  build-ext   - Build extension only"
	@echo "  test-ext    - Test extension only"
	@echo ""
	@echo "Backend:"
	@echo "  build-backend - Build backend only"
	@echo "  test-backend  - Test backend only"
	@echo "  run-backend   - Run backend locally"

# Install dependencies
install:
	@echo "Installing dependencies..."
	cd extension && pnpm install
	cd backend && pip install -e .

# Build all components
build: build-ext build-backend

# Build extension
build-ext:
	@echo "Building extension..."
	cd extension && pnpm build

# Build backend
build-backend:
	@echo "Building backend..."
	cd backend && python -m pip install -e .

# Run all tests
test: test-ext test-backend

# Test extension
test-ext:
	@echo "Testing extension..."
	cd extension && pnpm test

# Test backend
test-backend:
	@echo "Testing backend..."
	cd backend && pytest

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf extension/dist
	rm -rf backend/build
	rm -rf backend/dist
	rm -rf backend/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker commands
up:
	@echo "Starting all services..."
	docker-compose -f docker/docker-compose.yml up -d

up-dev:
	@echo "Starting development services..."
	docker-compose -f docker/docker-compose.yml --profile dev up -d

down:
	@echo "Stopping all services..."
	docker-compose -f docker/docker-compose.yml down

logs:
	@echo "Showing logs..."
	docker-compose -f docker/docker-compose.yml logs -f

shell:
	@echo "Opening shell in backend container..."
	docker-compose -f docker/docker-compose.yml exec backend /bin/bash

# Build extension with Docker
build-ext-docker:
	@echo "Building extension with Docker..."
	docker-compose -f docker/docker-compose.yml --profile build run --rm extension_build

# Run backend locally
run-backend:
	@echo "Running backend locally..."
	cd backend && uvicorn app.main:app --reload --port 8080

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	cp env.example .env
	@echo "Development setup complete!"
	@echo "Run 'make up-dev' to start development services"

# Production build
prod-build:
	@echo "Building for production..."
	docker-compose -f docker/docker-compose.yml build --no-cache

# CI/CD commands
ci-test:
	@echo "Running CI tests..."
	make test-ext
	make test-backend

ci-build:
	@echo "Running CI build..."
	make build-ext
	make build-backend

# Extension specific
extension-dev:
	@echo "Starting extension development server..."
	cd extension && pnpm dev

extension-test-e2e:
	@echo "Running extension E2E tests..."
	cd extension && pnpm test:e2e

# Backend specific
backend-dev:
	@echo "Starting backend development server..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

backend-test-cov:
	@echo "Running backend tests with coverage..."
	cd backend && pytest --cov=app --cov-report=html --cov-report=term

# Database commands (for future use)
db-migrate:
	@echo "Running database migrations..."
	# Add migration commands here

db-reset:
	@echo "Resetting database..."
	# Add database reset commands here

# Utility commands
status:
	@echo "Checking service status..."
	docker-compose -f docker/docker-compose.yml ps

restart:
	@echo "Restarting services..."
	docker-compose -f docker/docker-compose.yml restart

# Help for specific targets
help-ext:
	@echo "Extension commands:"
	@echo "  build-ext      - Build extension"
	@echo "  test-ext       - Test extension"
	@echo "  extension-dev  - Start extension dev server"
	@echo "  extension-test-e2e - Run E2E tests"

help-backend:
	@echo "Backend commands:"
	@echo "  build-backend    - Build backend"
	@echo "  test-backend     - Test backend"
	@echo "  backend-dev      - Start backend dev server"
	@echo "  backend-test-cov - Run tests with coverage"

help-docker:
	@echo "Docker commands:"
	@echo "  up        - Start all services"
	@echo "  up-dev    - Start development services"
	@echo "  down      - Stop all services"
	@echo "  logs      - Show logs"
	@echo "  shell     - Open shell in backend"
