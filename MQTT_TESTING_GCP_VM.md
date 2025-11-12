# 🚀 MQTT Testing Guide for GCP VM

## 📋 Overview

This guide helps you test MQTT communication on your GCP VM instance. It covers:
- ✅ Setting up firewall rules
- ✅ Testing MQTT from within the VM
- ✅ Testing MQTT from external clients
- ✅ Troubleshooting common issues

---

## 🔧 Step 1: Configure GCP Firewall Rules

### A. Open MQTT Ports in GCP Console

1. **Go to GCP Console:**
   - Navigate to: **VPC Network → Firewall**
   - Or use direct link: https://console.cloud.google.com/networking/firewalls

2. **Create Firewall Rule for MQTT:**
   - Click **"Create Firewall Rule"**
   - **Name:** `mqtt-broker-allow`
   - **Direction:** Ingress
   - **Targets:** All instances in the network (or specific VM)
   - **Source IP ranges:** 
     - `0.0.0.0/0` (for testing from anywhere)
     - OR specific IP ranges for security
   - **Protocols and ports:**
     - ✅ TCP: `1883` (MQTT)
     - ✅ TCP: `9001` (MQTT WebSockets)
   - Click **"Create"**

### B. Alternative: Using gcloud CLI

```bash
# SSH into your GCP VM first, then run:
gcloud compute firewall-rules create mqtt-broker-allow \
    --allow tcp:1883,tcp:9001 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow MQTT broker connections" \
    --direction INGRESS
```

### C. Verify Firewall Rule

```bash
# Check if rule exists
gcloud compute firewall-rules list | grep mqtt

# Check rule details
gcloud compute firewall-rules describe mqtt-broker-allow
```

---

## 🐳 Step 2: Verify Docker Containers on VM

### A. SSH into Your GCP VM

```bash
# From your local machine
gcloud compute ssh YOUR_VM_NAME --zone YOUR_ZONE

# Or use SSH key if configured
ssh -i ~/.ssh/gcp_key user@YOUR_VM_EXTERNAL_IP
```

### B. Check Running Containers

```bash
# Check if containers are running
docker ps

# Expected output:
# CONTAINER ID   IMAGE                    PORTS                    NAMES
# xxxxx          iotnarad_app            0.0.0.0:8050->8050/tcp   iotnarad_app
# xxxxx          eclipse-mosquitto:2      0.0.0.0:1883->1883/tcp  iotnarad_mqtt
# xxxxx          influxdb:2.7            0.0.0.0:8086->8086/tcp  iotnarad_influxdb
```

### C. Check MQTT Container Logs

```bash
# View MQTT broker logs
docker logs iotnarad_mqtt

# Follow logs in real-time
docker logs iotnarad_mqtt -f

# Expected output:
# mosquitto version X.X.X running
# Opening ipv4 listen socket on port 1883
# Opening websockets listen socket on port 9001
```

### D. Start Containers if Not Running

```bash
# Navigate to project directory
cd ~/IOTNarad_dashboard

# Start all containers
docker compose up -d

# Or start only MQTT
docker compose up -d mqtt
```

---

## 🧪 Step 3: Test MQTT from Within the VM

### A. Test 1: Subscribe to All Topics (Terminal 1)

```bash
# Subscribe to all topics to monitor messages
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t '#' -v

# This will show all messages published to any topic
```

### B. Test 2: Publish Test Message (Terminal 2)

```bash
# Open a new terminal/SSH session, then publish a test message
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t 'test/topic' \
    -m '{"test": "message", "timestamp": "2025-01-15T10:00:00Z"}'
```

**Expected Result:**
- Terminal 1 (subscriber) should show: `test/topic {"test": "message", ...}`
- Terminal 2 (publisher) should complete without errors

### C. Test 3: Test Device Data Topic

```bash
# Publish device data (simulating hardware)
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t 'iotnarad/devices/test_device_01/data' \
    -m '{
        "timestamp": "2025-01-15T10:00:00Z",
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
```

### D. Test 4: Test Device Status Topic

```bash
# Publish device status
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t 'iotnarad/devices/test_device_01/status' \
    -m '{
        "status": "online",
        "timestamp": "2025-01-15T10:00:00Z",
        "uptime": 3600,
        "firmware_version": "1.0.0",
        "mqtt_connected": true
    }'
```

### E. Test 5: Check Dashboard App Logs

