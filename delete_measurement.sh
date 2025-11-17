#!/bin/bash
# Bash script to delete Device_Config_Analog measurement from InfluxDB
# This will delete ALL data from Device_Config_Analog measurement

echo "🔍 Checking InfluxDB connection..."

# Get InfluxDB environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

BUCKET=${INFLUXDB_BUCKET}
ORG=${INFLUXDB_ORG}
TOKEN=${INFLUXDB_TOKEN}

if [ -z "$BUCKET" ] || [ -z "$ORG" ] || [ -z "$TOKEN" ]; then
    echo "❌ Error: InfluxDB credentials not found in environment variables"
    echo "Please set INFLUXDB_BUCKET, INFLUXDB_ORG, and INFLUXDB_TOKEN in .env file"
    exit 1
fi

echo "✅ InfluxDB Credentials found:"
echo "   Bucket: $BUCKET"
echo "   Org: $ORG"

echo ""
echo "⚠️  WARNING: This will DELETE ALL DATA from 'Device_Config_Analog' measurement!"
read -p "Press Enter to continue, or Ctrl+C to cancel..."

echo ""
echo "🔍 Executing delete query..."

# Execute delete query using InfluxDB CLI in Docker container
docker exec -i iotnarad_influxdb influx delete \
    --org "$ORG" \
    --bucket "$BUCKET" \
    --token "$TOKEN" \
    --start 1970-01-01T00:00:00Z \
    --stop 2099-12-31T23:59:59Z \
    --predicate '_measurement="Device_Config_Analog"'

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully deleted all data from Device_Config_Analog measurement!"
    echo "   You can now save fresh data with float type for 'value' field"
else
    echo ""
    echo "❌ Error deleting data. Please check the error message above."
    echo ""
    echo "Alternative method: Use InfluxDB UI Data Explorer"
fi

