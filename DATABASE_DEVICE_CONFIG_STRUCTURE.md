# Device Configuration Database Structure

## Overview
Yeh document explain karta hai ki device configurations kaise InfluxDB mein store hote hain aur kaise unhein query karein.

---

## 📊 Database Tables (Measurements)

InfluxDB mein device configurations ko multiple measurements mein store kiya jata hai:

### 1. **Device_Config** (Complete Configuration)
Complete device configuration JSON store hota hai.

### 2. **Device_Config_Analog** (Analog Channels)
Individual analog channels ki details.

### 3. **Device_Config_Digital** (Digital Channels)
Individual digital channels ki details.

### 4. **Device_Config_MODBUS** (MODBUS Configuration)
MODBUS settings aur slave devices.

### 5. **Device_Config_CANBus** (CAN Bus Configuration)
CAN Bus settings, messages, aur data mappings.

---

## 📋 Table Structures

### 1. Device_Config Table

**Measurement:** `Device_Config`

**Tags:**
- `device_id`: Device identifier (e.g., "esp32_gw_01")
- `device_name`: Device name (e.g., "ESP32-Gateway-01")
- `device_type`: Device type (e.g., "esp32_gateway")
- `location`: Device location (e.g., "Production Line 1")

**Fields:**
- `config_json`: Complete configuration as JSON string
- `version`: Configuration version (e.g., "1.0.0")

**Timestamp:** Configuration save time

**Example Point:**
```python
Point("Device_Config")
    .tag("device_id", "esp32_gw_01")
    .tag("device_name", "ESP32-Gateway-01")
    .tag("device_type", "esp32_gateway")
    .tag("location", "Production Line 1")
    .field("config_json", '{"device_id": "esp32_gw_01", ...}')
    .field("version", "1.0.0")
    .time(timestamp, WritePrecision.NS)
```

---

### 2. Device_Config_Analog Table

**Measurement:** `Device_Config_Analog`

**Tags:**
- `device_id`: Device identifier
- `channel_type`: Channel type ("input_4_20ma", "input_1_10v", "output_0_10v")
- `channel`: Channel number (e.g., "1", "2")
- `io_pin`: IO pin name (e.g., "AIN0", "DOUT0")
- `name`: Channel name (e.g., "Temperature Sensor")

**Fields:**
- `enabled`: Enable/disable flag (true/false)
- `divider`: Divider value
- `multiplier`: Multiplier value
- `min_value`: Minimum value
- `max_value`: Maximum value
- `unit`: Unit of measurement ("mA" or "V")
- `value`: Output value (for outputs only)

**Example Points:**
```python
# 4-20mA Input
Point("Device_Config_Analog")
    .tag("device_id", "esp32_gw_01")
    .tag("channel_type", "input_4_20ma")
    .tag("channel", "1")
    .tag("io_pin", "AIN0")
    .tag("name", "Temperature Sensor")
    .field("enabled", True)
    .field("divider", 100)
    .field("multiplier", 1)
    .field("min_value", 4)
    .field("max_value", 20)
    .field("unit", "mA")
    .time(timestamp, WritePrecision.NS)

# 0-10V Output
Point("Device_Config_Analog")
    .tag("device_id", "esp32_gw_01")
    .tag("channel_type", "output_0_10v")
    .tag("channel", "1")
    .tag("io_pin", "DOUT0")
    .tag("name", "Valve Control")
    .field("enabled", True)
    .field("value", 5.0)
    .field("min_value", 0)
    .field("max_value", 10)
    .field("unit", "V")
    .time(timestamp, WritePrecision.NS)
```

---

### 3. Device_Config_Digital Table

**Measurement:** `Device_Config_Digital`

**Tags:**
- `device_id`: Device identifier
- `channel_type`: Channel type ("npn_input", "npn_output", "pnp_input", "pnp_output", "relay")
- `channel`: Channel number (e.g., "1", "2")
- `io_pin`: IO pin name (e.g., "INP1H", "OUTL1", "RLY1")
- `name`: Channel name (e.g., "Start Button")

**Fields:**
- `enabled`: Enable/disable flag (true/false)
- `pullup`: Pullup resistor enabled (true/false) - for inputs only
- `debounce_ms`: Debounce time in milliseconds - for inputs only
- `initial_state`: Initial output state (true/false) - for outputs/relays only

