# Comprehensive MQTT Device Initialization Test Script
# Tests: MQTT Connection, Subscription, Message Reception, Database Saving
# Usage: .\test_mqtt_device_init.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MQTT Device Initialization Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Docker containers are running
Write-Host "Step 1: Checking Docker Containers..." -ForegroundColor Yellow
$mqttContainer = docker ps --filter "name=iotnarad_mqtt" --format "{{.Names}}"
$appContainer = docker ps --filter "name=iotnarad_app" --format "{{.Names}}"

if (-not $mqttContainer) {
    Write-Host "❌ MQTT container (iotnarad_mqtt) is not running!" -ForegroundColor Red
    Write-Host "   Please start containers: docker compose up -d" -ForegroundColor Yellow
    exit 1
}

if (-not $appContainer) {
    Write-Host "❌ App container (iotnarad_app) is not running!" -ForegroundColor Red
    Write-Host "   Please start containers: docker compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ MQTT Container: $mqttContainer" -ForegroundColor Green
Write-Host "✅ App Container: $appContainer" -ForegroundColor Green
Write-Host ""

# Step 2: Check MQTT Connection Status
Write-Host "Step 2: Checking MQTT Connection Status..." -ForegroundColor Yellow
Write-Host "Looking for connection logs in app container..." -ForegroundColor Gray

$connectionLogs = docker compose logs app --tail 100 | Select-String -Pattern "Connected to MQTT|Subscribed to: Dev/Init" | Select-Object -Last 5

if ($connectionLogs) {
    Write-Host "✅ MQTT Connection Found:" -ForegroundColor Green
    $connectionLogs | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  MQTT connection logs not found. Checking if app is running..." -ForegroundColor Yellow
    $appLogs = docker compose logs app --tail 20
    if ($appLogs) {
        Write-Host "   Recent app logs:" -ForegroundColor Gray
        $appLogs | Select-Object -Last 5 | ForEach-Object {
            Write-Host "   $_" -ForegroundColor Gray
        }
    }
}
Write-Host ""

# Step 3: Generate a unique test serial number
Write-Host "Step 3: Preparing Test Message..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testSerialNumber = "TEST$timestamp"
$topic = "Dev/Init/$testSerialNumber"
$payload = '{"SerialNumber": "' + $testSerialNumber + '"}'

Write-Host "   Serial Number: $testSerialNumber" -ForegroundColor Cyan
Write-Host "   Topic: $topic" -ForegroundColor Cyan
Write-Host "   Payload: $payload" -ForegroundColor Cyan
Write-Host ""

# Step 4: Clear previous logs to see fresh messages
Write-Host "Step 4: Clearing old logs (showing last 10 lines only)..." -ForegroundColor Yellow
docker compose logs app --tail 10 > $null
Write-Host ""

# Step 5: Publish test message
Write-Host "Step 5: Publishing Test Message to MQTT..." -ForegroundColor Yellow
Write-Host "   Command: docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t `"$topic`" -m `"$payload`"" -ForegroundColor Gray

$publishResult = docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t $topic -m $payload 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Message published successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to publish message!" -ForegroundColor Red
    Write-Host "   Error: $publishResult" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: Wait a moment for processing
Write-Host "Step 6: Waiting for message processing (3 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host ""

# Step 7: Check if message was received
Write-Host "Step 7: Checking if Server Received the Message..." -ForegroundColor Yellow
Write-Host "Looking for logs containing: '$testSerialNumber' or 'Device initialization'" -ForegroundColor Gray

$receivedLogs = docker compose logs app --tail 50 | Select-String -Pattern "$testSerialNumber|Device initialization|Message received|SerialNumber" -Context 2,2

if ($receivedLogs) {
    Write-Host "✅ Message Received! Logs found:" -ForegroundColor Green
    $receivedLogs | ForEach-Object {
        if ($_ -match $testSerialNumber -or $_ -match "Device initialization" -or $_ -match "Message received") {
            Write-Host "   $_" -ForegroundColor Green
        } else {
            Write-Host "   $_" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "⚠️  Message reception logs not found. Checking all recent logs..." -ForegroundColor Yellow
    $allLogs = docker compose logs app --tail 30
    Write-Host "   Recent logs:" -ForegroundColor Gray
    $allLogs | Select-Object -Last 10 | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Gray
    }
}
Write-Host ""

# Step 8: Check if device was registered
Write-Host "Step 8: Checking Device Registration Status..." -ForegroundColor Yellow
Write-Host "Looking for logs containing: 'registered|Registering|New device'" -ForegroundColor Gray

$registrationLogs = docker compose logs app --tail 50 | Select-String -Pattern "$testSerialNumber.*registered|Registering.*$testSerialNumber|New device.*$testSerialNumber|Device registered" -Context 1,1

if ($registrationLogs) {
    Write-Host "✅ Device Registration Found:" -ForegroundColor Green
    $registrationLogs | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Registration logs not found for this serial number." -ForegroundColor Yellow
}
Write-Host ""

# Step 9: Check for acknowledgment
Write-Host "Step 9: Checking for Acknowledgment..." -ForegroundColor Yellow
Write-Host "Looking for acknowledgment logs..." -ForegroundColor Gray

$ackLogs = docker compose logs app --tail 50 | Select-String -Pattern "Ack|acknowledgment|publish_ack" -Context 1,1

if ($ackLogs) {
    Write-Host "✅ Acknowledgment Found:" -ForegroundColor Green
    $ackLogs | Select-Object -Last 3 | ForEach-Object {
        Write-Host "   $_" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  Acknowledgment logs not found." -ForegroundColor Yellow
}
Write-Host ""

# Step 10: Verify in database (using Python script if available)
Write-Host "Step 10: Database Verification..." -ForegroundColor Yellow
Write-Host "To verify in database, run this SQL query in InfluxDB Cloud UI:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   SELECT * FROM `"Device_info`" " -ForegroundColor White
Write-Host "   WHERE `"Sr_No`" = '$testSerialNumber' " -ForegroundColor White
Write-Host "   AND time > now() - interval '1 day'" -ForegroundColor White
Write-Host ""

# Step 11: Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Serial Number: $testSerialNumber" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Check full logs: docker compose logs app --tail 100" -ForegroundColor White
Write-Host "2. Check MQTT subscription: docker compose logs app | Select-String -Pattern 'Subscribed to: Dev/Init'" -ForegroundColor White
Write-Host "3. Verify in database using the SQL query above" -ForegroundColor White
Write-Host "4. Test with real device by sending to topic: Dev/Init/YOUR_SERIAL_NUMBER" -ForegroundColor White
Write-Host ""

# Step 12: Monitor live logs (optional)
Write-Host "Would you like to monitor live logs? (Y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Monitoring live logs (Press Ctrl+C to stop)..." -ForegroundColor Cyan
    Write-Host "Looking for: '$testSerialNumber', 'Dev/Init', 'SerialNumber'" -ForegroundColor Gray
    Write-Host ""
    docker compose logs -f app | Select-String -Pattern "$testSerialNumber|Dev/Init|SerialNumber|Device initialization"
}

