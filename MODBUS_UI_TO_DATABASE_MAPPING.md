# RS485 MODBUS: UI to Database Mapping Guide

## 📋 Overview

This document explains **exactly** how values entered in the RS485 MODBUS UI are saved to the InfluxDB database. It clarifies which fields go to which database rows and why some values might not be saving.

---

## 🗂️ Database Structure

The MODBUS configuration is saved in the **`Device_Config_MODBUS`** measurement in InfluxDB. It uses **two types of rows**:

1. **Settings Row** (`config_type = "settings"`) - One row per device
2. **Slave Device Rows** (`config_type = "slave_device"`) - One row per slave device

---

## 📊 Complete UI to Database Mapping

### Section 1: Communication Settings → Settings Row

| UI Field | UI Component ID | Database Field | Database Row Type | Notes |
|----------|----------------|----------------|-------------------|-------|
| **Baud Rate** | `modbus-baud-rate` | `baud_rate` | `settings` | Integer (e.g., 38400) |
| **Data Bits** | `modbus-data-bits` | `data_bits` | `settings` | Integer (e.g., 8) |
| **Parity** | `modbus-parity` | `parity` | `settings` | String (e.g., "Odd") |
| **Stop Bits** | `modbus-stop-bits` | `stop_bits` | `settings` | Integer (e.g., 1) |

### Section 2: Protocol Settings → Settings Row

| UI Field | UI Component ID | Database Field | Database Row Type | Notes |
|----------|----------------|----------------|-------------------|-------|
| **Mode** | `modbus-mode` | `mode` | `settings` | String (e.g., "ASCII") |
| **Role** | `modbus-role` | `role` | `settings` | String (e.g., "Master") |

### Section 3: Polling Interval → Settings Row

| UI Field | UI Component ID | Database Field | Database Row Type | Notes |
|----------|----------------|----------------|-------------------|-------|
| **Polling Interval (ms)** | `modbus-polling-interval` | `polling_interval_ms` | `settings` | Integer (e.g., 4000) |

### Section 4: Slave Devices → Slave Device Rows (One Row Per Device)

| UI Field | UI Component ID | Database Field | Database Row Type | Notes |
|----------|----------------|----------------|-------------------|-------|
| **Slave ID** | `{'type': 'modbus-slave-id', 'index': N}` | `slave_id` (tag) | `slave_device` | String (e.g., "4") |
| **Function Code** | `{'type': 'modbus-function-code', 'index': N}` | `function_code` (tag) | `slave_device` | String (e.g., "0x01") |
| **Register Address** | `{'type': 'modbus-register-addr', 'index': N}` | `register_address` (tag) | `slave_device` | String (e.g., "0X0987") |
| **Data Type** | `{'type': 'modbus-data-type', 'index': N}` | `data_type` (tag) | `slave_device` | String (e.g., "int8") |
| **Endianness** | `{'type': 'modbus-endianness', 'index': N}` | `endianness` (tag) | `slave_device` | String (e.g., "Big Endian") |
| **Variable Name** | `{'type': 'modbus-var-name', 'index': N}` | `variable_name` (tag) | `slave_device` | String (e.g., "REGISTER123") |
| **Index** | (auto-generated) | `index` (field) | `slave_device` | Integer (0, 1, 2, ...) |
| **Register Count** | (auto-generated) | `register_count` (field) | `slave_device` | Integer (always 1) |

**Note:** `N` in the component ID represents the row index (0, 1, 2, ...)

---

## 🔄 Complete Data Flow

### Step 1: User Enters Values in UI

```
User fills in:
├── Communication Settings
│   ├── Baud Rate: 38400
│   ├── Data Bits: 8
│   ├── Parity: Odd
│   └── Stop Bits: 1
├── Protocol Settings
│   ├── Mode: ASCII
│   └── Role: Master
├── Polling Interval: 4000
└── Slave Devices (1 row)
    ├── Slave ID: 4
    ├── Function Code: 0x01
    ├── Register Address: 0X0987
    ├── Data Type: int8
    ├── Endianness: Big Endian
    └── Variable Name: REGISTER123
```

### Step 2: User Clicks "Save Configuration"

The `save_modbus_configuration` callback is triggered.

### Step 3: Values Read from UI State

```python
# Values are read from State() inputs:
modbus_baud_rate = "38400"
modbus_data_bits = "8"
modbus_parity = "Odd"
modbus_stop_bits = "1"
modbus_mode = "ASCII"
modbus_role = "Master"
modbus_polling_interval = 4000
modbus_devices_store = [
    {
        "index": 0,
        "slave_id": "4",
        "function_code": "0x01",
        "register_addr": "0X0987",
        "data_type": "int8",
        "endianness": "Big Endian",
        "var_name": "REGISTER123"
    }
]
```

