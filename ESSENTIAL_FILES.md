# Essential Files - Device Initialization

## ✅ Core Files (Required)

### 1. Service Files
- `app/services/device_info_service.py` - Device registration service
- `app/services/mqtt_client.py` - MQTT client (updated)
- `app/main.py` - Main app (updated with device init callback)

### 2. Test Script
- `test_mqtt_publish.ps1` - Test device initialization

### 3. Documentation
- `DEVICE_INIT_GUIDE.md` - Complete guide
- `DEVICE_INFO_SQL_QUERIES.md` - SQL queries reference

---

## 📋 Quick Usage

### Test Device Initialization:
```powershell
.\test_mqtt_publish.ps1
```

### Check Logs:
```powershell
docker compose logs app --tail 30
```

### Check Database (SQL):
```sql
SELECT * FROM "Device_info" 
WHERE "Sr_No" = 'DF5647' 
AND time > now() - interval '1 year'
```

---

## 🗑️ Deleted Files (Not Needed)

- `test_device_init.py` ❌
- `test_device_init_mqtt.py` ❌
- `DEVICE_INIT_QUICK_START.md` ❌
- `DEBUG_DEVICE_INIT.md` ❌
- `MQTT_TEST_COMMANDS.md` ❌
- `DEVICE_INITIALIZATION_GUIDE.md` ❌ (merged into DEVICE_INIT_GUIDE.md)

---

## 📚 Other Documentation (Keep for Reference)

- `DEVICE_CONFIG_JSON_EXAMPLE.json` - JSON structure example
- `DEVICE_CONFIG_JSON_STRUCTURE.md` - JSON structure details
- `HOW_TO_SAVE_CONFIG_JSON.md` - Save config guide
- `HOW_TO_VIEW_ALL_TABLES.md` - View tables guide
- `SQL_QUERIES_FOR_DEVICE_INFO.sql` - SQL queries file

