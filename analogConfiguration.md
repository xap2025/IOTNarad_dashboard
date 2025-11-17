# Analog Configuration - Complete Process Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [InfluxDB Table Structure](#influxdb-table-structure)
3. [Visual Table View in InfluxDB Data Explorer](#visual-table-view-in-influxdb-data-explorer)
4. [Data Saving Process](#data-saving-process)
5. [Viewing Individual Parameter Values](#viewing-individual-parameter-values)
6. [MQTT Transmission to Hardware](#mqtt-transmission-to-hardware)
7. [Configuration Loading and UI Features](#configuration-loading-and-ui-features)
8. [Complete Data Flow Diagram](#complete-data-flow-diagram)

---

## Overview

### **Individual Configuration Save (Any Tab)**
When a user configures settings in any tab (Analog, Digital, RS485, CAN Bus) and clicks **"Save Configuration"** button:

**STEP 1: Save to Individual Table**
1. **Validates** all required parameters
2. **Saves** only that section to its respective InfluxDB table:
   - Analog → `Device_Config_Analog` measurement
   - Digital → `Device_Config_Digital` measurement
   - RS485 MODBUS → `Device_Config_MODBUS` measurement
   - CAN Bus → `Device_Config_CANBus` measurement

**STEP 2: Rebuild Complete Merged Config**
3. **Retrieves** the latest configurations from ALL other tabs from their respective tables
4. **Builds** ONE complete merged JSON combining:
   - The newly saved section (just saved)
   - Latest Analog config (from `Device_Config_Analog`)
   - Latest Digital config (from `Device_Config_Digital`)
   - Latest RS485 MODBUS config (from `Device_Config_MODBUS`)
   - Latest CAN Bus config (from `Device_Config_CANBus`)

**STEP 3: Save Merged Config to Device_Config**
5. **Saves** the complete merged JSON to `Device_Config` measurement
   - **Important:** `Device_Config` always contains ONE merged JSON per device
   - Each save operation creates a new entry with the latest merged configuration
   - When querying, always retrieve the latest entry (sorted by time, descending)
   - This merged config represents the current state from all 4 tables

**STEP 4: Publish to MQTT**
6. **Publishes** the complete merged JSON to hardware via MQTT (if enabled)
   - Topic: `Dev/Checksum/{device_id}`
   - Hardware subscribes to this topic to receive configuration updates

### **Key Points:**
- Each tab saves **only to its own table** (individual section)
- Each save automatically **rebuilds and updates** the complete merged config in `Device_Config`
- `Device_Config` always contains **ONE merged JSON** representing the latest state from all 4 tables
- The merged config is **automatically published to MQTT** for hardware to receive
- When loading configuration, the UI retrieves from **individual tables** (not `Device_Config`)

---

## InfluxDB Table Structure

### Measurement: `Device_Config_Analog`

**Important:**
- This measurement is created **automatically** when you save the first Analog Configuration
- **Created only once** - all devices share this same measurement
- All devices (identified by `device_id` tag) store their analog configurations in this **single table**
- Example: If you have 5 devices, all 5 devices' analog configs are in the same `Device_Config_Analog` measurement

This measurement stores individual analog channel configurations. Each row represents one channel configuration for a specific device.

#### **Tags** (Indexed - Used for Filtering)
- `device_id` - **Serial Number (Sr_No)** from Device_info measurement
- `channel_type` - Type of channel: `input_4_20ma`, `input_1_10v`, `output_0_10v`
- `channel` - Channel number (1, 2, 3, 4)
- `io_pin` - Physical IO pin name (AIN0, AIN1, AIN2, AIN3, DOUT0, DOUT1)
- `name` - Channel name/label (e.g., "Temperature Sensor", "Pressure", "Valve Control")

#### **Fields** (Actual Data Values)
- `enabled` - Boolean: Channel enabled/disabled
- `divider` - Float: Division factor for scaling (for input channels only)
- `multiplier` - Float: Multiplication factor for scaling (for input channels only)
- `value` - Float: Output value (only for 0-10V output channels)
- `scan_rate` - Integer: Scan rate in seconds (minimum 1000) - **Present in ALL channel rows with the same value**

#### **Scan Rate Field**
- The `scan_rate` field is stored in **every channel row** (input_4_20ma, input_1_10v, output_0_10v)
- All channels share the **same scan_rate value** (e.g., 1000 seconds)
- This value defines how often ALL analog channels collect data
- There is **NO separate row** for scan_rate - it's a field in each channel row

#### **Timestamp**
- `time` - When the configuration was saved (nanosecond precision)

---

## Visual Table View in InfluxDB Data Explorer

When you open `Device_Config_Analog` measurement in InfluxDB Data Explorer, you'll see a table like this:

### **Example: Device with Serial Number "TEST78787"**

| time | device_id | channel_type | channel | io_pin | name | enabled | divider | multiplier | scan_rate | value |
|------|-----------|--------------|---------|--------|------|---------|---------|------------|-----------|-------|
| 2025-01-15T10:30:00Z | TEST78787 | input_4_20ma | 1 | AIN0 | Temperature Sensor | true | 1.0 | 1.0 | 1000 | - |
| 2025-01-15T10:30:00Z | TEST78787 | input_4_20ma | 2 | AIN1 | Flow Meter | false | 1.0 | 1.0 | 1000 | - |
| 2025-01-15T10:30:00Z | TEST78787 | input_1_10v | 3 | AIN2 | Pressure Sensor | true | 100.0 | 1.0 | 1000 | - |
| 2025-01-15T10:30:00Z | TEST78787 | input_1_10v | 4 | AIN3 | Level Sensor | true | 1.0 | 2.5 | 1000 | - |
| 2025-01-15T10:30:00Z | TEST78787 | output_0_10v | 1 | DOUT0 | Valve Control | true | - | - | 1000 | 5.5 |
| 2025-01-15T10:30:00Z | TEST78787 | output_0_10v | 2 | DOUT1 | Pump Control | false | - | - | 1000 | 0.0 |

**Note:** 
- The `scan_rate` field is present in **ALL channel rows** with the **same value** (e.g., 1000 seconds)
- All channels (input_4_20ma, input_1_10v, output_0_10v) share the same scan_rate value
- This value defines how often ALL analog channels collect data for that device
- There is **NO separate row** for scan_rate - it's stored as a field in each channel row

### **Key Observations:**

1. **Each channel = One row** - Each analog channel gets its own row (6 channels total: 2x 4-20mA, 2x 0-10V input, 2x 0-10V output)
2. **Same timestamp** - All channel rows saved together with the same timestamp
3. **device_id** contains the **Serial Number** (not device ID like "esp32_gw_01")
4. **scan_rate field** - Present in **ALL channel rows** with the **same value** (e.g., 1000 seconds)
5. **value field** - Only appears for `output_0_10v` channels
6. **divider/multiplier** - Only for input channels, not for outputs
7. **All parameters are required** - no null/empty values allowed
8. **Scan Rate applies to all** - The scan_rate value (same in all rows) defines how often ALL analog channels collect data
9. **No separate scan_rate row** - scan_rate is stored as a field in each channel row, not as a separate record

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
│   └── Name/Label: ✓ (required, defaults to IO pin if empty)
│
├── 0-10V Outputs: Channel 1 & 2
│   ├── Value: ✓ (required)
│   └── Name/Label: ✓ (required, defaults to IO pin if empty)
│
└── Analog Scan Rate: ✓ (required, minimum 1000 seconds)
    └── Global parameter for ALL analog channels (4-20mA inputs, 0-10V inputs, 0-10V outputs)
```

**Validation Checks:**
- All fields must be filled (no blanks)
- Scan Rate must be ≥ 1000 seconds
- Name defaults to IO pin if empty
- Serial Number must be selected from dropdown

#### **Step 2: Build Configuration JSON** 📦

The system builds a complete configuration dictionary:

**Complete JSON Structure (Device_Config - For MQTT Publishing):**

```json
{
  "device_id": "TEST78787",
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": true,
        "divider": 1.0,
        "multiplier": 1.0,
        "io_pin": "AIN0",
        "name": "Temperature Sensor"
      },
      {
        "channel": 2,
        "enabled": false,
        "divider": 1.0,
        "multiplier": 1.0,
        "io_pin": "AIN1",
        "name": "AIN1"
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": true,
        "divider": 100.0,
        "multiplier": 1.0,
        "io_pin": "AIN2",
        "name": "Pressure Sensor"
      },
      {
        "channel": 4,
        "enabled": true,
        "divider": 1.0,
        "multiplier": 2.5,
        "io_pin": "AIN3",
        "name": "Level Sensor"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": true,
        "value": 5.5,
        "io_pin": "DOUT0",
        "name": "Valve Control"
      },
      {
        "channel": 2,
        "enabled": false,
        "value": 0.0,
        "io_pin": "DOUT1",
        "name": "DOUT1"
      }
    ],
    "scan_rate": 1000
  },
  "digital": {
    "scan_rate": 2000,
    "npn_input": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "INP1H",
        "name": "Door Sensor",
        "pullup": true,
        "debounce_ms": 50
      }
    ],
    "npn_output": [
      {
        "channel": 1,
        "enabled": false,
        "io_pin": "OUTL1",
        "name": "LED Control",
        "initial_state": false
      }
    ],
    "pnp_input": [],
    "pnp_output": [],
    "relay": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "RLY1",
        "name": "Main Relay",
        "initial_state": false
      }
    ]
  },
  "rs485_modbus": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": 9600,
      "data_bits": 8,
      "parity": "None",
      "stop_bits": 1
    },
    "protocol_settings": {
      "mode": "RTU",
      "role": "Master"
    },
    "polling_interval_ms": 1000,
    "slave_devices": [
      {
        "index": 0,
        "slave_id": "1",
        "function_code": "0x03",
        "register_address": "0",
        "data_type": "int16",
        "endianness": "Big Endian",
        "variable_name": "Temperature",
        "register_count": 1
      }
    ]
  },
  "can_bus": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": 500,
      "identifier_length": "11-bit",
      "can_mode": "Normal",
      "filter_mode": "None",
      "filter_id": "0x000",
      "filter_mask": "0x000"
    },
    "can_messages": [
      {
        "index": 0,
        "can_id": "0x123",
        "direction": "TX",
        "period_ms": 100,
        "variable_name": "Sensor Data",
        "data_length": 8
      }
    ],
    "data_mapping": [
      {
        "index": 0,
        "can_id": "0x123",
        "byte_position": "Byte 0",
        "data_length": "2 Bytes",
        "data_type": "int16",
        "endianness": "Big Endian",
        "variable_name": "Engine RPM",
        "scale_factor": 1.0,
        "offset": 0.0
      }
    ]
  }
}
```

**Key Points:**
- This is the **complete JSON** saved in `Device_Config` measurement
- This is the JSON that will be **published to hardware via MQTT**
- Contains only required sections: Analog, Digital, RS485 MODBUS, CAN Bus
- **MQTT and Network sections removed** - not required for hardware configuration
- Top-level fields: `device_id`, `device_name`, `created_at`, `updated_at`
- Hardware receives this JSON to configure Analog, Digital, RS485, and CAN Bus sections

#### **Step 3: Save to InfluxDB** 💾

**Understanding InfluxDB Measurements:**
- **Measurements are created automatically** when the first Point is written
- All devices share the **same measurements** (Device_Config, Device_Config_Analog)
- Devices are distinguished by the `device_id` tag (Serial Number)
- **No pre-creation needed** - InfluxDB creates measurements on first write

**3a. Save Complete Config (Device_Config measurement) - OPTIONAL**

**When is Device_Config created?**
- Created automatically when you save the first complete device configuration
- A new Point is added to this measurement when a **complete configuration** is saved
- All devices store their complete config in the same `Device_Config` measurement

**When is Device_Config actually used?**
- **✅ Correct Implementation:** `Device_Config` is saved **AUTOMATICALLY** when you click **"Save Configuration"** button in ANY tab (Analog, Digital, RS485, CAN Bus)
- Each individual "Save Configuration" button:
  - **STEP 1:** Saves only that section to its respective table (e.g., Analog → `Device_Config_Analog`)
  - **STEP 2:** Retrieves latest configurations from ALL other tabs from their respective tables
  - **STEP 3:** Builds ONE complete merged JSON combining:
    - The newly saved section (just saved)
    - Latest Analog config (from `Device_Config_Analog`)
    - Latest Digital config (from `Device_Config_Digital`)
    - Latest RS485 MODBUS config (from `Device_Config_MODBUS`)
    - Latest CAN Bus config (from `Device_Config_CANBus`)
  - **STEP 4:** Saves the complete merged JSON to `Device_Config` measurement
  - **STEP 5:** Publishes the complete merged JSON to hardware via MQTT (if enabled)

**Why do we need Device_Config table?**
The `Device_Config` table stores the **complete merged configuration JSON** (all sections together). It is automatically updated whenever ANY tab's "Save Configuration" button is clicked. It is useful for:
- **MQTT publishing:** Hardware needs complete JSON to configure all sections at once
- **Single query access:** Get entire device config in one query (always retrieve latest entry)
- **Configuration snapshots:** Save complete merged state at a point in time
- **Backup/Restore:** Restore entire device configuration from one place

**Important Notes:**
- `Device_Config` always contains **ONE merged JSON** per device (latest state from all 4 tables)
- Each save operation creates a new entry with the latest merged configuration
- When querying, always retrieve the **latest entry** (sorted by time, descending)
- The merged config represents the **current state** from all 4 individual tables
- When loading configuration in UI, retrieve from **individual tables** (not `Device_Config`)

**Complete JSON Structure:**
The `Device_Config` stores the complete JSON with required sections only:
- ✅ `device_id` - Serial Number (Sr_No)
- ✅ `analog` - Analog configuration (4-20mA, 0-10V inputs/outputs, scan_rate)
- ✅ `digital` - Digital configuration (NPN/PNP inputs/outputs, relays, scan_rate)
- ✅ `rs485_modbus` - RS485 MODBUS configuration (communication settings, slave devices)
- ✅ `can_bus` - CAN Bus configuration (communication settings, messages, data mapping)
- ❌ `device_name` - **NOT INCLUDED** (not required)
- ❌ `created_at` - **NOT INCLUDED** (not required)
- ❌ `updated_at` - **NOT INCLUDED** (not required)
- ❌ `mqtt` - **NOT INCLUDED** (not required for hardware configuration)
- ❌ `network` - **NOT INCLUDED** (not required for hardware configuration)

**Note:** Only `device_id` and configuration sections (Analog, Digital, RS485, CAN Bus) are included. No metadata fields, MQTT, or Network settings.

**Point Structure:**
```
Point Structure:
├── Measurement: "Device_Config"  (Shared by ALL devices)
├── Tags:
│   └── device_id: "TEST78787" (Serial Number - distinguishes devices)
├── Fields:
│   └── config_json: "{...complete JSON string with all sections...}"
└── Time: 2025-01-15T10:30:00.000000000Z (timestamp of this save operation)
```

**Note:** Tags only include `device_id`. The JSON contains only `device_id` and configuration sections (no metadata fields).

### **Table View: Device_Config**

When you open `Device_Config` measurement in InfluxDB Data Explorer, you'll see a table like this:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Measurement: Device_Config                                                                                               │
├──────────────┬──────────────┬───────────────────────────────────────────────────────────────────────────────────────────┤
│ time         │ device_id   │ config_json                                                                                │
├──────────────┼──────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
│ 2025-01-15   │ TEST78787    │ {"device_id":"TEST78787","analog":{"input_4_20ma":[...],"input_1_10v":[...],            │
│ 10:30:00Z    │              │ "output_0_10v":[...],"scan_rate":1000},"digital":{...},"rs485_modbus":{...},            │
│              │              │ "can_bus":{...}}                                                                           │
├──────────────┼──────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
│ 2025-01-15   │ TEST78788    │ {"device_id":"TEST78788","analog":{...},"digital":{...},"rs485_modbus":{...},          │
│ 10:30:00Z    │              │ "can_bus":{...}}                                                                         │
├──────────────┼──────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
│ 2025-01-15   │ TEST78789    │ {"device_id":"TEST78789","analog":{...},"digital":{...},"rs485_modbus":{...},            │
│ 10:30:00Z    │              │ "can_bus":{...}}                                                                         │
└──────────────┴──────────────┴───────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key Points:**
1. **One row per device** - Each device has one row (or multiple rows if configuration is saved multiple times)
2. **device_id tag** - Identifies which device this configuration belongs to
3. **config_json field** - Contains the complete JSON string with all sections (analog, digital, rs485_modbus, can_bus)
4. **Same measurement for all devices** - All devices store their complete config in the same `Device_Config` measurement
5. **To view JSON:** Click on `config_json` field value to see the formatted JSON, or query and parse it programmatically

**Important Notes:**
- **Individual "Save Configuration" button** (inside Analog tab):
  - Creates **6 new Points** in `Device_Config_Analog` only (one per channel)
  - Does NOT save to `Device_Config` measurement
- **"💾 Save All Configuration" button** (at top, replaces Device Status):
  - Creates **1 new Point** in `Device_Config` (complete config JSON with all sections)
  - Also saves to individual tables (Device_Config_Analog, Device_Config_Digital, etc.)
  - Used for MQTT publishing to hardware
- To get the latest analog config, query `Device_Config_Analog` by `device_id` and sort by `time DESC LIMIT 6`
- To get the latest complete config, query `Device_Config` by `device_id` and sort by `time DESC LIMIT 1`
- All devices share the same measurements, distinguished by `device_id` tag

**3b. Save Individual Channels (Device_Config_Analog measurement)**

**When is Device_Config_Analog created?**
- Created automatically when you save the first Analog Configuration
- **Created only once** - all devices share this same measurement
- A new set of Points (one per channel) is added **every time** you click "Save Configuration"
- All devices store their analog config in the same `Device_Config_Analog` measurement

**How are multiple devices handled?**
- All 5 devices (or any number) use the **same measurement**: `Device_Config_Analog`
- Each device is identified by the `device_id` tag (Serial Number)
- When you query: `device_id = 'TEST78787'`, you get only that device's channels
- When you query: `channel_type = 'input_4_20ma'`, you get that channel type from ALL devices

**Example with Multiple Devices:**
```
Device_Config_Analog measurement (shared by all devices):
├── device_id: "TEST78787" → 6 channel rows
├── device_id: "TEST78788" → 6 channel rows  
├── device_id: "TEST78789" → 6 channel rows
├── device_id: "TEST78790" → 6 channel rows
└── device_id: "TEST78791" → 6 channel rows

