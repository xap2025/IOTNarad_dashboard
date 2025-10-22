@echo off
echo ==========================================
echo  Fix WSL Docker Integration
echo ==========================================
echo.

echo [1/6] Shutting down WSL...
wsl --shutdown
echo.

echo [2/6] Waiting for WSL to stop...
timeout /t 10 /nobreak >nul
echo.

echo [3/6] Checking WSL status...
wsl --list --verbose
echo.

echo [4/6] Restarting Docker Desktop processes...
taskkill /f /im "com.docker.backend.exe" /im "docker.exe" /im "docker-compose.exe" 2>nul
echo Docker processes killed.
echo.

echo [5/6] Waiting for Docker to restart...
timeout /t 15 /nobreak >nul
echo.

echo [6/6] Testing Docker connection...
docker --version
echo.

echo ==========================================
echo  Next Steps
echo ==========================================
echo.
echo 1. Go to Docker Desktop
echo 2. Click "Restart the WSL integration" 
echo 3. Wait 2-3 minutes
echo 4. Check "Engine running" status
echo 5. Run: test_after_restart.bat
echo.
echo OR if Docker still doesn't work:
echo 6. Run: run_without_docker.bat
echo.
pause
