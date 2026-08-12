#!/bin/bash

# Redis Startup Script for KisanSathi

echo "🚀 Starting Redis Server..."
echo "================================"

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed!"
    echo ""
    echo "Installation instructions:"
    echo "  Linux: sudo apt-get install redis-server"
    echo "  Mac: brew install redis"
    echo "  Windows: Download from https://github.com/microsoftarchive/redis/releases"
    exit 1
fi

# Start Redis server
echo "✅ Redis found at: $(which redis-server)"
echo ""
echo "Starting Redis on localhost:6379..."
echo ""

redis-server

echo ""
echo "❌ Redis stopped"
