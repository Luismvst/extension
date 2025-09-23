#!/usr/bin/env bash
set -euo pipefail

# Verify script for Mirakl-TIPSA system
echo "🔍 Verifying Mirakl-TIPSA System..."

# Check backend health
echo "1. Checking backend health..."
if curl -sS http://localhost:8080/api/v1/health | grep -qi "healthy"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
    exit 1
fi

# Check frontend
echo "2. Checking frontend..."
if curl -sI http://localhost:3000 | grep -qi "200"; then
    echo "✅ Frontend is responding"
else
    echo "⚠️ Frontend status != 200 (check manually)"
fi

# Check TIPSA mock
echo "3. Checking TIPSA mock..."
if curl -sI http://localhost:3001/docs | grep -qi "200"; then
    echo "✅ TIPSA mock is responding"
else
    echo "⚠️ TIPSA mock not responding"
fi

# Check Mirakl mock
echo "4. Checking Mirakl mock..."
if curl -sI http://localhost:3002/docs | grep -qi "200"; then
    echo "✅ Mirakl mock is responding"
else
    echo "⚠️ Mirakl mock not responding"
fi

# Check log files
echo "5. Checking log files..."
if [ -d "backend/logs" ]; then
    log_count=$(ls -1 backend/logs/run-*.log 2>/dev/null | wc -l)
    if [ "$log_count" -gt 0 ]; then
        echo "✅ Found $log_count log file(s)"
        echo "📋 Latest log file:"
        ls -la backend/logs/run-*.log | tail -1
    else
        echo "⚠️ No log files found"
    fi
else
    echo "⚠️ Log directory not found"
fi

# Check orders CSV
echo "6. Checking orders CSV..."
if [ -f "backend/logs/orders_view.csv" ]; then
    echo "✅ Orders CSV exists"
    echo "📊 CSV info:"
    wc -l backend/logs/orders_view.csv
else
    echo "ℹ️ Orders CSV not found (will be created on first use)"
fi

echo ""
echo "🎉 System verification completed!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8080"
echo "📚 API Docs: http://localhost:8080/docs"

