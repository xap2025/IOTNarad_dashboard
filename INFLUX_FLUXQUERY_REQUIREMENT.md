# ⚠️ IMPORTANT: Flux Queries Required

## Database Configuration
- **Database:** Self-Hosted InfluxDB 2.x (Local Docker Container)
- **Query Language:** Flux (NOT SQL)
- **Flux Support:** ✅ Fully Available
- **DELETE API:** ✅ Fully Available

---

## ✅ Always Use Flux Queries

### ✅ DO:
- Use Flux syntax for all queries
- Use `from(bucket: "...") |> range(...)`
- Use `|> filter(fn: (r) => r._measurement == "...")`
- Use `|> filter(fn: (r) => r.tag_name == "...")` for tag filtering
- Use `|> sort(columns: ["_time"], desc: true)`
- Use `|> limit(n: 1)` for limiting results
- Use `range(start: -365d)` for 1 year time range
- Use `range(start: -1d)` for 1 day time range
- Access tags via `r.tag_name` (e.g., `r.User_Id`, `r.Sr_No`)
- Access fields via `r._field` and `r._value`

### ❌ DON'T:
- Don't use SQL queries
- Don't use `SELECT`, `FROM`, `WHERE` syntax
- Don't use `interval '1 year'` for time ranges
- Don't use double quotes for column names in SQL style

---

## 📋 Flux Query Examples

### Device_info Measurement
```flux
// Get device by serial number
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Sr_No == "DF5647")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)

// Check if device exists (count)
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Sr_No == "DF5647")
  |> count()

// List all devices (distinct serial numbers)
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> distinct(column: "Sr_No")
  |> sort(columns: ["Sr_No"])

  from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> group()

```

### User_info Measurement
```flux
// Get user by ID
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "User_info")
  |> filter(fn: (r) => r.User_Id == "admin")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)

// Get user by ID and Phone Number
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "User_info")
  |> filter(fn: (r) => r.User_Id == "admin")
  |> filter(fn: (r) => r.Phone_No == "7042703926")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)

// Get all user entries for a user ID
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "User_info")
  |> filter(fn: (r) => r.User_Id == "admin")
  |> sort(columns: ["_time"], desc: true)
```

### Device_Config Measurement
```flux
// Get device configuration by device_id
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config")
  |> filter(fn: (r) => r.device_id == "device123")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

---

## 🔧 Implementation Notes

### Python Client Usage
**Note:** InfluxDB Python client's `query_api` fully supports Flux queries:

```python
from influxdb_client import InfluxDBClient

client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# Flux query
query = '''
    from(bucket: "iot_data_gcp")
      |> range(start: -365d)
      |> filter(fn: (r) => r._measurement == "User_info")
      |> filter(fn: (r) => r.User_Id == "admin")
      |> sort(columns: ["_time"], desc: true)
      |> limit(n: 1)
'''

result = query_api.query(org=org, query=query)

# Process results
for table in result:
    for record in table.records:
        user_id = record.values.get('User_Id')
        password = record.get_value()  # Field value
```

### Best Practices
- **Always use Flux queries** in Python code
- **Use Flux in InfluxDB UI** (Data Explorer)
- **Use `range(start: -365d)`** for 1 year lookback
- **Access tags via `record.values.get('tag_name')`**
- **Access fields via `record.get_value()`** or `record.get_field()`
- **Use `sort(columns: ["_time"], desc: true)`** for latest-first ordering

---

## 🔧 Time Range Options

```flux
// Last 1 day
range(start: -1d)

// Last 7 days
range(start: -7d)

// Last 30 days
range(start: -30d)

// Last 365 days (1 year)
range(start: -365d)

// Specific date range
range(start: 2024-01-01T00:00:00Z, stop: 2024-12-31T23:59:59Z)
```

---

## 🔧 Tag vs Field Access

### Tags (Metadata):
- Stored in `record.values` dictionary
- Access via: `record.values.get('tag_name')`
- Examples: `User_Id`, `Sr_No`, `Company_Name`, `Email_Id`

### Fields (Values):
- Stored as separate records per field
- Access via: `record.get_value()` (gets the field value)
- Access via: `record.get_field()` (gets the field name)
- Examples: `Password`, `Owner`, `Device_Name`

---

## 📝 Remember
- **Always use Flux queries** in code and documentation
- **Provide Flux examples** in guides
- **Use Flux in InfluxDB UI** for testing
- **Self-Hosted InfluxDB 2.x** supports full Flux functionality
- **DELETE API** is available for data cleanup

---

## 🔗 Related Files
- `MIGRATION_TO_SELF_HOSTED_INFLUXDB.md` - Migration guide
- `app/services/user_service.py` - User service with Flux queries
- `app/services/device_info_service.py` - Device service with Flux queries
- `app/services/device_config_db.py` - Config service with Flux queries