```bash
# View application logs to see if messages are received
docker logs iotnarad_app -f

# Look for messages like:
# 📨 Message received on iotnarad/devices/test_device_01/data: {...}
# ✅ Connected to MQTT Broker: mqtt:1883
```

---

## 🌐 Step 4: Test MQTT from External Client

### A. Get Your VM's External IP

```bash
# From GCP VM
curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip

# Or from GCP Console:
# Compute Engine → VM instances → Your VM → External IP
```

### B. Test from Local Machine (Windows PowerShell)

#### Option 1: Using mosquitto-clients (if installed)

```powershell
# Install mosquitto-clients (if not installed)
# Download from: https://mosquitto.org/download/

# Subscribe to all topics
mosquitto_sub -h YOUR_VM_EXTERNAL_IP -p 1883 -t '#' -v

# Publish test message (in another terminal)
mosquitto_pub -h YOUR_VM_EXTERNAL_IP -p 1883 -t 'test/external' -m '{"from": "external_client"}'
```

#### Option 2: Using Docker on Local Machine

```powershell
# If you have Docker installed locally
docker run -it --rm eclipse-mosquitto:2 mosquitto_sub \
    -h YOUR_VM_EXTERNAL_IP \
    -p 1883 \
    -t '#' \
    -v

# Publish from another terminal
docker run -it --rm eclipse-mosquitto:2 mosquitto_pub \
    -h YOUR_VM_EXTERNAL_IP \
    -p 1883 \
    -t 'test/external' \
    -m '{"from": "external_client"}'
```

#### Option 3: Using Python Script

Create a test script `test_mqtt_external.py`:

```python
import paho.mqtt.client as mqtt
import json
import time

# Your GCP VM external IP
BROKER_IP = "YOUR_VM_EXTERNAL_IP"
BROKER_PORT = 1883

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")
        client.subscribe("#")  # Subscribe to all topics
    else:
        print(f"❌ Failed to connect. Return code: {rc}")

def on_message(client, userdata, msg):
    print(f"📨 Topic: {msg.topic}")
    print(f"   Message: {msg.payload.decode()}")

# Create client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect
print(f"🔌 Connecting to {BROKER_IP}:{BROKER_PORT}...")
client.connect(BROKER_IP, BROKER_PORT, 60)

# Publish test message
test_topic = "test/external/python"
test_payload = {
    "test": True,
    "client": "python_external",
    "timestamp": "2025-01-15T10:00:00Z"
}
client.publish(test_topic, json.dumps(test_payload))
print(f"📤 Published to {test_topic}")

# Keep listening
client.loop_start()
time.sleep(10)
client.loop_stop()
client.disconnect()
```

Run it:
```bash
pip install paho-mqtt
python test_mqtt_external.py
```

### C. Test from ESP32/Arduino (Hardware)

Update your hardware code with GCP VM IP:

```cpp
// MQTT Broker
const char* mqtt_broker = "YOUR_VM_EXTERNAL_IP";  // GCP VM external IP
const int mqtt_port = 1883;
const char* device_id = "esp32_gw_01";

// Rest of your code remains the same
```

---

## 🔍 Step 5: Verify Network Connectivity

### A. Test Port Connectivity from External

```bash
# From your local machine (Windows PowerShell)
Test-NetConnection -ComputerName YOUR_VM_EXTERNAL_IP -Port 1883

# Or using telnet
telnet YOUR_VM_EXTERNAL_IP 1883

# Or using curl (if available)
curl -v telnet://YOUR_VM_EXTERNAL_IP:1883
```

### B. Test from VM Itself

```bash
# From GCP VM, test local connection
docker exec -it iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t 'test/local' \
    -m '{"test": "local"}'
```

### C. Check if Port is Listening

```bash
# On GCP VM
sudo netstat -tuln | grep 1883
# Should show: tcp 0.0.0.0:1883 LISTEN

# Or using ss
sudo ss -tuln | grep 1883
```

---

## 🛠️ Step 6: Troubleshooting

### Problem 1: Cannot Connect from External Client

**Symptoms:**
- Connection timeout
- "Connection refused" error

**Solutions:**
1. ✅ Check GCP firewall rules:
   ```bash
   gcloud compute firewall-rules list | grep mqtt
   ```

2. ✅ Verify VM has external IP:
   ```bash
   gcloud compute instances describe YOUR_VM_NAME --zone YOUR_ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
   ```

