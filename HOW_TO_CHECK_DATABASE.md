# How to Check Device Configuration in Database

## Overview
Yeh guide explain karta hai ki kaise device configurations ko database mein check karein.

---

## 📊 Database Tables (Measurements)

InfluxDB mein device configurations ko yeh measurements mein store kiya jata hai:

1. **Device_Config** - Complete configuration JSON
2. **Device_Config_Analog** - Analog channels
3. **Device_Config_Digital** - Digital channels
4. **Device_Config_MODBUS** - MODBUS configuration
5. **Device_Config_CANBus** - CAN Bus configuration

---

## 🔍 Method 1: InfluxDB Cloud UI

### Step 1: Open InfluxDB Cloud UI
1. Browser mein InfluxDB Cloud UI open karein
2. Login karein with your credentials

### Step 2: Go to Data Explorer
1. Left sidebar mein "Data Explorer" click karein
2. Bucket select karein: `iot_data_gcp`

### Step 3: Select Measurement
1. Measurement dropdown se select karein:
   - `Device_Config` - Complete configuration
   - `Device_Config_Analog` - Analog channels
   - `Device_Config_Digital` - Digital channels
   - `Device_Config_MODBUS` - MODBUS configuration
   - `Device_Config_CANBus` - CAN Bus configuration

### Step 4: Add Filters
1. "Filter" button click karein
2. Filter add karein:
   - `device_id` = `esp32_gw_01` (your device ID)
   - `_measurement` = `Device_Config` (or other measurement)

### Step 5: Set Time Range
1. Time range select karein: `-365d` (last 1 year)
2. "Submit" click karein

### Step 6: View Results
1. Results table mein data dikhega
2. Har row ek configuration point hai
3. Latest configuration ke liye sort by `_time` descending

---

## 🔍 Method 2: Flux Query in Data Explorer

### Query 1: Get Latest Complete Configuration

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
```

**Result:**
- `config_json`: Complete configuration as JSON string
- `version`: Configuration version
- `device_id`: Device identifier
- `device_name`: Device name
- `device_type`: Device type
- `location`: Device location

### Query 2: Get All Analog Channels

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> sort(columns: ["_time"], desc: true)
  |> group(columns: ["channel_type", "channel"])
  |> limit(n: 1)
```

**Result:**
- Har channel ki individual details
- `channel_type`: "input_4_20ma", "input_1_10v", "output_0_10v"
- `channel`: Channel number
- `io_pin`: IO pin name
- `name`: Channel name
- `enabled`: Enable/disable flag
- `divider`, `multiplier`, `value`, etc.

### Query 3: Get MODBUS Slave Devices

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> filter(fn: (r) => r.config_type == "slave_device")
  |> sort(columns: ["_time"], desc: true)
```

**Result:**
- Har slave device ki details
- `slave_id`: MODBUS slave ID
- `function_code`: Function code (e.g., "0x03")
- `register_address`: Register address
- `data_type`: Data type (e.g., "int16")
- `endianness`: Endianness (e.g., "Big Endian")
- `variable_name`: Variable name

### Query 4: Get CAN Bus Messages

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_CANBus")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> filter(fn: (r) => r.config_type == "can_message")
  |> sort(columns: ["_time"], desc: true)
```

**Result:**
- Har CAN message ki details
- `can_id`: CAN message ID (e.g., "0x123")
- `direction`: Direction ("TX" or "RX")
- `period_ms`: Message period in milliseconds
- `variable_name`: Variable name

### Query 5: Get All Devices

```flux
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "iot_data_gcp",
  tag: "device_id",
  predicate: (r) => r._measurement == "Device_Config",
  start: -365d
)
```

**Result:**
- List of all device IDs that have configurations

---

## 🔍 Method 3: Python Script

### Script: Check Device Configuration

```python
from app.services.device_config_db import DeviceConfigDBService
import json

# Initialize service
db_service = DeviceConfigDBService()

# Check connection
if not db_service.is_connected():
    print("❌ InfluxDB not connected!")
    exit(1)

print("✅ InfluxDB connected successfully!")

# Get device configuration
device_id = "esp32_gw_01"
config = db_service.get_device_config(device_id)

if config:
    print(f"\n📄 Configuration for device: {device_id}")
    print("=" * 60)
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print("=" * 60)
else:
    print(f"❌ Configuration not found for device: {device_id}")

# List all devices
print("\n📋 All devices with configurations:")
devices = db_service.list_devices()
for device_id in devices:
    print(f"  - {device_id}")
```