Total: 30 rows (5 devices × 6 channels each)
```

Each channel is saved with the scan_rate field included:

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
│   └── scan_rate: 1000
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
│   └── scan_rate: 1000
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
│   └── scan_rate: 1000
└── Time: 2025-01-15T10:30:00.000000000Z
```

**Note:** The `scan_rate` field is stored in **every channel row** with the **same value** (e.g., 1000 seconds). All channels (input_4_20ma, input_1_10v, output_0_10v) share this scan_rate value, which defines how often ALL analog channels collect data for that device. There is **NO separate row** for scan_rate.

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

**Option A: Get from Complete Config JSON**
```python
from app.services.device_config_db import DeviceConfigDBService

# Initialize service
db_service = DeviceConfigDBService()

# Get complete config
config = db_service.get_device_config("TEST78787")

if config:
    # Access analog config
    analog_config = config.get("analog", {})
    
    # Get scan rate from complete config
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
            print(f"  Scan Rate: {scan_rate} seconds (applies to all analog channels)")
```

**Option B: Query Device_Config_Analog Directly**
```python
from app.services.influx import InfluxDBService

# Initialize InfluxDB service
influx_service = InfluxDBService()

# Query scan_rate from any channel row (all have the same value)
query = f'''
    from(bucket: "{influx_service.bucket}")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
    |> filter(fn: (r) => r.device_id == "TEST78787")
    |> filter(fn: (r) => r._field == "scan_rate")
    |> sort(columns: ["_time"], desc: true)
    |> limit(n: 1)
'''

result = influx_service.query_api.query(org=influx_service.org, query=query)

# Extract scan_rate (same value from any channel)
for table in result:
    for record in table.records:
        scan_rate = record.get_value()
        print(f"Analog Scan Rate: {scan_rate} seconds (applies to all analog channels)")
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
Dev/Config/{SerialNumber}
```

