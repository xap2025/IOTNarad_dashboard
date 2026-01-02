# Configuration Data Save Mapping to InfluxDB Database

## Overview

This document explains how configuration data flows from the UI to InfluxDB database when you click the **"Save Configuration"** button in any tab (Analog, Digital, RS485 MODBUS, or CAN Bus).

---

## 🔄 General Save Workflow

When you click **"Save Configuration"** in any tab, the following steps occur:

1. **UI Values Collection**: All form values from the active tab are collected
2. **JSON Building**: Values are converted to JSON using `ConfigJSONBuilder`
3. **Individual Table Save**: The tab-specific section is saved to its dedicated table (e.g., `Device_Config_Analog`)
4. **Complete Config Rebuild**: The system fetches existing configs from other tabs and builds a complete merged configuration
5. **Merged Config Save**: The complete merged JSON is saved to `Device_Config` table
6. **MQTT Publish**: The complete configuration is published to MQTT (optional, non-critical)

---

## 📊 Database Structure Overview

### InfluxDB Measurements (Tables)

Your application uses **5 InfluxDB measurements**:

1. **`Device_Config`** - Stores complete merged JSON configuration (one row per device)
2. **`Device_Config_Analog`** - Stores individual Analog channel configurations
3. **`Device_Config_Digital`** - Stores individual Digital channel configurations
4. **`Device_Config_MODBUS`** - Stores MODBUS settings and slave devices
5. **`Device_Config_CANBus`** - Stores CAN Bus settings, messages, and data mappings

---

## 1️⃣ Analog Tab Configuration Save

### UI → Database Flow

```
UI Form Values
    ↓
ConfigJSONBuilder.build_analog_config()
    ↓
JSON Structure: { "input_4_20ma": [...], "input_1_10v": [...], "output_0_10v": [...], "scan_rate": 1000 }
    ↓
DeviceConfigDBService.save_config_sections_only()
    ↓
Device_Config_Analog Table (one row per channel)
```

### Measurement: `Device_Config_Analog`

#### For 4-20mA Input Channels

**Tags** (Indexed, used for filtering):
- `device_id` - Device Serial Number (e.g., "ESP32_GW_001")
- `channel_type` - Always `"input_4_20ma"`
- `channel` - Channel number (e.g., "1", "2")
- `io_pin` - IO pin identifier (e.g., "AIN0", "AIN1")
- `name` - Channel name from UI (e.g., "Temperature Sensor")

**Fields** (Values stored):
- `enabled` - Boolean (true/false)
- `divider` - Integer (from UI "Divider" field)
- `multiplier` - Integer (from UI "Multiplier" field)
- `scan_rate` - Integer (from UI "Scan Rate" field, same for all channels)

**Example Point:**
```
Measurement: Device_Config_Analog
Tags: device_id="ESP32_GW_001", channel_type="input_4_20ma", channel="1", io_pin="AIN0", name="Temperature"
Fields: enabled=true, divider=100, multiplier=1, scan_rate=2000
Time: 2025-12-06T17:30:00Z
```

#### For 1-10V Input Channels

**Tags**:
- `device_id` - Device Serial Number
- `channel_type` - Always `"input_1_10v"`
- `channel` - Channel number (e.g., "3", "4")
- `io_pin` - IO pin identifier (e.g., "AIN2", "AIN3")
- `name` - Channel name from UI

**Fields**:
- `enabled` - Boolean
- `divider` - Integer
- `multiplier` - Integer
- `scan_rate` - Integer

**Example Point:**
```
Measurement: Device_Config_Analog
Tags: device_id="ESP32_GW_001", channel_type="input_1_10v", channel="3", io_pin="AIN2", name="Flow Meter"
Fields: enabled=true, divider=1000, multiplier=1, scan_rate=2000
Time: 2025-12-06T17:30:00Z
```

#### For 0-10V Output Channels

**Tags**:
- `device_id` - Device Serial Number
- `channel_type` - Always `"output_0_10v"`
- `channel` - Channel number (e.g., "1", "2")
- `io_pin` - IO pin identifier (e.g., "DOUT0", "DOUT1")
- `name` - Channel name from UI

