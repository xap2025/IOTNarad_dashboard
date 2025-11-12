# MQTT Device Initialization - Quick Test Guide

## 🚀 तुरंत Test करने के लिए

### Option 1: Automated Test Script (सबसे आसान)
```powershell
.\test_mqtt_device_init.ps1
```
यह script automatically सभी checks करती है।

---

### Option 2: Manual Test (Step by Step)

#### Step 1: MQTT Connection Check
```powershell
docker compose logs app | Select-String "Connected to MQTT|Subscribed to: Dev/Init"
```
**Expected:** `✅ Connected to MQTT Broker` और `📡 Subscribed to: Dev/Init/#`

#### Step 2: Test Message Publish
```powershell
$serialNumber = "DF5647"
$topic = "Dev/Init/$serialNumber"
$payload = '{"SerialNumber": "' + $serialNumber + '"}'
docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t $topic -m $payload
```

#### Step 3: Check Logs
```powershell
docker compose logs app --tail 30 | Select-String "DF5647|Message received|registered"
```
**Expected:** Message received और device registered के logs दिखने चाहिए

#### Step 4: Check Database
```powershell
python check_device_in_database.py DF5647
```
**Expected:** Device database में दिखना चाहिए

---

## 📋 Complete Flow

### 1. Device भेजता है:
```
Topic: Dev/Init/DF5647
Payload: {"SerialNumber": "DF5647"}
```

### 2. Server receive करता है:
- MQTT client message receive करता है
- `on_device_init_received` callback call होता है
- SerialNumber extract होता है

### 3. Server database check करता है:
- SerialNumber exists है या नहीं check करता है
- अगर new है → Register करता है
- अगर exists है → Ignore करता है

### 4. Server acknowledgment भेजता है:
```
Topic: Dev/Init/Ack/DF5647
Payload: {"status": "success", "message": "Device registered successfully"}
```

---

## ✅ Verification Commands

### Check MQTT Connection
```powershell
docker compose logs app | Select-String "Connected to MQTT"
```

### Check Subscription
```powershell
docker compose logs app | Select-String "Subscribed to: Dev/Init"
```

### Monitor Messages (Real-time)
```powershell
.\tools\test_mqtt_subscribe_init.ps1
```

### Check Device in Database
```powershell
python check_device_in_database.py DF5647
```

### List All Devices
```powershell
python check_device_in_database.py
```

---

## 🔍 Troubleshooting

### Problem: MQTT Connection नहीं हो रहा
```powershell
# Check containers
docker ps

# Restart app
docker compose restart app

# Check logs
docker compose logs app --tail 50
```

### Problem: Message receive नहीं हो रहा
```powershell
# Verify subscription
docker compose logs app | Select-String "Subscribed to: Dev/Init"

# Test subscription manually
docker exec -i iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/#" -v
```

### Problem: Device database में save नहीं हो रहा
```powershell
# Check database connection
docker compose logs app | Select-String "Device Info Service connected"

# Check for errors
docker compose logs app | Select-String "Error.*registering|Error.*InfluxDB"

# Verify device manually
python check_device_in_database.py DF5647
```

---

## 📝 Important Points

1. **Topic Format:** `Dev/Init/#` (wildcard # means all subtopics)
2. **Payload Format:** `{"SerialNumber": "DF5647"}` (must be valid JSON)
3. **Database:** InfluxDB Cloud में `Device_info` measurement में save होता है
4. **Acknowledgment:** Server हमेशा acknowledgment भेजता है

---

## 🎯 Quick Test Checklist

- [ ] MQTT connection established
- [ ] Subscribed to `Dev/Init/#`
- [ ] Test message published
- [ ] Message received in logs
- [ ] Device registered (if new)
- [ ] Acknowledgment sent
- [ ] Device verified in database

---

## 📚 Related Files

- `test_mqtt_device_init.ps1` - Comprehensive test script
- `tools/test_mqtt_subscribe_init.ps1` - MQTT subscribe test
- `check_device_in_database.py` - Database verification script
- `MQTT_TESTING_GUIDE_DEVICE_INIT.md` - Detailed guide
- `DEVICE_INIT_GUIDE.md` - Device initialization guide

---

## 💡 Tips

1. **Always use unique serial numbers for testing** - Use timestamp: `TEST20240120103000`
2. **Monitor logs in real-time** - Use `docker compose logs -f app`
3. **Check database after 2-3 seconds** - Database write takes a moment
4. **Verify JSON format** - Must be valid JSON: `{"SerialNumber": "DF5647"}`