**Example:**
```
Dev/Config/TEST78787
```

### **Step 2: MQTT Message Payload**

The complete configuration JSON is published as the message payload:

```json
{
  "device_id": "TEST78787",
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": true,
        "divider": 1.0,
        "multiplier": 1.0,
        "io_pin": "AIN0",
        "name": "Temperature Sensor"
      },
      {
        "channel": 2,
        "enabled": false,
        "divider": 1.0,
        "multiplier": 1.0,
        "io_pin": "AIN1",
        "name": "AIN1"
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": true,
        "divider": 100.0,
        "multiplier": 1.0,
        "io_pin": "AIN2",
        "name": "Pressure Sensor"
      },
      {
        "channel": 4,
        "enabled": true,
        "divider": 1.0,
        "multiplier": 2.5,
        "io_pin": "AIN3",
        "name": "Level Sensor"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": true,
        "value": 5.5,
        "io_pin": "DOUT0",
        "name": "Valve Control"
      },
      {
        "channel": 2,
        "enabled": false,
        "value": 0.0,
        "io_pin": "DOUT1",
        "name": "DOUT1"
      }
    ],
    "scan_rate": 1000
  },
  "digital": {
    "scan_rate": 2000,
    "npn_input": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "INP1H",
        "name": "Door Sensor",
        "pullup": true,
        "debounce_ms": 50
      }
    ],
    "npn_output": [],
    "pnp_input": [],
    "pnp_output": [],
    "relay": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "RLY1",
        "name": "Main Relay",
        "initial_state": false
      }
    ]
  },
  "rs485_modbus": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": 9600,
      "data_bits": 8,
      "parity": "None",
      "stop_bits": 1
    },
    "protocol_settings": {
      "mode": "RTU",
      "role": "Master"
    },
    "polling_interval_ms": 1000,
    "slave_devices": [
      {
        "index": 0,
        "slave_id": "1",
        "function_code": "0x03",
        "register_address": "0",
        "data_type": "int16",
        "endianness": "Big Endian",
        "variable_name": "Temperature",
        "register_count": 1
      }
    ]
  },
  "can_bus": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": 500,
      "identifier_length": "11-bit",
      "can_mode": "Normal",
      "filter_mode": "None",
      "filter_id": "0x000",
      "filter_mask": "0x000"
    },
    "can_messages": [
      {
        "index": 0,
        "can_id": "0x123",
        "direction": "TX",
        "period_ms": 100,
        "variable_name": "Sensor Data",
        "data_length": 8
      }
    ],
    "data_mapping": [
      {
        "index": 0,
        "can_id": "0x123",
        "byte_position": "Byte 0",
        "data_length": "2 Bytes",
        "data_type": "int16",
        "endianness": "Big Endian",
        "variable_name": "Engine RPM",
        "scale_factor": 1.0,
        "offset": 0.0
      }
    ]
  }
}
```