**Fields**:
- `enabled` - Boolean
- `value` - **Integer (stored in millivolts)** - UI shows volts (0.0-10.0), but database stores as integer millivolts (0-10000)
  - Example: UI value `5.5V` → Database stores `5500` (millivolts)
  - Example: UI value `0.0V` → Database stores `0` (millivolts)
  - Example: UI value `10.0V` → Database stores `10000` (millivolts)
- `scan_rate` - Integer

**Example Point:**
```
Measurement: Device_Config_Analog
Tags: device_id="ESP32_GW_001", channel_type="output_0_10v", channel="1", io_pin="DOUT0", name="Valve Control"
Fields: enabled=true, value=5500, scan_rate=2000
Time: 2025-12-06T17:30:00Z
```

**⚠️ Important Note on Output Value Storage:**
- The UI displays values in **Volts** (0.0 to 10.0)
- The database stores values as **Integer millivolts** (0 to 10000)
- Conversion: `database_value = int(round(ui_volts * 1000))`
- When loading: `ui_volts = database_value / 1000.0`

### Complete Config Save: `Device_Config`

After saving individual channels, the complete merged configuration is saved to `Device_Config`:

**Tags**:
- `device_id` - Device Serial Number

**Fields**:
- `config_json` - **Complete JSON string** containing all sections (Analog, Digital, MODBUS, CAN Bus)

**Example Point:**
```
Measurement: Device_Config
Tags: device_id="ESP32_GW_001"
Fields: config_json='{"device_id":"ESP32_GW_001","analog":{...},"digital":{...},"rs485_modbus":{...},"can_bus":{...}}'
Time: 2025-12-06T17:30:00Z
```

---

## 2️⃣ Digital Tab Configuration Save

### UI → Database Flow

```
UI Form Values (NPN Input/Output, PNP Input/Output, Relay)
    ↓
ConfigJSONBuilder.build_digital_config()
    ↓
JSON Structure: { "npn_input": [...], "npn_output": [...], "pnp_input": [...], "pnp_output": [...], "relay": [...] }
    ↓
DeviceConfigDBService.save_config_sections_only()
    ↓
Device_Config_Digital Table (one row per channel)
```

### Measurement: `Device_Config_Digital`

#### For NPN Input Channels

**Tags**:
- `device_id` - Device Serial Number
- `channel_type` - Always `"npn_input"`
- `channel` - Channel number (e.g., "1", "2", "3", "4")
- `io_pin` - IO pin identifier (e.g., "INP1H", "INP2H")
- `name` - Channel name from UI

**Fields**:
- `enabled` - Boolean (from UI checkbox)

**⚠️ Note**: Only UI-visible parameters are saved. `pullup` and `debounce_ms` are NOT saved as they are not present in the UI.

**Example Point:**
```
Measurement: Device_Config_Digital
Tags: device_id="ESP32_GW_001", channel_type="npn_input", channel="1", io_pin="INP1H", name="Sensor1"
Fields: enabled=true
Time: 2025-12-06T17:30:00Z
```

#### For NPN Output Channels

**Tags**:
- `device_id` - Device Serial Number
- `channel_type` - Always `"npn_output"`
- `channel` - Channel number
- `io_pin` - IO pin identifier (e.g., "OUTL1", "OUTL2")
- `name` - Channel name from UI

**Fields**:
- `enabled` - Boolean (from UI checkbox)

**⚠️ Note**: Only UI-visible parameters are saved. `initial_state` is NOT saved as it is not present in the UI.

**Example Point:**
```
Measurement: Device_Config_Digital
Tags: device_id="ESP32_GW_001", channel_type="npn_output", channel="1", io_pin="OUTL1", name="Output1"
Fields: enabled=true
Time: 2025-12-06T17:30:00Z
```

#### For PNP Input Channels

**Tags**:
- `device_id` - Device Serial Number
- `channel_type` - Always `"pnp_input"`
- `channel` - Channel number
- `io_pin` - IO pin identifier (e.g., "INP1L", "INP2L")
- `name` - Channel name from UI

**Fields**:
- `enabled` - Boolean (from UI checkbox)

