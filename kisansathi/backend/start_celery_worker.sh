#!/bin/bash

# Celery Worker Startup Script for KisanSathi

echo "🚀 Starting Celery Worker..."
echo "================================"

# Check if Redis is running
echo "Checking Redis connection..."
redis-cli ping > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Redis is not running!"
    echo "Please start Redis first:"
    echo "  redis-server"
    exit 1
fi

echo "✅ Redis is running"
echo ""

# Start Celery worker
echo "Starting Celery worker..."
echo "  Broker: redis://localhost:6379/0"
echo "  Concurrency: 4 workers"
echo ""

celery -A tasks worker --loglevel=info --concurrency=4

echo ""
echo "❌ Celery worker stopped"
