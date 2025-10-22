@echo off
echo Testing Docker...
echo.

echo Command: docker --version
docker --version
echo.

echo Command: docker ps
docker ps
echo.

echo Command: docker-compose --version
docker-compose --version
echo.

echo Command: docker compose version
docker compose version
echo.

echo Command: docker-compose config
docker-compose config
echo.

echo Test completed.
pause
