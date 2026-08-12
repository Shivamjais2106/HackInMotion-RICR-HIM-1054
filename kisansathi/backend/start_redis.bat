@echo off
REM Redis Startup Script for KisanSathi (Windows)

echo.
echo 🚀 Starting Redis Server...
echo ================================
echo.

REM Check if redis-server is in PATH
where redis-server >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Redis is not installed or not in PATH!
    echo.
    echo Installation instructions:
    echo   1. Download from: https://github.com/microsoftarchive/redis/releases
    echo   2. Extract to a folder
    echo   3. Add folder to PATH or run redis-server.exe directly
    echo.
    pause
    exit /b 1
)

echo ✅ Redis found!
echo.
echo Starting Redis on localhost:6379...
echo.

redis-server

echo.
echo ❌ Redis stopped
pause
