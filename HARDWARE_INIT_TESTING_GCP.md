# 🔌 Hardware Device Initialization Testing Guide - GCP VM

## 📋 Overview

This guide helps you test the complete hardware device initialization flow on your GCP VM:

1. **Hardware sends:** `{"SerialNumber": "DF5647"}` to topic `Dev/Init/#`
2. **Server receives:** Extracts serial number and checks database
3. **Server stores:** New serial numbers in database (ignores existing)
4. **Server acknowledges:** Sends acknowledgment to `Dev/Ack/<Sr_No>`

---

## 🚀 Quick Start

### Option 1: Test from GCP VM (Recommended)

**SSH into your GCP VM:**
```bash
gcloud compute ssh YOUR_VM_NAME --zone YOUR_ZONE
```

**Run the test script:**
```bash
cd ~/IOTNarad_dashboard
chmod +x tools/test_hardware_init_gcp.sh
./tools/test_hardware_init_gcp.sh DF5647
```

### Option 2: Test from Local Machine (Windows)

**Run PowerShell script:**
```powershell
.\tools\test_hardware_init_gcp.ps1 -VM_IP "34.131.186.225" -SerialNumber "DF5647"
```

---

## 📡 Step-by-Step Testing

### Step 1: Verify Server is Ready

**On GCP VM:**
```bash
# Check containers are running
docker ps | grep -E "mqtt|app"

# Check MQTT subscription
docker logs iotnarad_app | grep "Subscribed to: Dev/Init"

# Expected output:
# 📡 Subscribed to: Dev/Init/+
```

### Step 2: Simulate Hardware Sending Initialization

**On GCP VM:**
```bash
# Set your serial number
SERIAL_NUMBER="DF5647"

# Publish initialization message
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t "Dev/Init/$SERIAL_NUMBER" \
    -m '{"SerialNumber": "'$SERIAL_NUMBER'"}'
```

**From Local Machine (if Docker installed):**
```powershell
$serialNumber = "DF5647"
$vmIP = "34.131.186.225"

docker run --rm eclipse-mosquitto:2 mosquitto_pub `
    -h $vmIP `
    -p 1883 `
    -t "Dev/Init/$serialNumber" `
    -m "{`"SerialNumber`": `"$serialNumber`"}"
```

### Step 3: Monitor Acknowledgment

**On GCP VM (Terminal 1 - Subscribe to acknowledgment):**
```bash
SERIAL_NUMBER="DF5647"

docker exec -it iotnarad_mqtt mosquitto_sub \
    -h localhost \
    -p 1883 \
    -t "Dev/Ack/$SERIAL_NUMBER" \
    -v
```

**From Local Machine:**
```powershell
$serialNumber = "DF5647"
$vmIP = "34.131.186.225"

docker run --rm eclipse-mosquitto:2 mosquitto_sub `
    -h $vmIP `
    -p 1883 `
    -t "Dev/Ack/$serialNumber" `
    -v
```

**Expected Output:**
```
Dev/Ack/DF5647 {"status":"success","message":"Device registered successfully","timestamp":"2025-01-15T10:30:45Z"}
```

### Step 4: Check Server Logs

**On GCP VM:**
```bash
# View real-time logs
docker logs iotnarad_app -f

# Look for:
# 📨 Device initialization message received on topic: Dev/Init/DF5647
# 🔍 Processing serial number: DF5647
# ✅ Device registered successfully
# 📤 Published acknowledgment to Dev/Ack/DF5647
```

### Step 5: Verify Database Storage

**Check if device was stored in database:**
```bash
# If you have a database check script
python check_device_in_database.py DF5647

# Or check InfluxDB directly (if you have access)
```

---

## 🔧 Hardware Configuration

### For ESP32/Arduino Hardware

**1. MQTT Broker Configuration:**
```cpp
// Your GCP VM external IP
const char* mqtt_broker = "34.131.186.225";  // Replace with your VM IP
const int mqtt_port = 1883;
const char* device_id = "DF5647";  // Your serial number
```

**2. WiFi Configuration:**
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

**3. Device Initialization Code:**
```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

WiFiClient espClient;
PubSubClient client(espClient);

