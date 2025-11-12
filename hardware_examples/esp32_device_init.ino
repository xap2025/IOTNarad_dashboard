/*
 * ESP32 Device Initialization Example
 * 
 * This code demonstrates how to:
 * 1. Connect to WiFi
 * 2. Connect to MQTT broker (GCP VM)
 * 3. Send device initialization message
 * 4. Receive and process acknowledgment
 * 
 * Required Libraries:
 * - WiFi (built-in)
 * - PubSubClient (install via Library Manager)
 * - ArduinoJson (install via Library Manager)
 * 
 * Installation:
 * 1. Install PubSubClient: Tools → Manage Libraries → Search "PubSubClient"
 * 2. Install ArduinoJson: Tools → Manage Libraries → Search "ArduinoJson"
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ============================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================

// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker (GCP VM)
const char* mqtt_broker = "34.131.186.225";  // Replace with your GCP VM IP
const int mqtt_port = 1883;

// Device Serial Number (Unique per device)
const char* serial_number = "DF5647";  // Replace with your device serial number

// ============================================
// GLOBAL VARIABLES
// ============================================

WiFiClient espClient;
PubSubClient client(espClient);

// State tracking
bool mqtt_connected = false;
bool init_sent = false;
bool ack_received = false;
unsigned long last_reconnect_attempt = 0;
unsigned long last_init_attempt = 0;

// ============================================
// SETUP
// ============================================

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n");
  Serial.println("========================================");
  Serial.println("ESP32 Device Initialization");
  Serial.println("========================================");
  Serial.print("Serial Number: ");
  Serial.println(serial_number);
  Serial.println();
  
  // Connect to WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(mqttCallback);
  
  Serial.println("Setup complete!");
  Serial.println();
}

// ============================================
// MAIN LOOP
// ============================================

void loop() {
  // Maintain WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️  WiFi disconnected. Reconnecting...");
    setup_wifi();
  }
  
  // Maintain MQTT connection
  if (!client.connected()) {
    mqtt_connected = false;
    unsigned long now = millis();
    if (now - last_reconnect_attempt > 5000) {
      last_reconnect_attempt = now;
      reconnect_mqtt();
    }
  } else {
    mqtt_connected = true;
    client.loop();
    
    // Send initialization if connected and not sent yet
    if (!init_sent && (millis() - last_init_attempt > 2000)) {
      send_device_init();
      last_init_attempt = millis();
    }
  }
  
  delay(100);
}

// ============================================
// WIFI SETUP
// ============================================

void setup_wifi() {
  Serial.print("📶 Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected!");
    Serial.print("   IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("   Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
    Serial.println("   Check SSID and password");
  }
  Serial.println();
}

// ============================================
// MQTT CONNECTION
// ============================================

void reconnect_mqtt() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️  WiFi not connected. Cannot connect to MQTT.");
    return;
  }
  
  Serial.print("🔌 Connecting to MQTT broker: ");
  Serial.print(mqtt_broker);
  Serial.print(":");
  Serial.println(mqtt_port);
  
  // Connect with serial number as client ID
  if (client.connect(serial_number)) {
    Serial.println("✅ MQTT connected!");
    
    // Subscribe to acknowledgment topic
    String ack_topic = "Dev/Ack/";
    ack_topic += serial_number;
    
    if (client.subscribe(ack_topic.c_str())) {
      Serial.print("📡 Subscribed to: ");
      Serial.println(ack_topic);
    } else {
      Serial.println("❌ Failed to subscribe to acknowledgment topic");
    }
    
    // Reset flags to allow re-initialization
    init_sent = false;
    ack_received = false;
    
  } else {
    Serial.print("❌ MQTT connection failed. State: ");
    Serial.println(client.state());
    Serial.println("   Retrying in 5 seconds...");
  }
  Serial.println();
}

// ============================================
// SEND DEVICE INITIALIZATION
// ============================================

void send_device_init() {
  if (!client.connected()) {
    Serial.println("⚠️  MQTT not connected. Cannot send initialization.");
    return;
  }
  
  // Create topic
  String topic = "Dev/Init/";
  topic += serial_number;
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["SerialNumber"] = serial_number;
  
  char payload[200];
  serializeJson(doc, payload);
  
  // Publish
  if (client.publish(topic.c_str(), payload, true)) {  // retain=true
    Serial.println("📤 Device initialization sent!");
    Serial.print("   Topic: ");
    Serial.println(topic);
    Serial.print("   Payload: ");
    Serial.println(payload);
    init_sent = true;
  } else {
    Serial.println("❌ Failed to send initialization message");
    Serial.print("   MQTT State: ");
    Serial.println(client.state());
  }
  Serial.println();
}

// ============================================
// MQTT MESSAGE CALLBACK
// ============================================

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.println("📨 MQTT message received!");
  Serial.print("   Topic: ");
  Serial.println(topic);
  
  // Convert payload to string
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("   Payload: ");
  Serial.println(message);
  
  // Check if this is an acknowledgment (topic: Dev/Ack/<SerialNumber>)
  String topic_str = String(topic);
  if (topic_str.startsWith("Dev/Ack/")) {
    // Parse JSON
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
      Serial.print("❌ JSON parsing failed: ");
      Serial.println(error.c_str());
      return;
    }
    
    // Extract acknowledgment data
    const char* status = doc["status"];
    const char* msg = doc["message"];
    const char* timestamp = doc["timestamp"];
    
    Serial.println();
    Serial.println("✅ ACKNOWLEDGMENT RECEIVED!");
    Serial.print("   Status: ");
    Serial.println(status);
    Serial.print("   Message: ");
    Serial.println(msg);
    if (timestamp) {
      Serial.print("   Timestamp: ");
      Serial.println(timestamp);
    }
    
    ack_received = true;
    
    // Optional: Blink LED or other indication
    // digitalWrite(LED_BUILTIN, HIGH);
    // delay(500);
    // digitalWrite(LED_BUILTIN, LOW);
    
  } else {
    Serial.println("⚠️  Unknown message topic");
  }
  Serial.println();
}

// ============================================
// STATUS INFORMATION
// ============================================

void print_status() {
  Serial.println("========================================");
  Serial.println("Device Status");
  Serial.println("========================================");
  Serial.print("WiFi: ");
  Serial.println(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
  Serial.print("MQTT: ");
  Serial.println(mqtt_connected ? "Connected" : "Disconnected");
  Serial.print("Init Sent: ");
  Serial.println(init_sent ? "Yes" : "No");
  Serial.print("Ack Received: ");
  Serial.println(ack_received ? "Yes" : "No");
  Serial.println("========================================");
  Serial.println();
}

