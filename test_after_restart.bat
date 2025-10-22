@echo off
echo ==========================================
echo  Test After Docker Desktop Restart
echo ==========================================
echo.

echo [1/4] Checking Docker Desktop status...
tasklist | findstr docker
echo.

echo [2/4] Testing Docker connection...
docker --version
echo.

echo [3/4] Testing Docker images...
docker images
echo.

echo [4/4] Starting IOTNarad services...
docker-compose up -d --build
echo.

echo ==========================================
echo  Check Results
echo ==========================================
echo.
echo If you see containers starting above, SUCCESS!
echo If you see errors, Docker Desktop is still not ready.
echo.
echo Wait 30 seconds, then check:
echo docker ps
echo.
echo Open browser: http://localhost:8050
echo.
pause
