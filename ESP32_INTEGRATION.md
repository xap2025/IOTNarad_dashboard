# 🔌 ESP32 Integration Guide

Complete guide for integrating ESP32 devices with IOTNarad Dashboard.

---

## 📋 Overview

Your ESP32 devices will:
1. Connect to WiFi
2. Subscribe to MQTT configuration topic
3. Publish sensor data to MQTT
4. Receive configuration updates from dashboard
5. Store minimal config in EEPROM/SPIFFS (just connection info)

---

## 🔧 Hardware Requirements

- ESP32 Development Board
- Sensors (Temperature, Humidity, etc.)
- Analog inputs (4-20mA, 0-10V)
- Digital I/O (NPN, PNP sensors)
- Relays (optional)
- CAN Bus / Modbus modules (optional)

---

## 📚 Required Libraries

```cpp
// Install these libraries in Arduino IDE
#include <WiFi.h>
#include <PubSubClient.h>      // MQTT Client
#include <ArduinoJson.h>        // JSON handling
#include <Preferences.h>        // Store WiFi/MQTT config
```

---

## 💾 ESP32 Configuration Storage

**Store only essential info in ESP32 flash:**

```cpp
#include <Preferences.h>

Preferences preferences;

void saveBasicConfig() {
    preferences.begin("iotnarad", false);
    preferences.putString("wifi_ssid", "YourWiFi");
    preferences.putString("wifi_pass", "YourPassword");
    preferences.putString("mqtt_broker", "YOUR_GCP_VM_IP");
    preferences.putInt("mqtt_port", 1883);
    preferences.putString("device_id", "esp32_gw_01");
    preferences.end();
}

void loadBasicConfig() {
    preferences.begin("iotnarad", true);
    String wifi_ssid = preferences.getString("wifi_ssid", "");
    String wifi_pass = preferences.getString("wifi_pass", "");
    String mqtt_broker = preferences.getString("mqtt_broker", "");
    int mqtt_port = preferences.getInt("mqtt_port", 1883);
    String device_id = preferences.getString("device_id", "esp32_gw_01");
    preferences.end();
}
```

---

## 📡 Complete ESP32 Code Example

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>

// WiFi & MQTT Config (loaded from Preferences or hardcoded for testing)
const char* wifi_ssid = "YourWiFi";
const char* wifi_password = "YourPassword";
const char* mqtt_server = "YOUR_GCP_VM_IP";
const int mqtt_port = 1883;
const char* device_id = "esp32_gw_01";

// MQTT Topics
String topic_data;
String topic_config;
String topic_status;

// MQTT Client
WiFiClient espClient;
PubSubClient mqtt(espClient);

// Device Configuration (received from server)
struct DeviceConfig {
    // Analog inputs
    struct AnalogInput {
        bool enabled;
        int div;
        int mul;
        String name;
    } analog_inputs[4];
    
    // Digital I/O
    bool digital_inputs[8];
    bool digital_outputs[8];
    
    // Communication
    int publish_interval;
} config;

// Timing
unsigned long lastPublish = 0;
int publishInterval = 5000; // Default 5 seconds

void setup() {
    Serial.begin(115200);
    
    // Set up topics
    topic_data = "iotnarad/devices/" + String(device_id) + "/data";
    topic_config = "iotnarad/devices/" + String(device_id) + "/config";
    topic_status = "iotnarad/devices/" + String(device_id) + "/status";
    
    // Connect to WiFi
    setupWiFi();
    
    // Setup MQTT
    mqtt.setServer(mqtt_server, mqtt_port);
    mqtt.setCallback(mqttCallback);
    
    // Initialize hardware
    setupHardware();
    
    Serial.println("ESP32 IoT Gateway Ready!");
}

void loop() {
    // Maintain MQTT connection
    if (!mqtt.connected()) {
        reconnectMQTT();
    }
    mqtt.loop();
    
    // Publish sensor data at interval
    if (millis() - lastPublish > publishInterval) {
        publishSensorData();
        lastPublish = millis();
    }
}

void setupWiFi() {
    Serial.print("Connecting to WiFi: ");
    Serial.println(wifi_ssid);
    
    WiFi.begin(wifi_ssid, wifi_password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi Connected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi Connection Failed!");
    }
}

