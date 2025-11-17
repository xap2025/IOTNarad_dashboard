# Reset InfluxDB for Fresh UI Setup
# This will DELETE all existing InfluxDB data!

Write-Host "⚠️  WARNING: This will DELETE all InfluxDB data!" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to cancel, or Enter to continue..." -ForegroundColor Yellow
Read-Host

Write-Host "🛑 Stopping InfluxDB container..." -ForegroundColor Cyan
docker compose stop influxdb

Write-Host "🗑️  Removing InfluxDB volume (all data will be deleted)..." -ForegroundColor Cyan
docker volume rm iotnarad_dashboard_influxdb-data

Write-Host "✅ InfluxDB reset complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update docker-compose.yml to use UI setup mode"
Write-Host "2. Run: docker compose up -d influxdb"
Write-Host "3. Open: http://localhost:8086"
Write-Host "4. Complete the setup form in browser"