**⚠️ Note**: Only UI-visible parameters are saved. `pullup` and `debounce_ms` are NOT saved as they are not present in the UI.

**Example Point:**
```
Measurement: Device_Config_Digital
Tags: device_id="ESP32_GW_001", channel_type="pnp_input", channel="1", io_pin="INP1L", name="Sensor2"
Fields: enabled=true
Time: 2025-12-06T17:30:00Z
```

#### For PNP Output Channels

**Tags**:
- `device_id` - Device Serial Number
- `channel_type` - Always `"pnp_output"`
- `channel` - Channel number
- `io_pin` - IO pin identifier (e.g., "OUTH1", "OUTH2")
- `name` - Channel name from UI

**Fields**:
- `enabled` - Boolean (from UI checkbox)

**⚠️ Note**: Only UI-visible parameters are saved. `initial_state` is NOT saved as it is not present in the UI.

**Example Point:**
```
Measurement: Device_Config_Digital
Tags: device_id="ESP32_GW_001", channel_type="pnp_output", channel="1", io_pin="OUTH1", name="Output2"
Fields: enabled=true
Time: 2025-12-06T17:30:00Z
```

#### For Relay Channels

**Tags**:
- `device_id` - Device Serial Number
- `channel_type` - Always `"relay"`
- `channel` - Channel number
- `io_pin` - IO pin identifier (e.g., "RLY1", "RLY2")
- `name` - Channel name from UI

**Fields**:
- `enabled` - Boolean (from UI checkbox)

**⚠️ Note**: Only UI-visible parameters are saved. `initial_state` is NOT saved as it is not present in the UI.

**Example Point:**
```
Measurement: Device_Config_Digital
Tags: device_id="ESP32_GW_001", channel_type="relay", channel="1", io_pin="RLY1", name="Relay1"
Fields: enabled=true
Time: 2025-12-06T17:30:00Z
```

**⚠️ Important**: Digital configuration only saves parameters that are visible in the UI:
- ✅ **Saved**: `enabled`, `channel`, `io_pin`, `name`
- ❌ **NOT Saved**: `pullup`, `debounce_ms`, `initial_state` (not in UI)

---

## 3️⃣ RS485 MODBUS Tab Configuration Save

### UI → Database Flow

```
UI Form Values (Communication Settings, Protocol Settings, Polling Interval, Slave Devices)
    ↓
ConfigJSONBuilder.build_modbus_config()
    ↓
JSON Structure: { "enabled": true, "communication_settings": {...}, "protocol_settings": {...}, "polling_interval_ms": 1000, "slave_devices": [...] }
    ↓
DeviceConfigDBService.save_config_sections_only()
    ↓
Device_Config_MODBUS Table (one row for settings + one row per slave device)
```

### Measurement: `Device_Config_MODBUS`

The MODBUS configuration is saved in **two types of rows**:

#### Type 1: Settings Row (Communication & Protocol Settings)

**Tags**:
- `device_id` - Device Serial Number
- `config_type` - Always `"settings"`

**Fields**:
- `enabled` - Boolean (always true when saved)
- `baud_rate` - Integer (from UI "Baud Rate" dropdown, e.g., 9600, 19200, 38400)
- `data_bits` - Integer (from UI "Data Bits" dropdown, e.g., 8)
- `parity` - String (from UI "Parity" dropdown: "None", "Even", "Odd")
- `stop_bits` - Integer (from UI "Stop Bits" dropdown, e.g., 1, 2)
- `mode` - String (from UI "Mode" dropdown: "RTU", "ASCII", "TCP")
- `role` - String (from UI "Role" dropdown: "Master", "Slave")
- `polling_interval_ms` - Integer (from UI "Polling Interval" field, in milliseconds)

**Example Point:**
```
Measurement: Device_Config_MODBUS
Tags: device_id="ESP32_GW_001", config_type="settings"
Fields: enabled=true, baud_rate=9600, data_bits=8, parity="None", stop_bits=1, mode="RTU", role="Master", polling_interval_ms=1000
Time: 2025-12-06T17:30:00Z
```

#### Type 2: Slave Device Rows (One per slave device)

