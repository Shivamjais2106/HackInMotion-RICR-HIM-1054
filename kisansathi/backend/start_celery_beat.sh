#!/bin/bash

# Celery Beat Scheduler Startup Script for KisanSathi

echo "🚀 Starting Celery Beat Scheduler..."
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

# Start Celery Beat
echo "Starting Celery Beat scheduler..."
echo "  Broker: redis://localhost:6379/0"
echo ""

celery -A tasks beat --loglevel=info

echo ""
echo "❌ Celery Beat stopped"
