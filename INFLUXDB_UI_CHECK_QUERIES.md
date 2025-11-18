# InfluxDB UI - Database Check Queries (Flux)

**Database:** Self-Hosted InfluxDB 2.x  
**UI Access:** `http://34.131.186.225:8086` (GCP VM) or `http://localhost:8086` (Local)

---

## 📋 Table of Contents

1. [Check All Measurements (Tables)](#1-check-all-measurements-tables)
2. [Check Device_info Measurement](#2-check-device_info-measurement)
3. [Check All Devices in Device_info](#3-check-all-devices-in-device_info)
4. [Check Specific Device by Serial Number](#4-check-specific-device-by-serial-number)
5. [Check Device_Config Measurement](#5-check-device_config-measurement)
6. [Check User_info Measurement](#6-check-user_info-measurement)
7. [Check All Buckets](#7-check-all-buckets)

---

## 1. Check All Measurements (Tables)

**Purpose:** Dekhna ke database mein kaun-kaun se measurements (tables) hain

### Flux Query:
```flux
import "influxdata/influxdb/schema"

schema.measurements(bucket: "iotnarad-bucket")
```

**Or simpler version:**
```flux
import "influxdata/influxdb/schema"

schema.measurements(
  bucket: "iotnarad-bucket",
  start: -365d
)
```

**Expected Result:**
- `Device_info`
- `Device_Config`
- `Device_Config_Analog`
- `Device_Config_Digital`
- `Device_Config_Modbus`
- `Device_Config_CANBus`
- `User_info`

---

## 2. Check Device_info Measurement

**Purpose:** Verify karna ke `Device_info` measurement exist karta hai aur usmein data hai

### Flux Query:
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> limit(n: 10)
```
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> limit(n: 10)
  |> group()

**What this shows:**
- Measurement exists ya nahi
- Latest 10 records
- Tags (Sr_No, etc.)
- Fields (Owner, Device_Name, Date_Of_Register)

---

## 3. Check All Devices in Device_info

**Purpose:** Saare registered devices ki list dekha na

### Flux Query:
```flux
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "iotnarad-bucket",
  tag: "Sr_No",
  predicate: (r) => r._measurement == "Device_info",
  start: -365d
)
```

**Expected Result:**
- Unique serial numbers ki list
- Example: `0x7f3b`, `NAD-6623`, `DF5647`, etc.

**Or get full device info:**
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

## 4. Check Specific Device by Serial Number

**Purpose:** Kisi specific device ka data check karna

### Flux Query (Replace `0x7f3b` with your device serial):
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Sr_No == "0x7f3b")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```

**What this shows:**
- Device exists ya nahi
- Latest record ka complete data
- Owner, Device_Name, Date_Of_Register

**For multiple devices at once:**
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Sr_No == "0x7f3b" or r.Sr_No == "NAD-6623" or r.Sr_No == "DF5647")
  |> pivot(rowKey: ["_time", "Sr_No"], columnKey: ["_field"], valueColumn: "_value")
  |> group(columns: ["Sr_No"])
  |> sort(columns: ["_time"], desc: true)
  |> first()
```

---

## 5. Check Device_Config Measurement

**Purpose:** Device configurations check karna

### Check all device configs:
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> group(columns: ["device_id"])
  |> sort(columns: ["_time"], desc: true)
  |> first()
```

**Check specific device config:**
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "0x7f3b")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

**Note:** `config_json` field meh complete JSON stored hai as string.

---

## 6. Check User_info Measurement

**Purpose:** Registered users check karna

### Check all users:
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "User_info")
  |> pivot(rowKey: ["_time", "User_Id"], columnKey: ["_field"], valueColumn: "_value")
  |> group(columns: ["User_Id"])
  |> sort(columns: ["_time"], desc: true)
  |> keep(columns: ["_time", "User_Id", "User_Type", "Company_Name", "Email_Id", "Phone_No"])
  |> first()
```

**Check specific user:**
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "User_info")
  |> filter(fn: (r) => r.User_Id == "admin")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
```

---

## 7. Check All Buckets

**Purpose:** Available buckets list karna

### Flux Query:
```flux
buckets()
```

**Or via UI:**
- Left sidebar meh "Load Data" → "Buckets" section meh dikh jayega

---

## 📊 InfluxDB UI Me Kaise Use Karein

### Step-by-Step:

1. **Open InfluxDB UI:**
   - URL: `http://34.131.186.225:8086` (GCP) ya `http://localhost:8086` (Local)
   - Login karo

2. **Go to Data Explorer:**
   - Left sidebar meh blue "i" icon click karo (Data Explorer)

3. **From Section:**
   - "Search buckets" meh `iotnarad-bucket` type karo
   - Bucket select karo

4. **Filter Section (Optional):**
   - "_measurement" dropdown se measurement select karo
   - Example: `Device_info`

5. **Script Editor:**
   - "SCRIPT EDITOR" button click karo
   - Upar diye gaye Flux queries paste karo
   - "SUBMIT" button click karo

6. **View Results:**
   - Table view meh data dikhega
   - Graph view meh visualization dikhega

---

## 🔍 Quick Verification Queries

### Check if Device Registered:
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Sr_No == "0x7f3b")
  |> count()
```

**Result:**
- `0` = Device not registered
- `> 0` = Device registered (count shows kitne records hain)

---

### Check Latest Registered Devices:
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> pivot(rowKey: ["_time", "Sr_No"], columnKey: ["_field"], valueColumn: "_value")
  |> group(columns: ["Sr_No"])
  |> sort(columns: ["_time"], desc: true)
  |> keep(columns: ["_time", "Sr_No", "Owner", "Device_Name", "Date_Of_Register"])
  |> first()
  |> limit(n: 10)
```

---

### Check Data Structure of Device_info:
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> limit(n: 1)
```

**This shows:**
- Tags: `Sr_No`
- Fields: `Owner`, `Device_Name`, `Date_Of_Register`
- Time: `_time`

---

## 📝 Important Notes

### Time Range:
- Queries meh `range(start: -365d)` use kiya gaya hai (1 year)
- Agar koi data nahi dikh raha, time range badhao:
  ```flux
  |> range(start: -2y)  // 2 years
  ```

### Pivot:
- InfluxDB meh fields long format meh store hote hain
- `pivot()` use karke wide format meh convert karte hain
- Har field alag row meh aata hai, pivot se ek record meh combine hota hai

### Tags vs Fields:
- **Tags:** `Sr_No`, `device_id`, `User_Id` (indexed, filtering meh fast)
- **Fields:** `Owner`, `Device_Name`, `Password` (values, searchable)

---

## ✅ Verification Checklist

Device registration verify karne ke liye:

1. ✅ **Check measurement exists:**
   ```flux
   schema.measurements(bucket: "iotnarad-bucket")
   ```
   → `Device_info` list meh hona chahiye

2. ✅ **Check device serial number:**
   ```flux
   schema.tagValues(
     bucket: "iotnarad-bucket",
     tag: "Sr_No",
     predicate: (r) => r._measurement == "Device_info",
     start: -365d
   )
   ```
   → Apka serial number (`0x7f3b`) list meh hona chahiye

3. ✅ **Check device data:**
   ```flux
   from(bucket: "iotnarad-bucket")
     |> range(start: -24h)
     |> filter(fn: (r) => r._measurement == "Device_info")
     |> filter(fn: (r) => r.Sr_No == "0x7f3b")
     |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
   ```
   → Device ka complete info dikhna chahiye

---

**Document Version:** 1.0  
**Last Updated:** November 18, 2025

