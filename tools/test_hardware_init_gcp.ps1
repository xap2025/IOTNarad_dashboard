# Test Hardware Device Initialization on GCP VM
# Simulates hardware sending initialization message and monitors acknowledgment
# Usage: .\test_hardware_init_gcp.ps1 -VM_IP "34.131.186.225" -SerialNumber "DF5647"

param(
    [Parameter(Mandatory=$true)]
    [string]$VM_IP,
    
    [Parameter(Mandatory=$false)]
    [string]$SerialNumber = "DF5647",
    
    [int]$Port = 1883
)

Write-Host "🧪 Testing Hardware Device Initialization on GCP VM" -ForegroundColor Cyan
Write-Host "   VM IP: $VM_IP" -ForegroundColor Gray
Write-Host "   Serial Number: $SerialNumber" -ForegroundColor Gray
Write-Host ""

# Check if Docker is available
$dockerAvailable = $false
try {
    docker --version | Out-Null
    $dockerAvailable = $true
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Test 1: Check connectivity
Write-Host "1️⃣ Testing network connectivity..." -ForegroundColor Yellow
try {
    $connection = Test-NetConnection -ComputerName $VM_IP -Port $Port -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "   ✅ Port $Port is accessible" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Port $Port is not accessible" -ForegroundColor Red
        Write-Host "   💡 Check GCP firewall rules!" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ⚠️  Could not test connectivity: $_" -ForegroundColor Yellow
}

# Test 2: Subscribe to acknowledgment topic (in background)
Write-Host ""
Write-Host "2️⃣ Starting acknowledgment monitor..." -ForegroundColor Yellow
$ackTopic = "Dev/Ack/$SerialNumber"
Write-Host "   Listening on: $ackTopic" -ForegroundColor Gray

$ackJob = Start-Job -ScriptBlock {
    param($vmIP, $port, $topic)
    docker run --rm eclipse-mosquitto:2 mosquitto_sub `
        -h $vmIP `
        -p $port `
        -t $topic `
        -v `
        -W 30
} -ArgumentList $VM_IP, $Port, $ackTopic

Start-Sleep -Seconds 2

# Test 3: Publish device initialization message
Write-Host ""
Write-Host "3️⃣ Publishing device initialization message..." -ForegroundColor Yellow

$initTopic = "Dev/Init/$SerialNumber"
$payload = @{
    SerialNumber = $SerialNumber
} | ConvertTo-Json -Compress

Write-Host "   Topic: $initTopic" -ForegroundColor Gray
Write-Host "   Payload: $payload" -ForegroundColor Gray

try {
    docker run --rm eclipse-mosquitto:2 mosquitto_pub `
        -h $VM_IP `
        -p $Port `
        -t $initTopic `
        -m $payload
    
    Write-Host "   ✅ Initialization message sent successfully" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to send message: $_" -ForegroundColor Red
    Stop-Job $ackJob
    Remove-Job $ackJob
    exit 1
}

# Test 4: Wait for acknowledgment
Write-Host ""
Write-Host "4️⃣ Waiting for acknowledgment (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$ackResult = Receive-Job -Job $ackJob -Wait -Timeout 30
Stop-Job $ackJob
Remove-Job $ackJob

if ($ackResult) {
    Write-Host "   ✅ Acknowledgment received!" -ForegroundColor Green
    foreach ($line in $ackResult) {
        Write-Host "   $line" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ⚠️  No acknowledgment received within 30 seconds" -ForegroundColor Yellow
    Write-Host "   💡 Check server logs: docker logs iotnarad_app -f" -ForegroundColor Gray
}

# Test 5: Verify message format
Write-Host ""
Write-Host "5️⃣ Testing with different serial numbers..." -ForegroundColor Yellow

$testSerials = @("TEST001", "TEST002", "DF5647")
foreach ($testSerial in $testSerials) {
    Write-Host "   Testing serial: $testSerial" -ForegroundColor Gray
    $testTopic = "Dev/Init/$testSerial"
    $testPayload = @{ SerialNumber = $testSerial } | ConvertTo-Json -Compress
    
    try {
        docker run --rm eclipse-mosquitto:2 mosquitto_pub `
            -h $VM_IP `
            -p $Port `
            -t $testTopic `
            -m $testPayload | Out-Null
        Write-Host "      ✅ Sent" -ForegroundColor Green
    } catch {
        Write-Host "      ❌ Failed" -ForegroundColor Red
    }
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "✅ Testing complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. SSH into GCP VM: gcloud compute ssh YOUR_VM_NAME" -ForegroundColor Gray
Write-Host "   2. Check server logs: docker logs iotnarad_app -f" -ForegroundColor Gray
Write-Host "   3. Verify database: Check if device is registered" -ForegroundColor Gray
Write-Host ""

