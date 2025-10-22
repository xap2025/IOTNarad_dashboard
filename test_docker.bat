@echo off
echo Testing Docker...
echo.

echo Docker version:
docker --version
echo.

echo Docker Compose version:
docker-compose --version
echo.

echo Current directory:
cd
echo.

echo Listing files:
dir /b
echo.

echo Checking if .env exists:
if exist .env (
    echo .env file exists
) else (
    echo .env file NOT found
)
echo.

echo Trying to start containers:
docker-compose -f docker-compose-fixed.yml up -d --build
echo.

echo Waiting 10 seconds...
timeout /t 10 /nobreak >nul

echo Checking container status:
docker ps
echo.

echo Checking all containers:
docker ps -a
echo.

echo Press any key to continue...
pause >nul
