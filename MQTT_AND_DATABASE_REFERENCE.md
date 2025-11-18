# MQTT & Database Reference Guide

**Last Updated:** November 18, 2025  
**Database:** Self-Hosted InfluxDB 2.x (Flux Queries)  
**MQTT Broker:** Mosquitto (Docker)

---

## 📋 Table of Contents

1. [Database Configuration](#database-configuration)
2. [File Review Status](#file-review-status)
3. [MQTT Topic Structure](#mqtt-topic-structure)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [Code Verification](#code-verification)

---

## 🔧 Database Configuration

### InfluxDB Setup
- **Type:** Self-Hosted InfluxDB 2.x
- **Query Language:** Flux (NOT SQL)
- **Location:** Docker container (`influxdb:8086`)
- **Default Org:** `iotnarad`
- **Default Bucket:** `iotnarad-bucket`

### Environment Variables
```env
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=<your-token>
INFLUXDB_ORG=iotnarad
INFLUXDB_BUCKET=iotnarad-bucket
```

### MQTT Broker Setup
- **Type:** Mosquitto (Docker)
- **Host:** `mqtt` (container name)
- **Port:** `1883`
- **WebSocket Port:** `9001`

### Environment Variables
```env
MQTT_BROKER=mqtt
MQTT_PORT=1883
```

---

## ✅ File Review Status

### 1. `mqtt_client.py` - ✅ FULLY UPDATED

**Status:** ✅ **Fully compatible with current setup**

#### Verification:
- ✅ No SQL queries (MQTT only, no database queries)
- ✅ No Cloud-specific code
- ✅ Uses `paho-mqtt` library (standard MQTT client)
- ✅ Correct topic structure for device communication
- ✅ Proper callback mechanism for message handling

#### Features:
- MQTT connection management
- Topic subscription handling
- Message publish/subscribe operations
- Duplicate message detection
- Background thread execution

---

### 2. `device_info_service.py` - ✅ FULLY UPDATED

**Status:** ✅ **Fully updated for Self-Hosted InfluxDB 2.x with Flux**

#### Verification:
- ✅ **All queries use Flux syntax** (no SQL)
- ✅ Uses `InfluxDBClient` with `query_api` for Flux queries
- ✅ Default URL: `http://influxdb:8086` (Self-Hosted)
- ✅ No Cloud-specific code
- ✅ Proper Flux query structure with `from()`, `filter()`, `pivot()`, etc.

#### Key Functions Using Flux:

**1. `check_serial_number_exists()`** - Lines 60-66
```flux
from(bucket: "iotnarad-bucket")
|> range(start: -365d)
|> filter(fn: (r) => r._measurement == "Device_info")
|> filter(fn: (r) => r.Sr_No == "{serial_number}")
|> limit(n: 1)
```

**2. `get_device_info()`** - Lines 175-183
```flux
from(bucket: "iotnarad-bucket")
|> range(start: -365d)
|> filter(fn: (r) => r._measurement == "Device_info")
|> filter(fn: (r) => r.Sr_No == "{serial_number}")
|> sort(columns: ["_time"], desc: true)
|> limit(n: 1)
|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
```

**3. `list_all_devices()`** - Lines 215-224
```flux
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "iotnarad-bucket",
  tag: "Sr_No",
  predicate: (r) => r._measurement == "Device_info",
  start: -365d
)
```

**4. `get_all_devices_info()`** - Lines 251-260
```flux
from(bucket: "iotnarad-bucket")
|> range(start: -365d)
|> filter(fn: (r) => r._measurement == "Device_info")
|> pivot(rowKey: ["_time", "Sr_No"], columnKey: ["_field"], valueColumn: "_value")
|> group(columns: ["Sr_No"])
|> sort(columns: ["_time"], desc: true)
|> keep(columns: ["_time", "Sr_No", "Owner", "Device_Name", "Date_Of_Register"])
|> first()
```

---

## 📡 MQTT Topic Structure

### Server (Dashboard) Subscribes To:

| Topic Pattern | Description | Purpose | Example |
|--------------|-------------|---------|---------|
| `iotnarad/devices/+/data` | Device sensor data | Receive real-time sensor readings | `iotnarad/devices/NAD-6623/data` → `{"temperature": 25, "humidity": 60}` |
| `iotnarad/devices/+/status` | Device status updates | Monitor device online/offline status | `iotnarad/devices/NAD-6623/status` → `{"status": "online"}` |
| `Dev/Init/Reg/#` | Device registration | Auto-register new devices | `Dev/Init/Reg/NAD-6623` → Device serial number |
| `Dev/ConfigACK/#` | Config acknowledgements (Legacy) | Receive confirmation from hardware | `Dev/ConfigACK/NAD-6623` → `{"status": "success"}` |

**Wildcard Explanation:**
- `+` = Single level wildcard (matches one topic level)
- `#` = Multi-level wildcard (matches multiple topic levels)

---

### Server (Dashboard) Publishes To:

| Topic Pattern | Description | Purpose | QoS | Retain | Example |
|--------------|-------------|---------|-----|--------|---------|
| `Dev/Checksum/<Device ID>` | Device configuration | Send complete config JSON to device | 1 | ✅ Yes | `Dev/Checksum/NAD-6623` → `{"analog": {...}, "digital": {...}}` |
| `Dev/Ack/<Device ID>` | Registration acknowledgment | Confirm device registration | 1 | ❌ No | `Dev/Ack/NAD-6623` → `{"status": "success", "message": "Registered"}` |
| `iotnarad/devices/<Device ID>/cmd` | Device commands | Send commands to device | 1 | ❌ No | `iotnarad/devices/NAD-6623/cmd` → `{"command": "restart"}` |

**Note:** `<Device ID>` = Device Serial Number (Sr_No) from `Device_info` measurement

---

### Hardware (Device) Subscribes To:

| Topic Pattern | Description | Purpose | Example |
|--------------|-------------|---------|---------|
| `Dev/Checksum/<Device ID>` | Device configuration | Receive configuration updates from dashboard | `Dev/Checksum/NAD-6623` → Complete config JSON |
| `iotnarad/devices/<Device ID>/cmd` | Device commands | Receive commands from dashboard | `iotnarad/devices/NAD-6623/cmd` → `{"command": "restart"}` |

**Where:**
- `<Device ID>` = Device's own Serial Number (e.g., `NAD-6623`)

---

### Hardware (Device) Publishes To:

| Topic Pattern | Description | Purpose | Example |
|--------------|-------------|---------|---------|
| `Dev/Init/Reg/<Device ID>` | Device registration | Register itself when first starts | `Dev/Init/Reg/NAD-6623` → Serial number message |
| `iotnarad/devices/<Device ID>/data` | Sensor data | Send real-time sensor readings | `iotnarad/devices/NAD-6623/data` → `{"temperature": 25}` |
| `iotnarad/devices/<Device ID>/status` | Device status | Send online/offline status | `iotnarad/devices/NAD-6623/status` → `{"status": "online"}` |
| `Dev/ConfigACK/<Device ID>` | Config acknowledgement (Legacy) | Confirm config received (optional) | `Dev/ConfigACK/NAD-6623` → `{"status": "success"}` |

**Where:**
- `<Device ID>` = Device's own Serial Number (e.g., `NAD-6623`)

---

## 🔄 Data Flow Diagrams

### 1. Device Registration Flow

```
┌─────────────┐                           ┌──────────────┐
│   Device    │                           │   Dashboard  │
│  (Hardware) │                           │   (Server)   │
└──────┬──────┘                           └──────┬───────┘
       │                                         │
       │ 1. Publish: Dev/Init/Reg/NAD-6623     │
       │────────────────────────────────────────>│
       │                                         │
       │                                         │ 2. MQTT Client receives
       │                                         │    (mqtt_client.py)
       │                                         │
       │                                         │ 3. Call init_callback()
       │                                         │
       │                                         │ 4. device_info_service
       │                                         │    .register_device()
       │                                         │
       │                                         │ 5. Save to InfluxDB:
       │                                         │    Device_info measurement
       │                                         │
       │ 6. Publish: Dev/Ack/NAD-6623           │
       │<────────────────────────────────────────│
       │    {"status": "success"}               │
       │                                         │
```

### 2. Device Data Flow (Sensor Readings)

```
┌─────────────┐                           ┌──────────────┐
│   Device    │                           │   Dashboard  │
│  (Hardware) │                           │   (Server)   │
└──────┬──────┘                           └──────┬───────┘
       │                                         │
       │ 1. Publish:                            │
       │    iotnarad/devices/NAD-6623/data      │
       │────────────────────────────────────────>│
       │    {"temperature": 25, "humidity": 60} │
       │                                         │
       │                                         │ 2. MQTT Client receives
       │                                         │    (mqtt_client.py)
       │                                         │
       │                                         │ 3. Call data_callback()
       │                                         │
       │                                         │ 4. influx.py saves to DB
       │                                         │    (Time-series data)
       │                                         │
```

### 3. Configuration Flow (Dashboard → Device)

```
┌─────────────┐                           ┌──────────────┐
│   Device    │                           │   Dashboard  │
│  (Hardware) │                           │   (Server)   │
└──────┬──────┘                           └──────┬───────┘
       │                                         │
       │                                         │ 1. User saves config
       │                                         │    (device_config.py)
       │                                         │
       │                                         │ 2. device_config_db.py
       │                                         │    saves to InfluxDB
       │                                         │
       │                                         │ 3. mqtt_client.py
       │                                         │    .publish_config()
       │                                         │
       │ 4. Receive:                             │
       │    Dev/Checksum/NAD-6623                │
       │<────────────────────────────────────────│
       │    {complete config JSON}               │
       │    (retain=true, so device gets it     │
       │     even if offline)                    │
       │                                         │
       │ 5. Device updates configuration         │
       │                                         │
       │ 6. (Optional) Publish:                  │
       │    Dev/ConfigACK/NAD-6623               │
       │────────────────────────────────────────>│
       │    {"status": "success"}                │
       │                                         │
```

---

## ✅ Code Verification

### InfluxDB 2.x Compatibility Checklist

#### `device_info_service.py`
- ✅ Uses `InfluxDBClient` (correct for 2.x)
- ✅ Uses `query_api.query()` for Flux queries
- ✅ Uses `write_api.write()` for writes
- ✅ All queries use Flux syntax (no SQL)
- ✅ Default URL: `http://influxdb:8086` (Self-Hosted)
- ✅ Uses `org` and `bucket` parameters correctly
- ✅ No Cloud-specific APIs
- ✅ Comments mention "Self-Hosted InfluxDB 2.x"

#### `mqtt_client.py`
- ✅ Uses standard `paho-mqtt` library
- ✅ No database queries (MQTT only)
- ✅ Correct topic structure
- ✅ Proper callback mechanism
- ✅ Message deduplication logic

### Topic Configuration Verification

#### Server Subscriptions (`mqtt_client.py` lines 65-68):
```python
self.client.subscribe(self.topic_device_data)      # iotnarad/devices/+/data
self.client.subscribe(self.topic_device_status)    # iotnarad/devices/+/status
self.client.subscribe(self.topic_device_init_reg)  # Dev/Init/Reg/#
self.client.subscribe(self.topic_device_config_ack) # Dev/ConfigACK/#
```
✅ **Correct** - All necessary topics subscribed

#### Server Publications:
```python
# Configuration (line 225)
topic = f"{self.topic_device_checksum}/{device_id}"  # Dev/Checksum/<Device ID>

# Acknowledgment (line 269)
topic = f"Dev/Ack/{serial_number}"  # Dev/Ack/<Device ID>

# Commands (line 237)
topic = f"iotnarad/devices/{device_id}/cmd"  # iotnarad/devices/<Device ID>/cmd
```
✅ **Correct** - All topics match expected structure

---

## 📊 InfluxDB Data Structure

### Measurement: `Device_info`

**Purpose:** Store device registration and metadata

**Structure:**
```
Measurement: Device_info
Tags:
  - Sr_No: Device Serial Number (e.g., "NAD-6623")
Fields:
  - Owner: Owner name (e.g., "Xaptronics")
  - Device_Name: Device name (e.g., "Production Device 1")
  - Date_Of_Register: Registration date (e.g., "2025-11-18")
Time:
  - _time: Timestamp (nanoseconds precision)
```

**Example Point:**
```python
Point("Device_info")
    .tag("Sr_No", "NAD-6623")
    .field("Owner", "Xaptronics")
    .field("Device_Name", "Production Device 1")
    .field("Date_Of_Register", "2025-11-18")
    .time(datetime.utcnow(), WritePrecision.NS)
```

**Query Example (Flux):**
```flux
from(bucket: "iotnarad-bucket")
|> range(start: -365d)
|> filter(fn: (r) => r._measurement == "Device_info")
|> filter(fn: (r) => r.Sr_No == "NAD-6623")
|> sort(columns: ["_time"], desc: true)
|> limit(n: 1)
```

---

## 🔍 Key Functions Summary

### `mqtt_client.py`

| Function | Purpose | Used For |
|----------|---------|----------|
| `start()` | Connect to broker and start background thread | Initialize MQTT client |
| `publish()` | Generic publish function | Send any message |
| `publish_config()` | Publish device configuration | Send config to hardware |
| `publish_ack()` | Publish acknowledgment | Confirm device registration |
| `publish_command()` | Publish command | Send commands to device |
| `set_data_callback()` | Register callback for data messages | Handle sensor data |
| `set_init_callback()` | Register callback for init messages | Handle device registration |
| `set_status_callback()` | Register callback for status messages | Handle device status |

### `device_info_service.py`

| Function | Purpose | Returns |
|----------|---------|---------|
| `register_device()` | Register new device in database | `bool` (success/failure) |
| `check_serial_number_exists()` | Check if device already exists | `bool` (exists/not exists) |
| `get_device_info()` | Get single device information | `Dict` or `None` |
| `list_all_devices()` | List all device serial numbers | `List[str]` |
| `get_all_devices_info()` | Get all devices with full info | `List[Dict]` |
| `update_device_info()` | Update device metadata | `bool` (success/failure) |

---

## 🚨 Important Notes

### 1. Device ID vs Serial Number
- **Device ID** = **Serial Number** = **Sr_No** (all refer to the same thing)
- Used in MQTT topics: `Dev/Checksum/<Device ID>` where `<Device ID>` is the serial number
- Example: Device with `Sr_No = "NAD-6623"` → Topic: `Dev/Checksum/NAD-6623`

### 2. Configuration Publishing
- Configuration is published with `retain=True` (QoS=1, retain=True)
- This ensures device gets configuration even if it was offline when config was saved
- Device should subscribe to `Dev/Checksum/<its-own-serial-number>`

### 3. Message Deduplication
- `mqtt_client.py` implements duplicate message detection
- Uses MD5 hash of `topic + payload` to detect duplicates
- Prevents processing same message multiple times

### 4. Race Condition Prevention
- `device_info_service.py` has double-check logic in `register_device()`
- Checks if device exists before AND after write operation
- Prevents duplicate device registrations from concurrent messages

### 5. Flux Query Best Practices
- All queries use `range(start: -365d)` for 1-year time window
- Use `filter()` for measurement and tag filtering
- Use `pivot()` to convert long format to wide format when needed
- Use `sort()` and `limit()` to get latest record
- Use `schema.tagValues()` for getting unique tag values

---

## 📝 Summary

### ✅ Status: FULLY UPDATED AND COMPATIBLE

**Both files are correctly configured for:**
- ✅ Self-Hosted InfluxDB 2.x
- ✅ Flux queries (no SQL)
- ✅ Correct MQTT topic structure
- ✅ Proper data flow and message handling

**No changes needed** - Both files are production-ready and match the current architecture.

---

**Document Version:** 1.0  
**Last Review:** November 18, 2025

