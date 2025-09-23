#!/usr/bin/env bash
set -euo pipefail

# Start script for Mirakl-TIPSA system
echo "🚀 Starting Mirakl-TIPSA System..."

# Set run timestamp
export RUN_TS="$(date +%Y%m%d-%H%M%S)"
echo "RUN_TS=$RUN_TS"

# Clean up previous containers
echo "🧹 Cleaning up previous containers..."
docker compose down -v --remove-orphans || true

# Build and start services
echo "🔨 Building and starting services..."
docker compose build --no-cache
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Show service status
echo "📊 Service status:"
docker compose ps

# Show backend logs
echo "📋 Backend logs (last 20 lines):"
docker compose logs --tail=20 backend

echo "✅ System started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8080"
echo "📚 API Docs: http://localhost:8080/docs"
echo "📝 Logs: tail -f backend/logs/run-*.log"

