# How to View All Tables in InfluxDB

## Overview
Yeh guide explain karta hai ki kaise InfluxDB mein sabhi tables (measurements) ko check karein.

---

## 📊 Method 1: InfluxDB Cloud UI (Easiest)

### Step 1: Open InfluxDB Cloud UI
1. Browser mein InfluxDB Cloud UI open karein
2. Login karein with your credentials
3. URL: `https://cloud2.influxdata.com`

### Step 2: Go to Data Explorer
1. Left sidebar mein **"Data Explorer"** click karein
2. Ya top menu se **"Explore"** → **"Data Explorer"** select karein

### Step 3: Select Bucket
1. Top par **"Bucket"** dropdown se select karein: `iot_data_gcp`
2. Agar bucket nahi dikh raha, to check karein ki sahi org select hai

### Step 4: View All Measurements (Tables)
1. **"Measurement"** dropdown click karein
2. Yeh sab measurements dikhenge:
   - `User_info` - User information
   - `Device_Config` - Device configurations
   - `Device_Config_Analog` - Analog channels
   - `Device_Config_Digital` - Digital channels
   - `Device_Config_MODBUS` - MODBUS configuration
   - `Device_Config_CANBus` - CAN Bus configuration
   - `device_data` - Device sensor data (if any)

### Step 5: Select Measurement and View Data
1. Kisi bhi measurement select karein (e.g., `Device_Config`)
2. **"Submit"** button click karein
3. Data table mein dikhega

---

## 🔍 Method 2: Flux Query in Data Explorer

### Query 1: List All Measurements (Tables)

```flux
import "influxdata/influxdb/schema"

schema.measurements(bucket: "iot_data_gcp")
```

**Steps:**
1. Data Explorer open karein
2. **"Script Editor"** tab select karein
3. Upar wala query paste karein
4. **"Submit"** click karein
5. Result mein sabhi measurements ki list dikhegi

### Query 2: List All Devices in Device_Config

```flux
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "iot_data_gcp",
  tag: "device_id",
  predicate: (r) => r._measurement == "Device_Config",
  start: -365d
)
```

**Result:** Sabhi device IDs jo configurations mein hain

### Query 3: List All Users in User_info

```flux
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "iot_data_gcp",
  tag: "User_Id",
  predicate: (r) => r._measurement == "User_info",
  start: -365d
)
```

**Result:** Sabhi user IDs

### Query 4: View All Data from Device_Config Table

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 100)
```

**Result:** Latest 100 device configurations

### Query 5: View All Analog Channels

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 100)
```

**Result:** Latest 100 analog channel configurations

### Query 6: View All MODBUS Slave Devices

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
  |> filter(fn: (r) => r.config_type == "slave_device")
  |> sort(columns: ["_time"], desc: true)
```

**Result:** Sabhi MODBUS slave devices

### Query 7: View All CAN Bus Messages

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_CANBus")
  |> filter(fn: (r) => r.config_type == "can_message")
  |> sort(columns: ["_time"], desc: true)
```

**Result:** Sabhi CAN Bus messages

### Query 8: Count Records in Each Measurement

```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> group(columns: ["_measurement"])
  |> count()
  |> sort(columns: ["_value"], desc: true)
```

**Result:** Har measurement mein kitne records hain

---

## 💻 Method 3: Python Script

### Script: View All Tables and Data

