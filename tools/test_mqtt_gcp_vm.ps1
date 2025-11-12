# MQTT Testing Script for GCP VM (Windows PowerShell)
# Usage: .\test_mqtt_gcp_vm.ps1 -VM_IP "YOUR_VM_EXTERNAL_IP"

param(
    [Parameter(Mandatory=$true)]
    [string]$VM_IP,
    
    [int]$Port = 1883
)

Write-Host "🧪 Testing MQTT Connection to GCP VM: $VM_IP:$Port" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
$dockerAvailable = $false
try {
    docker --version | Out-Null
    $dockerAvailable = $true
} catch {
    Write-Host "⚠️  Docker not found. Will try direct connection if mosquitto-clients installed." -ForegroundColor Yellow
}

# Test 1: Check connectivity
Write-Host "1️⃣ Testing network connectivity..." -ForegroundColor Yellow
try {
    $connection = Test-NetConnection -ComputerName $VM_IP -Port $Port -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "   ✅ Port $Port is open and accessible" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Port $Port is not accessible" -ForegroundColor Red
        Write-Host "   💡 Check GCP firewall rules!" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ⚠️  Could not test connectivity: $_" -ForegroundColor Yellow
}

# Test 2: Publish test message
Write-Host ""
Write-Host "2️⃣ Publishing test message..." -ForegroundColor Yellow

$testTopic = "test/gcp/external"
$testPayload = @{
    test = $true
    client = "powershell_external"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    vm_ip = $VM_IP
} | ConvertTo-Json -Compress

if ($dockerAvailable) {
    Write-Host "   Using Docker to publish..." -ForegroundColor Gray
    try {
        docker run --rm eclipse-mosquitto:2 mosquitto_pub `
            -h $VM_IP `
            -p $Port `
            -t $testTopic `
            -m $testPayload
        Write-Host "   ✅ Message published successfully" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Failed to publish: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  Docker not available. Install mosquitto-clients or Docker Desktop." -ForegroundColor Yellow
    Write-Host "   📝 Manual command:" -ForegroundColor Gray
    Write-Host "      mosquitto_pub -h $VM_IP -p $Port -t $testTopic -m '$testPayload'" -ForegroundColor Gray
}

# Test 3: Subscribe to messages (5 seconds)
Write-Host ""
Write-Host "3️⃣ Subscribing to all topics (5 seconds)..." -ForegroundColor Yellow

if ($dockerAvailable) {
    Write-Host "   Listening for messages..." -ForegroundColor Gray
    Write-Host "   (Publish a message from VM to see it here)" -ForegroundColor Gray
    Write-Host ""
    
    try {
        docker run --rm eclipse-mosquitto:2 mosquitto_sub `
            -h $VM_IP `
            -p $Port `
            -t '#' `
            -v `
            -W 5
        Write-Host ""
        Write-Host "   ✅ Subscription test complete" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Failed to subscribe: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  Docker not available. Install mosquitto-clients or Docker Desktop." -ForegroundColor Yellow
    Write-Host "   📝 Manual command:" -ForegroundColor Gray
    Write-Host "      mosquitto_sub -h $VM_IP -p $Port -t '#' -v" -ForegroundColor Gray
}

# Test 4: Test device data topic
Write-Host ""
Write-Host "4️⃣ Testing device data topic..." -ForegroundColor Yellow

$deviceTopic = "iotnarad/devices/test_device_01/data"
$devicePayload = @{
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    sensors = @{
        temperature = 25.5
        humidity = 65.2
    }
    production = @{
        line_id = "Line_A"
        units_produced = 1250
        oee = 89.2
        status = "running"
    }
} | ConvertTo-Json -Depth 10 -Compress

if ($dockerAvailable) {
    try {
        docker run --rm eclipse-mosquitto:2 mosquitto_pub `
            -h $VM_IP `
            -p $Port `
            -t $deviceTopic `
            -m $devicePayload
        Write-Host "   ✅ Device data published successfully" -ForegroundColor Green
        Write-Host "   📝 Check dashboard logs on VM: docker logs iotnarad_app -f" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ Failed to publish device data: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Testing complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. SSH into your GCP VM" -ForegroundColor Gray
Write-Host "   2. Run: docker logs iotnarad_app -f" -ForegroundColor Gray
Write-Host "   3. Check if messages are being received" -ForegroundColor Gray
Write-Host ""

