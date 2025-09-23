#!/usr/bin/env bash
set -euo pipefail

# Stop script for Mirakl-TIPSA system
echo "🛑 Stopping Mirakl-TIPSA System..."

# Stop all services
docker compose down

echo "✅ System stopped successfully!"