**Important Notes:**
- **Only device_id at top level** - No device_name, created_at, updated_at (not required)
- **No MQTT section** - MQTT settings are not included in hardware configuration
- **No Network section** - Network settings are not included in hardware configuration
- Only configuration sections: Analog, Digital, RS485 MODBUS, CAN Bus
- This JSON is published to hardware via MQTT topic: `Dev/Config/{SerialNumber}`

### **Step 3: MQTT Publishing Settings**

- **QoS Level:** 1 (At least once delivery - ensures message is received)
- **Retain Flag:** `true` (Broker keeps the message for new subscribers)
- **Format:** JSON string

### **Step 4: Hardware Subscription**

Hardware device subscribes to:
```
Dev/Config/{SerialNumber}
```

Or uses wildcard:
```
Dev/Config/#
```

### **Step 5: Hardware Processing**

When hardware receives the MQTT message:

1. **Parse JSON** payload
2. **Extract configuration sections:**
   - `analog` section → Configure analog inputs/outputs
   - `digital` section → Configure digital IOs and relays
   - `rs485_modbus` section → Configure RS485 MODBUS communication
   - `can_bus` section → Configure CAN Bus communication

3. **Apply Analog configuration:**
   - Set up ADC channels with divider/multiplier
   - Configure scan intervals using `scan_rate`
   - Set output values for 0-10V outputs
   - Enable/disable channels