### Run Script

```bash
# Activate virtual environment (if using)
# source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Run script
python EXAMPLE_SAVE_TO_DATABASE.py
```

---

## 🔍 Method 4: Docker Command (Local InfluxDB)

### Check Device_Config Table

```bash
docker exec -i iotnarad_influxdb influx query '
  from(bucket: "iot_data_gcp")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "Device_Config")
    |> filter(fn: (r) => r.device_id == "esp32_gw_01")
    |> sort(columns: ["_time"], desc: true)
    |> limit(n: 1)
    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
'
```

### Check Analog Channels

```bash
docker exec -i iotnarad_influxdb influx query '
  from(bucket: "iot_data_gcp")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
    |> filter(fn: (r) => r.device_id == "esp32_gw_01")
    |> sort(columns: ["_time"], desc: true)
'
```

### Check MODBUS Configuration

```bash
docker exec -i iotnarad_influxdb influx query '
  from(bucket: "iot_data_gcp")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
    |> filter(fn: (r) => r.device_id == "esp32_gw_01")
    |> sort(columns: ["_time"], desc: true)
'
```

---

## 📊 Table Structure Summary

### Device_Config Table

| Tag | Field | Description |
|-----|-------|-------------|
| device_id | - | Device identifier |
| device_name | - | Device name |
| device_type | - | Device type |
| location | - | Device location |
| - | config_json | Complete configuration JSON |
| - | version | Configuration version |

### Device_Config_Analog Table

| Tag | Field | Description |
|-----|-------|-------------|
| device_id | - | Device identifier |
| channel_type | - | "input_4_20ma", "input_1_10v", "output_0_10v" |
| channel | - | Channel number |
| io_pin | - | IO pin name |
| name | - | Channel name |
| - | enabled | Enable/disable flag |
| - | divider | Divider value |
| - | multiplier | Multiplier value |
| - | value | Output value (for outputs) |
| - | min_value | Minimum value |
| - | max_value | Maximum value |
| - | unit | Unit ("mA" or "V") |

### Device_Config_MODBUS Table

| Tag | Field | Description |
|-----|-------|-------------|
| device_id | - | Device identifier |
| config_type | - | "settings" or "slave_device" |
| slave_id | - | MODBUS slave ID (for slave devices) |
| function_code | - | Function code (for slave devices) |
| register_address | - | Register address (for slave devices) |
| data_type | - | Data type (for slave devices) |
| endianness | - | Endianness (for slave devices) |
| variable_name | - | Variable name (for slave devices) |
| - | enabled | Enable/disable flag (for settings) |
| - | baud_rate | Baud rate (for settings) |
| - | polling_interval_ms | Polling interval (for settings) |
| - | index | Device index (for slave devices) |

---

## 🔄 Check Configuration History

### Get All Configurations for a Device

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> sort(columns: ["_time"], desc: true)
```

**Result:**
- Sabhi configurations with timestamps
- Latest configuration first (descending order)

---

## ✅ Verification Steps

1. **Check Connection**
   - InfluxDB Cloud UI open karein
   - Connection status check karein

2. **Check Bucket**
   - Bucket: `iot_data_gcp`
   - Org: `iot-narad-gcp`

3. **Check Measurement**
   - Measurement: `Device_Config`
   - Device ID filter lagayein

4. **Check Data**
   - Latest configuration check karein
   - Config JSON verify karein

5. **Check Individual Sections**
   - Analog channels check karein
   - Digital channels check karein
   - MODBUS configuration check karein
   - CAN Bus configuration check karein

---

## 🚀 Quick Check Commands

### Python Quick Check

```python
from app.services.device_config_db import DeviceConfigDBService

db = DeviceConfigDBService()
config = db.get_device_config("esp32_gw_01")
print(config)
```

### Flux Quick Query

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "esp32_gw_01")
  |> last()
```

---

## 📝 Notes

1. **Time Range**: Always use `-365d` (1 year) for configuration queries
2. **Latest Config**: Sort by `_time` descending and limit to 1
3. **JSON Field**: Complete config is in `config_json` field
4. **Individual Sections**: Check separate measurements for detailed data
5. **Device ID**: Always filter by `device_id` for specific device

---

## 🔗 Related Files

- `app/services/device_config_db.py` - Database service
- `EXAMPLE_SAVE_TO_DATABASE.py` - Example script
- `DATABASE_DEVICE_CONFIG_STRUCTURE.md` - Database structure
- `DEVICE_CONFIG_JSON_EXAMPLE.json` - JSON example

