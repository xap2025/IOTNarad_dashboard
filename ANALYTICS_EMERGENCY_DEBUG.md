# 🚨 Analytics Page - Emergency Debugging Guide

## 🔍 Current Issue

**Symptoms:**
- Hardware ON hai, device running hai
- Analytics page par sab kuch "No value" dikha raha hai
- Device status bhi update nahi ho raha
- Database queries 0 data points return kar rahi hain

**Root Cause Analysis:**
Logs mein **koi bhi MQTT RTD message receive ka log nahi dikh raha**, matlab:
- Ya device se data publish hi nahi ho raha
- Ya MQTT broker connection issue hai
- Ya topic mismatch hai

---

## ✅ Quick Checks (Step-by-Step)

### **Step 1: MQTT Connection Check**

Server logs mein yeh dikhna chahiye:
```
✅ Connected to MQTT Broker: mqtt:1883
📡 Subscribed to: RTD/# (RTD/#)
✅ RTD callback is registered and ready
```

**Agar yeh logs nahi dikh rahe:**
- MQTT broker running nahi hai
- Network connectivity issue
- Check Docker containers: `docker ps | grep mqtt`

---

### **Step 2: Device Publishing Check**

**Device se data publish ho raha hai ya nahi, check karein:**

**Option A: MQTTX Tool se check karein**
1. MQTTX open karein
2. Subscribe to: `RTD/#`
3. Device se data aana chahiye

**Option B: Server logs check karein**
Agar device publish kar raha hai, toh yeh log dikhna chahiye:
```
📨 Message received on RTD/8C4B144D3274: {...}
🔵 RTD MESSAGE DETECTED: Topic=RTD/8C4B144D3274, Payload length=...
📊 Real-time data received from device: 8C4B144D3274
```

**Agar yeh logs nahi dikh rahe:**
- Device se data publish nahi ho raha
- Device code check karein
- MQTT broker connection check karein

---

### **Step 3: Database Data Check**

**InfluxDB mein data hai ya nahi, check karein:**

**Flux Query (InfluxDB UI mein):**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "Realtime_Data")
  |> filter(fn: (r) => r.device_id == "8C4B144D3274")
  |> filter(fn: (r) => r._field == "value")
  |> limit(n: 10)
```

**Agar data hai:**
- Queries sahi hain, data display hoga
- Agar data nahi dikh raha, UI issue hai

**Agar data nahi hai:**
- MQTT se data receive nahi ho raha (Step 2 check karein)
- Ya data save nahi ho raha

---

### **Step 4: SocketIO Event Check**

**Browser Console mein check karein:**
```javascript
// Console mein yeh dikhna chahiye:
✅ Analytics: SocketIO connected
📊 RTD data update received: {device_id: "...", ...}
🔄 Clicking RTD trigger button...
```

**Agar yeh logs nahi dikh rahe:**
- SocketIO connection issue
- Client-side script load nahi hua
- Check browser console for errors

---

## 🔧 Immediate Fixes Applied

### **1. Enhanced MQTT Logging**
- Ab har RTD message ke liye detailed logs
- Callback registration status log
- Connection status log

### **2. SocketIO Broadcast**
- `broadcast=True` add kiya
- Sabhi clients ko event milega

### **3. Digital Data Conversion**
- Boolean → Integer conversion before save
- Integer → Boolean conversion for display

### **4. Error Handling**
- Type conflicts gracefully handle
- Empty results return instead of crash

---

## 🎯 Most Likely Issues

### **Issue 1: Device Not Publishing**
**Check:**
- Device code mein RTD topic par publish ho raha hai?
- Topic format: `RTD/<Device ID>` (e.g., `RTD/8C4B144D3274`)
- Payload format: `{"type": "Analog|Digital|Modbus|Canbus", "value": {...}}`

**Fix:**
- Device code verify karein
- MQTTX se manually publish karke test karein

---

### **Issue 2: MQTT Broker Not Connected**
**Check:**
- Server logs mein MQTT connection log dikh raha hai?
- Docker container running hai?

**Fix:**
```bash
docker ps | grep mqtt
docker logs <mqtt_container_name>
```

---

### **Issue 3: Topic Mismatch**
**Check:**
- Device publish kar raha hai: `RTD/8C4B144D3274`
- Server subscribe kar raha hai: `RTD/#`

**Fix:**
- Topic format verify karein
- Case-sensitive hai, exact match chahiye

---

## 📋 Testing Checklist

### **Test 1: MQTT Connection**
- [ ] Server logs mein "✅ Connected to MQTT Broker" dikh raha hai
- [ ] "📡 Subscribed to: RTD/#" dikh raha hai
- [ ] "✅ RTD callback is registered" dikh raha hai

### **Test 2: Device Publishing**
- [ ] MQTTX se subscribe karke data receive ho raha hai
- [ ] Server logs mein "📊 Real-time data received" dikh raha hai
- [ ] "📡 Emitted SocketIO RTD update event" dikh raha hai

### **Test 3: Database Save**
- [ ] "✅ Successfully saved RTD" logs dikh rahe hain
- [ ] InfluxDB UI mein data dikh raha hai
- [ ] Data format sahi hai (integers for Digital)

### **Test 4: UI Update**
- [ ] Browser console mein SocketIO events dikh rahe hain
- [ ] Analytics page par data update ho raha hai
- [ ] Device status "Running" dikh raha hai

---

## 🚀 Quick Test Commands

### **Check MQTT Connection:**
```bash
# Server logs mein check karein
grep "MQTT" server.log | tail -20
```

### **Check RTD Messages:**
```bash
# Server logs mein check karein
grep "RTD" server.log | tail -20
```

### **Check Database:**
```bash
# InfluxDB UI mein query run karein (see Step 3)
```

### **Check SocketIO:**
```bash
# Browser console mein check karein
# F12 → Console tab
```

---

## ⚠️ Critical Points

1. **MQTT Data Flow:**
   - Device → MQTT Broker → Server → Database → UI
   - Agar kisi bhi step mein break ho, data nahi dikhega

2. **Digital Data:**
   - MQTT: `true`/`false` (boolean)
   - Database: `1`/`0` (integer)
   - UI: "ON"/"OFF" (string)

3. **SocketIO Events:**
   - Event emit hoga jab data save hoga
   - Client-side listener trigger karega
   - Callback update karega

---

## 🆘 If Still Not Working

1. **Check MQTT Broker:**
   ```bash
   docker exec -it <mqtt_container> mosquitto_sub -t "RTD/#" -v
   ```

2. **Check Server Logs:**
   - MQTT connection status
   - RTD message reception
   - Database save status
   - SocketIO event emission

3. **Check Browser Console:**
   - SocketIO connection
   - RTD event reception
   - Button click triggers

4. **Manual Test:**
   - MQTTX se manually publish karein
   - Check if server receives
   - Check if database saves
   - Check if UI updates

---

**Last Updated:** January 23, 2026

