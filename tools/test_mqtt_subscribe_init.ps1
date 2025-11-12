# MQTT Subscribe Test - Monitor Dev/Init/# topic
# This script subscribes to Dev/Init/# topic to see all device initialization messages
# Usage: .\tools\test_mqtt_subscribe_init.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MQTT Subscribe Test - Dev/Init/# Topic" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Subscribing to topic: Dev/Init/#" -ForegroundColor Yellow
Write-Host "This will show all messages received on this topic" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Subscribe to Dev/Init/# topic
docker exec -i iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/#" -v

