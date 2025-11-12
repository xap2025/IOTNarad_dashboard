# MQTT Device Initialization Testing Guide

## 📋 Overview
यह guide आपको बताता है कि कैसे check करें:
1. MQTT connection सही से हो रहा है या नहीं
2. Server `Dev/Init/#` topic पर subscribe हो रहा है या नहीं
3. Device से आने वाले JSON messages receive हो रहे हैं या नहीं
4. नया SerialNumber database में save हो रहा है या नहीं

---

## 🔍 Step-by-Step Testing

### Step 1: Check MQTT Connection Status

**PowerShell Command:**
```powershell
docker compose logs app | Select-String -Pattern "Connected to MQTT|Subscribed to: Dev/Init"
```

**Expected Output:**
```
✅ Connected to MQTT Broker: mqtt:1883
📡 Subscribed to: Dev/Init/#
```

**अगर connection नहीं दिख रहा:**
- Check करें containers running हैं: `docker ps`
- App container restart करें: `docker compose restart app`
- Full logs देखें: `docker compose logs app --tail 100`

---

### Step 2: Test Message Publishing

**PowerShell Command:**
```powershell
# Test serial number
$serialNumber = "DF5647"
$topic = "Dev/Init/$serialNumber"
$payload = '{"SerialNumber": "' + $serialNumber + '"}'

docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t $topic -m $payload
```

**या comprehensive test script use करें:**
```powershell
.\test_mqtt_device_init.ps1
```

---

### Step 3: Check if Message was Received

**PowerShell Command:**
```powershell
docker compose logs app --tail 50 | Select-String -Pattern "Message received|Device initialization|DF5647|SerialNumber"
```

**Expected Output:**
```
📨 Message received on Dev/Init/DF5647: {"SerialNumber":"DF5647"}
🔔 Routing to init callback for topic: Dev/Init/DF5647
📨 Device initialization message received on topic: Dev/Init/DF5647
   Payload: {'SerialNumber': 'DF5647'}
🔍 Processing serial number: DF5647
```

---

### Step 4: Check Device Registration

**PowerShell Command:**
```powershell
docker compose logs app --tail 50 | Select-String -Pattern "registered|Registering|New device|DF5647"
```

**Expected Output (for new device):**
```
🆕 New device detected. Registering serial number: DF5647
✅ Device registered successfully!
   Serial Number: DF5647
   Measurement: Device_info
   Owner: Unassigned
   Date of Register: 2024-01-20
   Device Name: Unnamed
```

**Expected Output (for existing device):**
```
ℹ️ Device already registered: DF5647
```

---

### Step 5: Check Acknowledgment

**PowerShell Command:**
```powershell
docker compose logs app --tail 50 | Select-String -Pattern "Ack|acknowledgment|publish_ack"
```

**Expected Output:**
```
📤 Published to Dev/Init/Ack/DF5647: {"status":"success","message":"Device registered successfully","timestamp":"2024-01-20T10:30:00Z"}
```

**MQTT Subscribe से verify करें:**
```powershell
# Another terminal में run करें
docker exec -i iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/Ack/#" -v
```

---

### Step 6: Verify in Database

**InfluxDB Cloud UI में SQL Query:**
```sql
SELECT * FROM "Device_info" 
WHERE "Sr_No" = 'DF5647' 
AND time > now() - interval '1 day'
ORDER BY time DESC
LIMIT 10
```

**Expected Result:**
- एक record दिखना चाहिए
- `Sr_No` tag = 'DF5647'
- `Owner` field = 'Unassigned'
- `Device_Name` field = 'Unnamed'
- `Date_Of_Register` field = आज की date

---

## 🚀 Quick Test Scripts

### 1. Comprehensive Test (Recommended)
```powershell
.\test_mqtt_device_init.ps1
```
यह script automatically सभी checks करती है और detailed report देती है।

### 2. Subscribe to Messages (Real-time Monitoring)
```powershell
.\tools\test_mqtt_subscribe_init.ps1
```
यह script `Dev/Init/#` topic पर subscribe करके real-time messages दिखाती है।

### 3. Manual Test
```powershell
# Publish test message
$serialNumber = "TEST$(Get-Date -Format 'yyyyMMddHHmmss')"
$topic = "Dev/Init/$serialNumber"
$payload = '{"SerialNumber": "' + $serialNumber + '"}'
docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t $topic -m $payload

# Check logs immediately
docker compose logs app --tail 30
```

---

## 📊 Message Flow