**Tags**:
- `device_id` - Device Serial Number
- `config_type` - Always `"slave_device"`
- `slave_id` - Slave device ID (from UI "Slave ID" field, e.g., "1", "2")
- `function_code` - Function code (from UI "Function Code" dropdown, e.g., "0x03", "0x04")
- `register_address` - Register address (from UI "Register Address" field, e.g., "0", "100")
- `data_type` - Data type (from UI "Data Type" dropdown, e.g., "int8", "int16", "uint16", "float32")
- `endianness` - Endianness (from UI "Endianness" dropdown, e.g., "Big Endian", "Little Endian")
- `variable_name` - Variable name (from UI "Variable Name" field)

**Fields**:
- `index` - Integer (row index in the table, 0-based)
- `register_count` - Integer (always 1, can be extended in future)

**Example Point:**
```
Measurement: Device_Config_MODBUS
Tags: device_id="ESP32_GW_001", config_type="slave_device", slave_id="1", function_code="0x03", register_address="0", data_type="int16", endianness="Big Endian", variable_name="Temperature"
Fields: index=0, register_count=1
Time: 2025-12-06T17:30:00Z
```

**Example with Multiple Slave Devices:**
```
Row 1:
Tags: device_id="ESP32_GW_001", config_type="slave_device", slave_id="1", function_code="0x03", register_address="0", data_type="int16", endianness="Big Endian", variable_name="Temperature"
Fields: index=0, register_count=1

Row 2:
Tags: device_id="ESP32_GW_001", config_type="slave_device", slave_id="1", function_code="0x03", register_address="1", data_type="int16", endianness="Big Endian", variable_name="Pressure"
Fields: index=1, register_count=1
```

---

## 4️⃣ CAN Bus Tab Configuration Save

### UI → Database Flow

```
UI Form Values (Communication Settings, CAN Messages, Data Mappings)
    ↓
ConfigJSONBuilder.build_can_bus_config()
    ↓
JSON Structure: { "enabled": true, "communication_settings": {...}, "can_messages": [...], "data_mapping": [...] }
    ↓
DeviceConfigDBService.save_config_sections_only()
    ↓
Device_Config_CANBus Table (one row for settings + one row per CAN message + one row per data mapping)
```

### Measurement: `Device_Config_CANBus`

The CAN Bus configuration is saved in **three types of rows**:

#### Type 1: Settings Row (Communication Settings)

**Tags**:
- `device_id` - Device Serial Number
- `config_type` - Always `"settings"`

**Fields**:
- `enabled` - Boolean (always true when saved)
- `baud_rate` - Integer (from UI "Baud Rate" dropdown, e.g., 125, 250, 500, 1000)
- `identifier_length` - String (from UI "Identifier Length" dropdown: "11-bit", "29-bit")
- `can_mode` - String (from UI "CAN Mode" dropdown: "Normal", "Listen", "Loopback")
- `filter_mode` - String (from UI "Filter Mode" dropdown: "None", "Accept", "Reject")
- `filter_id` - String (from UI "Filter ID" field, hex format, e.g., "0x123")
- `filter_mask` - String (from UI "Filter Mask" field, hex format, e.g., "0x7FF")

**Example Point:**
```
Measurement: Device_Config_CANBus
Tags: device_id="ESP32_GW_001", config_type="settings"
Fields: enabled=true, baud_rate=500, identifier_length="11-bit", can_mode="Normal", filter_mode="None", filter_id="0x123", filter_mask="0x7FF"
Time: 2025-12-06T17:30:00Z
```

#### Type 2: CAN Message Rows (One per CAN message)

**Tags**:
- `device_id` - Device Serial Number
- `config_type` - Always `"can_message"`
- `can_id` - CAN ID (from UI "CAN ID" field, hex format, e.g., "0x123")
- `direction` - Direction (from UI "Direction" dropdown: "TX", "RX")
- `variable_name` - Variable name (from UI "Variable Name" field)

**Fields**:
- `index` - Integer (row index in the table, 0-based)
- `period_ms` - Integer (from UI "Period" field, in milliseconds)
- `data_length` - Integer (always 8 bytes, can be extended in future)