String serialNumber = "DF5647";  // Your device serial number

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
  client.setCallback(mqttCallback);
  
  if (client.connect(serialNumber.c_str())) {
    Serial.println("MQTT Connected!");
    
    // Subscribe to acknowledgment topic
    String ackTopic = "Dev/Ack/" + serialNumber;
    client.subscribe(ackTopic.c_str());
    Serial.println("Subscribed to: " + ackTopic);
    
    // Send initialization message
    sendDeviceInit();
  }
}

void loop() {
  client.loop();
  
  // Reconnect if disconnected
  if (!client.connected()) {
    reconnect();
  }
  
  delay(1000);
}

void sendDeviceInit() {
  String topic = "Dev/Init/" + serialNumber;
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["SerialNumber"] = serialNumber;
  
  char payload[200];
  serializeJson(doc, payload);
  
  // Publish
  if (client.publish(topic.c_str(), payload)) {
    Serial.println("✅ Initialization message sent!");
    Serial.println("   Topic: " + topic);
    Serial.println("   Payload: " + String(payload));
  } else {
    Serial.println("❌ Failed to send initialization message");
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("📨 Message received on topic: ");
  Serial.println(topic);
  
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("   Payload: " + message);
  
  // Parse acknowledgment
  if (String(topic).indexOf("/Ack/") > 0) {
    StaticJsonDocument<200> doc;
    deserializeJson(doc, message);
    
    String status = doc["status"];
    String msg = doc["message"];
    
    Serial.println("✅ Acknowledgment received!");
    Serial.println("   Status: " + status);
    Serial.println("   Message: " + msg);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect(serialNumber.c_str())) {
      Serial.println("✅ Connected!");
      
      // Resubscribe
      String ackTopic = "Dev/Ack/" + serialNumber;
      client.subscribe(ackTopic.c_str());
      
      // Resend initialization
      sendDeviceInit();
    } else {
      Serial.print("❌ Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}
```

---

## 🧪 Complete Test Flow

### Test Scenario 1: New Device (First Time)

```bash
# 1. Send initialization
SERIAL="NEWDEVICE001"
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t "Dev/Init/$SERIAL" \
    -m '{"SerialNumber": "'$SERIAL'"}'

# 2. Monitor acknowledgment
docker exec -it iotnarad_mqtt mosquitto_sub \
    -h localhost \
    -p 1883 \
    -t "Dev/Ack/$SERIAL" \
    -v

# Expected: Device registered in database + acknowledgment received
```

### Test Scenario 2: Existing Device (Duplicate)

```bash
# 1. Send same serial number again
SERIAL="DF5647"  # Already registered
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t "Dev/Init/$SERIAL" \
    -m '{"SerialNumber": "'$SERIAL'"}'

# 2. Check logs
docker logs iotnarad_app --tail 20 | grep "$SERIAL"

# Expected: Device ignored (already exists) + acknowledgment still sent
```

### Test Scenario 3: Multiple Devices Simultaneously

```bash
# Send multiple initialization messages
for serial in DEV001 DEV002 DEV003 DEV004 DEV005; do
    docker exec -i iotnarad_mqtt mosquitto_pub \
        -h localhost \
        -p 1883 \
        -t "Dev/Init/$serial" \
        -m "{\"SerialNumber\": \"$serial\"}" &
done

# Monitor all acknowledgments
docker exec -it iotnarad_mqtt mosquitto_sub \
    -h localhost \
    -p 1883 \
    -t "Dev/Ack/#" \
    -v
```

---

## 📊 Monitoring Commands

### Monitor All Initialization Messages

**On GCP VM:**
```bash
docker exec -it iotnarad_mqtt mosquitto_sub \
    -h localhost \
    -p 1883 \
    -t "Dev/Init/+" \
    -v
```

### Monitor All Acknowledgments

**On GCP VM:**
```bash
docker exec -it iotnarad_mqtt mosquitto_sub \
    -h localhost \
    -p 1883 \
    -t "Dev/Ack/+" \
    -v
```

### Monitor Server Processing

**On GCP VM:**
```bash
# Real-time logs
docker logs iotnarad_app -f | grep -E "Device initialization|SerialNumber|Acknowledgment"

# Or view all logs
docker logs iotnarad_app -f
```

### Monitor MQTT Broker Activity

**On GCP VM:**
```bash
docker logs iotnarad_mqtt -f
```

---

## 🔍 Verification Checklist

After testing, verify:

- [ ] **Hardware can connect to MQTT broker** (GCP VM IP:1883)
- [ ] **Initialization message is sent** to `Dev/Init/<SerialNumber>`
- [ ] **Server receives the message** (check logs)
- [ ] **Serial number is extracted** correctly
- [ ] **New devices are stored** in database
- [ ] **Existing devices are ignored** (not duplicated)
- [ ] **Acknowledgment is sent** to `Dev/Ack/<SerialNumber>`
- [ ] **Hardware receives acknowledgment** (if subscribed)

---

## 🛠️ Troubleshooting

### Problem 1: Hardware Cannot Connect to MQTT

**Symptoms:**
- Connection timeout
- "Connection refused" error

**Solutions:**
1. ✅ Verify GCP firewall allows port 1883:
   ```bash
   gcloud compute firewall-rules list | grep mqtt
   ```

2. ✅ Test connectivity from hardware network:
   ```bash
   # From hardware network, test connection
   telnet YOUR_VM_IP 1883
   ```

3. ✅ Verify MQTT broker is running:
   ```bash
   docker ps | grep mqtt
   ```

### Problem 2: Initialization Message Not Received

**Symptoms:**
- No logs in server
- Message published but not processed

**Solutions:**
1. ✅ Check server subscription:
   ```bash
   docker logs iotnarad_app | grep "Subscribed to: Dev/Init"
   ```

2. ✅ Verify topic format:
   - ✅ Correct: `Dev/Init/DF5647`
   - ❌ Wrong: `dev/init/DF5647` (case sensitive)
   - ❌ Wrong: `Dev/Init` (missing serial number)

3. ✅ Check JSON format:
   ```json
   {"SerialNumber": "DF5647"}  ✅ Correct
   {SerialNumber: "DF5647"}     ❌ Wrong (missing quotes)
   ```

### Problem 3: Acknowledgment Not Received

**Symptoms:**
- Initialization sent but no acknowledgment

**Solutions:**
1. ✅ Check if hardware is subscribed:
   ```cpp
   // Hardware must subscribe to:
   client.subscribe("Dev/Ack/DF5647");
   ```

2. ✅ Verify acknowledgment topic:
   ```bash
   # Monitor on server
   docker exec -it iotnarad_mqtt mosquitto_sub \
       -h localhost \
       -t "Dev/Ack/#" \
       -v
   ```

3. ✅ Check server logs for errors:
   ```bash
   docker logs iotnarad_app | grep -i error
   ```

### Problem 4: Device Not Stored in Database

**Symptoms:**
- Acknowledgment received but device not in database

**Solutions:**
1. ✅ Check database connection:
   ```bash
   docker logs iotnarad_app | grep -i "database\|influxdb\|connected"
   ```

2. ✅ Verify database write:
   ```bash
   # Check for database errors
   docker logs iotnarad_app | grep -i "error.*database\|error.*influxdb"
   ```

3. ✅ Check device registration logic:
   ```bash
   docker logs iotnarad_app | grep -E "Device registered|SerialNumber.*registered"
   ```

---

## 📝 Test Scripts Summary

| Script | Purpose | Where to Run |
|--------|---------|--------------|
| `test_hardware_init_gcp.sh` | Complete test on VM | GCP VM |
| `test_hardware_init_gcp.ps1` | Test from local machine | Windows (local) |
| Manual commands | Step-by-step testing | GCP VM or local |

---

## 🎯 Quick Reference

### Topic Formats

```
Device Initialization:  Dev/Init/<SerialNumber>
Acknowledgment:         Dev/Ack/<SerialNumber>
```

### Message Formats

**Initialization:**
```json
{"SerialNumber": "DF5647"}
```

**Acknowledgment:**
```json
{
  "status": "success",
  "message": "Device registered successfully",
  "timestamp": "2025-01-15T10:30:45Z"
}
```

### GCP VM Details

- **External IP:** `34.131.186.225` (from your screenshot)
- **MQTT Port:** `1883`
- **WebSocket Port:** `9001`

---

## 📚 Related Files

- `MQTT_TESTING_GCP_VM.md` - General MQTT testing guide
- `MQTT_DEVICE_INIT_QUICK_TEST.md` - Quick test reference
- `tools/test_hardware_init_gcp.sh` - Bash test script
- `tools/test_hardware_init_gcp.ps1` - PowerShell test script

---

**Last Updated:** 2025-01-15  
**GCP VM IP:** 34.131.186.225 (update with your actual IP)  
**MQTT Port:** 1883

