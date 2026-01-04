# Device ACK Troubleshooting Guide

## 🔍 Problem

**Symptom**: 
- ✅ MQTTX client se bhejne par ACK mil raha hai
- ❌ Hardware device se bhejne par ACK nahi mil raha
- ✅ Serial number server tak pahunch raha hai (server receive kar raha hai)
- ❌ Device ko ACK nahi mil raha

---

## ✅ Server Side Check (Ridhi - Working)

### Server ACK Publish Details

**Topic Format**: `Dev/Ack/<Serial-Number>`  
**Example**: `Dev/Ack/8C4B14BA7948`

**Payload Format**:
```json
{
  "status": "success",
  "message": "Device registered successfully",
  "timestamp": "2026-01-04T07:13:19.229956Z"
}
```

**MQTT Settings**:
- **QoS**: 1 (At least once delivery)
- **Retain**: false (ACK messages retain nahi hote)

**Code Reference** (`app/services/mqtt_client.py` line 269):
```python
topic = f"Dev/Ack/{serial_number}"
payload = {
    "status": status,
    "message": message,
    "timestamp": self._get_timestamp()
}
return self.publish(topic, payload, qos=1, retain=False)
```

---

## ❌ Hardware Side Problem (Naman - Fix Required)

### Problem: Device ACK Topic Par Subscribe Nahi Kar Raha

**Root Cause**: Device ko ACK receive karne ke liye **subscribe** karna padega.

---

## 🔧 Solution: Hardware Device Ko Fix Karna

### Step 1: Device Ko ACK Topic Par Subscribe Karo

**Device ko yeh topic par subscribe karna hoga:**

```
Dev/Ack/<Your-Device-Serial-Number>
```

**Example**:
- Agar device serial number hai: `8C4B14BA7948`
- To subscribe karo: `Dev/Ack/8C4B14BA7948`

**Important**: 
- ✅ Exact serial number use karo (jo registration mein bheja tha)
- ✅ Case-sensitive hai (uppercase/lowercase match hona chahiye)
- ✅ Wildcard `#` use kar sakte ho: `Dev/Ack/#` (sab devices ke ACK receive honge)

---

### Step 2: Subscribe Timing

**Device ko ACK topic par subscribe karna chahiye:**

1. **Before Registration**: Device ko pehle ACK topic par subscribe karna chahiye, phir registration message bhejna chahiye
2. **Persistent Subscription**: Device ko ACK topic par **always** subscribe rakhna chahiye (disconnect nahi karna)

**Correct Flow**:
```
1. Device connects to MQTT broker
2. Device subscribes to: Dev/Ack/<Serial-Number>  ← IMPORTANT!
3. Device publishes to: Dev/Init/Reg/<Serial-Number>
4. Server receives registration
5. Server publishes ACK to: Dev/Ack/<Serial-Number>
6. Device receives ACK ✅
```

**Wrong Flow** (Current Problem):
```
1. Device connects to MQTT broker
2. Device publishes to: Dev/Init/Reg/<Serial-Number>  ← Subscribe nahi kiya!
3. Server receives registration
4. Server publishes ACK to: Dev/Ack/<Serial-Number>
5. Device receives ACK ❌ (kyunki subscribe nahi kiya)
```

---

### Step 3: Code Example (Hardware Side)

**Arduino/ESP32 Example**:
```cpp
#include <WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);

String deviceSerialNumber = "8C4B14BA7948";  // Your device serial number

void setup() {
  // ... WiFi connection code ...
  
  // Connect to MQTT broker
  client.setServer("mqtt-broker-ip", 1883);
  client.setCallback(onMqttMessage);
  
  if (client.connect("device-client-id")) {
    // ✅ IMPORTANT: Subscribe to ACK topic BEFORE publishing registration
    String ackTopic = "Dev/Ack/" + deviceSerialNumber;
    client.subscribe(ackTopic.c_str(), 1);  // QoS 1
    
    Serial.println("Subscribed to: " + ackTopic);
    
    // Now publish registration
    String regTopic = "Dev/Init/Reg/" + deviceSerialNumber;
    String payload = "{\"SerialNumber\":\"" + deviceSerialNumber + "\"}";
    client.publish(regTopic.c_str(), payload.c_str(), false);  // QoS 1, retain false
    
    Serial.println("Published registration to: " + regTopic);
  }
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String topicStr = String(topic);
  
  // Check if this is ACK message
  if (topicStr.startsWith("Dev/Ack/")) {
    String message = "";
    for (int i = 0; i < length; i++) {
      message += (char)payload[i];
    }
    
    Serial.println("ACK received!");
    Serial.println("Topic: " + topicStr);
    Serial.println("Payload: " + message);
    
    // Parse JSON and check status
    // {"status":"success","message":"Device registered successfully",...}
  }
  
  client.loop();  // Keep connection alive
}
```

---

## 🔍 Common Issues & Solutions

### Issue 1: Device Subscribe Nahi Kar Raha

**Symptom**: ACK nahi mil raha

**Solution**: 
- Device ko `Dev/Ack/<Serial-Number>` par subscribe karna hoga
- Subscribe registration se **pehle** karna hoga

---

### Issue 2: Wrong Serial Number in Subscription

**Symptom**: ACK nahi mil raha

**Problem**: 
- Registration mein: `Dev/Init/Reg/8C4B14BA7948`
- Subscribe mein: `Dev/Ack/8C4B14BA7949` (wrong serial number)

**Solution**: 
- Subscribe mein **exact same serial number** use karo jo registration mein bheja tha
- Ya phir wildcard use karo: `Dev/Ack/#` (sab ACK receive honge)

