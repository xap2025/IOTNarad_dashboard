# MQTT Subscribe Script
# Monitor all messages on MQTT broker

param(
    [string]$Topic = "#",
    [switch]$Verbose
)

Write-Host "📡 MQTT Message Monitor" -ForegroundColor Green
Write-Host "Topic Pattern: $Topic" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

$mqttContainer = "iotnarad_mqtt"

# Check if container is running
$containerCheck = docker ps --filter "name=$mqttContainer" --format "{{.Names}}"
if ($containerCheck -ne $mqttContainer) {
    Write-Host "❌ MQTT container '$mqttContainer' is not running!" -ForegroundColor Red
    Write-Host "Start it with: docker-compose up -d mqtt" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Connected to MQTT broker" -ForegroundColor Green
Write-Host "Listening for messages..." -ForegroundColor Yellow
Write-Host "─" * 60 -ForegroundColor Gray
Write-Host ""

if ($Verbose) {
    docker exec -it $mqttContainer mosquitto_sub -h localhost -t $Topic -v
} else {
    docker exec -it $mqttContainer mosquitto_sub -h localhost -t $Topic
}

