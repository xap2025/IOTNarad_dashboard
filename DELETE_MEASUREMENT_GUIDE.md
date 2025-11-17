# How to Delete Device_Config_Analog Measurement

यह guide आपको `Device_Config_Analog` measurement से सभी data delete करने में help करेगा, ताकि आप `float` type के साथ fresh start कर सकें।

## ⚠️ WARNING
इस operation से `Device_Config_Analog` measurement की **सभी data permanently delete** हो जाएगी!

---

## Method 1: PowerShell Script (Windows - Recommended)

```powershell
# Run the script
.\delete_measurement.ps1
```

Script automatically आपके `.env` file से InfluxDB credentials read करेगा।

---

## Method 2: Manual Command (Windows PowerShell)

```powershell
# First, set your InfluxDB credentials
$BUCKET = "iot_data_gcp"  # Replace with your bucket name
$ORG = "iot-narad-gcp"     # Replace with your org name  
$TOKEN = "your-token-here" # Replace with your token

# Delete all data from Device_Config_Analog measurement
docker exec -i iotnarad_influxdb influx delete `
    --org "$ORG" `
    --bucket "$BUCKET" `
    --token "$TOKEN" `
    --start 1970-01-01T00:00:00Z `
    --stop 2099-12-31T23:59:59Z `
    --predicate '_measurement="Device_Config_Analog"'
```

---

## Method 3: Bash Script (Linux/Mac)

```bash
# Make script executable
chmod +x delete_measurement.sh

# Run the script
./delete_measurement.sh
```

---

## Method 4: Manual Command (Linux/Mac)

```bash
# Set your InfluxDB credentials
export BUCKET="iot_data_gcp"       # Replace with your bucket name
export ORG="iot-narad-gcp"          # Replace with your org name
export TOKEN="your-token-here"      # Replace with your token

# Delete all data from Device_Config_Analog measurement
docker exec -i iotnarad_influxdb influx delete \
    --org "$ORG" \
    --bucket "$BUCKET" \
    --token "$TOKEN" \
    --start 1970-01-01T00:00:00Z \
    --stop 2099-12-31T23:59:59Z \
    --predicate '_measurement="Device_Config_Analog"'
```

---

## Method 5: Using InfluxDB UI (Browser)

1. **InfluxDB UI** खोलें: `http://localhost:8086`
2. Login करें
3. **Data Explorer** पर जाएं
4. **Script Editor** में निम्नलिखित Flux query run करें:

```flux
from(bucket: "iot_data_gcp")
  |> range(start: 1970-01-01T00:00:00Z)
  |> filter(fn: (r) => r["_measurement"] == "Device_Config_Analog")
  |> delete()
```

**Note:** InfluxDB UI में delete operation directly available नहीं हो सकता। Best approach CLI command use करना है।

---

## Method 6: Using InfluxDB REST API

```powershell
# PowerShell example
$BUCKET = "iot_data_gcp"
$ORG = "iot-narad-gcp"
$TOKEN = "your-token-here"

$headers = @{
    "Authorization" = "Token $TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    start = "1970-01-01T00:00:00Z"
    stop = "2099-12-31T23:59:59Z"
    predicate = '_measurement="Device_Config_Analog"'
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8086/api/v2/delete?org=$ORG&bucket=$BUCKET" `
    -Method Post `
    -Headers $headers `
    -Body $body
```

---

## Verification: Check if Data is Deleted

Data delete करने के बाद verify करें:

```powershell
# Query to check if Device_Config_Analog has any data
docker exec -i iotnarad_influxdb influx query `
    --org "$ORG" `
    --token "$TOKEN" `
    'from(bucket: "iot_data_gcp") |> range(start: -30d) |> filter(fn: (r) => r["_measurement"] == "Device_Config_Analog") |> count()'
```

अगर result `0` आए, तो data successfully delete हो गई है।

---

## After Deletion

1. ✅ `Device_Config_Analog` measurement अब empty है
2. ✅ Next time जब आप data save करेंगे, InfluxDB automatically `value` field के type को detect करेगा
3. ✅ अगर आप `float` type में data save करेंगे, तो `value` field `float` type में set हो जाएगी
4. ✅ आपका code अब बिना error के work करेगा!

---

## Troubleshooting

### Error: "container iotnarad_influxdb not found"
```powershell
# Check if InfluxDB container is running
docker ps | grep influxdb

# If not running, start it
docker compose up -d influxdb
```

### Error: "authentication failed"
- Check आपका `TOKEN` correct है या नहीं
- `.env` file में credentials verify करें

### Error: "bucket not found"
- Verify `BUCKET` name correct है
- InfluxDB UI में bucket exists है या नहीं check करें

---

## Next Steps

Data delete करने के बाद:

1. ✅ अपने code में `float(channel_value)` use करें (जैसा आपने already किया है)
2. ✅ Save Configuration button click करें
3. ✅ Data successfully save होनी चाहिए with `float` type
4. ✅ Verify करें InfluxDB UI में कि `value` field अब `float` type में है

