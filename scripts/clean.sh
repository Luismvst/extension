#!/usr/bin/env bash
set -euo pipefail

# Clean script for Mirakl-TIPSA system
echo "🧹 Cleaning Mirakl-TIPSA System..."

# Stop and remove containers, volumes, and networks
echo "🛑 Stopping and removing containers..."
docker compose down -v --remove-orphans

# Clean up Docker system
echo "🗑️ Cleaning Docker system..."
docker system prune -f

# Clean up old log files (keep last 10)
echo "📝 Cleaning old log files (keeping last 10)..."
if [ -d "backend/logs" ]; then
    ls -1t backend/logs/run-*.log 2>/dev/null | tail -n +11 | xargs -r rm -f
    echo "✅ Old log files cleaned"
else
    echo "ℹ️ No log directory found"
fi

# Clean up build artifacts
echo "🔨 Cleaning build artifacts..."
rm -rf frontend/dist
rm -rf extension/dist
rm -rf extension/out

echo "✅ System cleaned successfully!"

