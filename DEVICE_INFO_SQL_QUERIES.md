# Device Info - SQL Queries for InfluxDB Cloud Serverless

## Overview
InfluxDB Cloud Serverless (Storage Engine Version 3) SQL syntax use karta hai. Yeh document SQL queries provide karta hai Device_info measurement ke liye.

---

## 📊 SQL Queries

### Query 1: Get Device by Serial Number

**Flux Query:**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Sr_No == "DF5647")
```

**SQL Query:**
```sql
SELECT *
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;
```

### Query 2: Get All Devices

**Flux Query:**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
```

**SQL Query:**
```sql
SELECT DISTINCT "Sr_No", 
       "Owner", 
       "Date_Of_Register", 
       "Device_Name",
       time
FROM "Device_info"
WHERE time > now() - interval '1 year'
ORDER BY time DESC;
```

### Query 3: Check if Serial Number Exists

**Flux Query:**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Sr_No == "DF5647")
  |> limit(n: 1)
```

**SQL Query:**
```sql
SELECT COUNT(*) as count
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year';
```

### Query 4: Get Latest Device Info

**Flux Query:**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Sr_No == "DF5647")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
```

**SQL Query:**
```sql
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;
```

### Query 5: List All Unique Serial Numbers

**Flux Query:**
```flux
import "influxdata/influxdb/schema"

schema.tagValues(
  bucket: "iot_data_gcp",
  tag: "Sr_No",
  predicate: (r) => r._measurement == "Device_info",
  start: -365d
)
```

**SQL Query:**
```sql
SELECT DISTINCT "Sr_No"
FROM "Device_info"
WHERE time > now() - interval '1 year'
ORDER BY "Sr_No";
```

### Query 6: Count Registered Devices

**Flux Query:**
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> group(columns: ["Sr_No"])
  |> count()
```

**SQL Query:**
```sql
SELECT COUNT(DISTINCT "Sr_No") as total_devices
FROM "Device_info"
WHERE time > now() - interval '1 year';
```

### Query 7: Get Devices by Owner

**SQL Query:**
```sql
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Owner" = 'Unassigned'
  AND time > now() - interval '1 year'
ORDER BY time DESC;
```

### Query 8: Get Devices Registered Today

**SQL Query:**
```sql
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Date_Of_Register" = CURRENT_DATE
  AND time > now() - interval '1 year'
ORDER BY time DESC;
```

### Query 9: Get Devices Registered in Date Range

**SQL Query:**
```sql
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Date_Of_Register" >= '2024-01-01'
  AND "Date_Of_Register" <= '2024-01-31'
  AND time > now() - interval '1 year'
ORDER BY time DESC;
```

### Query 10: Get Unassigned Devices

**SQL Query:**
```sql
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Owner" = 'Unassigned'
  AND time > now() - interval '1 year'
ORDER BY "Date_Of_Register" DESC;
```

---

## 🔍 Using SQL in InfluxDB Cloud UI

### Step 1: Open Data Explorer
1. InfluxDB Cloud UI open karein
2. Left sidebar se **"Data Explorer"** click karein

### Step 2: Select Query Language
1. Top par **"Flux"** dropdown se **"SQL"** select karein

### Step 3: Enter SQL Query
1. Query editor mein SQL query paste karein
2. Example:
   ```sql
   SELECT *
   FROM "Device_info"
   WHERE "Sr_No" = 'DF5647'
     AND time > now() - interval '1 year'
   ORDER BY time DESC
   LIMIT 1;
   ```

### Step 4: Run Query
1. **"Submit"** button click karein
2. Results table mein dikhenge

---

## 💻 Using SQL in Python

### Example: Check Serial Number Exists

```python
from app.services.device_info_service import DeviceInfoService

service = DeviceInfoService()

# Using service method (recommended)
exists = service.check_serial_number_exists("DF5647")

# Or using direct SQL query
query = '''
SELECT COUNT(*) as count
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year'
'''

result = service.query_api.query(org=service.org, query=query)
for table in result:
    for record in table.records:
        count = record.get_value()
        exists = count > 0
```

### Example: Get Device Info

```python
query = '''
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name",
       time
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1
'''