```python
"""
Script to view all tables (measurements) in InfluxDB
"""
import os
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Configuration
url = os.getenv('INFLUXDB_URL', 'https://us-east-1-1.aws.cloud2.influxdata.com')
token = os.getenv('INFLUXDB_TOKEN', 'T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA==')
org = os.getenv('INFLUXDB_ORG', 'iot-narad-gcp')
bucket = os.getenv('INFLUXDB_BUCKET', 'iot_data_gcp')

# Initialize client
client = InfluxDBClient(url=url, token=token, org=org, timeout=30000)
query_api = client.query_api()

print("=" * 60)
print("InfluxDB Tables (Measurements) Viewer")
print("=" * 60)

# 1. List All Measurements
print("\n📊 Step 1: Listing All Measurements (Tables)")
print("-" * 60)

query = f'''
import "influxdata/influxdb/schema"

schema.measurements(bucket: "{bucket}")
'''

try:
    result = query_api.query(org=org, query=query)
    
    measurements = []
    for table in result:
        for record in table.records:
            measurement = record.get_value()
            measurements.append(measurement)
    
    if measurements:
        print(f"✅ Found {len(measurements)} measurements:")
        for i, measurement in enumerate(measurements, 1):
            print(f"   {i}. {measurement}")
    else:
        print("❌ No measurements found")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Count Records in Each Measurement
print("\n📈 Step 2: Counting Records in Each Measurement")
print("-" * 60)

for measurement in measurements:
    try:
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -365d)
          |> filter(fn: (r) => r._measurement == "{measurement}")
          |> count()
        '''
        
        result = query_api.query(org=org, query=query)
        
        count = 0
        for table in result:
            for record in table.records:
                count = record.get_value()
        
        print(f"   {measurement}: {count} records")
        
    except Exception as e:
        print(f"   {measurement}: Error - {e}")

# 3. View Sample Data from Each Measurement
print("\n📄 Step 3: Viewing Sample Data from Each Measurement")
print("-" * 60)

for measurement in measurements:
    try:
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -365d)
          |> filter(fn: (r) => r._measurement == "{measurement}")
          |> sort(columns: ["_time"], desc: true)
          |> limit(n: 1)
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        result = query_api.query(org=org, query=query)
        
        print(f"\n   📋 {measurement}:")
        for table in result:
            for record in table.records:
                print(f"      Tags: {record.values.get('device_id', 'N/A')}")
                print(f"      Time: {record.get_time()}")
                # Print first few fields
                fields = [k for k in record.values.keys() 
                         if k not in ['_start', '_stop', '_time', '_measurement', 'result', 'table']]
                print(f"      Fields: {fields[:5]}...")  # Show first 5 fields
                break
            break
        
    except Exception as e:
        print(f"   {measurement}: Error - {e}")

# 4. List All Devices in Device_Config
print("\n🔌 Step 4: Listing All Devices in Device_Config")
print("-" * 60)

try:
    query = f'''
    import "influxdata/influxdb/schema"
    
    schema.tagValues(
      bucket: "{bucket}",
      tag: "device_id",
      predicate: (r) => r._measurement == "Device_Config",
      start: -365d
    )
    '''
    
    result = query_api.query(org=org, query=query)
    
    devices = []
    for table in result:
        for record in table.records:
            devices.append(record.get_value())
    
    if devices:
        print(f"✅ Found {len(devices)} devices:")
        for device in devices:
            print(f"   - {device}")
    else:
        print("❌ No devices found")
        
except Exception as e:
    print(f"❌ Error: {e}")

# 5. List All Users in User_info
print("\n👥 Step 5: Listing All Users in User_info")
print("-" * 60)

try:
    query = f'''
    import "influxdata/influxdb/schema"
    
    schema.tagValues(
      bucket: "{bucket}",
      tag: "User_Id",
      predicate: (r) => r._measurement == "User_info",
      start: -365d
    )
    '''
    
    result = query_api.query(org=org, query=query)
    
    users = []
    for table in result:
        for record in table.records:
            users.append(record.get_value())
    
    if users:
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"   - {user}")
    else:
        print("❌ No users found")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Close client
client.close()

print("\n" + "=" * 60)
print("✅ Completed!")
print("=" * 60)
```

### Run Script

```bash
python VIEW_ALL_TABLES.py
```

---

## 🐳 Method 4: Docker Command (Local InfluxDB)

### List All Measurements

```bash
docker exec -i iotnarad_influxdb influx query '
  import "influxdata/influxdb/schema"
  
  schema.measurements(bucket: "iot_data_gcp")
'
```

### View Device_Config Table

```bash
docker exec -i iotnarad_influxdb influx query '
  from(bucket: "iot_data_gcp")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "Device_Config")
    |> limit(n: 10)
'
```

### View User_info Table

```bash
docker exec -i iotnarad_influxdb influx query '
  from(bucket: "iot_data_gcp")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "User_info")
    |> limit(n: 10)
'
```

### Count Records in Each Table

```bash
docker exec -i iotnarad_influxdb influx query '
  from(bucket: "iot_data_gcp")
    |> range(start: -365d)
    |> group(columns: ["_measurement"])
    |> count()
    |> sort(columns: ["_value"], desc: true)
'
```

---

## 📋 Expected Tables (Measurements)

### 1. User_info
- **Purpose**: User information storage
- **Tags**: User_Id, Company_Name, Email_Id, Phone_No, User_Type, status
- **Fields**: Password
- **Usage**: User authentication and management

### 2. Device_Config
- **Purpose**: Complete device configuration JSON
- **Tags**: device_id, device_name, device_type, location
- **Fields**: config_json, version
- **Usage**: Store complete device configuration

