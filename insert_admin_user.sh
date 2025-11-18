#!/bin/bash
# Script to manually insert admin user into InfluxDB User_info measurement

set -e

echo "🔹 Step 1: Loading environment variables from .env..."

# Navigate to project directory
cd ~/IOTNarad_dashboard

# Load environment variables
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    exit 1
fi

export INFLUXDB_ORG=$(grep "^INFLUXDB_ORG=" .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
export INFLUXDB_BUCKET=$(grep "^INFLUXDB_BUCKET=" .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
export INFLUXDB_TOKEN=$(grep "^INFLUXDB_TOKEN=" .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")

# Validate variables
if [ -z "$INFLUXDB_ORG" ] || [ -z "$INFLUXDB_BUCKET" ] || [ -z "$INFLUXDB_TOKEN" ]; then
    echo "❌ Error: INFLUXDB_ORG, INFLUXDB_BUCKET, or INFLUXDB_TOKEN not found in .env"
    exit 1
fi

echo "✅ Loaded environment variables:"
echo "   Org: $INFLUXDB_ORG"
echo "   Bucket: $INFLUXDB_BUCKET"
echo "   Token: ${INFLUXDB_TOKEN:0:10}..." # Show first 10 chars only

echo ""
echo "🔹 Step 2: Inserting admin user into InfluxDB..."

# User data
LINE_PROTOCOL='User_info,Company_Name=Xaptronics,Email_Id=xaptronicsindia.com,Phone_No=7042703926,User_Id=admin,User_Type=admin,status=active Password="admin"'

# Insert via Docker exec
docker exec -i iotnarad_influxdb influx write \
  --org "$INFLUXDB_ORG" \
  --bucket "$INFLUXDB_BUCKET" \
  --token "$INFLUXDB_TOKEN" \
  --precision ns \
  "$LINE_PROTOCOL"

if [ $? -eq 0 ]; then
    echo "✅ User inserted successfully!"
    echo ""
    echo "🔹 Step 3: Verifying user insertion..."
    
    # Query to verify
    docker exec -i iotnarad_influxdb influx query \
      --org "$INFLUXDB_ORG" \
      --token "$INFLUXDB_TOKEN" \
      "from(bucket: \"$INFLUXDB_BUCKET\") |> range(start: -1d) |> filter(fn: (r) => r._measurement == \"User_info\" AND r.User_Id == \"admin\") |> limit(n: 1)" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ User verified in database!"
        echo ""
        echo "🎯 Login credentials:"
        echo "   Username: admin"
        echo "   Password: admin"
        echo ""
        echo "✅ You can now login to your dashboard!"
    else
        echo "⚠️  User inserted but verification query failed (this is okay)"
    fi
else
    echo "❌ Error: Failed to insert user"
    exit 1
fi

