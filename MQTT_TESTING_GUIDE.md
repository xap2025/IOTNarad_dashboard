# 📡 MQTT Communication Testing Guide

## 🎯 Overview

IOTNarad dashboard uses **MQTT protocol** to communicate with IoT gateways/devices. This guide explains:
- ✅ How to check if MQTT is working
- ✅ What commands to send to hardware
- ✅ What messages hardware should send
- ✅ Step-by-step testing process

---

## 📊 MQTT Architecture

```
┌─────────────────┐         MQTT Broker          ┌──────────────────┐
│  IoT Gateway    │◄─────────────────────────────►│  Dashboard App   │
│   (ESP32/etc)   │     (Mosquitto - Port 1883)    │   (Python)       │
└─────────────────┘                                └──────────────────┘
       │                                                     │
       │  Subscribe: config, cmd                            │  Subscribe: data, status
       │  Publish: data, status                             │  Publish: config, cmd
       └─────────────────────────────────────────────────────┘
```

---

## 🔧 Step 1: Check MQTT Broker Status

### A. Check Docker Containers
```bash
# Windows PowerShell
docker ps

# Should show:
# iotnarad_mqtt    (Port 1883, 9001)
# iotnarad_app     (Port 8050)
# iotnarad_influxdb (Port 8086)
```

### B. Check MQTT Broker Logs
```bash
# View MQTT broker logs
docker logs iotnarad_mqtt

# Should show:
# mosquitto version X.X.X running
# Opening ipv4 listen socket on port 1883
```

### C. Test MQTT Connection Locally
```bash
# Subscribe to all topics (in one terminal)
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t '#' -v

# Publish a test message (in another terminal)
docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -t 'test/topic' -m '{"test": "message"}'
```

**Expected Output:**
```
# Terminal 1 (subscriber):
test/topic {"test": "message"}

# Terminal 2 (publisher):
# Message sent successfully
```

---

## 📋 MQTT Topic Structure

Your dashboard uses these **topic patterns**:

### **Topics Dashboard SUBSCRIBES to (receives from hardware):**

1. **Device Data:**
   ```
   iotnarad/devices/{device_id}/data
   ```
   - **Example:** `iotnarad/devices/esp32_gw_01/data`
   - **Purpose:** Receive sensor readings, production data

2. **Device Status:**
   ```
   iotnarad/devices/{device_id}/status
   ```
   - **Example:** `iotnarad/devices/esp32_gw_01/status`
   - **Purpose:** Receive device online/offline status, heartbeat

### **Topics Dashboard PUBLISHES to (sends to hardware):**

1. **Device Configuration:**
   ```
   iotnarad/devices/{device_id}/config
   ```
   - **Purpose:** Send channel configurations, sensor settings

2. **Device Commands:**
   ```
   iotnarad/devices/{device_id}/cmd
   ```
   - **Purpose:** Send control commands (start, stop, reset)

---

## 🚀 Step 2: Testing with Hardware (ESP32/IoT Gateway)

### **Configuration Required on Hardware:**

1. **MQTT Broker Details:**
   - **Host:** Your server IP (or `localhost` if testing locally)
   - **Port:** `1883`
   - **Username:** None (anonymous allowed)
   - **Password:** None
   - **Client ID:** Unique per device (e.g., `esp32_gw_01`)

2. **Connection Code Example (Arduino/ESP32):**
```cpp
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker
const char* mqtt_broker = "YOUR_SERVER_IP";  // e.g., "192.168.1.100"
const int mqtt_port = 1883;
const char* device_id = "esp32_gw_01";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  // Connect WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected!");
  
  // Connect MQTT
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(mqttCallback);  // Handle incoming messages
  
  if (client.connect(device_id)) {
    Serial.println("MQTT Connected!");
    
    // Subscribe to config topic
    String config_topic = "iotnarad/devices/" + String(device_id) + "/config";
    client.subscribe(config_topic.c_str());
    Serial.println("Subscribed to: " + config_topic);
    
    // Subscribe to command topic
    String cmd_topic = "iotnarad/devices/" + String(device_id) + "/cmd";
    client.subscribe(cmd_topic.c_str());
    Serial.println("Subscribed to: " + cmd_topic);
  }
}

void loop() {
  client.loop();  // Maintain MQTT connection
  
  // Send data every 5 seconds
  sendDeviceData();
  delay(5000);
}
```