**Example Point:**
```
Measurement: Device_Config_CANBus
Tags: device_id="ESP32_GW_001", config_type="can_message", can_id="0x123", direction="TX", variable_name="Temperature Message"
Fields: index=0, period_ms=100, data_length=8
Time: 2025-12-06T17:30:00Z
```

#### Type 3: Data Mapping Rows (One per data mapping)

**Tags**:
- `device_id` - Device Serial Number
- `config_type` - Always `"data_mapping"`
- `can_id` - CAN ID (from UI "CAN ID" field, hex format)
- `byte_position` - Byte position (from UI "Byte Position" dropdown, e.g., "Byte 0", "Byte 1")
- `data_type` - Data type (from UI "Data Type" dropdown, e.g., "int8", "int16", "uint16", "float32")
- `endianness` - Endianness (from UI "Endianness" dropdown, e.g., "Big Endian", "Little Endian")
- `variable_name` - Variable name (from UI "Variable Name" field)

**Fields**:
- `index` - Integer (row index in the table, 0-based)
- `data_length` - String (from UI "Data Length" dropdown, e.g., "1 Byte", "2 Bytes", "4 Bytes")
- `scale_factor` - Float (from UI "Scale Factor" field, e.g., 1.0, 0.1, 10.0)
- `offset` - Float (from UI "Offset" field, e.g., 0.0, -273.15)

**Example Point:**
```
Measurement: Device_Config_CANBus
Tags: device_id="ESP32_GW_001", config_type="data_mapping", can_id="0x123", byte_position="Byte 0", data_type="int16", endianness="Big Endian", variable_name="Temperature"
Fields: index=0, data_length="2 Bytes", scale_factor=0.1, offset=0.0
Time: 2025-12-06T17:30:00Z
```

---

## 🔍 Complete Data Flow Summary

### Step-by-Step Process for Each Tab

#### 1. User Clicks "Save Configuration"

#### 2. UI Values Collection
- All form inputs are collected via Dash `State` parameters
- Values are passed to the save callback function

#### 3. JSON Building
- `ConfigJSONBuilder.build_*_config()` method is called
- UI values are converted to structured JSON dictionary

#### 4. Individual Section Save
- `DeviceConfigDBService.save_config_sections_only()` is called
- Only the active tab's section is saved to its dedicated table:
  - Analog → `Device_Config_Analog`
  - Digital → `Device_Config_Digital`
  - MODBUS → `Device_Config_MODBUS`
  - CAN Bus → `Device_Config_CANBus`

#### 5. Complete Config Rebuild
- System fetches existing configs from other tabs:
  - `db_service.get_analog_config(device_id)`
  - `db_service.get_digital_config(device_id)`
  - `db_service.get_modbus_config(device_id)`
  - `db_service.get_can_bus_config(device_id)`
- Builds a complete merged configuration dictionary

#### 6. Merged Config Save
- `DeviceConfigDBService.save_device_config()` is called
- Complete merged JSON is saved to `Device_Config` table
- This ensures `Device_Config` always contains the latest complete configuration

