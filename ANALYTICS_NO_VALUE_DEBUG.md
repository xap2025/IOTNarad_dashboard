# 🔍 Analytics Page "No Value" Debugging Guide

## 🎯 Problem

MQTT topic `RTD/#` par data aa raha hai, lekin Analytics page par:
- ❌ Real-time values show nahi ho rahe
- ❌ Graphs update nahi ho rahe
- ❌ Sab charts mein "No value" dikh raha hai

---

## 📊 Your MQTT Data

```
RTD/8C4B144D3274 {
    "type": "Modbus",
    "value": {
        "Conductivity": 391,
        "Ph": 56,
        "Humidity": 456,
        "Air_Temp": 271,
        "moisture": 635,
        "Soil_Temp": 244
    }
}
```

**Expected:** Analytics page par yeh 6 parameters dikhne chahiye with their values.

---

## 🔍 Step-by-Step Debugging

### **Step 1: Check if Data is Being Saved to Database**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "Writing to InfluxDB\|Successfully saved RTD\|FAILED to save"
```

**Expected Output:**
```
💾 Writing to InfluxDB: device=8C4B144D3274, type=Modbus, param='Conductivity', value=391
✅ Successfully saved RTD: 8C4B144D3274/Modbus/Conductivity = 391
```

**If NOT seeing "Successfully saved":**
- ❌ Data database mein save nahi ho raha
- Check for errors: `docker logs iotnarad_app | grep -i "error.*rtd\|failed.*save"`
- Problem: Database connection issue ya data saving logic issue

---

### **Step 2: Check Parameter Names Match**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "Loaded.*parameter\|Parameter list"
```

**Expected Output:**
```
✅ Loaded 6 parameter(s) (including historical) for device 8C4B144D3274
   Parameter list: ['Conductivity', 'Ph', 'Humidity', 'Air_Temp', 'moisture', 'Soil_Temp']
```

**If Parameter names don't match:**
- ❌ Config mein names: "Conductivity", "Ph", etc.
- ❌ Data mein names: "Conductivity", "Ph", etc.
- **Check:** Exact match required (case-sensitive, spaces matter)

**Common Issues:**
- Config: "Conductivity " (trailing space) vs Data: "Conductivity" (no space)
- Config: "ph" (lowercase) vs Data: "Ph" (mixed case)
- Config: "Air Temp" (space) vs Data: "Air_Temp" (underscore)

---

### **Step 3: Check Active Periods Filtering**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "active period\|Skipping parameter\|valid parameter"
```

**Expected Output:**
```
✅ Parameter 'Conductivity' is valid (has overlapping active period)
✅ Filtered to 6 valid parameter(s) out of 6 total
```

**If seeing "Skipping parameter":**
- ❌ Active periods filtering parameters ko remove kar rahi hai
- Check: `docker logs iotnarad_app | grep -i "Skipping parameter"`

**Common Issue:**
- MODBUS config was saved BEFORE time range
- Active period doesn't overlap with current time range
- Solution: Check MODBUS config save timestamp

---

### **Step 4: Check Data Query**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "Querying data\|Data query result\|data point"
```

**Expected Output:**
```
🔍 Querying data for 6 parameter(s): ['Conductivity', 'Ph', ...]
📊 Data query result: 6 parameter(s) have data
   'Conductivity': 120 data point(s)
   'Ph': 120 data point(s)
```

**If seeing "0 data point(s)":**
- ❌ Database query se data nahi mil raha
- Check: Parameter names exact match ho rahe hain ya nahi
- Check: Time range correct hai ya nahi

---

### **Step 5: Check Analytics Callback Trigger**

**Terminal Command:**
```bash
docker logs iotnarad_app -f | grep -i "Analytics callback triggered"
```

**Expected Output:**
```
🔄 Analytics callback triggered: n_intervals=1, device_id=8C4B144D3274, enabled_params_count=7
```

