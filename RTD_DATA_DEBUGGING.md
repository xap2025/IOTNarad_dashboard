# 🔍 RTD Data Debugging Guide

## ✅ Verification: Code Changes Did NOT Affect Data Saving

### **Files Changed (Analytics Only - Read Operations)**
1. `app/services/device_config_db.py` - Added historical config query methods (READ ONLY)
2. `app/services/realtime_data_db.py` - Added `get_realtime_data_multiple_params()` (READ ONLY)
3. `app/pages/analytics.py` - Modified chart display logic (READ ONLY)

### **Files NOT Changed (Data Saving Flow)**
- ✅ `app/services/mqtt_client.py` - MQTT subscription intact
- ✅ `app/main.py` - Callback registration intact
- ✅ `app/services/realtime_data_db.py` - `save_realtime_data()` method intact

**Conclusion:** Code changes did NOT break data saving flow.

---

## 🔍 Debugging Steps

### **Step 1: Check MQTT Subscription**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "RTD"
```

**Expected Output:**
```
📡 Subscribed to: RTD/#
📊 Real-time data received from device: <device_id>
```

**If NOT seeing subscription:**
- Check MQTT client startup logs
- Verify MQTT broker is running: `docker ps | grep mqtt`

---

### **Step 2: Check if Hardware is Sending Data**

**Terminal Command:**
```bash
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "RTD/#" -v
```

**Expected:** Should see messages like:
```
RTD/0x573C {"type":"Analog","value":{"parameter1":123.45}}
```

**If NO data:**
- ✅ Problem is on **hardware side** - device is not publishing
- Check hardware logs
- Verify hardware MQTT connection
- Check hardware configuration

---

### **Step 3: Check Server-Side Data Reception**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "real-time data"
```

**Expected Output:**
```
📊 Real-time data received from device: 0x573C
   Topic: RTD/0x573C
   Payload preview: {"type":"Analog","value":{...}}
   Data Type: 'Analog', Values count: 2
   ✅ Real-time data callback exists, calling...
   ✅ Real-time data callback completed successfully
```

**If NOT seeing "Real-time data received":**
- MQTT message is not reaching server
- Check MQTT broker connectivity
- Check network between broker and app

---

### **Step 4: Check Database Saving**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "Writing to InfluxDB"
```

**Expected Output:**
```
💾 Writing to InfluxDB: device=0x573C, type=Analog, param=parameter1, value=123.45
✅ Successfully wrote to InfluxDB: 0x573C/Analog/parameter1
```

**If seeing errors:**
- Check InfluxDB connection
- Check database permissions
- Check bucket/org configuration

---

### **Step 5: Verify Database Connection**

**Check InfluxDB Connection:**
```bash
docker logs iotnarad_app | grep -i "Real-Time Data DB Service"
```

**Expected:**
```
✅ Real-Time Data DB Service connected to InfluxDB: http://influxdb:8086
   Database: Self-Hosted InfluxDB 2.x
   Bucket: iot_data_gcp, Org: iot-narad-gcp
```

---

### **Step 6: Check for Errors**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "error\|failed\|exception" | grep -i "rtd\|realtime"
```

**Look for:**
- ❌ "Error in real-time data callback"
- ❌ "FAILED to save RTD"
- ❌ "InfluxDB write error"
- ❌ "Real-time data callback not registered"

---

## 🎯 Most Likely Causes

### **1. Hardware Not Sending Data (Most Likely)**
**Symptoms:**
- `mosquitto_sub` shows no data
- Server logs show no "Real-time data received"

**Solution:**
- Check hardware device
- Verify hardware MQTT connection
- Check hardware configuration
- Restart hardware device

---

### **2. MQTT Broker Issue**
**Symptoms:**
- Hardware is sending but server not receiving
- Subscription logs missing

**Solution:**
```bash
# Restart MQTT broker
docker restart iotnarad_mqtt

# Check broker logs
docker logs iotnarad_mqtt -f
```

---

### **3. Database Connection Issue**
**Symptoms:**
- Data received but not saved
- "InfluxDB write error" in logs

**Solution:**
```bash
# Check InfluxDB status
docker ps | grep influxdb

# Check InfluxDB logs
docker logs iotnarad_influxdb -f

# Verify connection
docker exec -it iotnarad_app python3 -c "
from app.services.realtime_data_db import RealtimeDataDBService
service = RealtimeDataDBService()
print('Connected:', service.is_connected())
"
```

---

### **4. Database Empty (Data Retention Policy)**
**Symptoms:**
- Old data missing
- Only recent data visible

**Solution:**
- Check InfluxDB retention policy
- Verify bucket configuration
- Check if data was deleted

---

## 📊 Quick Diagnostic Commands

### **Complete Diagnostic:**
```bash
# 1. Check MQTT subscription
docker logs iotnarad_app | grep "Subscribed to: RTD"

# 2. Check data reception
docker logs iotnarad_app -f | grep "Real-time data received"

# 3. Check database writes
docker logs iotnarad_app -f | grep "Writing to InfluxDB"

# 4. Check for errors
docker logs iotnarad_app | grep -i "error.*rtd\|error.*realtime"

# 5. Test MQTT subscription manually
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "RTD/#" -v
```

---

## 🔧 Quick Fixes

### **Restart Services:**
```bash
# Restart app
docker restart iotnarad_app

# Restart MQTT broker
docker restart iotnarad_mqtt

# Restart InfluxDB (if needed)
docker restart iotnarad_influxdb
```

### **Check Service Status:**
```bash
docker ps | grep -E "iotnarad_app|iotnarad_mqtt|iotnarad_influxdb"
```

---

## 📝 Summary

**My code changes:**
- ✅ Did NOT modify data saving flow
- ✅ Did NOT modify MQTT subscription
- ✅ Did NOT modify callback registration
- ✅ Only modified analytics page (read operations)

**Most likely issue:**
- 🔴 **Hardware side** - Device is not sending data to MQTT broker
- 🟡 **MQTT broker** - Connection issue
- 🟢 **Database** - Less likely, but check connection

**Next steps:**
1. Verify hardware is sending data (`mosquitto_sub` test)
2. Check server logs for data reception
3. Verify database connection
4. Check for errors in logs