### Step 4: Config JSON Built

The `ConfigJSONBuilder.build_modbus_config()` function creates:

```json
{
  "enabled": true,
  "communication_settings": {
    "baud_rate": 38400,
    "data_bits": 8,
    "parity": "Odd",
    "stop_bits": 1
  },
  "protocol_settings": {
    "mode": "ASCII",
    "role": "Master"
  },
  "polling_interval_ms": 4000,
  "slave_devices": [
    {
      "index": 0,
      "slave_id": "4",
      "function_code": "0x01",
      "register_address": "0X0987",
      "data_type": "int8",
      "endianness": "Big Endian",
      "variable_name": "REGISTER123",
      "register_count": 1
    }
  ]
}
```

### Step 5: Database Save Function Called

`DeviceConfigDBService._save_modbus_config()` is called with:
- `device_id`: "0x235b" (example)
- `modbus_config`: The JSON above
- `timestamp`: Current UTC time

### Step 6: Database Writes Two Types of Rows

#### Row 1: Settings Row

```python
Point("Device_Config_MODBUS")
    .tag("device_id", "0x235b")
    .tag("config_type", "settings")  # ← This identifies it as settings
    .field("enabled", true)
    .field("baud_rate", 38400)        # ← From communication_settings
    .field("data_bits", 8)            # ← From communication_settings
    .field("parity", "Odd")           # ← From communication_settings
    .field("stop_bits", 1)            # ← From communication_settings
    .field("mode", "ASCII")           # ← From protocol_settings
    .field("role", "Master")          # ← From protocol_settings
    .field("polling_interval_ms", 4000) # ← From top level
```

**Database Result:**
- **Measurement:** `Device_Config_MODBUS`
- **Tags:** `device_id="0x235b"`, `config_type="settings"`
- **Fields:** `enabled`, `baud_rate`, `data_bits`, `parity`, `stop_bits`, `mode`, `role`, `polling_interval_ms`
- **All other fields:** `null` (not applicable to settings row)

#### Row 2: Slave Device Row (One per slave device)

```python
Point("Device_Config_MODBUS")
    .tag("device_id", "0x235b")
    .tag("config_type", "slave_device")  # ← This identifies it as slave device
    .tag("slave_id", "4")                 # ← From slave_devices[0]
    .tag("function_code", "0x01")         # ← From slave_devices[0]
    .tag("register_address", "0X0987")   # ← From slave_devices[0]
    .tag("data_type", "int8")             # ← From slave_devices[0]
    .tag("endianness", "Big Endian")      # ← From slave_devices[0]
    .tag("variable_name", "REGISTER123")  # ← From slave_devices[0]
    .field("index", 0)                    # ← From slave_devices[0]
    .field("register_count", 1)           # ← Auto-generated
```

**Database Result:**
- **Measurement:** `Device_Config_MODBUS`
- **Tags:** `device_id="0x235b"`, `config_type="slave_device"`, `slave_id="4"`, `function_code="0x01"`, `register_address="0X0987"`, `data_type="int8"`, `endianness="Big Endian"`, `variable_name="REGISTER123"`
- **Fields:** `index`, `register_count`
- **All other fields:** `null` (not applicable to slave_device row)

---

## 🔍 Understanding the Database Query Results

When you query `Device_Config_MODBUS` in InfluxDB, you'll see:

### Settings Row (config_type = "settings")
```
_time: 2025-12-03T13:35:00Z
_measurement: Device_Config_MODBUS
device_id: 0x235b
config_type: settings
baud_rate: 38,400
data_bits: 8
enabled: true
mode: ASCII
parity: Odd
polling_interval_ms: 4,000
role: Master
stop_bits: 1
data_type: null          ← null (not applicable)
endianness: null         ← null (not applicable)
function_code: null      ← null (not applicable)
register_address: null   ← null (not applicable)
slave_id: null           ← null (not applicable)
variable_name: null      ← null (not applicable)
```

### Slave Device Row (config_type = "slave_device")
```
_time: 2025-12-03T13:35:00Z
_measurement: Device_Config_MODBUS
device_id: 0x235b
config_type: slave_device
slave_id: 4
function_code: 0x01
register_address: 0X0987
data_type: int8
endianness: Big Endian
variable_name: REGISTER123
index: 0
register_count: 1
baud_rate: null          ← null (not applicable)
data_bits: null          ← null (not applicable)
enabled: null            ← null (not applicable)
mode: null               ← null (not applicable)
parity: null             ← null (not applicable)
polling_interval_ms: null ← null (not applicable)
role: null               ← null (not applicable)
stop_bits: null          ← null (not applicable)
```

