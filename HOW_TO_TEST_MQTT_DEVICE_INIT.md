# MQTT Device Initialization Testing - Complete Guide

## 🎯 आपका सवाल
1. MQTT connection सही से हो रहा है या नहीं?
2. Server `Dev/Init/#` topic पर subscribe हो रहा है या नहीं?
3. Device से JSON format में data आ रहा है या नहीं?
4. नया SerialNumber database में save हो रहा है या नहीं?

---

## ✅ जवाब: Step-by-Step Testing

### 🚀 Quick Test (सबसे आसान तरीका)

**PowerShell में run करें:**
```powershell
.\test_mqtt_device_init.ps1
```

यह script automatically सभी checks करती है:
- ✅ Docker containers running हैं या नहीं
- ✅ MQTT connection established है या नहीं
- ✅ `Dev/Init/#` topic पर subscribe हो रहा है या नहीं
- ✅ Test message publish और receive हो रहा है या नहीं
- ✅ Device database में save हो रहा है या नहीं

---

## 📋 Manual Testing (Step by Step)

### Step 1: MQTT Connection Check

```powershell
docker compose logs app | Select-String "Connected to MQTT|Subscribed to: Dev/Init"
```

**Expected Output:**
```
✅ Connected to MQTT Broker: mqtt:1883
📡 Subscribed to: Dev/Init/#
```

**अगर यह दिख रहा है तो:**
- ✅ MQTT connection सही से हो रहा है
- ✅ Server `Dev/Init/#` topic पर subscribe हो रहा है

---

### Step 2: Test Message Publish

**PowerShell Command:**
```powershell
$serialNumber = "DF5647"
$topic = "Dev/Init/$serialNumber"
$payload = '{"SerialNumber": "' + $serialNumber + '"}'

docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t $topic -m $payload
```

**यह command:**
- MQTT broker को एक test message भेजती है
- Topic: `Dev/Init/DF5647`
- Payload: `{"SerialNumber": "DF5647"}`

---

### Step 3: Check if Server Received Message

```powershell
docker compose logs app --tail 50 | Select-String "DF5647|Message received|Device initialization|SerialNumber"
```

**Expected Output:**
```
📨 Message received on Dev/Init/DF5647: {"SerialNumber":"DF5647"}...
🔔 Routing to init callback for topic: Dev/Init/DF5647
📨 Device initialization message received on topic: Dev/Init/DF5647
   Payload: {'SerialNumber': 'DF5647'}
🔍 Processing serial number: DF5647
```

**अगर यह दिख रहा है तो:**
- ✅ Server message receive कर रहा है
- ✅ JSON payload parse हो रहा है
- ✅ SerialNumber extract हो रहा है

---

### Step 4: Check Device Registration

```powershell
docker compose logs app --tail 50 | Select-String "DF5647.*registered|Registering.*DF5647|New device.*DF5647|Device registered"
```

**Expected Output (नए device के लिए):**
```
🆕 New device detected. Registering serial number: DF5647
✅ Device registered successfully!
   Serial Number: DF5647
   Measurement: Device_info
   Owner: Unassigned
   Date of Register: 2024-01-20
   Device Name: Unnamed
```

**Expected Output (existing device के लिए):**
```
ℹ️ Device already registered: DF5647
```

**अगर यह दिख रहा है तो:**
- ✅ Device database में register हो रहा है
- ✅ नया SerialNumber save हो रहा है

---

### Step 5: Verify in Database

**Python Script:**
```powershell
python check_device_in_database.py DF5647
```

**Expected Output:**
```
✅ Device 'DF5647' EXISTS in database
Device Information:
  Serial Number: DF5647
  Owner: Unassigned
  Device Name: Unnamed
  Date of Register: 2024-01-20
```

**अगर यह दिख रहा है तो:**
- ✅ Device database में successfully save हो गया है

---

### Step 6: Check Acknowledgment

```powershell
docker compose logs app --tail 50 | Select-String "Ack|acknowledgment|Published to Dev/Init/Ack"
```

**Expected Output:**
```
📤 Published to Dev/Init/Ack/DF5647: {"status":"success","message":"Device registered successfully","timestamp":"2024-01-20T10:30:00Z"}...
```

**अगर यह दिख रहा है तो:**
- ✅ Server device को acknowledgment भेज रहा है

---

## 🔍 Real-time Monitoring

### Monitor MQTT Messages (Real-time)

**Terminal 1 - Subscribe to MQTT Topic:**
```powershell
.\tools\test_mqtt_subscribe_init.ps1
```

या manually:
```powershell
docker exec -i iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/#" -v
```

यह command real-time में सभी `Dev/Init/#` topic पर आने वाले messages दिखाएगी।

---

### Monitor Server Logs (Real-time)

**Terminal 2 - Watch Server Logs:**
```powershell
docker compose logs -f app | Select-String "Dev/Init|SerialNumber|registered|Message received"
```

यह command real-time में server logs दिखाएगी।

---

## 📊 Complete Message Flow

### 1. Device भेजता है:
```
Topic: Dev/Init/DF5647
Payload: {"SerialNumber": "DF5647"}
```

### 2. MQTT Broker receive करता है:
- Message MQTT broker पर आता है
- Broker message को सभी subscribers को forward करता है

### 3. Server receive करता है:
- MQTT client message receive करता है
- `_on_message` callback call होता है
- Topic check होता है: `Dev/Init/` से start हो रहा है?
- JSON payload parse होता है

### 4. Server processes करता है:
- `on_device_init_received` callback call होता है
- SerialNumber extract होता है: `data.get('SerialNumber')`
- Database check होता है: SerialNumber exists है या नहीं?

