# ⚠️ IMPORTANT: SQL Queries Required

## Database Configuration
- **Database:** InfluxDB Cloud Serverless (Storage Engine Version 3)
- **Query Language:** SQL (NOT Flux)
- **Flux Support:** NOT Available

---

## ✅ Always Use SQL Queries

### ✅ DO:
- Use SQL syntax for all queries
- Use `SELECT`, `FROM`, `WHERE`, `ORDER BY`, `LIMIT`
- Use `interval '1 year'` for time ranges
- Use double quotes for column names: `"Sr_No"`, `"Owner"`
- Use single quotes for string values: `'DF5647'`

### ❌ DON'T:
- Don't use Flux queries
- Don't use `from(bucket: "...") |> range(...)`
- Don't use `|> filter(...)` syntax

---

## 📋 SQL Query Examples

### Device_info Table
```sql
-- Get device by serial number
SELECT * FROM "Device_info" 
WHERE "Sr_No" = 'DF5647' 
AND time > now() - interval '1 year'
ORDER BY time DESC LIMIT 1;

-- Check if device exists
SELECT COUNT(*) FROM "Device_info" 
WHERE "Sr_No" = 'DF5647' 
AND time > now() - interval '1 year';

-- List all devices
SELECT DISTINCT "Sr_No" FROM "Device_info" 
WHERE time > now() - interval '1 year'
ORDER BY "Sr_No";
```

### User_info Table
```sql
-- Get user by ID
SELECT * FROM "User_info" 
WHERE "User_Id" = 'admin' 
AND time > now() - interval '1 year'
ORDER BY time DESC LIMIT 1;
```

---

## 🔧 Implementation Notes

### Python Client Limitation
**Note:** InfluxDB Python client's `query_api` primarily supports Flux. For SQL queries:
- Use InfluxDB Cloud UI for SQL queries
- Or use REST API for direct SQL execution
- Python code mein Flux queries use ho sakte hain (client limitation), but documentation mein SQL format provide karein

### Best Practice
- Documentation mein hamesha SQL format provide karein
- InfluxDB Cloud UI mein SQL queries use karein
- Python code mein Flux use ho sakta hai (client limitation), but SQL equivalent documentation mein mention karein

---

## 📝 Remember
- **Always document SQL queries** in guides
- **Provide SQL examples** in documentation
- **Use SQL in InfluxDB Cloud UI** for testing
- **Note Flux limitation** in Python code comments

---

## 🔗 Related Files
- `DEVICE_INFO_SQL_QUERIES.md` - SQL queries reference
- `SQL_QUERIES_FOR_DEVICE_INFO.sql` - SQL queries file