**Example Points:**
```python
# NPN Input
Point("Device_Config_Digital")
    .tag("device_id", "esp32_gw_01")
    .tag("channel_type", "npn_input")
    .tag("channel", "1")
    .tag("io_pin", "INP1H")
    .tag("name", "Start Button")
    .field("enabled", True)
    .field("pullup", True)
    .field("debounce_ms", 50)
    .time(timestamp, WritePrecision.NS)

# Relay
Point("Device_Config_Digital")
    .tag("device_id", "esp32_gw_01")
    .tag("channel_type", "relay")
    .tag("channel", "1")
    .tag("io_pin", "RLY1")
    .tag("name", "Main Power Relay")
    .field("enabled", True)
    .field("initial_state", False)
    .time(timestamp, WritePrecision.NS)
```

---

### 4. Device_Config_MODBUS Table

**Measurement:** `Device_Config_MODBUS`

**Tags:**
- `device_id`: Device identifier
- `config_type`: Configuration type ("settings" or "slave_device")
- `slave_id`: MODBUS slave ID (for slave devices only)
- `function_code`: Function code (for slave devices only, e.g., "0x03")
- `register_address`: Register address (for slave devices only)
- `data_type`: Data type (for slave devices only, e.g., "int16")
- `endianness`: Endianness (for slave devices only, e.g., "Big Endian")
- `variable_name`: Variable name (for slave devices only)

**Fields:**
- `enabled`: Enable/disable flag (for settings only)
- `baud_rate`: Baud rate (for settings only)
- `data_bits`: Data bits (for settings only)
- `parity`: Parity (for settings only)
- `stop_bits`: Stop bits (for settings only)
- `mode`: MODBUS mode (for settings only, e.g., "RTU")
- `role`: MODBUS role (for settings only, e.g., "Master")
- `polling_interval_ms`: Polling interval in milliseconds (for settings only)
- `index`: Device index (for slave devices only)
- `register_count`: Register count (for slave devices only)

**Example Points:**
```python
# MODBUS Settings
Point("Device_Config_MODBUS")
    .tag("device_id", "esp32_gw_01")
    .tag("config_type", "settings")
    .field("enabled", True)
    .field("baud_rate", 9600)
    .field("data_bits", 8)
    .field("parity", "None")
    .field("stop_bits", 1)
    .field("mode", "RTU")
    .field("role", "Master")
    .field("polling_interval_ms", 1000)
    .time(timestamp, WritePrecision.NS)

# Slave Device
Point("Device_Config_MODBUS")
    .tag("device_id", "esp32_gw_01")
    .tag("config_type", "slave_device")
    .tag("slave_id", "1")
    .tag("function_code", "0x03")
    .tag("register_address", "0")
    .tag("data_type", "int16")
    .tag("endianness", "Big Endian")
    .tag("variable_name", "Temperature")
    .field("index", 0)
    .field("register_count", 1)
    .time(timestamp, WritePrecision.NS)
```

---

### 5. Device_Config_CANBus Table

**Measurement:** `Device_Config_CANBus`

**Tags:**
- `device_id`: Device identifier
- `config_type`: Configuration type ("settings", "can_message", "data_mapping")
- `can_id`: CAN message ID (for messages/mappings only, e.g., "0x123")
- `direction`: Message direction (for messages only, "TX" or "RX")
- `variable_name`: Variable name (for messages/mappings only)
- `byte_position`: Byte position (for mappings only, e.g., "Byte 0")
- `data_type`: Data type (for mappings only, e.g., "int8")
- `endianness`: Endianness (for mappings only, e.g., "Big Endian")

**Fields:**
- `enabled`: Enable/disable flag (for settings only)
- `baud_rate`: Baud rate (for settings only)
- `identifier_length`: Identifier length (for settings only, e.g., "11-bit")
- `can_mode`: CAN mode (for settings only, e.g., "Normal")
- `filter_mode`: Filter mode (for settings only, e.g., "Accept")
- `filter_id`: Filter ID (for settings only, e.g., "0x123")
- `filter_mask`: Filter mask (for settings only, e.g., "0x7FF")
- `index`: Message/mapping index (for messages/mappings only)
- `period_ms`: Message period in milliseconds (for messages only)
- `data_length`: Data length (for messages/mappings only)
- `scale_factor`: Scale factor (for mappings only)
- `offset`: Offset value (for mappings only)