4. **Apply Digital configuration:**
   - Configure NPN/PNP inputs/outputs
   - Set up relay states
   - Configure debounce settings

5. **Apply RS485 MODBUS configuration:**
   - Set communication settings (baud rate, parity, etc.)
   - Configure slave devices
   - Set polling interval

6. **Apply CAN Bus configuration:**
   - Set communication settings (baud rate, filter mode, etc.)
   - Configure CAN messages
   - Set up data mappings

7. **Acknowledge receipt** (optional):
   - Publish to: `Dev/ConfigACK/{SerialNumber}`
   - Payload: `{"status": "received", "timestamp": "..."}`

### **Step 6: Current Implementation Status**

**Individual "Save Configuration" (in each tab):**
- ✅ Configuration is saved to individual table (e.g., Analog → `Device_Config_Analog`)
- ✅ Configuration is saved to local JSON file
- ❌ Does NOT save to `Device_Config` measurement
- ❌ Does NOT publish to MQTT

**"💾 Save All Configuration" button:**
- ✅ Gathers configuration from ALL tabs (Analog, Digital, RS485, CAN Bus)
- ✅ Saves complete JSON to `Device_Config` measurement
- ✅ Also saves to individual tables (`Device_Config_Analog`, `Device_Config_Digital`, etc.)
- ✅ Can publish to MQTT for hardware to receive complete configuration

**To enable MQTT publishing when clicking "Save All Configuration":**
```python
# After successful save of all configurations
if success:
    # Get complete config from Device_Config
    from app.services.device_config_db import DeviceConfigDBService
    db_service = DeviceConfigDBService()
    complete_config = db_service.get_device_config(serial_number)
    
    # Publish to MQTT
    from app.services.mqtt_client import MQTTClientService
    mqtt_service = MQTTClientService()
    mqtt_service.publish_config(serial_number, complete_config)
```

---

## Configuration Loading and UI Features

### **Auto-Load Saved Configuration**
When a device is selected from the "Select Device" dropdown:

1. **Retrieves** latest saved configuration from individual tables:
   - Analog config from `Device_Config_Analog`
   - Digital config from `Device_Config_Digital`
   - RS485 MODBUS config from `Device_Config_MODBUS`
   - CAN Bus config from `Device_Config_CANBus`

2. **Populates** all UI fields automatically:
   - Analog inputs/outputs with their saved values
   - Digital I/O with their saved states
   - RS485 MODBUS settings with their saved parameters
   - CAN Bus settings with their saved configuration
   - Scan rates and polling intervals

3. **Persists** across page reloads:
   - Configuration is automatically loaded when you return to the page
   - No need to re-enter configuration values
   - Latest saved state is always displayed

**Important Notes:**
- Configuration is loaded from **individual tables** (not `Device_Config`)
- Each tab's data is retrieved from its respective table
- If no saved config exists, defaults are shown
- Configuration is loaded immediately when device is selected

### **UI Improvements**

#### **Save Button Loading Indicators**
- **Loading Spinner:** Shows spinner on Save button while saving
- **Button Disabled:** Save button becomes inactive (disabled) during save process
- **Visual Feedback:** User knows the click was registered and save is in progress
- **Status Message:** Success/error message appears next to Save button immediately after save completes

#### **Device Selector Dropdown**
- **Wider Width:** Dropdown is set to minimum 400px width for better visibility
- **Full Device Name:** Complete Serial Number and Device Name are clearly visible
- **Loading Indicator:** Shows spinner while fetching device list from database
- **Instant Loading:** Device list is cached for 30 seconds for faster subsequent loads

#### **User-Specific Configuration (Future Enhancement)**
- Configuration loading based on logged-in user ID
- User/Device mapping for personalized configurations
- Each user sees their own saved configurations
- Never resets to factory defaults unless manually cleared

---

## Complete Data Flow Diagram