result = service.query_api.query(org=service.org, query=query)
for table in result:
    for record in table.records:
        device_info = {
            'Sr_No': record.values.get('Sr_No'),
            'Owner': record.values.get('Owner'),
            'Date_Of_Register': record.values.get('Date_Of_Register'),
            'Device_Name': record.values.get('Device_Name'),
            'timestamp': record.get_time().isoformat()
        }
        print(device_info)
```

---

## 📋 SQL Query Reference

### Common Patterns

#### Pattern 1: Get Latest Record
```sql
SELECT *
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;
```

#### Pattern 2: Check Existence
```sql
SELECT COUNT(*) as count
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year';
```

#### Pattern 3: List All
```sql
SELECT DISTINCT "Sr_No"
FROM "Device_info"
WHERE time > now() - interval '1 year'
ORDER BY "Sr_No";
```

#### Pattern 4: Filter by Field
```sql
SELECT *
FROM "Device_info"
WHERE "Owner" = 'Unassigned'
  AND time > now() - interval '1 year'
ORDER BY time DESC;
```

#### Pattern 5: Date Range
```sql
SELECT *
FROM "Device_info"
WHERE "Date_Of_Register" >= '2024-01-01'
  AND "Date_Of_Register" <= '2024-01-31'
  AND time > now() - interval '1 year'
ORDER BY time DESC;
```

---

## 🔄 Converting Flux to SQL

### Flux → SQL Conversion Guide

| Flux | SQL |
|------|-----|
| `from(bucket: "iot_data_gcp")` | `FROM "Device_info"` |
| `\|> range(start: -365d)` | `WHERE time > now() - interval '1 year'` |
| `\|> filter(fn: (r) => r._measurement == "Device_info")` | `FROM "Device_info"` (already in FROM) |
| `\|> filter(fn: (r) => r.Sr_No == "DF5647")` | `WHERE "Sr_No" = 'DF5647'` |
| `\|> sort(columns: ["_time"], desc: true)` | `ORDER BY time DESC` |
| `\|> limit(n: 1)` | `LIMIT 1` |
| `\|> pivot(...)` | Not needed in SQL (fields are already columns) |
| `\|> count()` | `SELECT COUNT(*)` |
| `\|> distinct()` | `SELECT DISTINCT` |

---

## 📊 Table Structure (SQL View)

### Device_info Table

| Column | Type | Description |
|--------|------|-------------|
| `time` | TIMESTAMP | Record timestamp |
| `Sr_No` | TAG | Serial number (indexed) |
| `Owner` | FIELD | Owner name |
| `Date_Of_Register` | FIELD | Registration date |
| `Device_Name` | FIELD | Device name |

### Example Row

```
time: 2024-01-20T10:30:00Z
Sr_No: DF5647
Owner: Unassigned
Date_Of_Register: 2024-01-20
Device_Name: Unnamed
```

---

## 🚀 Quick Reference

### Most Common Queries

1. **Check if device exists:**
   ```sql
   SELECT COUNT(*) FROM "Device_info" 
   WHERE "Sr_No" = 'DF5647' 
   AND time > now() - interval '1 year';
   ```

2. **Get device info:**
   ```sql
   SELECT * FROM "Device_info" 
   WHERE "Sr_No" = 'DF5647' 
   AND time > now() - interval '1 year'
   ORDER BY time DESC LIMIT 1;
   ```

3. **List all devices:**
   ```sql
   SELECT DISTINCT "Sr_No" FROM "Device_info" 
   WHERE time > now() - interval '1 year'
   ORDER BY "Sr_No";
   ```

4. **Count devices:**
   ```sql
   SELECT COUNT(DISTINCT "Sr_No") FROM "Device_info" 
   WHERE time > now() - interval '1 year';
   ```

---

## 📝 Notes

1. **Time Range**: Always use `time > now() - interval '1 year'` for recent data
2. **Tags vs Fields**: `Sr_No` is a TAG (indexed), others are FIELDS
3. **Case Sensitivity**: Column names are case-sensitive in SQL
4. **Quotes**: Use single quotes for string values: `'DF5647'`
5. **Double Quotes**: Use double quotes for column names: `"Sr_No"`

---

## 🔗 Related Files

- `app/services/device_info_service.py` - Service implementation
- `DEVICE_INITIALIZATION_GUIDE.md` - Complete guide
- `HOW_TO_VIEW_ALL_TABLES.md` - View tables guide

