# 📋 Device Configuration Save & MQTT Flow

**Document Version:** 1.0  
**Last Updated:** November 18, 2025  
**Purpose:** Complete explanation of how device configurations are saved to database and sent to hardware via MQTT

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Database Structure](#database-structure)
3. [Save Configuration Flow (All Tabs)](#save-configuration-flow-all-tabs)
4. [Step-by-Step: Analog Tab Save](#step-by-step-analog-tab-save)
5. [Step-by-Step: Digital Tab Save](#step-by-step-digital-tab-save)
6. [Step-by-Step: RS485 MODBUS Tab Save](#step-by-step-rs485-modbus-tab-save)
7. [Step-by-Step: CAN Bus Tab Save](#step-by-step-can-bus-tab-save)
8. [Merged JSON Building Process](#merged-json-building-process)
9. [MQTT Publishing Flow](#mqtt-publishing-flow)
10. [Device Request & Receive Flow](#device-request--receive-flow)

---

## 🎯 Overview

When a user clicks **"Save Configuration"** in any tab (Analog, Digital, RS485 MODBUS, or CAN Bus), the system:

1. ✅ **Validates** user input (device selection, required fields)
2. ✅ **Builds** JSON configuration for the selected tab
3. ✅ **Saves** tab-specific data to its individual InfluxDB measurement
4. ✅ **Fetches** latest configs from other tabs from database
5. ✅ **Merges** all sections into ONE complete JSON
6. ✅ **Saves** merged JSON to `Device_Config` measurement
7. ✅ **Publishes** complete merged JSON to device via MQTT

**Important:** The merged JSON **always** contains all sections (Analog, Digital, RS485 MODBUS, CAN Bus), even if some sections are empty or default values.

---

## 🗄️ Database Structure

### Individual Section Tables (Measurements)

| Measurement | Description | Contains |
|------------|-------------|----------|
| `Device_Config_Analog` | Analog configuration | 4-20mA inputs, 0-10V inputs, 0-10V outputs, scan_rate |
| `Device_Config_Digital` | Digital configuration | NPN inputs/outputs, PNP inputs/outputs, relays, scan_rate |
| `Device_Config_Modbus` | RS485 MODBUS configuration | Communication settings, protocol settings, slave devices |
| `Device_Config_CANBus` | CAN Bus configuration | Communication settings, CAN messages, data mappings |

### Merged Configuration Table (Measurement)

| Measurement | Description | Contains |
|------------|-------------|----------|
| `Device_Config` | **Complete merged JSON** | ONE JSON string containing all sections (`analog`, `digital`, `rs485_modbus`, `can_bus`) |

**Critical Point:** `Device_Config` **only** stores the merged JSON string. Individual sections are stored in their respective measurements.

---

## 💾 Save Configuration Flow (All Tabs)

### General Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User clicks "Save Configuration" in any tab                 │
│ (Analog / Digital / RS485 MODBUS / CAN Bus)                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Validate Input                                      │
│ - Check device is selected                                  │
│ - Validate required fields (scan_rate, values, etc.)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Build Tab-Specific JSON                            │
│ - Collect UI form data                                      │
│ - Use ConfigJSONBuilder to build JSON                       │
│ - Example: analog_config = {                                │
│     "input_4_20ma": [...],                                  │
│     "input_1_10v": [...],                                   │
│     "output_0_10v": [...],                                  │
│     "scan_rate": 1000                                       │
│   }                                                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Save to Individual Table                           │
│ - Call: db_service.save_config_sections_only()             │
│ - Saves ONLY the current tab's section                     │
│   • Analog → Device_Config_Analog                           │
│   • Digital → Device_Config_Digital                         │
│   • MODBUS → Device_Config_Modbus                           │
│   • CAN Bus → Device_Config_CANBus                          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Fetch Latest Configs from Other Tabs               │
│ - Get latest:                                               │
│   • digital_config = db_service.get_digital_config()       │
│   • modbus_config = db_service.get_modbus_config()         │
│   • can_bus_config = db_service.get_can_bus_config()       │
│ - If tab is Analog, fetch Digital/Modbus/CAN Bus           │
│ - If tab is Digital, fetch Analog/Modbus/CAN Bus           │
│ - etc.                                                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Build Merged Complete Config                       │
│ complete_config = {                                         │
│   "device_id": "0x7f3b",                                    │
│   "analog": { ... },      // From current save              │
│   "digital": { ... },     // From database                  │
│   "rs485_modbus": { ... }, // From database                 │
│   "can_bus": { ... }      // From database                  │
│ }                                                           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Save Merged JSON to Device_Config                  │
│ - Call: db_service.save_device_config()                    │
│ - Saves complete_config as JSON string                     │
│ - Measurement: Device_Config                                │
│ - Tag: device_id = "0x7f3b"                                │
│ - Field: config_json = "{ ... }" (string)                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: Publish to MQTT                                     │
│ - Call: mqtt_service.publish_config()                      │
│ - Topic: Dev/Checksum/<Device ID>                          │
│ - Payload: complete_config (merged JSON)                   │
│ - QoS: 1, Retain: True                                     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ ✅ Success: Configuration saved and published               │
│ - UI shows success message                                  │
│ - Device receives complete merged JSON via MQTT             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Step-by-Step: Analog Tab Save

### User Action
- Clicks **"Save Configuration"** button in **Analog** tab
- Device selected: `0x7f3b`

### Code Flow

**File:** `app/pages/device_config.py`  
**Function:** `save_analog_configuration()`

#### Step 1: Collect UI Data
```python
# Collect from UI form inputs
input_4_20ma_data = [
    {"channel": 1, "enabled": True, "divider": 100, "multiplier": 1, 
     "io_pin": "AIN0", "name": "Temperature Sensor"},
    {"channel": 2, "enabled": False, ...}
]

input_1_10v_data = [
    {"channel": 3, "enabled": True, "divider": 1, "multiplier": 1, 
     "io_pin": "AIN2", "name": "Pressure Sensor"},
    ...
]

output_0_10v_data = [
    {"channel": 1, "enabled": True, "value": 5.5, 
     "io_pin": "DOUT0", "name": "Valve Control"},
    ...
]

scan_rate = 1000  # From UI input
```

#### Step 2: Build Analog JSON
```python
from app.services.config_json_builder import ConfigJSONBuilder

builder = ConfigJSONBuilder()
analog_config = builder.build_analog_config(
    input_4_20ma_data=input_4_20ma_data,
    input_1_10v_data=input_1_10v_data,
    output_0_10v_data=output_0_10v_data,
    scan_rate=scan_rate
)

# Result:
analog_config = {
    "input_4_20ma": [...],
    "input_1_10v": [...],
    "output_0_10v": [...],
    "scan_rate": 1000
}
```

#### Step 3: Save to Device_Config_Analog
```python
from app.services.device_config_db import DeviceConfigDBService

db_service = DeviceConfigDBService()
config_with_analog_only = {"analog": analog_config}

# Save ONLY analog section to Device_Config_Analog
db_service.save_config_sections_only(
    device_id="0x7f3b",
    config=config_with_analog_only
)

# This creates InfluxDB points in Device_Config_Analog measurement:
# - One point per 4-20mA input channel
# - One point per 0-10V input channel  
# - One point per 0-10V output channel (with value stored as int millivolts)
```

#### Step 4: Fetch Other Sections
```python
# Get latest configs from other tabs
digital_config_db = db_service.get_digital_config("0x7f3b")
modbus_config_db = db_service.get_modbus_config("0x7f3b")
can_bus_config_db = db_service.get_can_bus_config("0x7f3b")
```

#### Step 5: Build Merged Config
```python
complete_config = {
    "device_id": "0x7f3b"
}

# Add current tab's config (just saved)
complete_config["analog"] = analog_config

# Add other sections if they exist
if digital_config_db:
    complete_config["digital"] = digital_config_db
if modbus_config_db:
    complete_config["rs485_modbus"] = modbus_config_db
if can_bus_config_db:
    complete_config["can_bus"] = can_bus_config_db
```

#### Step 6: Save Merged JSON to Device_Config
```python
# Save complete merged JSON to Device_Config
db_service.save_device_config(
    device_id="0x7f3b",
    config=complete_config
)

# This creates ONE point in Device_Config measurement:
# Measurement: Device_Config
# Tag: device_id = "0x7f3b"
# Field: config_json = "{'device_id': '0x7f3b', 'analog': {...}, ...}" (JSON string)
# Time: Current timestamp
```

#### Step 7: Publish to MQTT
```python
from app.services.mqtt_client import MQTTClientService

mqtt_service = MQTTClientService()
mqtt_service.publish_config(
    device_id="0x7f3b",
    config=complete_config
)

# This publishes:
# Topic: Dev/Checksum/0x7f3b
# Payload: complete_config (complete merged JSON)
# QoS: 1, Retain: True
```

---

## 📊 Step-by-Step: Digital Tab Save

### User Action
- Clicks **"Save Configuration"** button in **Digital** tab
- Device selected: `0x7f3b`

### Code Flow

**File:** `app/pages/device_config.py`  
**Function:** `save_digital_configuration()`

#### Step 1: Collect UI Data
```python
# Collect from UI form inputs
npn_input_enable = [True, False, True, False]
npn_input_name = ["INP1H", "INP2H", "INP3H", "INP4H"]
npn_output_enable = [True, True, False, False]
npn_output_name = ["OUTL1", "OUTL2", "OUTL3", "OUTL4"]
# ... (pnp_input, pnp_output, relay)
digital_scan_rate = 1000
```

#### Step 2: Build Digital JSON
```python
builder = ConfigJSONBuilder()
digital_config = builder.build_digital_config(
    npn_input_data=[...],
    npn_output_data=[...],
    pnp_input_data=[...],
    pnp_output_data=[...],
    relay_data=[...]
)

# Result:
digital_config = {
    "npn_input": [...],
    "npn_output": [...],
    "pnp_input": [...],
    "pnp_output": [...],
    "relay": [...]
}
```

#### Step 3: Save to Device_Config_Digital
```python
config_with_digital_only = {"digital": digital_config}
db_service.save_config_sections_only(
    device_id="0x7f3b",
    config=config_with_digital_only
)

# Creates points in Device_Config_Digital measurement
```

#### Step 4: Fetch Other Sections
```python
# Get Analog, MODBUS, CAN Bus configs from database
analog_config_db = db_service.get_analog_config("0x7f3b")
modbus_config_db = db_service.get_modbus_config("0x7f3b")
can_bus_config_db = db_service.get_can_bus_config("0x7f3b")
```

#### Step 5: Build Merged Config
```python
complete_config = {
    "device_id": "0x7f3b",
    "digital": digital_config  # Current tab (just saved)
}

if analog_config_db:
    complete_config["analog"] = analog_config_db
if modbus_config_db:
    complete_config["rs485_modbus"] = modbus_config_db
if can_bus_config_db:
    complete_config["can_bus"] = can_bus_config_db
```

#### Step 6 & 7: Save Merged JSON & Publish to MQTT
```python
# Save to Device_Config
db_service.save_device_config("0x7f3b", complete_config)

# Publish to MQTT
mqtt_service.publish_config("0x7f3b", complete_config)
```

---

## 📊 Step-by-Step: RS485 MODBUS Tab Save

### User Action
- Clicks **"Save Configuration"** button in **RS485 MODBUS** tab
- Device selected: `0x7f3b`

### Code Flow

**File:** `app/pages/device_config.py`  
**Function:** `save_modbus_configuration()`

#### Steps (Same pattern as Analog/Digital):
1. **Collect UI Data**: Baud rate, data bits, parity, stop bits, mode, role, polling interval, slave devices
2. **Build MODBUS JSON**: `builder.build_modbus_config(...)`
3. **Save to Device_Config_Modbus**: `db_service.save_config_sections_only(...)`
4. **Fetch Other Sections**: Get Analog, Digital, CAN Bus from database
5. **Build Merged Config**: Combine all sections
6. **Save to Device_Config**: `db_service.save_device_config(...)`
7. **Publish to MQTT**: `mqtt_service.publish_config(...)`

---

## 📊 Step-by-Step: CAN Bus Tab Save

### User Action
- Clicks **"Save Configuration"** button in **CAN Bus** tab
- Device selected: `0x7f3b`

### Code Flow

**File:** `app/pages/device_config.py`  
**Function:** `save_canbus_configuration()`

#### Steps (Same pattern):
1. **Collect UI Data**: Baud rate, identifier length, CAN mode, filter settings, CAN messages, data mappings
2. **Build CAN Bus JSON**: `builder.build_can_bus_config(...)`
3. **Save to Device_Config_CANBus**: `db_service.save_config_sections_only(...)`
4. **Fetch Other Sections**: Get Analog, Digital, MODBUS from database
5. **Build Merged Config**: Combine all sections
6. **Save to Device_Config**: `db_service.save_device_config(...)`
7. **Publish to MQTT**: `mqtt_service.publish_config(...)`

---

## 🔄 Merged JSON Building Process

### Why Merge?

Each tab saves **only its own section** to avoid overwriting other sections. However, the device needs the **complete configuration** as one JSON.

### Merge Logic

```python
# After saving current tab's section, fetch all other sections:
complete_config = {
    "device_id": device_id
}

# Add current tab (just saved)
if saving_analog:
    complete_config["analog"] = analog_config  # From current save
    # Fetch others from database
    complete_config["digital"] = db_service.get_digital_config(device_id)
    complete_config["rs485_modbus"] = db_service.get_modbus_config(device_id)
    complete_config["can_bus"] = db_service.get_can_bus_config(device_id)

elif saving_digital:
    complete_config["analog"] = db_service.get_analog_config(device_id)  # From database
    complete_config["digital"] = digital_config  # From current save
    complete_config["rs485_modbus"] = db_service.get_modbus_config(device_id)
    complete_config["can_bus"] = db_service.get_can_bus_config(device_id)

# ... (same for MODBUS and CAN Bus)
```

### Example Merged JSON

```json
{
  "device_id": "0x7f3b",
  "analog": {
    "input_4_20ma": [...],
    "input_1_10v": [...],
    "output_0_10v": [...],
    "scan_rate": 1000
  },
  "digital": {
    "npn_input": [...],
    "npn_output": [...],
    "pnp_input": [...],
    "pnp_output": [...],
    "relay": [...]
  },
  "rs485_modbus": {
    "enabled": true,
    "communication_settings": {...},
    "protocol_settings": {...},
    "polling_interval_ms": 1000,
    "slave_devices": [...]
  },
  "can_bus": {
    "enabled": true,
    "communication_settings": {...},
    "can_messages": [...],
    "data_mapping": [...]
  }
}
```

**Important:** Even if a section is empty or has default values, it will still be included in the merged JSON (with empty arrays or default values).

---

## 📡 MQTT Publishing Flow

### When Configuration is Published

1. ✅ **After saving any tab** (Analog, Digital, MODBUS, CAN Bus)
2. ✅ **After merging all sections** into complete JSON
3. ✅ **Immediately after** saving merged JSON to `Device_Config`

### MQTT Publishing Details

**File:** `app/services/mqtt_client.py`  
**Function:** `publish_config()`

```python
def publish_config(self, device_id: str, config: Dict[str, Any]):
    """
    Publish device configuration to Dev/Checksum/<Device ID>
    Device subscribes to this topic to receive configuration updates
    """
    topic = f"Dev/Checksum/{device_id}"
    return self.publish(topic, config, qos=1, retain=True)
```

### MQTT Topic Structure

| Topic Pattern | Example | Description |
|--------------|---------|-------------|
| `Dev/Checksum/<Device ID>` | `Dev/Checksum/0x7f3b` | Complete merged JSON configuration |

### MQTT Message Properties

- **QoS:** 1 (At least once delivery - ensures message reaches device)
- **Retain:** True (MQTT broker stores last message for new subscribers)
- **Payload:** Complete merged JSON (all sections)

### Why Retain = True?

When a device subscribes to `Dev/Checksum/<Device ID>`, if `retain=True`, the broker immediately sends the **last published configuration** (even if device was offline). This ensures device always gets the latest configuration on startup.

---

## 🔄 Device Request & Receive Flow

### Current Implementation: Complete Merged JSON Only

**⚠️ Important:** Currently, devices can **ONLY** receive the **complete merged JSON** containing all sections (Analog, Digital, RS485 MODBUS, CAN Bus). Individual sections are **NOT** published separately via MQTT.

**How it works:**

1. **Individual sections are stored separately** in InfluxDB:
   - `Device_Config_Analog` - Analog configuration
   - `Device_Config_Digital` - Digital configuration
   - `Device_Config_Modbus` - RS485 MODBUS configuration
   - `Device_Config_CANBus` - CAN Bus configuration

2. **Individual sections can be retrieved** via Python functions:
   - `get_analog_config(device_id)` - Returns only analog JSON
   - `get_digital_config(device_id)` - Returns only digital JSON
   - `get_modbus_config(device_id)` - Returns only MODBUS JSON
   - `get_can_bus_config(device_id)` - Returns only CAN Bus JSON

3. **MQTT publishes ONLY complete merged JSON:**
   - Topic: `Dev/Checksum/<Device ID>`
   - Payload: Complete merged JSON with all sections
   - **No separate topics** for individual sections

### Can Device Request Individual Sections?

**Current Status:** ❌ **Not Supported**

Currently, there is **NO mechanism** for devices to request individual sections (like just Analog, or just Digital). The system always publishes the complete merged JSON.

**If you need individual section requests**, you would need to implement:

1. **New MQTT topics** for each section:
   - `Dev/Config/Analog/<Device ID>` - Analog only
   - `Dev/Config/Digital/<Device ID>` - Digital only
   - `Dev/Config/Modbus/<Device ID>` - MODBUS only
   - `Dev/Config/CANBus/<Device ID>` - CAN Bus only

2. **Device request mechanism** (optional):
   - Device publishes request: `Dev/Request/Analog/<Device ID>`
   - Server responds: `Dev/Config/Analog/<Device ID>` with analog JSON

3. **MQTT callback handler** in `app/main.py` to listen for device requests

**Recommendation:** For most use cases, the **complete merged JSON** is sufficient. Devices can parse the JSON and extract only the sections they need.

### How Device Receives Configuration

**Method 1: Device Subscribes on Startup**

```
┌─────────────┐                           ┌──────────────┐
│   Device    │                           │  MQTT Broker │
│  (Hardware) │                           │   (Mosquitto)│
└──────┬──────┘                           └──────┬───────┘
       │                                         │
       │ 1. Subscribe: Dev/Checksum/0x7f3b     │
       │────────────────────────────────────────>│
       │                                         │
       │ 2. Broker sends retained message       │
       │    (Last complete merged JSON)          │
       │<────────────────────────────────────────│
       │    {"device_id": "0x7f3b",             │
       │     "analog": {...},                   │
       │     "digital": {...},                  │
       │     "rs485_modbus": {...},             │
       │     "can_bus": {...}}                  │
       │                                         │
       │ 3. Device processes complete config     │
       │    (or extracts only needed sections)   │
       │                                         │
```

**Method 2: Device Receives on Save (Real-time)**

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Dashboard  │     │  MQTT Broker │     │   Device    │
│   (Server)  │     │  (Mosquitto) │     │  (Hardware) │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                     │
       │ User saves config │                     │
       │                   │                     │
       │ 1. Publish:       │                     │
       │    Dev/Checksum/0x7f3b                 │
       │──────────────────>│                     │
       │    {complete merged JSON}              │
       │                   │                     │
       │                   │ 2. Forward to       │
       │                   │    subscribers      │
       │                   │────────────────────>│
       │                   │    {complete JSON}  │
       │                   │                     │
       │                   │ 3. Device processes │
       │                   │    complete config  │
       │                   │                     │
```

### Device Implementation

Hardware should:

1. ✅ **Subscribe** to `Dev/Checksum/<Device ID>` on startup
   ```cpp
   // Example (C++/Arduino)
   mqttClient.subscribe("Dev/Checksum/0x7f3b");
   ```

2. ✅ **Handle** incoming configuration messages (Complete Merged JSON)
   ```cpp
   void onMqttMessage(String topic, String payload) {
       if (topic == "Dev/Checksum/0x7f3b") {
           // Parse complete merged JSON payload
           DynamicJsonDocument doc(8192);  // Use larger size for complete JSON
           deserializeJson(doc, payload);
           
           // Extract individual sections from complete JSON
           if (doc.containsKey("analog")) {
               JsonObject analog = doc["analog"];
               applyAnalogConfig(analog);
           }
           
           if (doc.containsKey("digital")) {
               JsonObject digital = doc["digital"];
               applyDigitalConfig(digital);
           }
           
           if (doc.containsKey("rs485_modbus")) {
               JsonObject modbus = doc["rs485_modbus"];
               applyModbusConfig(modbus);
           }
           
           if (doc.containsKey("can_bus")) {
               JsonObject canBus = doc["can_bus"];
               applyCanBusConfig(canBus);
           }
       }
   }
   ```

3. ✅ **Acknowledge** (Optional) by publishing to `Dev/ConfigACK/<Device ID>`
   ```cpp
   // Optional: Send acknowledgment
   String ackTopic = "Dev/ConfigACK/0x7f3b";
   String ackPayload = "{\"status\": \"success\", \"message\": \"Config applied\"}";
   mqttClient.publish(ackTopic, ackPayload);
   ```

**Note:** Since devices receive the **complete merged JSON**, they can:
- Process all sections at once
- Extract only the sections they need
- Ignore sections that don't apply to their hardware
- Store the complete JSON for later use

---

## 📊 Complete Flow Example: Analog Tab Save

### Scenario
- **Device:** `0x7f3b`
- **User Action:** Click "Save Configuration" in Analog tab
- **Analog Config:** 4-20mA input enabled, 0-10V output set to 5.5V, scan_rate = 2000
- **Existing Configs:** Digital config already saved, MODBUS and CAN Bus empty

### Step-by-Step Execution

#### 1. User Clicks Save Button
```
UI: User clicks "Save Configuration" in Analog tab
→ Callback: save_analog_configuration() triggered
```

#### 2. Validate Input
```python
# Check device selected
if not serial_number:  # serial_number = "0x7f3b"
    return error_message

# Check scan_rate valid
if scan_rate < 1000:  # scan_rate = 2000
    return error_message
```

#### 3. Build Analog JSON
```python
analog_config = {
    "input_4_20ma": [
        {"channel": 1, "enabled": True, "divider": 100, "multiplier": 1, 
         "io_pin": "AIN0", "name": "Temperature", ...}
    ],
    "input_1_10v": [...],
    "output_0_10v": [
        {"channel": 1, "enabled": True, "value": 5.5, 
         "io_pin": "DOUT0", "name": "Valve Control", ...}
    ],
    "scan_rate": 2000
}
```

#### 4. Save to Device_Config_Analog
```python
# InfluxDB writes:
Measurement: Device_Config_Analog
Tag: device_id = "0x7f3b"
Tag: channel_type = "input_4_20ma"
Tag: channel = "1"
Tag: io_pin = "AIN0"
Tag: name = "Temperature"
Field: enabled = true
Field: divider = 100
Field: multiplier = 1
Field: scan_rate = 2000
Time: 2025-11-18T12:30:00Z

# ... (similar points for other channels)
```

#### 5. Fetch Other Sections
```python
digital_config_db = {
    "npn_input": [...],
    "npn_output": [...],
    ...
}  # ✅ Found in database

modbus_config_db = None  # ❌ Not configured yet
can_bus_config_db = None  # ❌ Not configured yet
```

#### 6. Build Merged Config
```python
complete_config = {
    "device_id": "0x7f3b",
    "analog": {
        # ... (from current save)
    },
    "digital": {
        # ... (from database)
    },
    "rs485_modbus": None,  # Not configured
    "can_bus": None  # Not configured
}
```

#### 7. Save to Device_Config
```python
# InfluxDB writes:
Measurement: Device_Config
Tag: device_id = "0x7f3b"
Field: config_json = "{'device_id': '0x7f3b', 'analog': {...}, 'digital': {...}, ...}" (JSON string)
Time: 2025-11-18T12:30:00Z
```

#### 8. Publish to MQTT
```python
# MQTT Publish:
Topic: Dev/Checksum/0x7f3b
Payload: {
    "device_id": "0x7f3b",
    "analog": {...},
    "digital": {...},
    "rs485_modbus": None,
    "can_bus": None
}
QoS: 1
Retain: True
```

#### 9. Device Receives Configuration
```
Device subscribes to Dev/Checksum/0x7f3b
→ Receives retained message with complete merged JSON
→ Parses JSON
→ Applies analog configuration (scan_rate = 2000, output = 5.5V)
→ Applies digital configuration (existing settings)
→ Saves configuration to device memory
```

---

## 🔍 Key Points Summary

### ✅ What Happens When You Save?

1. **Individual Section Saved:** Current tab's data → Individual measurement table
   - Analog → `Device_Config_Analog`
   - Digital → `Device_Config_Digital`
   - MODBUS → `Device_Config_Modbus`
   - CAN Bus → `Device_Config_CANBus`

2. **Merged JSON Built:** Fetches all sections from database → Combines into ONE JSON

3. **Merged JSON Saved:** Complete merged JSON → `Device_Config` measurement

4. **MQTT Published:** Complete merged JSON → `Dev/Checksum/<Device ID>` topic

### ✅ Why This Design?

- **Separation of Concerns:** Each section saved independently
- **No Data Loss:** Saving one tab doesn't overwrite other tabs
- **Complete Config:** Device always receives complete merged JSON
- **Real-time Updates:** Device receives config immediately after save
- **Offline Support:** Retained MQTT messages ensure device gets config on reconnect

### ✅ Database Tables Summary

| Table | Purpose | When Updated |
|-------|---------|--------------|
| `Device_Config_Analog` | Store analog channel configurations | Analog tab save |
| `Device_Config_Digital` | Store digital I/O configurations | Digital tab save |
| `Device_Config_Modbus` | Store RS485 MODBUS settings | MODBUS tab save |
| `Device_Config_CANBus` | Store CAN Bus settings | CAN Bus tab save |
| `Device_Config` | Store complete merged JSON | **Every tab save** |

### ✅ MQTT Flow Summary

| Action | Topic | Payload | When |
|--------|-------|---------|------|
| Server publishes config | `Dev/Checksum/<Device ID>` | Complete merged JSON | After any tab save |
| Device subscribes | `Dev/Checksum/<Device ID>` | - | On startup |
| Device receives config | `Dev/Checksum/<Device ID>` | Complete merged JSON | Immediately (retained) or on save |
| Device acknowledges (optional) | `Dev/ConfigACK/<Device ID>` | `{"status": "success"}` | After applying config |

---

## 📝 Code References

### Key Files

1. **`app/pages/device_config.py`**
   - `save_analog_configuration()` - Analog save callback
   - `save_digital_configuration()` - Digital save callback
   - `save_modbus_configuration()` - MODBUS save callback
   - `save_canbus_configuration()` - CAN Bus save callback

2. **`app/services/config_json_builder.py`**
   - `build_analog_config()` - Build analog JSON
   - `build_digital_config()` - Build digital JSON
   - `build_modbus_config()` - Build MODBUS JSON
   - `build_can_bus_config()` - Build CAN Bus JSON

3. **`app/services/device_config_db.py`**
   - `save_config_sections_only()` - Save individual sections
   - `save_device_config()` - Save merged JSON to Device_Config
   - `get_analog_config()` - Fetch analog config
   - `get_digital_config()` - Fetch digital config
   - `get_modbus_config()` - Fetch MODBUS config
   - `get_can_bus_config()` - Fetch CAN Bus config

4. **`app/services/mqtt_client.py`**
   - `publish_config()` - Publish configuration to device

---

**Document Version:** 1.0  
**Last Updated:** November 18, 2025  
**Status:** ✅ Active