### **Scenario 1: Individual Configuration Save (Analog Tab)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                              │
│  User fills Analog Configuration form and clicks                │
│  "Save Configuration" (inside Analog tab)                       │
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
│              BUILD ANALOG CONFIGURATION                          │
│  ConfigJSONBuilder.build_analog_config()                         │
│  ├── input_4_20ma: [channel1, channel2]                         │
│  ├── input_1_10v: [channel3, channel4]                           │
│  ├── output_0_10v: [channel1, channel2]                          │
│  └── scan_rate: 1000                                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              SAVE TO INFLUXDB (Individual Table Only)            │
│                                                                  │
│  ┌────────────────────────┐    ┌──────────────────────────┐    │
│  │  Local JSON File       │    │  InfluxDB Database       │    │
│  │                        │    │                          │    │
│  │  Path:                 │    │  Measurement:            │    │
│  │  data/configs/         │    │  Device_Config_Analog ✅ │    │
│  │  {SerialNumber}.json   │    │                          │    │
│  │                        │    │  Device_Config ❌        │    │
│  │  Analog Config Only    │    │  (NOT saved)             │    │
│  └────────────────────────┘    └──────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              ❌ NO MQTT PUBLISHING                                │
│  Individual "Save Configuration" does NOT publish to MQTT        │
└─────────────────────────────────────────────────────────────────┘
```

### **Scenario 2: Save All Configuration (Global Button)**

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                              │
│  User clicks "💾 Save All Configuration"                        │
│  (replaces "Device Status: Online" badge at top)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              GATHER CONFIGURATION FROM ALL TABS                  │
│  ✓ Get analog_config from Analog tab                            │
│  ✓ Get digital_config from Digital tab                          │
│  ✓ Get rs485_modbus_config from RS485 MODBUS tab                │
│  ✓ Get can_bus_config from CAN Bus tab                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              BUILD COMPLETE CONFIGURATION JSON                   │
│  ConfigJSONBuilder.build_complete_config()                       │
│  ├── device_id: "TEST78787"                                     │
│  ├── analog: {...}                                              │
│  ├── digital: {...}                                             │
│  ├── rs485_modbus: {...}                                        │
│  └── can_bus: {...}                                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              SAVE TO INFLUXDB (All Tables + Complete JSON)       │
│                                                                  │
│  ┌────────────────────────┐    ┌──────────────────────────┐    │
│  │  Local JSON File       │    │  InfluxDB Database       │    │
│  │                        │    │                          │    │
│  │  Path:                 │    │  Measurements:           │    │
│  │  data/configs/         │    │  Device_Config_Analog ✅ │    │
│  │  {SerialNumber}.json   │    │  Device_Config_Digital ✅│    │
│  │                        │    │  Device_Config_RS485 ✅  │    │
│  │  Complete JSON         │    │  Device_Config_CANBus ✅ │    │
│  │  (All sections)        │    │  Device_Config ✅        │    │
│  └────────────────────────┘    │  (Complete JSON)         │    │
│                                 └──────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              MQTT PUBLISHING (If Enabled)                        │
│                                                                  │
│  Topic: Dev/Config/{SerialNumber} (e.g., Dev/Config/TEST78787)                          │
│  Payload: Complete JSON configuration                           │
│  QoS: 1 (At least once)                                        │
│  Retain: true                                                   │
│                                                                  │
│  Hardware subscribes to: Dev/Config/# and receives configuration                        │
│  Hardware publishes acknowledgment to: Dev/ConfigACK/{SerialNumber}                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## InfluxDB Data Explorer - Visual Representation

### **Table View: Device_Config_Analog**

When you open this measurement in InfluxDB Data Explorer and filter by `device_id = 'TEST78787'`, you'll see:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Measurement: Device_Config_Analog                                                                                                          │
├──────────────┬──────────────┬─────────────────┬─────────┬────────┬──────────────────┬─────────┬──────────┬───────────┬───────────┬───────┤
│ time         │ device_id   │ channel_type    │ channel │ io_pin │ name             │ enabled │ divider  │ multiplier│ scan_rate │ value │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼───────────┼───────┤
│ 2025-01-15   │ TEST78787    │ input_4_20ma    │ 1       │ AIN0   │ Temperature      │ true    │ 1.0      │ 1.0       │ 1000      │ -     │
│ 10:30:00Z    │              │                 │         │        │ Sensor           │         │          │           │           │       │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼───────────┼───────┤
│ 2025-01-15   │ TEST78787    │ input_4_20ma    │ 2       │ AIN1   │ AIN1             │ false   │ 1.0      │ 1.0       │ 1000      │ -     │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │           │       │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼───────────┼───────┤
│ 2025-01-15   │ TEST78787    │ input_1_10v     │ 3       │ AIN2   │ Pressure Sensor  │ true    │ 100.0    │ 1.0       │ 1000      │ -     │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │           │       │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼───────────┼───────┤
│ 2025-01-15   │ TEST78787    │ input_1_10v     │ 4       │ AIN3   │ Level Sensor     │ true    │ 1.0      │ 2.5       │ 1000      │ -     │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │           │       │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼───────────┼───────┤
│ 2025-01-15   │ TEST78787    │ output_0_10v    │ 1       │ DOUT0  │ Valve Control    │ true    │ -        │ -         │ 1000      │ 5.5   │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │           │       │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────┼───────────┼───────────┼───────┤
│ 2025-01-15   │ TEST78787    │ output_0_10v    │ 2       │ DOUT1  │ DOUT1            │ false   │ -        │ -         │ 1000      │ 0.0   │
│ 10:30:00Z    │              │                 │         │        │                  │         │          │           │           │       │
└──────────────┴──────────────┴─────────────────┴─────────┴────────┴──────────────────┴─────────┴──────────┴───────────┴───────────┴───────┘

**Key Points:**
1. **value column** - Shows output value for `output_0_10v` channels (5.5, 0.0)
2. **value = "-"** for input channels (input_4_20ma, input_1_10v) - not applicable
3. **All channel rows** contain the `scan_rate` field with the **same value** (1000 seconds)
4. **Total: 6 rows per device** - One row for each channel (2x 4-20mA, 2x 0-10V input, 2x 0-10V output)
5. **Same timestamp** for all rows (saved together in the same operation)
6. **scan_rate field** - Present in **every channel row** with the same value - defines how often ALL analog channels collect data
7. **Tags are indexed** - Fast filtering by device_id, channel_type, channel, io_pin, name
8. **Fields contain values** - scan_rate, enabled, divider, multiplier, value (for outputs only)
9. **No nulls** - All required parameters are filled (validation ensures this)
10. **No separate scan_rate row** - scan_rate is a field in each channel row, not a separate record

### **Table View: Device_Config_Digital**

When you open this measurement in InfluxDB Data Explorer and filter by `device_id = 'TEST78787'`, you'll see:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Measurement: Device_Config_Digital                                                                                               │
├──────────────┬──────────────┬─────────────────┬─────────┬────────┬──────────────────┬─────────┬──────────────┬──────────────┬─────────────────┤
│ time         │ device_id   │ channel_type    │ channel │ io_pin │ name             │ enabled │ pullup       │ debounce_ms  │ initial_state   │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────────┼──────────────┼─────────────────┤
│ 2025-01-15   │ TEST78787    │ npn_input       │ 1       │ INP1H  │ Door Sensor      │ true    │ true         │ 50           │ -               │
│ 10:30:00Z    │              │                 │         │        │                  │         │              │              │                 │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────────┼──────────────┼─────────────────┤
│ 2025-01-15   │ TEST78787    │ npn_input       │ 2       │ INP2H  │ INP2H            │ false   │ true         │ 50           │ -               │
│ 10:30:00Z    │              │                 │         │        │                  │         │              │              │                 │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────────┼──────────────┼─────────────────┤
│ 2025-01-15   │ TEST78787    │ npn_output      │ 1       │ OUTL1  │ LED Control      │ true    │ -            │ -            │ false           │
│ 10:30:00Z    │              │                 │         │        │                  │         │              │              │                 │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────────┼──────────────┼─────────────────┤
│ 2025-01-15   │ TEST78787    │ pnp_input       │ 1       │ INP1L  │ Switch Sensor    │ true    │ false        │ 50           │ -               │
│ 10:30:00Z    │              │                 │         │        │                  │         │              │              │                 │
├──────────────┼──────────────┼─────────────────┼─────────┼────────┼──────────────────┼─────────┼──────────────┼──────────────┼─────────────────┤
│ 2025-01-15   │ TEST78787    │ relay           │ 1       │ RLY1   │ Main Relay       │ true    │ -            │ -            │ false           │
│ 10:30:00Z    │              │                 │         │        │                  │         │              │              │                 │
└──────────────┴──────────────┴─────────────────┴─────────┴────────┴──────────────────┴─────────┴──────────────┴──────────────┴─────────────────┘

**Key Points:**
1. **channel_type** - Can be: npn_input, npn_output, pnp_input, pnp_output, relay
2. **pullup field** - Only for inputs (npn_input: true, pnp_input: false, outputs/relays: not applicable = "-")
3. **debounce_ms field** - Only for inputs (default: 50ms, outputs/relays: not applicable = "-")
4. **initial_state field** - Only for outputs and relays (default: false, inputs: not applicable = "-")
5. **Total rows vary** - Depends on number of enabled channels (typically 4 NPN inputs, 4 NPN outputs, 4 PNP inputs, 4 PNP outputs, 4 relays = 20 rows)
6. **Note:** Digital scan_rate is stored at the configuration level, not per channel (can be retrieved from the complete config JSON in Device_Config)

### **Table View: Device_Config_MODBUS**

When you open this measurement in InfluxDB Data Explorer and filter by `device_id = 'TEST78787'`, you'll see:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Measurement: Device_Config_MODBUS                                                                                                       │
├──────────────┬──────────────┬──────────────┬──────────┬───────────┬───────────┬───────────┬───────────┬──────────────┬───────────────────┤
│ time         │ device_id   │ config_type  │ enabled  │ baud_rate │ data_bits │ parity   │ stop_bits │ mode         │ polling_interval  │
├──────────────┼──────────────┼──────────────┼──────────┼───────────┼───────────┼───────────┼───────────┼──────────────┼───────────────────┤
│ 2025-01-15   │ TEST78787    │ settings     │ true     │ 9600      │ 8         │ None     │ 1         │ RTU          │ 1000              │
│ 10:30:00Z    │              │              │          │           │           │          │           │              │                   │
├──────────────┼──────────────┼──────────────┼──────────┼───────────┼───────────┼───────────┼───────────┼──────────────┼───────────────────┤
│ 2025-01-15   │ TEST78787    │ slave_device │ true     │ -         │ -         │ -        │ -         │ Master       │ -                 │
│ 10:30:00Z    │              │              │          │           │           │          │           │              │                   │
└──────────────┴──────────────┴──────────────┴──────────┴───────────┴───────────┴───────────┴───────────┴──────────────┴───────────────────┘

Slave Device Details (config_type = "slave_device"):
┌──────────────┬──────────────┬──────────────┬───────────┬──────────┬────────────┬──────────────┬─────────────────┬─────────────┬───────────────┐
│ time         │ device_id   │ slave_id     │ function_ │ register │ data_type  │ endianness   │ variable_name   │ index       │ register_     │
│              │              │              │ code      │ _address │            │              │                 │             │ count         │
├──────────────┼──────────────┼──────────────┼───────────┼──────────┼────────────┼──────────────┼─────────────────┼─────────────┼───────────────┤
│ 2025-01-15   │ TEST78787    │ 1            │ 0x03      │ 0        │ int16      │ Big Endian   │ Temperature     │ 0           │ 1             │
│ 10:30:00Z    │              │              │           │          │            │              │                 │             │               │
├──────────────┼──────────────┼──────────────┼───────────┼──────────┼────────────┼──────────────┼─────────────────┼─────────────┼───────────────┤
│ 2025-01-15   │ TEST78787    │ 1            │ 0x03      │ 1        │ int16      │ Big Endian   │ Pressure        │ 1           │ 1             │
│ 10:30:00Z    │              │              │           │          │            │              │                 │             │               │
└──────────────┴──────────────┴──────────────┴───────────┴──────────┴────────────┴──────────────┴─────────────────┴─────────────┴───────────────┘

**Key Points:**
1. **Two types of rows**:
   - `config_type = "settings"` - One row with communication and protocol settings
   - `config_type = "slave_device"` - One row per slave device configured
2. **Settings row** - Contains: enabled, baud_rate, data_bits, parity, stop_bits, mode, role, polling_interval_ms
3. **Slave device rows** - Tags: slave_id, function_code, register_address, data_type, endianness, variable_name
4. **Slave device fields** - index, register_count
5. **Total: 1 settings row + N slave device rows** (where N = number of configured slave devices)

### **Table View: Device_Config_CANBus**

When you open this measurement in InfluxDB Data Explorer and filter by `device_id = 'TEST78787'`, you'll see:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Measurement: Device_Config_CANBus (Settings Row)                                                                                 │
├──────────────┬──────────────┬──────────────┬──────────┬───────────┬──────────────────┬───────────┬───────────┬───────────┬───────────┤
│ time         │ device_id   │ config_type  │ enabled  │ baud_rate │ identifier_len   │ can_mode  │ filter_   │ filter_id │ filter_   │
│              │              │              │          │           │                  │           │ mode      │           │ mask      │
├──────────────┼──────────────┼──────────────┼──────────┼───────────┼──────────────────┼───────────┼───────────┼───────────┼───────────┤
│ 2025-01-15   │ TEST78787    │ settings     │ true     │ 500       │ 11-bit           │ Normal    │ None      │ 0x000     │ 0x000     │
│ 10:30:00Z    │              │              │          │           │                  │           │           │           │           │
└──────────────┴──────────────┴──────────────┴──────────┴───────────┴──────────────────┴───────────┴───────────┴───────────┴───────────┘

CAN Messages (config_type = "can_message"):
┌──────────────┬──────────────┬──────────────┬───────────┬───────────┬──────────────┬─────────────┬──────────────┬───────────────┐
│ time         │ device_id   │ can_id       │ direction │ variable_ │ index        │ period_ms   │ data_length  │               │
│              │              │              │           │ name      │              │             │              │               │
├──────────────┼──────────────┼──────────────┼───────────┼───────────┼──────────────┼─────────────┼──────────────┼───────────────┤
│ 2025-01-15   │ TEST78787    │ 0x123        │ TX        │ Engine    │ 0            │ 100         │ 8            │               │
│ 10:30:00Z    │              │              │           │ Temp      │              │             │              │               │
└──────────────┴──────────────┴──────────────┴───────────┴───────────┴──────────────┴─────────────┴──────────────┴───────────────┘

Data Mappings (config_type = "data_mapping"):
┌──────────────┬──────────────┬──────────────┬───────────┬──────────────┬─────────────┬──────────────┬──────────────┬───────────────┬─────────────┐
│ time         │ device_id   │ can_id       │ byte_pos  │ data_type    │ endianness  │ variable_    │ index        │ scale_factor  │ offset      │
│              │              │              │           │              │             │ name         │              │               │             │
├──────────────┼──────────────┼──────────────┼───────────┼──────────────┼─────────────┼──────────────┼──────────────┼───────────────┼─────────────┤
│ 2025-01-15   │ TEST78787    │ 0x123        │ Byte 0    │ int8         │ Big Endian  │ Temperature  │ 0            │ 1.0           │ 0.0         │
│ 10:30:00Z    │              │              │           │              │             │              │              │               │             │
└──────────────┴──────────────┴──────────────┴───────────┴──────────────┴─────────────┴──────────────┴──────────────┴───────────────┴─────────────┘

**Key Points:**
1. **Three types of rows**:
   - `config_type = "settings"` - One row with communication settings
   - `config_type = "can_message"` - One row per CAN message configured
   - `config_type = "data_mapping"` - One row per data mapping configured
2. **Settings row** - Contains: enabled, baud_rate, identifier_length, can_mode, filter_mode, filter_id, filter_mask
3. **CAN message rows** - Tags: can_id, direction, variable_name. Fields: index, period_ms, data_length
4. **Data mapping rows** - Tags: can_id, byte_position, data_type, endianness, variable_name. Fields: index, data_length, scale_factor, offset
5. **Total: 1 settings row + M message rows + N mapping rows** (where M = number of CAN messages, N = number of data mappings)

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

### **3. Get Analog Scan Rate**

**Option A: Query from Device_Config_Analog (Recommended)**
```flux
// Get scan_rate from any channel row (all channels have the same scan_rate value)
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> filter(fn: (r) => r._field == "scan_rate")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