### 5. Server registers device (अगर new है):
- `device_info_service.register_device()` call होता है
- InfluxDB में new record create होता है:
  - Measurement: `Device_info`
  - Tag: `Sr_No` = "DF5647"
  - Fields: `Owner` = "Unassigned", `Device_Name` = "Unnamed", `Date_Of_Register` = current date

### 6. Server acknowledgment भेजता है:
```
Topic: Dev/Init/Ack/DF5647
Payload: {
  "status": "success",
  "message": "Device registered successfully",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## ✅ Verification Checklist

- [ ] **MQTT Connection:** `docker compose logs app | Select-String "Connected to MQTT"`
- [ ] **Subscription:** `docker compose logs app | Select-String "Subscribed to: Dev/Init"`
- [ ] **Message Received:** `docker compose logs app | Select-String "Message received"`
- [ ] **JSON Parsed:** `docker compose logs app | Select-String "SerialNumber"`
- [ ] **Device Registered:** `docker compose logs app | Select-String "registered"`
- [ ] **Database Saved:** `python check_device_in_database.py DF5647`
- [ ] **Acknowledgment Sent:** `docker compose logs app | Select-String "Ack"`

---

## 🔧 Troubleshooting

### Problem 1: MQTT Connection नहीं हो रहा

**Check:**
```powershell
docker ps
docker compose logs app --tail 50
```

**Solution:**
```powershell
docker compose restart app
docker compose logs app -f
```

---

### Problem 2: Message Receive नहीं हो रहा

**Check:**
```powershell
# Verify subscription
docker compose logs app | Select-String "Subscribed to: Dev/Init"

# Test subscription manually
docker exec -i iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/#" -v
```

**Solution:**
- Topic name verify करें: `Dev/Init/#` (exactly यह format)
- MQTT broker running है या नहीं check करें
- App container restart करें

---

### Problem 3: JSON Parse Error

**Check:**
```powershell
docker compose logs app | Select-String "Failed to decode JSON"
```

**Solution:**
- JSON format verify करें: `{"SerialNumber": "DF5647"}`
- Extra spaces या special characters check करें
- Valid JSON होना चाहिए

---

### Problem 4: Device Database में Save नहीं हो रहा

**Check:**
```powershell
# Check database connection
docker compose logs app | Select-String "Device Info Service connected"

# Check for errors
docker compose logs app | Select-String "Error.*registering|Error.*InfluxDB"

# Verify manually
python check_device_in_database.py DF5647
```

**Solution:**
- InfluxDB credentials verify करें (.env file में)
- Database connection check करें
- Bucket और org names verify करें

---

## 📝 Test with Real Device

जब आपका real device data भेजेगा:

### Device Configuration:
- **MQTT Broker:** Your server IP or domain
- **Port:** 1883
- **Topic:** `Dev/Init/YOUR_SERIAL_NUMBER`
- **Payload:** `{"SerialNumber": "YOUR_SERIAL_NUMBER"}`

### Monitor:
```powershell
# Terminal 1: Monitor server logs
docker compose logs -f app | Select-String "Dev/Init|SerialNumber|registered"

# Terminal 2: Subscribe to MQTT
docker exec -i iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/#" -v
```

---

## 📚 Related Files

### Test Scripts:
- `test_mqtt_device_init.ps1` - Comprehensive automated test
- `tools/test_mqtt_subscribe_init.ps1` - MQTT subscribe test
- `check_device_in_database.py` - Database verification script

### Documentation:
- `MQTT_TESTING_GUIDE_DEVICE_INIT.md` - Detailed testing guide
- `MQTT_DEVICE_INIT_QUICK_TEST.md` - Quick reference
- `DEVICE_INIT_GUIDE.md` - Device initialization guide

### Code Files:
- `app/services/mqtt_client.py` - MQTT client service
- `app/services/device_info_service.py` - Device registration service
- `app/main.py` - Main application (contains init callback)

---

## 💡 Tips

1. **Always use unique serial numbers for testing** - Use timestamp: `TEST20240120103000`
2. **Monitor logs in real-time** - Use `docker compose logs -f app`
3. **Check database after 2-3 seconds** - Database write takes a moment
4. **Verify JSON format** - Must be valid JSON: `{"SerialNumber": "DF5647"}`
5. **Check both logs and database** - Sometimes logs show success but database has issues

---

## 🎯 Summary

### आपके सवालों के जवाब:

1. **MQTT connection सही से हो रहा है?**
   - ✅ Check: `docker compose logs app | Select-String "Connected to MQTT"`
   - ✅ Expected: `✅ Connected to MQTT Broker: mqtt:1883`

2. **Server `Dev/Init/#` topic पर subscribe हो रहा है?**
   - ✅ Check: `docker compose logs app | Select-String "Subscribed to: Dev/Init"`
   - ✅ Expected: `📡 Subscribed to: Dev/Init/#`

3. **Device से JSON format में data आ रहा है?**
   - ✅ Check: `docker compose logs app | Select-String "Message received|SerialNumber"`
   - ✅ Expected: `📨 Message received on Dev/Init/DF5647: {"SerialNumber":"DF5647"}`

4. **नया SerialNumber database में save हो रहा है?**
   - ✅ Check: `python check_device_in_database.py DF5647`
   - ✅ Expected: Device information with SerialNumber, Owner, Device_Name, etc.

---

## 🚀 Quick Start

**सबसे आसान तरीका:**
```powershell
.\test_mqtt_device_init.ps1
```

यह script automatically सभी checks करके detailed report देगी!