**If NOT seeing callback triggers:**
- ❌ Refresh interval (5 seconds) kaam nahi kar raha
- Check: `analytics-refresh-interval` component working hai ya nahi

---

## 🎯 Most Likely Issues

### **Issue 1: Parameter Names Don't Match Exactly**

**Problem:**
- MODBUS config mein variable names: "Conductivity", "Ph", etc.
- Data mein parameter names: "Conductivity", "Ph", etc.
- **But:** Exact match required (case, spaces, special characters)

**Solution:**
1. Check MODBUS config variable names:
   ```bash
   # Check what's in database
   docker exec -it iotnarad_influxdb influx query --org iot-narad-gcp --bucket iot_data_gcp '
     from(bucket: "iot_data_gcp")
     |> range(start: -7d)
     |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
     |> filter(fn: (r) => r.device_id == "8C4B144D3274")
     |> filter(fn: (r) => r.config_type == "slave_device")
     |> keep(columns: ["variable_name"])
     |> distinct(column: "variable_name")
   '
   ```

2. Compare with MQTT data parameter names
3. Ensure exact match (case-sensitive)

---

### **Issue 2: Active Periods Filtering Removing Parameters**

**Problem:**
- MODBUS config was saved BEFORE time range
- Active period doesn't overlap with current time range
- Parameters get filtered out

**Solution:**
- Check MODBUS config save timestamp
- If config saved before time range, active_period should be (start_time, end_time)
- Verify active_periods are being set correctly

---

### **Issue 3: Data Not Being Saved**

**Problem:**
- MQTT data aa raha hai
- But database mein save nahi ho raha

**Check:**
```bash
docker logs iotnarad_app | grep -i "Real-time data received\|Attempting to save RTD\|Successfully saved RTD"
```

**If NOT seeing "Successfully saved":**
- Check database connection
- Check for errors in logs
- Verify InfluxDB is running

---

## 🔧 Quick Fixes

### **Fix 1: Check Database Connection**

```bash
docker logs iotnarad_app | grep -i "Real-Time Data DB Service connected"
```

**Expected:**
```
✅ Real-Time Data DB Service connected to InfluxDB: http://influxdb:8086
```

---

### **Fix 2: Verify Data is in Database**

```bash
docker exec -it iotnarad_influxdb influx query --org iot-narad-gcp --bucket iot_data_gcp '
  from(bucket: "iot_data_gcp")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "Realtime_Data")
  |> filter(fn: (r) => r.device_id == "8C4B144D3274")
  |> filter(fn: (r) => r.parameter_name == "Conductivity")
  |> limit(n: 5)
'
```

**Expected:** Should show recent data points

---

### **Fix 3: Check Parameter Names in Config**

```bash
docker exec -it iotnarad_influxdb influx query --org iot-narad-gcp --bucket iot_data_gcp '
  from(bucket: "iot_data_gcp")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
  |> filter(fn: (r) => r.device_id == "8C4B144D3274")
  |> filter(fn: (r) => r.config_type == "slave_device")
  |> keep(columns: ["_time", "variable_name"])
  |> distinct(column: "variable_name")
  |> sort(columns: ["_time"], desc: true)
'
```

**Expected:** Should show variable names like "Conductivity", "Ph", etc.

---

## 📝 Summary

**Check in Order:**
1. ✅ Data database mein save ho raha hai ya nahi
2. ✅ Parameter names exact match ho rahe hain ya nahi
3. ✅ Active periods filtering parameters ko remove kar rahi hai ya nahi
4. ✅ Analytics callback trigger ho raha hai ya nahi
5. ✅ Data query se data mil raha hai ya nahi

**Most Likely Issue:**
- 🔴 **Parameter names don't match exactly** (case, spaces, special characters)
- 🟡 **Active periods filtering** removing valid parameters
- 🟢 **Data not being saved** (less likely, but check)

---

## 🚀 Next Steps

1. Run debugging commands above
2. Check logs for errors
3. Verify parameter names match exactly
4. Check active periods are correct
5. Verify data is in database

