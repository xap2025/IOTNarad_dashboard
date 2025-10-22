@echo off
echo ==========================================
echo  Docker Diagnostic - Complete Check
echo ==========================================
echo.

echo [1/8] Checking Docker Desktop status...
tasklist | findstr docker
echo.

echo [2/8] Checking Docker version...
docker --version
echo.

echo [3/8] Checking Docker Compose version...
docker-compose --version
echo.

echo [4/8] Checking Docker images...
docker images > docker_images.txt 2>&1
if exist docker_images.txt (
    echo Docker images output saved to docker_images.txt
    type docker_images.txt
) else (
    echo Failed to get Docker images
)
echo.

echo [5/8] Checking all containers...
docker ps -a > docker_containers.txt 2>&1
if exist docker_containers.txt (
    echo Docker containers output saved to docker_containers.txt
    type docker_containers.txt
) else (
    echo Failed to get Docker containers
)
echo.

echo [6/8] Checking Docker system info...
docker system info > docker_info.txt 2>&1
if exist docker_info.txt (
    echo Docker system info saved to docker_info.txt
    findstr "Server Version" docker_info.txt
) else (
    echo Failed to get Docker system info
)
echo.

echo [7/8] Checking docker-compose config...
docker-compose config > docker_compose_config.txt 2>&1
if exist docker_compose_config.txt (
    echo Docker compose config saved to docker_compose_config.txt
    echo Config validation: SUCCESS
) else (
    echo Docker compose config validation: FAILED
)
echo.

echo [8/8] Trying to build and start services...
echo This may take a few minutes...
docker-compose up -d --build > docker_startup.txt 2>&1
if exist docker_startup.txt (
    echo Docker startup output saved to docker_startup.txt
    type docker_startup.txt
) else (
    echo Failed to start Docker services
)
echo.

echo ==========================================
echo  Diagnostic Complete
echo ==========================================
echo.
echo Check the generated files:
echo - docker_images.txt
echo - docker_containers.txt  
echo - docker_info.txt
echo - docker_compose_config.txt
echo - docker_startup.txt
echo.
pause
