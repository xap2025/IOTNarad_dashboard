@echo off
REM IOTNarad Dashboard - Quick Test Script
REM Run this step by step and verify each step works

echo.
echo ==========================================
echo  IOTNarad Dashboard - Quick Test
echo ==========================================
echo.

:MENU
echo.
echo Choose a test step:
echo.
echo  [1] Check Prerequisites (Docker, Python)
echo  [2] Create data directory
echo  [3] Start Docker services
echo  [4] Check container status
echo  [5] View app logs
echo  [6] Open dashboard in browser
echo  [7] Test MQTT (publish sample data)
echo  [8] Stop all services
echo  [9] View full testing guide
echo  [0] Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto CHECK_PREREQ
if "%choice%"=="2" goto CREATE_DIR
if "%choice%"=="3" goto START_SERVICES
if "%choice%"=="4" goto CHECK_STATUS
if "%choice%"=="5" goto VIEW_LOGS
if "%choice%"=="6" goto OPEN_BROWSER
if "%choice%"=="7" goto TEST_MQTT
if "%choice%"=="8" goto STOP_SERVICES
if "%choice%"=="9" goto VIEW_GUIDE
if "%choice%"=="0" goto EXIT
goto MENU

:CHECK_PREREQ
echo.
echo === Checking Prerequisites ===
echo.
echo Docker version:
docker --version
echo.
echo Docker Compose version:
docker-compose --version
echo.
echo Python version:
python --version
echo.
echo .env file:
if exist .env (
    echo ✅ .env file exists
) else (
    echo ❌ .env file NOT found
)
echo.
pause
goto MENU

:CREATE_DIR
echo.
echo === Creating data directory ===
if not exist "data\configs" (
    mkdir "data\configs"
    echo ✅ Created: data\configs
) else (
    echo ✅ Already exists: data\configs
)
echo.
pause
goto MENU

:START_SERVICES
echo.
echo === Starting Docker Services ===
echo This may take 2-3 minutes for first build...
echo.
docker-compose up -d --build
echo.
echo Waiting 15 seconds for services to start...
timeout /t 15 /nobreak >nul
echo.
echo ✅ Services started!
echo.
pause
goto MENU

:CHECK_STATUS
echo.
echo === Container Status ===
echo.
docker ps --filter "name=iotnarad"
echo.
echo === Quick Status Check ===
docker-compose ps
echo.
pause
goto MENU

:VIEW_LOGS
echo.
echo === Viewing App Logs (Press Ctrl+C to stop) ===
echo.
docker-compose logs -f app
goto MENU

:OPEN_BROWSER
echo.
echo === Opening Dashboard in Browser ===
echo.
echo Dashboard URL: http://localhost:8050
echo.
echo Login Credentials:
echo   Username: admin
echo   Password: iotnarad@2025
echo.
start http://localhost:8050
echo.
echo ✅ Browser opened!
echo.
pause
goto MENU

:TEST_MQTT
echo.
echo === Testing MQTT Communication ===
echo.
echo Publishing sample sensor data...
docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -t "iotnarad/devices/esp32_gw_01/data" -m "{\"device_id\":\"esp32_gw_01\",\"temperature\":25.5,\"humidity\":60.2,\"voltage_ain0\":5.2,\"current_ain1\":12.5}"
echo.
echo ✅ Sample data published!
echo Check the Analytics page in your browser to see the data
echo.
pause
goto MENU

:STOP_SERVICES
echo.
echo === Stopping All Services ===
echo.
docker-compose down
echo.
echo ✅ All services stopped!
echo.
pause
goto MENU

:VIEW_GUIDE
echo.
echo === Opening Testing Guide ===
echo.
if exist TESTING_GUIDE.md (
    start TESTING_GUIDE.md
    echo ✅ Testing guide opened!
) else (
    echo ❌ TESTING_GUIDE.md not found
)
echo.
pause
goto MENU

:EXIT
echo.
echo Thank you for testing IOTNarad Dashboard!
echo.
exit

