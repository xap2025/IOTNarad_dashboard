# Test Device Initialization via MQTT
# Usage: .\test_mqtt_publish.ps1

Write-Host "Testing Device Initialization..." -ForegroundColor Cyan

# Test serial number
$serialNumber = "DF5647"
$topic = "Dev/Init/$serialNumber"
$payload = '{"SerialNumber": "' + $serialNumber + '"}'

Write-Host "`nPublishing: $topic" -ForegroundColor Yellow
Write-Host "Payload: $payload"

docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t $topic -m $payload

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Message published!" -ForegroundColor Green
    Write-Host "`nCheck logs: docker compose logs app --tail 30" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Failed to publish" -ForegroundColor Red
}