### 3. Device_Config_Analog
- **Purpose**: Analog channel configurations
- **Tags**: device_id, channel_type, channel, io_pin, name
- **Fields**: enabled, divider, multiplier, value, min_value, max_value, unit
- **Usage**: Store analog input/output configurations

### 4. Device_Config_Digital
- **Purpose**: Digital channel configurations
- **Tags**: device_id, channel_type, channel, io_pin, name
- **Fields**: enabled, pullup, debounce_ms, initial_state
- **Usage**: Store digital input/output and relay configurations

### 5. Device_Config_MODBUS
- **Purpose**: MODBUS configuration
- **Tags**: device_id, config_type, slave_id, function_code, register_address, data_type, endianness, variable_name
- **Fields**: enabled, baud_rate, data_bits, parity, stop_bits, mode, role, polling_interval_ms, index, register_count
- **Usage**: Store MODBUS settings and slave device configurations

### 6. Device_Config_CANBus
- **Purpose**: CAN Bus configuration
- **Tags**: device_id, config_type, can_id, direction, variable_name, byte_position, data_type, endianness
- **Fields**: enabled, baud_rate, identifier_length, can_mode, filter_mode, filter_id, filter_mask, index, period_ms, data_length, scale_factor, offset
- **Usage**: Store CAN Bus settings, messages, and data mappings

### 7. device_data (Optional)
- **Purpose**: Device sensor data (if devices are sending data)
- **Tags**: device_id, device_type
- **Fields**: Various sensor readings
- **Usage**: Store real-time sensor data

---

## 🔍 Quick Reference Queries

### View All Tables
```flux
import "influxdata/influxdb/schema"
schema.measurements(bucket: "iot_data_gcp")
```

### View Specific Table
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> limit(n: 10)
```

### Count Records
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> count()
```

### List All Devices
```flux
import "influxdata/influxdb/schema"
schema.tagValues(
  bucket: "iot_data_gcp",
  tag: "device_id",
  predicate: (r) => r._measurement == "Device_Config",
  start: -365d
)
```

### List All Users
```flux
import "influxdata/influxdb/schema"
schema.tagValues(
  bucket: "iot_data_gcp",
  tag: "User_Id",
  predicate: (r) => r._measurement == "User_info",
  start: -365d
)
```

---

## 📊 Table Structure Summary

| Measurement | Records | Purpose |
|------------|---------|---------|
| **User_info** | User count | User authentication |
| **Device_Config** | Device count | Complete device configs |
| **Device_Config_Analog** | Channel count | Analog channels |
| **Device_Config_Digital** | Channel count | Digital channels |
| **Device_Config_MODBUS** | Slave count | MODBUS configs |
| **Device_Config_CANBus** | Message count | CAN Bus configs |
| **device_data** | Data points | Sensor data (optional) |

---

## ✅ Verification Steps

1. **Check Connection**
   - InfluxDB Cloud UI open karein
   - Connection status verify karein

2. **List Measurements**
   - Data Explorer → Script Editor
   - Run: `schema.measurements(bucket: "iot_data_gcp")`

3. **View Data**
   - Each measurement select karein
   - Data verify karein

4. **Count Records**
   - Count query run karein
   - Records verify karein

5. **Check Specific Data**
   - Device IDs list karein
   - User IDs list karein
   - Configurations verify karein

---

## 🚀 Quick Start

### Python Script Run Karein

```bash
python VIEW_ALL_TABLES.py
```

### InfluxDB UI Mein Check Karein

1. Data Explorer open karein
2. Bucket select karein: `iot_data_gcp`
3. Measurement dropdown se select karein
4. Data view karein

### Flux Query Run Karein

1. Script Editor open karein
2. Query paste karein
3. Submit click karein
4. Results view karein

---

## 📝 Notes

1. **Time Range**: Always use `-365d` (1 year) for queries
2. **Bucket**: Always use `iot_data_gcp`
3. **Org**: Always use `iot-narad-gcp`
4. **Latest Data**: Sort by `_time` descending
5. **Limits**: Use `limit(n: 100)` for large datasets

---

## 🔗 Related Files

- `VIEW_ALL_TABLES.py` - Python script to view all tables
- `HOW_TO_CHECK_DATABASE.md` - Database check guide
- `DATABASE_DEVICE_CONFIG_STRUCTURE.md` - Database structure
- `EXAMPLE_SAVE_TO_DATABASE.py` - Save example