---

## 📤 Step 3: Hardware Should Send (Publish) These Messages

### **A. Device Data Message (Required)**

**Topic:**
```
iotnarad/devices/{device_id}/data
```

**JSON Format:**
```json
{
  "timestamp": "2025-10-29T17:30:45Z",
  "sensors": {
    "temperature": 25.5,
    "humidity": 65.2,
    "pressure": 1013.25
  },
  "production": {
    "line_id": "Line_A",
    "units_produced": 1250,
    "oee": 89.2,
    "status": "running"
  },
  "channels": {
    "analog_in_0": 4.5,
    "analog_in_1": 3.2,
    "digital_in_0": 1,
    "digital_in_1": 0
  }
}
```

**Arduino/ESP32 Code:**
```cpp
void sendDeviceData() {
  String topic = "iotnarad/devices/" + String(device_id) + "/data";
  
  String payload = "{";
  payload += "\"timestamp\":\"2025-10-29T17:30:45Z\",";
  payload += "\"sensors\":{";
  payload += "\"temperature\":" + String(temperature) + ",";
  payload += "\"humidity\":" + String(humidity);
  payload += "},";
  payload += "\"production\":{";
  payload += "\"line_id\":\"Line_A\",";
  payload += "\"units_produced\":" + String(units) + ",";
  payload += "\"oee\":" + String(oee);
  payload += "}";
  payload += "}";
  
  client.publish(topic.c_str(), payload.c_str());
  Serial.println("Published: " + topic);
}
```

### **B. Device Status Message (Required)**

**Topic:**
```
iotnarad/devices/{device_id}/status
```

**JSON Format:**
```json
{
  "status": "online",
  "timestamp": "2025-10-29T17:30:45Z",
  "uptime": 3600,
  "firmware_version": "1.0.0",
  "wifi_signal": -65,
  "mqtt_connected": true
}
```

**Arduino/ESP32 Code:**
```cpp
void sendDeviceStatus() {
  String topic = "iotnarad/devices/" + String(device_id) + "/status";
  
  String payload = "{";
  payload += "\"status\":\"online\",";
  payload += "\"timestamp\":\"2025-10-29T17:30:45Z\",";
  payload += "\"uptime\":" + String(millis()/1000) + ",";
  payload += "\"firmware_version\":\"1.0.0\",";
  payload += "\"wifi_signal\":" + String(WiFi.RSSI()) + ",";
  payload += "\"mqtt_connected\":true";
  payload += "}";
  
  client.publish(topic.c_str(), payload.c_str());
}
```

---

## 📥 Step 4: Hardware Should Receive (Subscribe) These Messages

### **A. Device Configuration Message**

**Topic:**
```
iotnarad/devices/{device_id}/config
```

**JSON Format:**
```json
{
  "device_id": "esp32_gw_01",
  "channels": {
    "analog_in_0": {
      "enabled": true,
      "name": "Temperature Sensor",
      "min": 0,
      "max": 100,
      "unit": "°C"
    },
    "analog_in_1": {
      "enabled": true,
      "name": "Pressure Sensor",
      "min": 0,
      "max": 5000,
      "unit": "Pa"
    },
    "digital_out_0": {
      "enabled": true,
      "name": "Relay 1",
      "state": 0
    }
  },
  "data_interval": 5,
  "timestamp": "2025-10-29T17:30:45Z"
}
```

**Arduino/ESP32 Code:**
```cpp
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  if (String(topic).indexOf("/config") > 0) {
    // Parse and apply configuration
    parseConfig(message);
  } else if (String(topic).indexOf("/cmd") > 0) {
    // Parse and execute command
    parseCommand(message);
  }
}
```

### **B. Device Command Message**

**Topic:**
```
iotnarad/devices/{device_id}/cmd
```

**JSON Format:**
```json
{
  "command": "start",
  "params": {
    "line_id": "Line_A"
  },
  "timestamp": "2025-10-29T17:30:45Z"
}
```

**Available Commands:**
- `start` - Start production
- `stop` - Stop production
- `reset` - Reset device
- `reboot` - Reboot device
- `update_config` - Update configuration

---

## 🧪 Step 5: Manual Testing (Without Hardware)