**This is NORMAL!** The `null` values are expected because:
- Settings row doesn't have slave device fields
- Slave device rows don't have settings fields

---

## ❓ Why Some Values Don't Save

### Common Issues:

1. **Values are None/Empty**
   - **Problem:** UI State values are `None` or empty strings
   - **Solution:** Check logs to see what values are received
   - **Debug:** Added logging in `save_modbus_configuration()` callback

2. **Database Write Fails Silently**
   - **Problem:** Exception occurs but not logged
   - **Solution:** Check server logs for errors
   - **Debug:** Added logging in `_save_modbus_config()` function

3. **Config Structure Incorrect**
   - **Problem:** `build_modbus_config()` doesn't create correct structure
   - **Solution:** Verify JSON structure matches expected format
   - **Debug:** Added logging to show built config

4. **Values Not Read from UI**
   - **Problem:** State() inputs not connected to UI components
   - **Solution:** Verify component IDs match State() IDs
   - **Check:** All IDs are correctly mapped

---

## 🧪 Testing & Verification

### Step 1: Check What Values Are Received

After clicking "Save Configuration", check server logs for:

```
🔍 MODBUS Save - Received values:
   Baud Rate: 38400 (type: <class 'str'>)
   Data Bits: 8 (type: <class 'str'>)
   Parity: Odd (type: <class 'str'>)
   Stop Bits: 1 (type: <class 'str'>)
   Mode: ASCII (type: <class 'str'>)
   Role: Master (type: <class 'str'>)
   Polling Interval: 4000 (type: <class 'int'>)
   Slave Devices Count: 1
```

### Step 2: Check What Config Was Built

Look for:

```
🔍 MODBUS Config Built:
   Communication Settings: {'baud_rate': 38400, 'data_bits': 8, 'parity': 'Odd', 'stop_bits': 1}
   Protocol Settings: {'mode': 'ASCII', 'role': 'Master'}
   Polling Interval: 4000
   Slave Devices Count: 1
```

### Step 3: Check Database Write

Look for:

```
🔍 _save_modbus_config called for device: 0x235b
   Config keys: ['enabled', 'communication_settings', 'protocol_settings', 'polling_interval_ms', 'slave_devices']
   Communication settings: {'baud_rate': 38400, 'data_bits': 8, 'parity': 'Odd', 'stop_bits': 1}
   Protocol settings: {'mode': 'ASCII', 'role': 'Master'}
   Polling Interval: 4000
   Slave devices count: 1
🔍 Extracted values for saving:
   Baud Rate: 38400
   Data Bits: 8
   Parity: Odd
   Stop Bits: 1
   Mode: ASCII
   Role: Master
   Polling Interval: 4000
✅ MODBUS settings point written to database
```

### Step 4: Verify in InfluxDB

Query:
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
  |> filter(fn: (r) => r.device_id == "0x235b")
  |> sort(columns: ["_time"], desc: true)
```

You should see:
- **1 row** with `config_type="settings"` containing all communication/protocol/polling fields
- **N rows** with `config_type="slave_device"` (one per slave device)

---

## 📝 Summary

### Settings Row Contains:
✅ Baud Rate  
✅ Data Bits  
✅ Parity  
✅ Stop Bits  
✅ Mode  
✅ Role  
✅ Polling Interval  
✅ Enabled  

### Slave Device Row Contains (per device):
✅ Slave ID  
✅ Function Code  
✅ Register Address  
✅ Data Type  
✅ Endianness  
✅ Variable Name  
✅ Index  
✅ Register Count  

### What Goes Where:

```
UI Input → JSON Config → Database Row Type
─────────────────────────────────────────────
Communication Settings → communication_settings → settings row
Protocol Settings → protocol_settings → settings row
Polling Interval → polling_interval_ms → settings row
Slave Device Fields → slave_devices[] → slave_device rows (one per device)
```

---

## 🔧 Troubleshooting

If values are not saving:

1. **Check Logs:** Look for the debug messages added
2. **Verify UI Values:** Ensure dropdowns/inputs have values
3. **Check Database Connection:** Verify InfluxDB is connected
4. **Verify Timestamp:** All rows should have the same timestamp
5. **Check Query:** Use the Flux query above to verify data

---

**Last Updated:** Documentation created to clarify UI-to-database mapping
**Status:** ✅ Complete mapping explanation

