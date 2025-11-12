# Device Initialization Guide

## Overview
Device power ON hote hi server ko serial number bhejta hai, server use register karta hai aur acknowledgment bhejta hai.

---

## 🔄 How It Works

### Step 1: Device Sends Serial Number
**Topic:** `Dev/Init/DF5647`  
**Payload:**
```json
{"SerialNumber": "DF5647"}
```

### Step 2: Server Processes
- Serial number extract karta hai
- Database mein check karta hai
- Agar new hai → Register karta hai
- Agar exists hai → Ignore karta hai

### Step 3: Server Sends Acknowledgment
**Topic:** `Dev/Init/Ack/DF5647`  
**Payload:**
```json
{
  "status": "success",
  "message": "Device registered successfully",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

---

## 📊 Database Structure

**Measurement:** `Device_info`

**Point:**
```python
Point("Device_info")
    .tag("Sr_No", "DF5647")
    .field("Owner", "Unassigned")
    .field("Date_Of_Register", "2024-01-20")
    .field("Device_Name", "Unnamed")
```

---

## 🚀 Quick Test

### PowerShell Command:
```powershell
$payload = '{"SerialNumber": "DF5647"}'
docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t "Dev/Init/DF5647" -m $payload
```

### Check Logs:
```powershell
docker compose logs app --tail 50
```

### Check Database (SQL):
```sql
SELECT * FROM "Device_info" 
WHERE "Sr_No" = 'DF5647' 
AND time > now() - interval '1 year'
```

---

## 📋 Files

**Essential Files:**
- `app/services/device_info_service.py` - Device registration service
- `app/services/mqtt_client.py` - MQTT client (updated)
- `app/main.py` - Main app (updated)

**Test Script:**
- `test_mqtt_publish.ps1` - PowerShell test script

**Documentation:**
- `DEVICE_INIT_GUIDE.md` - This guide
- `DEVICE_INFO_SQL_QUERIES.md` - SQL queries reference

---

## ✅ Verification

1. **Check MQTT Connection:**
   ```powershell
   docker compose logs app | Select-String -Pattern "Connected to MQTT|Subscribed to: Dev/Init"
   ```

2. **Publish Test Message:**
   ```powershell
   $payload = '{"SerialNumber": "DF5647"}'
   docker exec -i iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t "Dev/Init/DF5647" -m $payload
   ```

3. **Check Logs:**
   ```powershell
   docker compose logs app --tail 30 | Select-String -Pattern "Message received|DF5647|registered"
   ```

4. **Check Database:**
   - InfluxDB Cloud UI → Data Explorer → SQL
   - Query: `SELECT * FROM "Device_info" WHERE "Sr_No" = 'DF5647'`

---

## 🔍 Troubleshooting

**Issue: Message not received**
- Check MQTT connection: `docker compose logs app | Select-String -Pattern "Connected"`
- Check subscription: `docker compose logs app | Select-String -Pattern "Subscribed"`

**Issue: Device not registered**
- Check logs for errors
- Verify database connection
- Check serial number format

---

## 📝 Notes

- Serial number format: Any string (e.g., "DF5647")
- Duplicate prevention: Same serial number register nahi hota do baar
- Acknowledgment: Har message ke baad acknowledgment bhejta hai