**Example Points:**
```python
# CAN Bus Settings
Point("Device_Config_CANBus")
    .tag("device_id", "esp32_gw_01")
    .tag("config_type", "settings")
    .field("enabled", True)
    .field("baud_rate", 500)
    .field("identifier_length", "11-bit")
    .field("can_mode", "Normal")
    .field("filter_mode", "Accept")
    .field("filter_id", "0x123")
    .field("filter_mask", "0x7FF")
    .time(timestamp, WritePrecision.NS)

# CAN Message
Point("Device_Config_CANBus")
    .tag("device_id", "esp32_gw_01")
    .tag("config_type", "can_message")
    .tag("can_id", "0x123")
    .tag("direction", "TX")
    .tag("variable_name", "Engine Speed")
    .field("index", 0)
    .field("period_ms", 100)
    .field("data_length", 8)
    .time(timestamp, WritePrecision.NS)

# Data Mapping
Point("Device_Config_CANBus")
    .tag("device_id", "esp32_gw_01")
    .tag("config_type", "data_mapping")
    .tag("can_id", "0x123")
    .tag("byte_position", "Byte 0")
    .tag("data_type", "int8")
    .tag("endianness", "Big Endian")
    .tag("variable_name", "Speed Low")
    .field("index", 0)
    .field("data_length", "1 Byte")
    .field("scale_factor", 1.0)
    .field("offset", 0.0)
    .time(timestamp, WritePrecision.NS)
```

---

## 💻 Usage Example

### Save Device Configuration

```python
from app.services.device_config_db import DeviceConfigDBService
from app.services.config_json_builder import ConfigJSONBuilder

# Initialize services
db_service = DeviceConfigDBService()
builder = ConfigJSONBuilder()

# Build configuration
config = builder.build_complete_config(
    device_id="esp32_gw_01",
    device_name="ESP32-Gateway-01",
    analog_config={...},
    digital_config={...},
    modbus_config={...},
    can_bus_config={...}
)

# Save to database
success = db_service.save_device_config("esp32_gw_01", config)

if success:
    print("✅ Configuration saved to database!")
else:
    print("❌ Error saving configuration")
```

### Get Device Configuration

```python
# Get latest configuration
config = db_service.get_device_config("esp32_gw_01")

if config:
    print(f"Device: {config['metadata']['device_name']}")
    print(f"Analog channels: {len(config['analog']['input_4_20ma'])}")
    print(f"MODBUS slaves: {len(config['rs485_modbus']['slave_devices'])}")
else:
    print("Configuration not found")
```

### List All Devices

```python
# List all devices
devices = db_service.list_devices()

print(f"Found {len(devices)} devices:")
for device_id in devices:
    print(f"  - {device_id}")
```

---

## 🔍 Query Examples

### Query Complete Configuration

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

### Query Analog Channels

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> filter(fn: (r) => r.channel_type == "input_4_20ma")
  |> sort(columns: ["_time"], desc: true)
```

### Query MODBUS Slave Devices

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> filter(fn: (r) => r.config_type == "slave_device")
  |> sort(columns: ["_time"], desc: true)
```

### Query CAN Bus Messages

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_CANBus")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> filter(fn: (r) => r.config_type == "can_message")
  |> sort(columns: ["_time"], desc: true)
```

---

## 📍 Database Check Commands

### Docker Command (Local InfluxDB)

```bash
# Check Device_Config table
docker exec -i iotnarad_influxdb influx query '
  from(bucket: "iot_data_gcp")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "Device_Config")
    |> limit(n: 10)
'
```

### InfluxDB Cloud UI

1. Open InfluxDB Cloud UI
2. Go to "Data Explorer"
3. Select bucket: `iot_data_gcp`
4. Select measurement: `Device_Config`, `Device_Config_Analog`, etc.
5. Add filters for `device_id`
6. Run query

---

## 📊 Data Visualization

### Check All Measurements

```flux
import "influxdata/influxdb/schema"

schema.measurements(bucket: "iot_data_gcp")
```

### Check All Devices

```flux
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "iot_data_gcp",
  tag: "device_id",
  predicate: (r) => r._measurement == "Device_Config",
  start: -365d
)
```

### Count Configurations by Device

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> group(columns: ["device_id"])
  |> count()
```

---

## 🔄 Update Configuration

Configuration update karne ke liye, naya Point save karein with current timestamp. Latest configuration automatically latest timestamp wala hoga.

---

## 📝 Notes

1. **All configurations** are stored with timestamps for version history
2. **Complete config** is stored in `Device_Config` measurement as JSON
3. **Individual sections** are stored in separate measurements for easier querying
4. **Tags** are used for filtering and indexing
5. **Fields** contain the actual configuration values
6. **Latest configuration** can be retrieved by sorting by timestamp descending

---

## 🚀 Next Steps

1. **Save Configuration** - Use `DeviceConfigDBService.save_device_config()`
2. **Load Configuration** - Use `DeviceConfigDBService.get_device_config()`
3. **Query Data** - Use Flux queries in InfluxDB UI or Python
4. **Visualize** - Create dashboards in InfluxDB UI
5. **Monitor** - Set up alerts for configuration changes

