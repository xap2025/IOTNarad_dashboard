@echo off
echo ======================================
echo  IOTNarad Dashboard - Quick Test
echo ======================================
echo.

echo [1/5] Stopping any running containers...
docker-compose down 2>nul

echo.
echo [2/5] Creating data directory...
if not exist "data\configs" mkdir "data\configs"

echo.
echo [3/5] Building and starting services...
docker-compose up -d --build

echo.
echo [4/5] Waiting for services to start (20 seconds)...
timeout /t 20 /nobreak >nul

echo.
echo [5/5] Checking container status...
docker-compose ps

echo.
echo ======================================
echo  Services Status
echo ======================================
docker ps --filter "name=iotnarad" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ======================================
echo  Dashboard URLs
echo ======================================
echo  Dashboard: http://localhost:8050
echo  Username:  admin
echo  Password:  iotnarad@2025
echo ======================================
echo.
echo Press any key to view logs (Ctrl+C to exit logs)...
pause >nul

docker-compose logs -f app

