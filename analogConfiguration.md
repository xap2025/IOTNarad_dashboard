# Analog Configuration - Complete Process Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [InfluxDB Table Structure](#influxdb-table-structure)
3. [Visual Table View in InfluxDB Data Explorer](#visual-table-view-in-influxdb-data-explorer)
4. [Data Saving Process](#data-saving-process)
5. [Viewing Individual Parameter Values](#viewing-individual-parameter-values)
6. [MQTT Transmission to Hardware](#mqtt-transmission-to-hardware)
7. [Complete Data Flow Diagram](#complete-data-flow-diagram)

---

## Overview

When a user configures Analog settings (4-20mA inputs, 0-10V inputs, 0-10V outputs) and clicks "Save Configuration", the system:

1. **Validates** all required parameters
2. **Saves** to InfluxDB in structured format
3. **Stores** complete JSON configuration
4. **Publishes** to MQTT for hardware to receive

---

## InfluxDB Table Structure

### Measurement: `Device_Config_Analog`

This measurement stores individual analog channel configurations. Each row represents one channel configuration.

#### **Tags** (Indexed - Used for Filtering)
- `device_id` - **Serial Number (Sr_No)** from Device_info measurement
- `channel_type` - Type of channel: `input_4_20ma`, `input_1_10v`, `output_0_10v`
- `channel` - Channel number (1, 2, 3, 4)
- `io_pin` - Physical IO pin name (AIN0, AIN1, AIN2, AIN3, DOUT0, DOUT1)
- `name` - Channel name/label (e.g., "Temperature Sensor", "Pressure", "Valve Control")

#### **Fields** (Actual Data Values)
- `enabled` - Boolean: Channel enabled/disabled
- `divider` - Float: Division factor for scaling
- `multiplier` - Float: Multiplication factor for scaling
- `scan_rate` - Integer: Scan rate in seconds (only for 0-10V inputs, minimum 1000)
- `min_value` - Float: Minimum value (4 for 4-20mA, 0 for 0-10V)
- `max_value` - Float: Maximum value (20 for 4-20mA, 10 for 0-10V)
- `unit` - String: Unit of measurement ("mA" or "V")
- `value` - Float: Output value (only for 0-10V outputs)

#### **Timestamp**
- `time` - When the configuration was saved (nanosecond precision)

---

## Visual Table View in InfluxDB Data Explorer

When you open `Device_Config_Analog` measurement in InfluxDB Data Explorer, you'll see a table like this:

### **Example: Device with Serial Number "TEST78787"**

| time | device_id | channel_type | channel | io_pin | name | enabled | divider | multiplier | scan_rate | min_value | max_value | unit | value |
|------|-----------|--------------|---------|--------|------|---------|---------|------------|-----------|-----------|-----------|------|-------|
| 2025-01-15T10:30:00Z | TEST78787 | input_4_20ma | 1 | AIN0 | Temperature Sensor | true | 1.0 | 1.0 | - | 4.0 | 20.0 | mA | - |
| 2025-01-15T10:30:00Z | TEST78787 | input_4_20ma | 2 | AIN1 | Flow Meter | false | 1.0 | 1.0 | - | 4.0 | 20.0 | mA | - |
| 2025-01-15T10:30:00Z | TEST78787 | input_1_10v | 3 | AIN2 | Pressure Sensor | true | 100.0 | 1.0 | 1000 | 0.0 | 10.0 | V | - |
| 2025-01-15T10:30:00Z | TEST78787 | input_1_10v | 4 | AIN3 | Level Sensor | true | 1.0 | 2.5 | 2000 | 0.0 | 10.0 | V | - |
| 2025-01-15T10:30:00Z | TEST78787 | output_0_10v | 1 | DOUT0 | Valve Control | true | - | - | - | 0.0 | 10.0 | V | 5.5 |
| 2025-01-15T10:30:00Z | TEST78787 | output_0_10v | 2 | DOUT1 | Pump Control | false | - | - | - | 0.0 | 10.0 | V | 0.0 |

### **Key Observations:**

1. **Each channel = One row** in the table
2. **Same timestamp** for all channels saved together (same save operation)
3. **device_id** contains the **Serial Number** (not device ID like "esp32_gw_01")
4. **scan_rate** appears only for `input_1_10v` channels (0-10V inputs)
5. **value** appears only for `output_0_10v` channels
6. **divider/multiplier** are `-` (not applicable) for outputs
7. **All parameters are required** - no null/empty values allowed

---

## Data Saving Process

### Step-by-Step: What Happens When User Clicks "Save Configuration"

#### **Step 1: Validation** ✅
```
User fills form:
├── 4-20mA Inputs: Channel 1 & 2
│   ├── Divider: ✓ (required)
│   ├── Multiplier: ✓ (required)
│   └── Name/Label: ✓ (required, defaults to IO pin if empty)
│
├── 0-10V Inputs: Channel 3 & 4
│   ├── Divider: ✓ (required)
│   ├── Multiplier: ✓ (required)
│   ├── Name/Label: ✓ (required, defaults to IO pin if empty)
│   └── Scan Rate: ✓ (required, minimum 1000 seconds)
│
├── 0-10V Outputs: Channel 1 & 2
│   ├── Value: ✓ (required)
│   └── Name/Label: ✓ (required, defaults to IO pin if empty)
│
└── Analog Scan Rate: ✓ (required, minimum 1000 seconds)
```

**Validation Checks:**
- All fields must be filled (no blanks)
- Scan Rate must be ≥ 1000 seconds
- Name defaults to IO pin if empty
- Serial Number must be selected from dropdown

#### **Step 2: Build Configuration JSON** 📦

The system builds a complete configuration dictionary:

```json
{
  "device_id": "TEST78787",
  "metadata": {
    "device_name": "ESP32-Gateway-01",
    "device_type": "esp32_gateway",
    "created_at": "2025-01-15T10:30:00.000Z",
    "updated_at": "2025-01-15T10:30:00.000Z"
  },
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": true,
        "divider": 1.0,
        "multiplier": 1.0,
        "io_pin": "AIN0",
        "name": "Temperature Sensor",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      },
      {
        "channel": 2,
        "enabled": false,
        "divider": 1.0,
        "multiplier": 1.0,
        "io_pin": "AIN1",
        "name": "AIN1",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": true,
        "divider": 100.0,
        "multiplier": 1.0,
        "io_pin": "AIN2",
        "name": "Pressure Sensor",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 4,
        "enabled": true,
        "divider": 1.0,
        "multiplier": 2.5,
        "io_pin": "AIN3",
        "name": "Level Sensor",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": true,
        "value": 5.5,
        "io_pin": "DOUT0",
        "name": "Valve Control",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 2,
        "enabled": false,
        "value": 0.0,
        "io_pin": "DOUT1",
        "name": "DOUT1",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "scan_rate": 1000
  },
  "digital": {
    "scan_rate": 1000,
    ...
  },
  "mqtt": {...},
  "network": {...}
}
```

#### **Step 3: Save to InfluxDB** 💾

**3a. Save Complete Config (Device_Config measurement)**
```
Point Structure:
├── Measurement: "Device_Config"
├── Tags:
│   ├── device_id: "TEST78787" (Serial Number)
│   ├── device_name: "ESP32-Gateway-01"
│   ├── device_type: "esp32_gateway"
│   └── location: ""
├── Fields:
│   ├── config_json: "{...complete JSON string...}"
│   └── version: "1.0.0"
└── Time: 2025-01-15T10:30:00.000000000Z
```

**3b. Save Individual Channels (Device_Config_Analog measurement)**

For each channel, a separate Point is created:

**Example: 4-20mA Input Channel 1**
```
Point Structure:
├── Measurement: "Device_Config_Analog"
├── Tags:
│   ├── device_id: "TEST78787"
│   ├── channel_type: "input_4_20ma"
│   ├── channel: "1"
│   ├── io_pin: "AIN0"
│   └── name: "Temperature Sensor"
├── Fields:
│   ├── enabled: true
│   ├── divider: 1.0
│   ├── multiplier: 1.0
│   ├── min_value: 4.0
│   ├── max_value: 20.0
│   └── unit: "mA"
└── Time: 2025-01-15T10:30:00.000000000Z
```

**Example: 0-10V Input Channel 3**
```
Point Structure:
├── Measurement: "Device_Config_Analog"
├── Tags:
│   ├── device_id: "TEST78787"
│   ├── channel_type: "input_1_10v"
│   ├── channel: "3"
│   ├── io_pin: "AIN2"
│   └── name: "Pressure Sensor"
├── Fields:
│   ├── enabled: true
│   ├── divider: 100.0
│   ├── multiplier: 1.0
│   ├── scan_rate: 1000
│   ├── min_value: 0.0
│   ├── max_value: 10.0
│   └── unit: "V"
└── Time: 2025-01-15T10:30:00.000000000Z
```

**Example: 0-10V Output Channel 1**
```
Point Structure:
├── Measurement: "Device_Config_Analog"
├── Tags:
│   ├── device_id: "TEST78787"
│   ├── channel_type: "output_0_10v"
│   ├── channel: "1"
│   ├── io_pin: "DOUT0"
│   └── name: "Valve Control"
├── Fields:
│   ├── enabled: true
│   ├── value: 5.5
│   ├── min_value: 0.0
│   ├── max_value: 10.0
│   └── unit: "V"
└── Time: 2025-01-15T10:30:00.000000000Z
```

**Note:** The global `scan_rate` (1000 seconds) is stored in the complete config JSON, but individual 0-10V input channels also have their own `scan_rate` field in the database.

#### **Step 4: Save to Local JSON File** 📁

Also saves to: `data/configs/{SerialNumber}.json`

This provides:
- Backup/offline access
- Version control friendly
- Easy manual editing

---

## Viewing Individual Parameter Values

### **Method 1: InfluxDB Data Explorer (Visual Interface)**

1. **Open InfluxDB Data Explorer**
2. **Select Measurement:** `Device_Config_Analog`
3. **Apply Filters:**
   - `device_id = 'TEST78787'` (Serial Number)
   - `channel_type = 'input_1_10v'` (optional - filter by type)
   - `channel = '3'` (optional - specific channel)

4. **View Results:**
   - All fields and tags are visible in table format
   - Can sort by time, channel, etc.
   - Can export to CSV

**Example Query (Flux):**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> filter(fn: (r) => r.channel_type == "input_1_10v")
  |> filter(fn: (r) => r.channel == "3")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

**SQL Equivalent (InfluxDB Cloud v3):**
```sql
SELECT * FROM "Device_Config_Analog"
WHERE "device_id" = 'TEST78787'
  AND "channel_type" = 'input_1_10v'
  AND "channel" = '3'
ORDER BY time DESC
LIMIT 1;
```

### **Method 2: Python Code (Programmatic Access)**

```python
from app.services.device_config_db import DeviceConfigDBService

# Initialize service
db_service = DeviceConfigDBService()

# Get complete config
config = db_service.get_device_config("TEST78787")

if config:
    # Access analog config
    analog_config = config.get("analog", {})
    
    # Get scan rate
    scan_rate = analog_config.get("scan_rate", 1000)
    print(f"Analog Scan Rate: {scan_rate} seconds")
    
    # Get specific channel
    input_1_10v = analog_config.get("input_1_10v", [])
    for channel in input_1_10v:
        if channel.get("channel") == 3:
            print(f"Channel 3 (0-10V Input):")
            print(f"  Name: {channel.get('name')}")
            print(f"  IO Pin: {channel.get('io_pin')}")
            print(f"  Divider: {channel.get('divider')}")
            print(f"  Multiplier: {channel.get('multiplier')}")
            print(f"  Enabled: {channel.get('enabled')}")
            print(f"  Range: {channel.get('min_value')}-{channel.get('max_value')} {channel.get('unit')}")
```

### **Method 3: Direct InfluxDB Query (Flux)**

```flux
// Get all analog channels for a device
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> group(columns: ["device_id", "channel_type", "channel"])
  |> first()
```

### **Method 4: Query Specific Parameter**

**Get Scan Rate for 0-10V Input Channel 3:**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> filter(fn: (r) => r.channel_type == "input_1_10v")
  |> filter(fn: (r) => r.channel == "3")
  |> filter(fn: (r) => r._field == "scan_rate")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

**Get Divider for 4-20mA Channel 1:**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> filter(fn: (r) => r.channel_type == "input_4_20ma")
  |> filter(fn: (r) => r.channel == "1")
  |> filter(fn: (r) => r._field == "divider")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

---

## MQTT Transmission to Hardware

### **Step 1: MQTT Topic Structure**

When configuration is saved, it can be published to MQTT using:

**Topic Format:**
```
iotnarad/devices/{SerialNumber}/config
```

**Example:**
```
iotnarad/devices/TEST78787/config
```

### **Step 2: MQTT Message Payload**

The complete configuration JSON is published as the message payload:

```json
{
  "device_id": "TEST78787",
  "metadata": {
    "device_name": "ESP32-Gateway-01",
    "device_type": "esp32_gateway",
    "created_at": "2025-01-15T10:30:00.000Z",
    "updated_at": "2025-01-15T10:30:00.000Z"
  },
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": true,
        "divider": 1.0,
        "multiplier": 1.0,
        "io_pin": "AIN0",
        "name": "Temperature Sensor",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": true,
        "divider": 100.0,
        "multiplier": 1.0,
        "io_pin": "AIN2",
        "name": "Pressure Sensor",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": true,
        "value": 5.5,
        "io_pin": "DOUT0",
        "name": "Valve Control",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "scan_rate": 1000
  },
  "digital": {
    "scan_rate": 1000,
    ...
  },
  "mqtt": {...},
  "network": {...}
}
```

### **Step 3: MQTT Publishing Settings**

- **QoS Level:** 1 (At least once delivery - ensures message is received)
- **Retain Flag:** `true` (Broker keeps the message for new subscribers)
- **Format:** JSON string

### **Step 4: Hardware Subscription**

Hardware device subscribes to:
```
iotnarad/devices/{SerialNumber}/config
```

Or uses wildcard:
```
iotnarad/devices/+/config
```

### **Step 5: Hardware Processing**

When hardware receives the MQTT message:

1. **Parse JSON** payload
2. **Extract analog section:**
   ```json
   {
     "input_4_20ma": [...],
     "input_1_10v": [...],
     "output_0_10v": [...],
     "scan_rate": 1000
   }
   ```

3. **Apply configuration:**
   - Set up ADC channels with divider/multiplier
   - Configure scan intervals
   - Set output values
   - Enable/disable channels

4. **Acknowledge receipt** (optional):
   - Publish to: `iotnarad/devices/{SerialNumber}/config/ack`
   - Payload: `{"status": "received", "timestamp": "..."}`

### **Step 6: Current Implementation Status**

**Currently in code:**
- ✅ Configuration is saved to InfluxDB
- ✅ Configuration is saved to local JSON file
- ⚠️ **MQTT publishing is NOT automatically triggered** after save

**To enable MQTT publishing, add this after saving:**
```python
# After successful save
if success:
    # Publish to MQTT
    from app.services.mqtt_client import MQTTClientService
    mqtt_service = MQTTClientService()
    mqtt_service.publish_config(serial_number, complete_config)
```

---

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                              │
│  User fills Analog Configuration form and clicks "Save"         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDATION                                    │
│  ✓ All parameters filled                                         │
│  ✓ Scan Rate ≥ 1000 seconds                                      │
│  ✓ Name defaults to IO pin if empty                              │
│  ✓ Serial Number selected                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              BUILD CONFIGURATION JSON                            │
│  ConfigJSONBuilder.build_analog_config()                         │
│  ├── input_4_20ma: [channel1, channel2]                         │
│  ├── input_1_10v: [channel3, channel4]                           │
│  ├── output_0_10v: [channel1, channel2]                          │
│  └── scan_rate: 1000                                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              DUAL STORAGE                                        │
│                                                                  │
│  ┌────────────────────────┐    ┌──────────────────────────┐    │
│  │  Local JSON File       │    │  InfluxDB Database       │    │
│  │                        │    │                          │    │
│  │  Path:                 │    │  Measurement:            │    │
│  │  data/configs/         │    │  Device_Config          │    │
│  │  {SerialNumber}.json   │    │  Device_Config_Analog    │    │
│  │                        │    │                          │    │
│  │  Complete JSON         │    │  Complete JSON +         │    │
│  │  (Backup/Offline)      │    │  Individual Channels     │    │
│  └────────────────────────┘    └──────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              MQTT PUBLISHING (Future Implementation)             │
│                                                                  │
│  Topic: iotnarad/devices/{SerialNumber}/config                  │
│  Payload: Complete JSON configuration                           │
│  QoS: 1 (At least once)                                        │
│  Retain: true                                                   │
│                                                                  │
│  Hardware subscribes and receives configuration                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## InfluxDB Data Explorer - Visual Representation

### **Table View: Device_Config_Analog**

When you open this measurement in InfluxDB Data Explorer and filter by `device_id = 'TEST78787'`, you'll see:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Measurement: Device_Config_Analog                                                                                                        │
├──────────────┬──────────────┬─────────────────┬─────────┬────────┬──────────────────┬─────────┬──────────┬───────────┬──────────┬──────┤
│ time         │ device_id   │ channel_type    │ channel │ io_pin │ name             │ enabled │ divider  │ multiplier│ scan_rate│ unit │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼──────────┼──────┤
│ 2025-01-15   │ TEST78787    │ input_4_20ma    │ 1       │ AIN0   │ Temperature      │ true    │ 1.0      │ 1.0       │ -        │ mA   │
│ 10:30:00Z    │              │                 │         │        │ Sensor           │         │          │           │          │      │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼──────────┼──────┤
│ 2025-01-15   │ TEST78787    │ input_4_20ma    │ 2       │ AIN1   │ AIN1             │ false   │ 1.0      │ 1.0       │ -        │ mA   │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │          │      │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼──────────┼──────┤
│ 2025-01-15   │ TEST78787    │ input_1_10v     │ 3       │ AIN2   │ Pressure Sensor  │ true    │ 100.0    │ 1.0       │ 1000     │ V    │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │          │      │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼──────────┼──────┤
│ 2025-01-15   │ TEST78787    │ input_1_10v     │ 4       │ AIN3   │ Level Sensor     │ true    │ 1.0      │ 2.5       │ 2000     │ V    │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │          │      │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼──────────┼──────┤
│ 2025-01-15   │ TEST78787    │ output_0_10v    │ 1       │ DOUT0  │ Valve Control    │ true    │ -        │ -         │ -        │ V    │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │          │      │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼──────────┼──────┤
│ 2025-01-15   │ TEST78787    │ output_0_10v    │ 2       │ DOUT1  │ DOUT1            │ false   │ -        │ -         │ -        │ V    │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │          │      │
└──────────────┴──────────────┴─────────────────┴─────────┴────────┴──────────────────┴─────────┴──────────┴───────────┴──────────┴──────┘

Additional Fields (not shown in compact view):
- min_value: 4.0 (for 4-20mA) or 0.0 (for 0-10V)
- max_value: 20.0 (for 4-20mA) or 10.0 (for 0-10V)
- value: 5.5 (for output_0_10v channel 1), 0.0 (for output_0_10v channel 2)
```

### **Key Points:**

1. **One row per channel** - Each analog channel gets its own database record
2. **Same timestamp** - All channels from the same save operation have identical timestamps
3. **Tags are indexed** - Fast filtering by device_id, channel_type, channel, io_pin, name
4. **Fields contain values** - enabled, divider, multiplier, scan_rate, min_value, max_value, unit, value
5. **scan_rate field** - Only appears for `input_1_10v` channels (0-10V inputs)
6. **value field** - Only appears for `output_0_10v` channels
7. **No nulls** - All required parameters are filled (validation ensures this)

---

## Query Examples for Common Tasks

### **1. Get All Analog Channels for a Device**

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["channel_type", "channel"])
```

### **2. Get Only 0-10V Input Channels**

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> filter(fn: (r) => r.channel_type == "input_1_10v")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```

### **3. Get Scan Rate for All 0-10V Inputs**

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> filter(fn: (r) => r.channel_type == "input_1_10v")
  |> filter(fn: (r) => r._field == "scan_rate")
  |> group(columns: ["channel"])
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

### **4. Get Latest Configuration (Complete JSON)**

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> filter(fn: (r) => r._field == "config_json")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

---

## Summary

### **What Gets Saved:**

1. **Complete Configuration JSON** → `Device_Config` measurement
   - Contains entire config including analog, digital, MQTT, network settings
   - Stored as JSON string in `config_json` field

2. **Individual Channel Records** → `Device_Config_Analog` measurement
   - One row per channel (6 rows total: 2x 4-20mA, 2x 0-10V input, 2x 0-10V output)
   - Each row has tags (device_id, channel_type, channel, io_pin, name)
   - Each row has fields (enabled, divider, multiplier, scan_rate, min_value, max_value, unit, value)

3. **Local JSON File** → `data/configs/{SerialNumber}.json`
   - Complete configuration for backup/offline access

### **What Gets Sent to Hardware (MQTT):**

- **Topic:** `iotnarad/devices/{SerialNumber}/config`
- **Payload:** Complete configuration JSON (same as saved to database)
- **Format:** JSON string
- **QoS:** 1 (at least once delivery)
- **Retain:** true (broker keeps message for new subscribers)

### **How to View Later:**

1. **InfluxDB Data Explorer:** Visual table interface
2. **Python Code:** Use `DeviceConfigDBService.get_device_config()`
3. **Flux Queries:** Direct database queries
4. **Local JSON Files:** Read from `data/configs/` directory

---

## Next Steps (After Technical Team Approval)

1. ✅ Add automatic MQTT publishing after save
2. ✅ Add "Load Configuration" button to populate form from database
3. ✅ Add configuration history/versioning
4. ✅ Add hardware acknowledgment tracking
5. ✅ Add configuration comparison/diff view

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Status:** Ready for Technical Team Review