### **Test 1: Simulate Device Data**

**Windows PowerShell:**
```powershell
# Simulate device sending data
$topic = 'iotnarad/devices/esp32_gw_01/data'
$payload = '{
  "timestamp": "2025-10-29T17:30:45Z",
  "sensors": {
    "temperature": 25.5,
    "humidity": 65.2
  },
  "production": {
    "line_id": "Line_A",
    "units_produced": 1250,
    "oee": 89.2,
    "status": "running"
  }
}'

docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t $topic -m "$payload"
```

### **Test 2: Simulate Device Status**

```powershell
$topic = 'iotnarad/devices/esp32_gw_01/status'
$payload = '{
  "status": "online",
  "timestamp": "2025-10-29T17:30:45Z",
  "uptime": 3600,
  "firmware_version": "1.0.0",
  "mqtt_connected": true
}'

docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t $topic -m "$payload"
```

### **Test 3: Monitor All Messages**

```powershell
# Terminal 1: Subscribe to all topics
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t '#' -v

# Terminal 2: Send test message (use Test 1 or Test 2 above)
```

### **Test 4: Check Dashboard Logs**

```powershell
# View dashboard logs to see if messages are received
docker logs iotnarad_app -f

# Should show:
# 📨 Message received on iotnarad/devices/esp32_gw_01/data: {...}
```

---

## 📝 Step 6: Verify Dashboard is Receiving Data

### **A. Check Application Logs**
```powershell
docker logs iotnarad_app -f | Select-String "Message received"
```

**Expected:**
```
📨 Message received on iotnarad/devices/esp32_gw_01/data: {...}
✅ Data callback registered
```

### **B. Check MQTT Connection Status**

1. Open dashboard: `http://localhost:8050`
2. Login with admin credentials
3. Check header bar (connection status removed, but check logs)

### **C. Monitor Real-time Data**

If data is being received, it should:
- Appear in the dashboard logs
- Be stored in InfluxDB (if configured)
- Show up in Analytics page (if implemented)

---

## 🔍 Troubleshooting

### **Problem 1: MQTT Broker Not Running**
```bash
# Solution:
docker-compose restart mqtt
docker logs iotnarad_mqtt
```

### **Problem 2: Hardware Can't Connect**
- ✅ Check MQTT broker IP address
- ✅ Verify port 1883 is open
- ✅ Check firewall settings
- ✅ Test with: `mosquitto_pub -h YOUR_SERVER_IP -t test -m "hello"`

### **Problem 3: Messages Not Received by Dashboard**
- ✅ Verify topic format matches exactly: `iotnarad/devices/{device_id}/data`
- ✅ Check JSON format is valid
- ✅ View dashboard logs: `docker logs iotnarad_app -f`
- ✅ Verify MQTT client is connected: Look for "✅ Connected to MQTT Broker"

### **Problem 4: JSON Parsing Errors**
- ✅ Validate JSON at: https://jsonlint.com
- ✅ Ensure proper escaping of quotes
- ✅ Check timestamp format: ISO 8601 format

---

## 📊 Quick Reference Card

### **Topic Patterns:**
```
# Hardware publishes to:
iotnarad/devices/{device_id}/data
iotnarad/devices/{device_id}/status

# Hardware subscribes to:
iotnarad/devices/{device_id}/config
iotnarad/devices/{device_id}/cmd
```

### **Test Commands:**
```powershell
# Subscribe to all
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t '#' -v

# Publish test data
docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -t 'iotnarad/devices/test/data' -m '{"test": true}'

# View logs
docker logs iotnarad_mqtt -f
docker logs iotnarad_app -f
```

---

## ✅ Testing Checklist

- [ ] Docker containers running (`docker ps`)
- [ ] MQTT broker accessible on port 1883
- [ ] Hardware connected to WiFi
- [ ] Hardware MQTT client connected
- [ ] Hardware subscribing to config/cmd topics
- [ ] Hardware publishing data every 5 seconds
- [ ] Dashboard logs showing received messages
- [ ] JSON format validated
- [ ] Device ID matches in all topics

---

**Last Updated:** 2025-10-29  
**MQTT Broker:** localhost:1883 (or your server IP)  
**Protocol:** MQTT 3.1.1  
**QoS:** 1 (At least once delivery)

