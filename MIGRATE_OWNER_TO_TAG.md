# Migrate Owner from FIELD to TAG in Device_info

## ✅ **Approach Approved**

Changing `Owner` from a **FIELD** to a **TAG** in the `Device_info` measurement is the **correct and recommended approach** for the following reasons:

### **Benefits:**

1. ✅ **Better Performance** - Tags are indexed in InfluxDB, making filtering much faster
2. ✅ **Simpler Queries** - Can filter by tag directly BEFORE pivot operation
3. ✅ **Efficient Filtering** - `Owner == User_Id` check works directly without needing pivot first
4. ✅ **Best Practice** - Owner is categorical data (like User_Id), perfect for tags

---

## 📋 **Migration Steps**

### **Step 1: Delete Existing Device_info Measurement**

**Option A: Using InfluxDB UI**

1. Open InfluxDB UI: `http://your-influxdb-url:8086`
2. Go to **Data Explorer**
3. Run this Flux query to see all devices:
   ```flux
   from(bucket: "iot_data_gcp")
     |> range(start: -365d)
     |> filter(fn: (r) => r._measurement == "Device_info")
   ```
4. Go to **Settings** → **Data** → **Measurements**
5. Find `Device_info` measurement and delete it

**Option B: Using InfluxDB CLI (Terminal)**

```bash
# Connect to InfluxDB container
docker exec -it iotnarad_influxdb influx

# Delete all data from Device_info measurement
from(bucket: "iot_data_gcp")
  |> range(start: 1970-01-01T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> drop()

# Or use DELETE API (requires InfluxDB 2.x with DELETE enabled)
```

**Option C: Using DELETE API (PowerShell/Windows)**

```powershell
$INFLUXDB_URL = "http://localhost:8086"
$INFLUXDB_TOKEN = "your-token-here"
$INFLUXDB_ORG = "iot-narad-gcp"
$INFLUXDB_BUCKET = "iot_data_gcp"

# Note: DELETE API may not be available in all InfluxDB versions
# Check: https://docs.influxdata.com/influxdb/v2.7/api/#operation/PostDelete
```

---

### **Step 2: Code Already Updated** ✅

The following files have been updated to use `Owner` as a **TAG**:

1. **`app/services/device_info_service.py`**:
   - ✅ `register_device()` - Now saves `Owner` as `.tag("Owner", ...)` instead of `.field("Owner", ...)`
   - ✅ `update_device_info()` - Now updates `Owner` as tag
   - ✅ `get_all_devices_info()` - Filters by tag BEFORE pivot (more efficient)
   - ✅ `get_device_info()` - Accesses `Owner` as tag from `record.values`

---

### **Step 3: Re-register Devices**

After deleting the old measurement, devices will need to be re-registered:

**Method 1: Automatic (Recommended)**
- Devices will re-register automatically when they send MQTT messages to `Dev/Init/Reg/<Serial Number>`
- New devices will be saved with `Owner` as a tag (defaults to "admin")

**Method 2: Manual Registration**
- Use the dashboard's device registration flow
- Or trigger device initialization via MQTT

**Method 3: Manual Insert via CLI** (if needed for testing)

```bash
docker exec -it iotnarad_influxdb influx write \
  --bucket iot_data_gcp \
  --org iot-narad-gcp \
  --precision ns \
  --format line \
  'Device_info,Sr_No=0x7f3b,Owner=admin Device_Name="Unnamed",Date_Of_Register="2025-11-19"'
```

---

## 🔍 **Updated Schema**

### **Before (Owner as FIELD):**

```python
Point("Device_info") \
    .tag("Sr_No", serial_number) \
    .field("Owner", "admin") \        # ❌ FIELD
    .field("Date_Of_Register", current_date) \
    .field("Device_Name", "Unnamed")
```

### **After (Owner as TAG):**

```python
Point("Device_info") \
    .tag("Sr_No", serial_number) \
    .tag("Owner", "admin") \          # ✅ TAG
    .field("Date_Of_Register", current_date) \
    .field("Device_Name", "Unnamed")
```

---

## 📊 **Updated Flux Queries**

### **Filtering by Owner (Before - Required Pivot First):**

```flux
# ❌ OLD WAY (Owner as field)
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> pivot(...)                       # Must pivot first
  |> filter(fn: (r) => r.Owner == "admin")  # Then filter
```

### **Filtering by Owner (After - Direct Tag Filter):**

```flux
# ✅ NEW WAY (Owner as tag)
from(bucket: "iot_data_gcp")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_info")
  |> filter(fn: (r) => r.Owner == "admin")  # Filter directly (faster!)
  |> pivot(...)                       # Pivot after filter
```

---

## ✅ **Verification Steps**

After migration, verify the changes:

1. **Check Device_info Structure:**
   ```flux
   from(bucket: "iot_data_gcp")
     |> range(start: -365d)
     |> filter(fn: (r) => r._measurement == "Device_info")
     |> limit(n: 1)
   ```
   - Verify `Owner` appears as a tag (not a field)

2. **Test Admin User:**
   - Login as admin
   - Go to Devices page
   - Should see ALL devices in dropdown (no filter)

3. **Test Regular User:**
   - Login as regular user (e.g., User_Id = "user1")
   - Assign a device to that user: `Owner = "user1"`
   - Should see ONLY devices where `Owner == "user1"`

4. **Test Device Registration:**
   - Register a new device via MQTT
   - Verify it saves with `Owner = "admin"` (as tag)
   - Check InfluxDB UI to confirm structure

---

## 🔧 **Device-User Mapping**

After migration, the mapping logic works as:

**Mapping Condition:**
```
Device_info.Owner (TAG) == User_info.User_Id (TAG)
```

**Example:**
- User logs in with `User_Id = "admin"`
- System queries: `filter(fn: (r) => r.Owner == "admin")`
- Returns all devices where `Owner` tag equals "admin"

---

## 📝 **Important Notes**

1. ⚠️ **Existing Data**: All existing `Device_info` data will be deleted. You'll need to re-register devices.

2. ✅ **New Devices**: All newly registered devices will automatically use `Owner` as a tag (defaults to "admin").

3. ✅ **Performance**: Filtering by tag is much faster than filtering by field, especially with many devices.

4. ✅ **Backward Compatibility**: Old code that accessed `Owner` as a field will break. But since you're deleting the old measurement, this is not a concern.

---

## 🚀 **Next Steps**

1. ✅ Code is already updated to use `Owner` as TAG
2. ⏳ **Your Action**: Delete existing `Device_info` measurement from InfluxDB
3. ⏳ **Your Action**: Re-register devices (or wait for automatic registration via MQTT)
4. ✅ **Verify**: Test device dropdown with admin and regular users

After you delete and re-register devices, the "Select Device" dropdown should work correctly! 🎉