3. ✅ Check if port is open:
   ```bash
   # From external machine
   nmap -p 1883 YOUR_VM_EXTERNAL_IP
   ```

4. ✅ Verify Docker port mapping:
   ```bash
   docker ps | grep mqtt
   # Should show: 0.0.0.0:1883->1883/tcp
   ```

### Problem 2: MQTT Container Not Running

**Solution:**
```bash
# Check container status
docker ps -a | grep mqtt

# Start container
docker compose up -d mqtt

# Check logs
docker logs iotnarad_mqtt
```

### Problem 3: Connection Works but No Messages

**Solutions:**
1. ✅ Verify topic names match exactly
2. ✅ Check JSON format is valid
3. ✅ View MQTT broker logs:
   ```bash
   docker logs iotnarad_mqtt -f
   ```

4. ✅ Check dashboard app logs:
   ```bash
   docker logs iotnarad_app -f
   ```

### Problem 4: Firewall Rule Not Applied

**Solution:**
```bash
# Delete and recreate firewall rule
gcloud compute firewall-rules delete mqtt-broker-allow
gcloud compute firewall-rules create mqtt-broker-allow \
    --allow tcp:1883,tcp:9001 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow MQTT broker connections" \
    --direction INGRESS

# Wait a few seconds for rule to propagate
```

---

## 📝 Quick Test Script for GCP VM

Create `test_mqtt_gcp.sh` on your VM:

```bash
#!/bin/bash

echo "🧪 Testing MQTT on GCP VM..."
echo ""

# Test 1: Check container
echo "1️⃣ Checking MQTT container..."
docker ps | grep iotnarad_mqtt || echo "❌ MQTT container not running"

# Test 2: Publish test message
echo ""
echo "2️⃣ Publishing test message..."
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t 'test/gcp/vm' \
    -m '{"test": "from_gcp_vm", "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}'

# Test 3: Subscribe (timeout after 3 seconds)
echo ""
echo "3️⃣ Subscribing to test topic (3 seconds)..."
timeout 3 docker exec -it iotnarad_mqtt mosquitto_sub \
    -h localhost \
    -t 'test/gcp/vm' \
    -C 1 || echo "⚠️ No message received"

echo ""
echo "✅ Test complete!"
```

Make it executable and run:
```bash
chmod +x test_mqtt_gcp.sh
./test_mqtt_gcp.sh
```

---

## 📊 Testing Checklist

- [ ] GCP firewall rule created for ports 1883 and 9001
- [ ] Docker containers running on VM
- [ ] MQTT broker accessible from within VM
- [ ] MQTT broker accessible from external client
- [ ] Can publish messages from VM
- [ ] Can subscribe to messages from VM
- [ ] Can publish messages from external client
- [ ] Can subscribe to messages from external client
- [ ] Dashboard app receiving messages
- [ ] Hardware can connect (if testing with real device)

---

## 🔐 Security Recommendations

### For Production:

1. **Restrict Source IPs:**
   ```bash
   # Only allow specific IP ranges
   gcloud compute firewall-rules create mqtt-broker-allow \
       --allow tcp:1883 \
       --source-ranges YOUR_OFFICE_IP/32,YOUR_HOME_IP/32 \
       --description "Allow MQTT from trusted IPs"
   ```

2. **Enable MQTT Authentication:**
   - Update `infra/mosquitto/mosquitto.conf`:
     ```
     allow_anonymous false
     password_file /mosquitto/config/passwd
     ```
   - Create password file (inside container)

3. **Use TLS/SSL:**
   - Configure MQTT over TLS (port 8883)
   - Generate certificates

4. **Use VPN:**
   - Connect devices via VPN instead of public IP

---

## 📚 Additional Resources

- **MQTT Testing Tools:**
  - MQTT.fx (Desktop client): https://mqttfx.jensd.de/
  - MQTT Explorer (Desktop client): http://mqtt-explorer.com/
  - HiveMQ WebSocket Client: https://www.hivemq.com/demos/websocket-client/

- **GCP Documentation:**
  - Firewall Rules: https://cloud.google.com/vpc/docs/firewalls
  - VM Networking: https://cloud.google.com/compute/docs/networking

---

**Last Updated:** 2025-01-15  
**MQTT Broker:** GCP VM External IP:1883  
**Protocol:** MQTT 3.1.1  
**QoS:** 1 (At least once delivery)