void reconnectMQTT() {
    while (!mqtt.connected()) {
        Serial.print("Connecting to MQTT...");
        
        if (mqtt.connect(device_id)) {
            Serial.println("Connected!");
            
            // Subscribe to config topic
            mqtt.subscribe(topic_config.c_str());
            Serial.println("Subscribed to: " + topic_config);
            
            // Publish status
            publishStatus("online");
            
        } else {
            Serial.print("Failed, rc=");
            Serial.print(mqtt.state());
            Serial.println(" Retrying in 5 seconds...");
            delay(5000);
        }
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message received on topic: ");
    Serial.println(topic);
    
    // Parse JSON
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    
    if (error) {
        Serial.print("JSON parsing failed: ");
        Serial.println(error.c_str());
        return;
    }
    
    // Update configuration from server
    updateConfiguration(doc);
}

void updateConfiguration(JsonDocument& doc) {
    Serial.println("Updating configuration...");
    
    // Update analog inputs
    if (doc.containsKey("analog")) {
        JsonArray analogInputs = doc["analog"]["input_4_20ma"];
        for (int i = 0; i < analogInputs.size() && i < 4; i++) {
            config.analog_inputs[i].enabled = analogInputs[i]["enabled"];
            config.analog_inputs[i].div = analogInputs[i]["div"];
            config.analog_inputs[i].mul = analogInputs[i]["mul"];
            config.analog_inputs[i].name = analogInputs[i]["name"].as<String>();
        }
    }
    
    // Update publish interval
    if (doc.containsKey("mqtt")) {
        publishInterval = doc["mqtt"]["publish_interval"].as<int>() * 1000;
    }
    
    Serial.println("Configuration updated successfully!");
}

void publishSensorData() {
    StaticJsonDocument<512> doc;
    
    // Basic info
    doc["device_id"] = device_id;
    doc["timestamp"] = getISOTimestamp();
    
    // Read and publish analog inputs
    for (int i = 0; i < 4; i++) {
        if (config.analog_inputs[i].enabled) {
            float raw = analogRead(36 + i); // ADC pins
            float value = (raw / config.analog_inputs[i].div) * config.analog_inputs[i].mul;
            doc["ain" + String(i)] = value;
        }
    }
    
    // Example sensor data
    doc["temperature"] = readTemperature();
    doc["humidity"] = readHumidity();
    doc["voltage_ain0"] = readVoltage(0);
    doc["current_ain1"] = readCurrent(1);
    
    // Digital inputs
    JsonArray digitalInputs = doc.createNestedArray("digital_inputs");
    for (int i = 0; i < 4; i++) {
        digitalInputs.add(digitalRead(13 + i));
    }
    
    // Serialize and publish
    char buffer[512];
    serializeJson(doc, buffer);
    
    mqtt.publish(topic_data.c_str(), buffer);
    
    Serial.print("Published: ");
    Serial.println(buffer);
}

void publishStatus(const char* status) {
    StaticJsonDocument<128> doc;
    doc["device_id"] = device_id;
    doc["status"] = status;
    doc["timestamp"] = getISOTimestamp();
    doc["ip"] = WiFi.localIP().toString();
    doc["rssi"] = WiFi.RSSI();
    
    char buffer[128];
    serializeJson(doc, buffer);
    mqtt.publish(topic_status.c_str(), buffer);
}

void setupHardware() {
    // Configure analog pins
    analogReadResolution(12); // 12-bit ADC
    
    // Configure digital I/O
    for (int i = 0; i < 4; i++) {
        pinMode(13 + i, INPUT);  // Digital inputs
        pinMode(25 + i, OUTPUT); // Digital outputs
    }
    
    Serial.println("Hardware initialized");
}

// Sensor reading functions
float readTemperature() {
    // Replace with actual sensor reading (DHT22, BME280, etc.)
    return 25.5 + (random(-10, 10) / 10.0);
}

float readHumidity() {
    // Replace with actual sensor reading
    return 60.0 + (random(-50, 50) / 10.0);
}

float readVoltage(int channel) {
    // Read 0-10V input (use voltage divider)
    int raw = analogRead(36 + channel);
    return (raw / 4095.0) * 10.0; // Scale to 0-10V
}

float readCurrent(int channel) {
    // Read 4-20mA input (use current loop converter)
    int raw = analogRead(36 + channel);
    return 4.0 + ((raw / 4095.0) * 16.0); // Scale to 4-20mA
}

String getISOTimestamp() {
    // Simple timestamp (you can use NTP for accurate time)
    unsigned long now = millis();
    char timestamp[30];
    sprintf(timestamp, "2025-10-08T%02d:%02d:%02dZ", 
            (int)((now / 3600000) % 24),
            (int)((now / 60000) % 60),
            (int)((now / 1000) % 60));
    return String(timestamp);
}
```

---

## 🧪 Testing

### 1. Upload Code to ESP32

1. Open Arduino IDE
2. Install required libraries
3. Update WiFi and MQTT credentials
4. Upload to ESP32

### 2. Monitor Serial Output

```
Connecting to WiFi: YourWiFi
.....
WiFi Connected!
IP Address: 192.168.1.100
Connecting to MQTT...Connected!
Subscribed to: iotnarad/devices/esp32_gw_01/config
Published: {"device_id":"esp32_gw_01","temperature":25.5,...}
```

### 3. Check Dashboard

1. Open dashboard: `http://YOUR_VM_IP:8050`
2. Login
3. Go to **Analytics** tab
4. You should see real-time data from ESP32

### 4. Test Configuration

1. Go to **Devices** tab
2. Select your device
3. Enable an analog input
4. Set name and multiplier
5. Click **Save Configuration**
6. ESP32 should receive config via MQTT and update

---

## 📊 Data Format Examples

### Sensor Data (ESP32 → Server)

```json
{
  "device_id": "esp32_gw_01",
  "timestamp": "2025-10-08T10:30:00Z",
  "temperature": 25.5,
  "humidity": 60.2,
  "voltage_ain0": 5.2,
  "voltage_ain1": 7.8,
  "current_ain2": 12.5,
  "current_ain3": 16.2,
  "digital_inputs": [true, false, true, false],
  "digital_outputs": [false, true, false, true],
  "relay_states": [true, false, false, false]
}
```

### Configuration (Server → ESP32)

```json
{
  "network": {
    "wifi_ssid": "YourWiFi",
    "ip_mode": "dhcp"
  },
  "mqtt": {
    "broker": "YOUR_VM_IP",
    "port": 1883,
    "publish_interval": 5
  },
  "analog": {
    "input_4_20ma": [
      {"channel": 1, "enabled": true, "div": 1, "mul": 1, "name": "Pressure"},
      {"channel": 2, "enabled": true, "div": 1, "mul": 1, "name": "Flow"}
    ]
  },
  "digital": {
    "npn_input": [
      {"channel": 1, "enabled": true, "name": "Door Sensor"},
      {"channel": 2, "enabled": true, "name": "Motion Sensor"}
    ]
  }
}
```

---

## 🔧 Advanced Features

### 1. OTA Updates

```cpp
#include <ArduinoOTA.h>

void setupOTA() {
    ArduinoOTA.setHostname(device_id);
    ArduinoOTA.begin();
}

void loop() {
    ArduinoOTA.handle();
    // ... rest of code
}
```

### 2. Deep Sleep for Battery Power

```cpp
void enterDeepSleep() {
    esp_sleep_enable_timer_wakeup(60 * 1000000); // 60 seconds
    esp_deep_sleep_start();
}
```

### 3. Modbus RTU Integration

```cpp
#include <ModbusMaster.h>

ModbusMaster modbus;

void setupModbus() {
    Serial2.begin(9600, SERIAL_8N1, 16, 17);
    modbus.begin(1, Serial2); // Slave ID 1
}

uint16_t readModbusRegister(uint16_t address) {
    uint8_t result = modbus.readHoldingRegisters(address, 1);
    if (result == modbus.ku8MBSuccess) {
        return modbus.getResponseBuffer(0);
    }
    return 0;
}
```

### 4. CAN Bus Integration

```cpp
#include <CAN.h>

void setupCAN() {
    CAN.setPins(5, 4); // RX, TX
    if (!CAN.begin(500E3)) {
        Serial.println("CAN init failed");
    }
}

void readCAN() {
    if (CAN.parsePacket()) {
        int id = CAN.packetId();
        while (CAN.available()) {
            int data = CAN.read();
            // Process CAN data
        }
    }
}
```

---

## 🐛 Troubleshooting

### WiFi Not Connecting

- Check SSID and password
- Check WiFi signal strength
- Try static IP instead of DHCP

### MQTT Connection Failed

- Verify MQTT broker IP
- Check firewall rules (port 1883)
- Test with MQTT Explorer app

### No Data in Dashboard

- Check MQTT topic format
- Verify JSON structure
- Check InfluxDB connection
- View app logs: `docker-compose logs app`

### Configuration Not Updating

- Check MQTT subscription
- Verify topic_config subscription
- Check callback function
- Monitor Serial output

---

## 📝 Pin Mapping Reference

### Analog Inputs (12-bit ADC)

| Channel | ESP32 Pin | Type | Range |
|---------|-----------|------|-------|
| AIN0 | GPIO36 (VP) | 4-20mA | 0-4095 |
| AIN1 | GPIO39 (VN) | 4-20mA | 0-4095 |
| AIN2 | GPIO34 | 1-10V | 0-4095 |
| AIN3 | GPIO35 | 1-10V | 0-4095 |

### Digital I/O

| Type | ESP32 Pins | Direction |
|------|------------|-----------|
| NPN Input | GPIO13-16 | Input |
| NPN Output | GPIO25-27 | Output |
| PNP Input | GPIO18-19 | Input |
| PNP Output | GPIO21-22 | Output |
| Relay | GPIO32-33 | Output |

### Communication

| Interface | TX Pin | RX Pin |
|-----------|--------|--------|
| Modbus RTU | GPIO17 | GPIO16 |
| CAN Bus | GPIO4 | GPIO5 |

---

## 🎯 Best Practices

1. **Memory Management**
   - Store only connection info on ESP32
   - Get full config from server
   - Use StaticJsonDocument for fixed size

2. **Error Handling**
   - Implement reconnection logic
   - Add watchdog timer
   - Log errors to MQTT

3. **Power Management**
   - Use deep sleep when possible
   - Optimize publish interval
   - Disable unused peripherals

4. **Security**
   - Use MQTT over TLS in production
   - Don't hardcode credentials
   - Implement OTA authentication

---

## 📚 Additional Resources

- [ESP32 Documentation](https://docs.espressif.com/)
- [PubSubClient Library](https://github.com/knolleary/pubsubclient)
- [ArduinoJson](https://arduinojson.org/)
- [MQTT Protocol](https://mqtt.org/)

---

**Happy Coding! 🚀**