**Option B: Get from Complete Configuration JSON**
```flux
// Get scan_rate from complete configuration JSON
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "TEST78787")
  |> filter(fn: (r) => r._field == "config_json")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
  |> map(fn: (r) => ({
      r with
      config: json.parse(data: bytes(v: r._value))
    }))
  |> map(fn: (r) => ({
      r with
      scan_rate: r.config.analog.scan_rate
    }))
```

**Note:** Scan rate is stored as a field in **all channel rows** (input_4_20ma, input_1_10v, output_0_10v) with the same value. Any channel row can be queried to get the scan_rate since they all share the same value. It defines how often ALL analog channels collect data.

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

**This returns the complete JSON including:**
- `device_id` - Serial Number
- `analog` - Complete analog configuration (scan_rate, input_4_20ma[], input_1_10v[], output_0_10v[])
- `digital` - Complete digital configuration (scan_rate, npn_input[], npn_output[], pnp_input[], pnp_output[], relay[])
- `rs485_modbus` - RS485 MODBUS configuration (if configured)
- `can_bus` - CAN Bus configuration (if configured)

**Note:** Only `device_id` and configuration sections are included. No device_name, created_at, updated_at, MQTT, or Network sections.

---

## Summary

### **What Gets Saved:**

1. **Complete Configuration JSON** → `Device_Config` measurement
   - Contains entire merged config including analog, digital, rs485_modbus, can_bus sections
   - Stored as JSON string in `config_json` field
   - **When saved:** **AUTOMATICALLY** when clicking **"Save Configuration"** button in ANY tab
   - **Save Process:**
     - Individual section saved to its own table (e.g., Analog → `Device_Config_Analog`)
     - Latest configs retrieved from ALL other tables
     - Complete merged JSON built from all sections
     - Merged JSON saved to `Device_Config` measurement
     - Complete merged JSON published to hardware via MQTT (if enabled)
   - **Purpose:** Provides complete merged configuration for MQTT publishing
   - **Note:** `Device_Config` always contains ONE merged JSON per device (latest state from all 4 tables)