### 1. Device Sends Message
**Topic:** `Dev/Init/DF5647`  
**Payload:**
```json
{"SerialNumber": "DF5647"}
```

### 2. Server Receives & Processes
- MQTT client receives message on `Dev/Init/#` topic
- Routes to `on_device_init_received` callback
- Extracts `SerialNumber` from payload
- Checks if serial number exists in database

### 3. Server Registers Device (if new)
- Creates new record in `Device_info` measurement
- Sets default values:
  - `Owner`: "Unassigned"
  - `Device_Name`: "Unnamed"
  - `Date_Of_Register`: Current date

### 4. Server Sends Acknowledgment
**Topic:** `Dev/Init/Ack/DF5647`  
**Payload:**
```json
{
  "status": "success",
  "message": "Device registered successfully",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## ✅ Verification Checklist

- [ ] MQTT connection established
- [ ] Subscribed to `Dev/Init/#` topic
- [ ] Message received on server
- [ ] JSON payload parsed correctly
- [ ] SerialNumber extracted from payload
- [ ] Database check performed
- [ ] New device registered (if new serial number)
- [ ] Acknowledgment sent to device
- [ ] Database record created/verified

---

## 🔧 Troubleshooting

### Issue 1: MQTT Connection Failed
**Symptoms:**
- Logs में "Failed to connect to MQTT Broker" दिख रहा है

**Solution:**
```powershell
# Check if MQTT container is running
docker ps | Select-String "mqtt"

# Restart containers
docker compose restart

# Check MQTT container logs
docker compose logs mqtt
```

### Issue 2: Message Not Received
**Symptoms:**
- Message publish हो गया लेकिन server logs में नहीं दिख रहा

**Solution:**
```powershell
# Verify subscription
docker compose logs app | Select-String "Subscribed to: Dev/Init"

# Check topic name (should be exactly "Dev/Init/#")
# Check if message is being published to correct topic

# Subscribe manually to verify message is reaching broker
docker exec -i iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/#" -v
```

### Issue 3: SerialNumber Not Extracted
**Symptoms:**
- Message received लेकिन "SerialNumber not found in payload" error

**Solution:**
- Verify JSON format: `{"SerialNumber": "DF5647"}`
- Check for extra spaces or special characters
- Ensure payload is valid JSON

### Issue 4: Device Not Saved to Database
**Symptoms:**
- Logs में "Device registered successfully" दिख रहा लेकिन database में नहीं है

**Solution:**
```powershell
# Check InfluxDB connection
docker compose logs app | Select-String "Device Info Service connected"

# Check for database errors
docker compose logs app | Select-String "Error.*registering device|InfluxDB"

# Verify InfluxDB credentials in .env file
# Check bucket and org names are correct
```

### Issue 5: Acknowledgment Not Sent
**Symptoms:**
- Device registered लेकिन acknowledgment नहीं भेजा गया

**Solution:**
```powershell
# Check MQTT publish logs
docker compose logs app | Select-String "Published to Dev/Init/Ack"

# Verify MQTT client is connected when publishing
docker compose logs app | Select-String "MQTT client not connected"
```

---

## 📝 Test with Real Device

जब आपका real device data भेजेगा:

1. **Device Configuration:**
   - MQTT Broker: Your server IP or domain
   - Port: 1883
   - Topic: `Dev/Init/YOUR_SERIAL_NUMBER`
   - Payload: `{"SerialNumber": "YOUR_SERIAL_NUMBER"}`

2. **Monitor in Real-time:**
   ```powershell
   # Terminal 1: Monitor server logs
   docker compose logs -f app | Select-String "Dev/Init|SerialNumber|registered"
   
   # Terminal 2: Subscribe to MQTT topic
   docker exec -i iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/#" -v
   ```

3. **Verify Registration:**
   - Check logs for registration message
   - Verify in database using SQL query
   - Check acknowledgment was sent

---

## 🔗 Related Files

- `app/services/mqtt_client.py` - MQTT client service
- `app/services/device_info_service.py` - Device registration service
- `app/main.py` - Main application (contains init callback)
- `test_mqtt_device_init.ps1` - Comprehensive test script
- `tools/test_mqtt_subscribe_init.ps1` - MQTT subscribe test
- `DEVICE_INIT_GUIDE.md` - Device initialization guide

---

## 📞 Support

अगर कोई issue है:
1. Full logs check करें: `docker compose logs app --tail 100`
2. MQTT container logs check करें: `docker compose logs mqtt --tail 50`
3. Database connection verify करें
4. Test script run करें और output share करें

