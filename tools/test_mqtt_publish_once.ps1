# Quick MQTT Publish Test
# Send a single test message

param(
    [string]$Topic = "iotnarad/devices/test/data",
    [string]$Message = '{"test": true, "timestamp": "2025-10-29T17:30:45Z"}'
)

Write-Host "📤 Sending MQTT Test Message" -ForegroundColor Green
Write-Host "Topic: $Topic" -ForegroundColor Cyan
Write-Host "Message: $Message" -ForegroundColor Gray
Write-Host ""

$mqttContainer = "iotnarad_mqtt"

# Check if container is running
$containerCheck = docker ps --filter "name=$mqttContainer" --format "{{.Names}}"
if ($containerCheck -ne $mqttContainer) {
    Write-Host "❌ MQTT container '$mqttContainer' is not running!" -ForegroundColor Red
    exit 1
}

# Publish message
Write-Host "Publishing..." -ForegroundColor Yellow
docker exec -i $mqttContainer mosquitto_pub -h localhost -p 1883 -t $Topic -m $Message

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Message published successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To monitor messages, run:" -ForegroundColor Cyan
    Write-Host "  .\tools\test_mqtt_subscribe.ps1" -ForegroundColor Yellow
} else {
    Write-Host "❌ Failed to publish message" -ForegroundColor Red
}

