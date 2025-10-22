@echo off
echo ==========================================
echo  IOTNarad Dashboard - Fix Script
echo ==========================================
echo.

echo [1/6] Navigating to project directory...
cd /d "C:\Users\ridhi\IOTNarad_dashboard"
echo Current directory: %CD%
echo.

echo [2/6] Checking if docker-compose.yml exists...
if exist "docker-compose.yml" (
    echo ✅ docker-compose.yml found
) else (
    echo ❌ docker-compose.yml NOT found
    echo Please make sure you're in the right directory
    pause
    exit /b 1
)
echo.

echo [3/6] Stopping any existing containers...
docker-compose down -v
echo.

echo [4/6] Cleaning Docker system...
docker system prune -f
echo.

echo [5/6] Building and starting services...
echo This may take 2-3 minutes for first build...
docker-compose up -d --build
echo.

echo [6/6] Waiting for services to start...
timeout /t 30 /nobreak >nul

echo.
echo ==========================================
echo  Checking Container Status
echo ==========================================
docker ps --filter "name=iotnarad"
echo.

echo ==========================================
echo  Dashboard URLs
echo ==========================================
echo  Dashboard: http://localhost:8050
echo  Username:  admin
echo  Password:  iotnarad@2025
echo ==========================================
echo.

echo Opening dashboard in browser...
start http://localhost:8050
echo.

echo ✅ Fix completed!
echo.
echo If dashboard doesn't load, wait 1-2 minutes and try again.
echo.
pause
