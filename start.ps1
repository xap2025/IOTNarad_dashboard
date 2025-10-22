# IOTNarad Dashboard Startup Script
# PowerShell script to start the application

Write-Host "🚀 Starting IOTNarad Dashboard..." -ForegroundColor Cyan

# Check if .env exists
if (!(Test-Path .env)) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ Please edit .env with your configuration" -ForegroundColor Green
    Write-Host ""
}

# Create data directory
if (!(Test-Path data\configs)) {
    Write-Host "📁 Creating data directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path data\configs -Force | Out-Null
}

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Stop existing containers
Write-Host ""
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down

# Build and start
Write-Host ""
Write-Host "🔨 Building and starting services..." -ForegroundColor Cyan
docker-compose up -d --build

# Wait for services to start
Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check status
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "✅ IOTNarad Dashboard is starting!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Dashboard URL: http://localhost:8050" -ForegroundColor Cyan
Write-Host "📡 MQTT Broker: localhost:1883" -ForegroundColor Cyan
Write-Host "💾 InfluxDB: http://localhost:8086" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔐 Login Credentials:" -ForegroundColor Yellow
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: iotnarad@2025" -ForegroundColor White
Write-Host ""
Write-Host "📋 View logs: docker-compose logs -f app" -ForegroundColor Gray
Write-Host "🛑 Stop services: docker-compose down" -ForegroundColor Gray
Write-Host ""
Write-Host "Happy Monitoring! 🎉" -ForegroundColor Green

