@echo off
REM Celery Worker Startup Script for KisanSathi (Windows)

echo.
echo 🚀 Starting Celery Worker...
echo ================================
echo.

REM Check if Redis is running
echo Checking Redis connection...
redis-cli ping >nul 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Redis is not running!
    echo.
    echo Please start Redis first:
    echo   redis-server
    echo.
    pause
    exit /b 1
)

echo ✅ Redis is running
echo.

REM Start Celery worker
echo Starting Celery worker...
echo   Broker: redis://localhost:6379/0
echo   Concurrency: 4 workers
echo.

celery -A tasks worker --loglevel=info --concurrency=4

echo.
echo ❌ Celery worker stopped
pause