2. **Analog Configuration** → `Device_Config_Analog` measurement
   - **Measurement Creation:** Created automatically on first save (only once)
   - **Shared by ALL devices:** All devices store their configs in this same measurement
   - **Device Identification:** Each device identified by `device_id` tag (Serial Number)
   - **Channel Rows** (6 rows per device: 2x 4-20mA, 2x 0-10V input, 2x 0-10V output)
   - Each channel row has tags (device_id, channel_type, channel, io_pin, name)
   - Each channel row has fields (enabled, divider, multiplier, value, scan_rate)
   - **Total: 6 rows per device** (one per channel)
   - **Multiple Devices Example:** 5 devices = 30 rows total (5 × 6 channels each)
   - **Note:** `scan_rate` is stored as a field in **every channel row** with the **same value** - it applies to all analog channels

3. **Local JSON File** → `data/configs/{SerialNumber}.json`
   - Complete configuration for backup/offline access

### **What Gets Sent to Hardware (MQTT):**

- **Topic:** `Dev/Checksum/{SerialNumber}` (e.g., `Dev/Checksum/TEST78787`)
- **Payload:** Complete configuration JSON (same as saved to database)
- **Format:** JSON string
- **QoS:** 1 (at least once delivery)
- **Retain:** true (broker keeps message for new subscribers)

**Hardware Acknowledgement:**
- **Subscription Topic:** `Dev/ConfigACK/#` (wildcard to receive acknowledgements from all devices)
- **Acknowledgment Format:** Hardware will publish confirmation on `Dev/ConfigACK/{SerialNumber}` topic
- **Example:** When device `TEST78787` successfully receives configuration, it publishes to `Dev/ConfigACK/TEST78787`

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

