# PowerShell script to delete Device_Config_Analog measurement from InfluxDB
# This will delete ALL data from Device_Config_Analog measurement

Write-Host "🔍 Checking InfluxDB connection..." -ForegroundColor Yellow

# Get InfluxDB environment variables from .env file or docker-compose
# You'll need to set these or get them from your environment

$BUCKET = $env:INFLUXDB_BUCKET
$ORG = $env:INFLUXDB_ORG
$TOKEN = $env:INFLUXDB_TOKEN

if (-not $BUCKET -or -not $ORG -or -not $TOKEN) {
    Write-Host "❌ Error: InfluxDB credentials not found in environment variables" -ForegroundColor Red
    Write-Host "Please set INFLUXDB_BUCKET, INFLUXDB_ORG, and INFLUXDB_TOKEN" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ InfluxDB Credentials found:" -ForegroundColor Green
Write-Host "   Bucket: $BUCKET" -ForegroundColor Cyan
Write-Host "   Org: $ORG" -ForegroundColor Cyan

Write-Host "`n⚠️  WARNING: This will DELETE ALL DATA from 'Device_Config_Analog' measurement!" -ForegroundColor Red
Write-Host "Press Ctrl+C to cancel, or any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Flux query to delete all data from Device_Config_Analog measurement
$deleteQuery = @"
from(bucket: "$BUCKET")
  |> range(start: 1970-01-01T00:00:00Z)
  |> filter(fn: (r) => r["_measurement"] == "Device_Config_Analog")
  |> delete()
"@

Write-Host "`n🔍 Executing delete query..." -ForegroundColor Yellow

# Execute delete query using InfluxDB CLI in Docker container
docker exec -i iotnarad_influxdb influx delete \
    --org "$ORG" \
    --bucket "$BUCKET" \
    --token "$TOKEN" \
    --start 1970-01-01T00:00:00Z \
    --stop 2099-12-31T23:59:59Z \
    --predicate '_measurement="Device_Config_Analog"'

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Successfully deleted all data from Device_Config_Analog measurement!" -ForegroundColor Green
    Write-Host "   You can now save fresh data with float type for 'value' field" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Error deleting data. Please check the error message above." -ForegroundColor Red
    Write-Host "`nAlternative method: Use InfluxDB UI Data Explorer" -ForegroundColor Yellow
}

