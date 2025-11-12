# SQL Queries Reference - InfluxDB Cloud Serverless (v3)

## ⚠️ IMPORTANT
**Database:** InfluxDB Cloud Serverless (Storage Engine Version 3)  
**Query Language:** SQL (NOT Flux)  
**Flux Support:** NOT Available

---

## 📊 Common SQL Queries

### Device_info Table

#### Get Device by Serial Number
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

#### Check if Device Exists
```sql
SELECT COUNT(*) as count
FROM "Device_info"
WHERE "Sr_No" = 'DF5647'
  AND time > now() - interval '1 year';
```

#### List All Devices
```sql
SELECT DISTINCT "Sr_No"
FROM "Device_info"
WHERE time > now() - interval '1 year'
ORDER BY "Sr_No";
```

#### Get Unassigned Devices
```sql
SELECT "Sr_No",
       "Owner",
       "Date_Of_Register",
       "Device_Name"
FROM "Device_info"
WHERE "Owner" = 'Unassigned'
  AND time > now() - interval '1 year'
ORDER BY time DESC;
```

---

### User_info Table

#### Get User by ID
```sql
SELECT *
FROM "User_info"
WHERE "User_Id" = 'admin'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;
```

#### Check if User Exists
```sql
SELECT COUNT(*) as count
FROM "User_info"
WHERE "User_Id" = 'admin'
  AND time > now() - interval '1 year';
```

#### List All Users
```sql
SELECT DISTINCT "User_Id"
FROM "User_info"
WHERE time > now() - interval '1 year'
ORDER BY "User_Id";
```

---

### Device_Config Table

#### Get Device Configuration
```sql
SELECT *
FROM "Device_Config"
WHERE "device_id" = 'esp32_gw_01'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;
```

---

## 🔧 Using SQL in InfluxDB Cloud UI

1. Open **Data Explorer**
2. Select **SQL** (not Flux) from dropdown
3. Paste SQL query
4. Click **Submit**

---

## 📝 Notes

- Always use `interval '1 year'` for time range
- Use double quotes for column names: `"Sr_No"`
- Use single quotes for string values: `'DF5647'`
- Use `ORDER BY time DESC` for latest records
- Use `LIMIT 1` for single record

---

## 🔗 Related Files

- `DEVICE_INFO_SQL_QUERIES.md` - Detailed SQL queries
- `SQL_QUERIES_FOR_DEVICE_INFO.sql` - SQL queries file
- `IMPORTANT_SQL_REQUIREMENT.md` - SQL requirement reminder