---

### Issue 3: Device Disconnect Ho Raha Hai

**Symptom**: ACK nahi mil raha

**Problem**: 
- Device registration bhejne ke baad disconnect ho jata hai
- ACK aane se pehle hi connection break ho jata hai

**Solution**: 
- Device ko **persistent connection** maintain karna chahiye
- `client.loop()` regularly call karo
- Keep-alive interval set karo (minimum 60 seconds)

---

### Issue 4: QoS Mismatch

**Symptom**: ACK kabhi milta hai, kabhi nahi

**Problem**: 
- Server QoS 1 use karta hai
- Device subscribe QoS 0 use kar raha hai

**Solution**: 
- Device ko bhi **QoS 1** use karna chahiye subscribe ke liye
- Example: `client.subscribe("Dev/Ack/8C4B14BA7948", 1);`

---

### Issue 5: Serial Number Case Mismatch

**Symptom**: ACK nahi mil raha

**Problem**: 
- Registration: `Dev/Init/Reg/8C4B14BA7948` (uppercase)
- Subscribe: `Dev/Ack/8c4b14ba7948` (lowercase)

**Solution**: 
- Serial number **case-sensitive** hai
- Exact same case use karo (uppercase/lowercase match hona chahiye)

---

### Issue 6: Device Subscribe Timing

**Symptom**: ACK nahi mil raha

**Problem**: 
- Device pehle registration bhej deta hai
- Phir subscribe karta hai (too late!)

**Solution**: 
- **Pehle subscribe karo**, phir registration bhejo
- Ya phir device ko startup par hi ACK topic par subscribe kar do

---

## 🧪 Testing Steps

### Step 1: Verify Server is Publishing ACK

**Terminal Command** (Server par):
```bash
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Ack/#" -v
```

**Expected Output**:
```
Dev/Ack/8C4B14BA7948 {"status":"success","message":"Device registered successfully","timestamp":"2026-01-04T07:13:19.229956Z"}
```

**Agar yeh dikh raha hai** → Server side theek hai ✅

---

### Step 2: Verify Device is Subscribing

**Hardware Device Code Mein Check Karo**:
- Device `Dev/Ack/<Serial-Number>` par subscribe kar raha hai ya nahi?
- Subscribe registration se pehle ho raha hai ya baad mein?

---

### Step 3: Verify Serial Number Match

**Check Karo**:
- Registration topic: `Dev/Init/Reg/8C4B14BA7948`
- Subscribe topic: `Dev/Ack/8C4B14BA7948`
- **Exact match** hona chahiye (case-sensitive)

---

### Step 4: Verify Connection Persistence

**Check Karo**:
- Device registration ke baad disconnect ho raha hai ya nahi?
- `client.loop()` regularly call ho raha hai ya nahi?
- Keep-alive interval set hai ya nahi?

---

## 📋 Hardware Team Checklist

Hardware team ko yeh ensure karna hoga:

- [ ] Device `Dev/Ack/<Serial-Number>` par subscribe kar raha hai
- [ ] Subscribe **registration se pehle** ho raha hai
- [ ] Serial number **exact match** hai (case-sensitive)
- [ ] QoS 1 use ho raha hai subscribe ke liye
- [ ] Device **persistent connection** maintain kar raha hai
- [ ] `client.loop()` regularly call ho raha hai
- [ ] Keep-alive interval set hai (minimum 60 seconds)

---

## 🎯 Quick Fix for Hardware Team

**Minimum Code Required**:

```cpp
// 1. Subscribe to ACK topic (BEFORE registration)
String ackTopic = "Dev/Ack/" + deviceSerialNumber;
client.subscribe(ackTopic.c_str(), 1);  // QoS 1

// 2. Publish registration
String regTopic = "Dev/Init/Reg/" + deviceSerialNumber;
String payload = "{\"SerialNumber\":\"" + deviceSerialNumber + "\"}";
client.publish(regTopic.c_str(), payload.c_str(), false);

// 3. Keep connection alive
void loop() {
  client.loop();  // Must call regularly
  delay(100);
}

// 4. Handle ACK messages
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  if (String(topic).startsWith("Dev/Ack/")) {
    // ACK received! Process it
  }
}
```

---

## 🔍 Debugging Commands

### Check Server Logs

```bash
docker compose logs -f app | grep -i "ack\|Dev/Ack"
```

**Expected Output**:
```
📤 Published to Dev/Ack/8C4B14BA7948: {"status":"success",...}
```

---

### Monitor MQTT Broker

**Terminal 1** (Registration messages):
```bash
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Init/Reg/#" -v
```

**Terminal 2** (ACK messages):
```bash
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Dev/Ack/#" -v
```

**Expected**: 
- Terminal 1 mein registration message dikhna chahiye
- Terminal 2 mein ACK message dikhna chahiye (server publish kar raha hai)

---

## ✅ Summary

**Problem**: Device ko ACK nahi mil raha

**Root Cause**: Device `Dev/Ack/<Serial-Number>` topic par subscribe nahi kar raha

**Solution**: 
1. Device ko `Dev/Ack/<Serial-Number>` par subscribe karna hoga
2. Subscribe **registration se pehle** karna hoga
3. Serial number **exact match** hona chahiye
4. QoS 1 use karna hoga
5. Connection **persistent** rakhna hoga

**Server Side**: ✅ Working correctly (ACK publish ho raha hai)

**Hardware Side**: ❌ Fix required (subscribe karna hoga)

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-04  
**Author**: IOTNarad Dashboard Documentation

