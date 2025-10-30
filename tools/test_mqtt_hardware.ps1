# MQTT Hardware Simulation Script
# Simulates IoT Gateway sending data to dashboard

param(
    [string]$DeviceId = "esp32_gw_01",
    [int]$Interval = 5
)

Write-Host "🚀 Starting MQTT Hardware Simulator" -ForegroundColor Green
Write-Host "Device ID: $DeviceId" -ForegroundColor Cyan
Write-Host "Data Interval: $Interval seconds" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

$mqttContainer = "iotnarad_mqtt"
$baseTopic = "iotnarad/devices/$DeviceId"

# Test MQTT connection first
Write-Host "Testing MQTT connection..." -ForegroundColor Yellow
$testResult = docker exec $mqttContainer mosquitto_pub -h localhost -t "test/connection" -m "test" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ MQTT broker not accessible!" -ForegroundColor Red
    Write-Host "Make sure Docker container 'iotnarad_mqtt' is running" -ForegroundColor Red
    exit 1
}
Write-Host "✅ MQTT broker connected" -ForegroundColor Green
Write-Host ""

# Counter for simulation
$counter = 0

try {
    while ($true) {
        $counter++
        $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        
        # Simulate sensor data
        $temperature = 20 + (Get-Random -Minimum -5 -Maximum 10)
        $humidity = 60 + (Get-Random -Minimum -10 -Maximum 10)
        $pressure = 1000 + (Get-Random -Minimum -50 -Maximum 50)
        
        # Simulate production data
        $unitsProduced = 1000 + ($counter * 10)
        $oee = 80 + (Get-Random -Minimum -5 -Maximum 15)
        
        # Device Data Message
        $dataTopic = "$baseTopic/data"
        $dataPayload = @{
            timestamp = $timestamp
            sensors = @{
                temperature = [math]::Round($temperature, 1)
                humidity = [math]::Round($humidity, 1)
                pressure = [math]::Round($pressure, 2)
            }
            production = @{
                line_id = "Line_A"
                units_produced = $unitsProduced
                oee = [math]::Round($oee, 1)
                status = "running"
            }
            channels = @{
                analog_in_0 = [math]::Round(4.5 + (Get-Random -Minimum -1.0 -Maximum 1.0), 2)
                analog_in_1 = [math]::Round(3.2 + (Get-Random -Minimum -0.5 -Maximum 0.5), 2)
                digital_in_0 = (Get-Random -Minimum 0 -Maximum 2)
                digital_in_1 = (Get-Random -Minimum 0 -Maximum 2)
            }
        } | ConvertTo-Json -Compress
        
        # Device Status Message
        $statusTopic = "$baseTopic/status"
        $statusPayload = @{
            status = "online"
            timestamp = $timestamp
            uptime = $counter * $Interval
            firmware_version = "1.0.0"
            wifi_signal = -65 + (Get-Random -Minimum -10 -Maximum 10)
            mqtt_connected = $true
        } | ConvertTo-Json -Compress
        
        # Publish Device Data
        Write-Host "[$counter] 📤 Publishing data..." -ForegroundColor Cyan
        docker exec -i $mqttContainer mosquitto_pub -h localhost -p 1883 -t $dataTopic -m $dataPayload 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Data published to: $dataTopic" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Failed to publish data" -ForegroundColor Red
        }
        
        # Publish Device Status
        docker exec -i $mqttContainer mosquitto_pub -h localhost -p 1883 -t $statusTopic -m $statusPayload 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Status published to: $statusTopic" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Failed to publish status" -ForegroundColor Red
        }
        
        Write-Host "  📊 OEE: $oee%, Units: $unitsProduced, Temp: $temperature°C" -ForegroundColor Gray
        Write-Host ""
        
        Start-Sleep -Seconds $Interval
    }
} catch {
    Write-Host "`n⚠️ Simulation stopped" -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Red
}