#### 7. MQTT Publish (Optional)
- Complete configuration is published to MQTT broker
- This step is non-critical (errors are logged but don't fail the save)

#### 8. Local JSON Backup (Optional)
- Configuration is also saved to local JSON file in `/app/data/configs/`
- This provides a backup in case of database issues

---

## 📋 Tags vs Fields - Key Differences

### Tags (Indexed, Used for Filtering)
- **Purpose**: Used for filtering and grouping queries
- **Characteristics**:
  - Indexed by InfluxDB (faster queries)
  - String values only
  - Limited cardinality (don't use unique values like timestamps)
  - Used in `WHERE` clauses in Flux queries

**Common Tags:**
- `device_id` - Device identifier
- `channel_type` - Type of channel (e.g., "input_4_20ma", "npn_input")
- `channel` - Channel number
- `io_pin` - IO pin identifier
- `name` - Channel/variable name
- `config_type` - Configuration type (e.g., "settings", "slave_device")

### Fields (Values, Used for Aggregation)
- **Purpose**: Store actual measurement values
- **Characteristics**:
  - Not indexed (slower queries, but can store any data type)
  - Can be integers, floats, booleans, or strings
  - Used in aggregation functions (SUM, MEAN, etc.)

**Common Fields:**
- `enabled` - Boolean (true/false)
- `divider`, `multiplier` - Integer values
- `value` - Integer or float (e.g., output voltage in millivolts)
- `scan_rate` - Integer (milliseconds)
- `baud_rate`, `data_bits`, `stop_bits` - Integer values
- `polling_interval_ms` - Integer (milliseconds)
- `index` - Integer (row index)

---

## 🎯 Query Examples

### Query Analog Configuration for a Device

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "ESP32_GW_001")
  |> filter(fn: (r) => r.channel_type == "input_4_20ma")
  |> pivot(rowKey: ["_time", "channel"], columnKey: ["_field"], valueColumn: "_value")
```

### Query MODBUS Settings for a Device

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
  |> filter(fn: (r) => r.device_id == "ESP32_GW_001")
  |> filter(fn: (r) => r.config_type == "settings")
  |> last()
```

### Query All Slave Devices for a Device

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
  |> filter(fn: (r) => r.device_id == "ESP32_GW_001")
  |> filter(fn: (r) => r.config_type == "slave_device")
  |> sort(columns: ["index"])
```

### Query Complete Merged Configuration

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "ESP32_GW_001")
  |> last()
  |> map(fn: (r) => ({ r with config_json: json.parse(data: r.config_json) }))
```

---

## ⚠️ Important Notes

1. **Timestamp**: All rows are saved with the current UTC timestamp (`datetime.utcnow()`)

2. **Value Conversion**: 
   - Analog output values are converted from Volts (UI) to millivolts (database)
   - When loading, millivolts are converted back to Volts for UI display

3. **Complete Config**: The `Device_Config` table always contains the latest merged configuration from all tabs

4. **Individual Tables**: Each tab's data is saved to its dedicated table for efficient querying

5. **No Duplicates**: Each save operation creates new rows with new timestamps. The latest rows are retrieved using `sort(desc: true)` and `limit(n: 1)` in queries

6. **Error Handling**: If saving to individual table fails, the entire save operation fails. If saving to `Device_Config` fails, it's logged but doesn't fail the operation (to preserve individual table data)

---

## 📝 Summary Table

| Tab | Measurement | Row Type | Key Tags | Key Fields |
|-----|------------|----------|----------|------------|
| **Analog** | `Device_Config_Analog` | Per Channel | `device_id`, `channel_type`, `channel`, `io_pin`, `name` | `enabled`, `divider`, `multiplier`, `value` (outputs), `scan_rate` |
| **Digital** | `Device_Config_Digital` | Per Channel | `device_id`, `channel_type`, `channel`, `io_pin`, `name` | `enabled` |
| **MODBUS** | `Device_Config_MODBUS` | Settings + Slave Devices | `device_id`, `config_type`, `slave_id`, `function_code`, `register_address`, `data_type`, `endianness`, `variable_name` | `enabled`, `baud_rate`, `data_bits`, `parity`, `stop_bits`, `mode`, `role`, `polling_interval_ms`, `index`, `register_count` |
| **CAN Bus** | `Device_Config_CANBus` | Settings + Messages + Mappings | `device_id`, `config_type`, `can_id`, `direction`, `byte_position`, `data_type`, `endianness`, `variable_name` | `enabled`, `baud_rate`, `identifier_length`, `can_mode`, `filter_mode`, `filter_id`, `filter_mask`, `index`, `period_ms`, `data_length`, `scale_factor`, `offset` |
| **All Tabs** | `Device_Config` | Merged JSON | `device_id` | `config_json` (complete JSON string) |

---

## 🔗 Related Files

- **Save Logic**: `app/pages/device_config.py` (save callbacks)
- **JSON Builder**: `app/services/config_json_builder.py`
- **Database Service**: `app/services/device_config_db.py`
- **Load Logic**: `app/pages/device_config.py` (load callbacks)

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-06  
**Author**: IOTNarad Dashboard Documentation

