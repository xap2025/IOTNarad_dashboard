# 🔍 Code Query Analysis - Issues Found

## 📊 Current Query Structure

### **Query 1: `get_realtime_data()` - Lines 184-192**

```flux
from(bucket: "iot_data_gcp")
|> range(start: -2h)
|> filter(fn: (r) => r._measurement == "Realtime_Data")
|> filter(fn: (r) => r.device_id == "8C4B144D3274")
|> filter(fn: (r) => r.parameter_name == "pump")
|> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
|> sort(columns: ["_time"], desc: false)
```

**Issues:**
1. ❌ **`pivot()` operation** - Type conflicts cause kar sakta hai
2. ❌ **No `_field` filter** - All fields process ho rahe hain
3. ⚠️ **Type conflict risk** - Boolean aur Integer values mix ho sakte hain

---

### **Query 2: `get_latest_value()` - Lines 237-245**

```flux
from(bucket: "iot_data_gcp")
|> range(start: -7d)
|> filter(fn: (r) => r._measurement == "Realtime_Data")
|> filter(fn: (r) => r.device_id == "8C4B144D3274")
|> filter(fn: (r) => r.parameter_name == "pump")
|> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
|> sort(columns: ["_time"], desc: true)
|> limit(n: 1)
```

**Same Issues:**
1. ❌ **`pivot()` operation** - Type conflicts
2. ❌ **No `_field` filter**

---

## ✅ Recommended Fix

### **Fix 1: Add `_field` Filter Before Pivot**

```flux
from(bucket: "iot_data_gcp")
|> range(start: -2h)
|> filter(fn: (r) => r._measurement == "Realtime_Data")
|> filter(fn: (r) => r.device_id == "8C4B144D3274")
|> filter(fn: (r) => r.parameter_name == "pump")
|> filter(fn: (r) => r._field == "value")  # ✅ ADD THIS
|> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
|> sort(columns: ["_time"], desc: false)
```

### **Fix 2: Remove Pivot (Better Approach)**

```flux
from(bucket: "iot_data_gcp")
|> range(start: -2h)
|> filter(fn: (r) => r._measurement == "Realtime_Data")
|> filter(fn: (r) => r.device_id == "8C4B144D3274")
|> filter(fn: (r) => r.parameter_name == "pump")
|> filter(fn: (r) => r._field == "value")  # ✅ Filter field first
|> sort(columns: ["_time"], desc: false)
```

**Then access value directly:**
```python
value = record.get_value()  # Instead of record.values.get("value")
```

---

## 🎯 Current Code Issues

### **Issue 1: Pivot Without Field Filter**

**Location:** `app/services/realtime_data_db.py` - Line 190

**Problem:**
- `pivot()` operation sabhi fields ko process karta hai
- Agar koi aur field hai (boolean type), type conflict ho sakta hai
- `_field == "value"` filter missing hai

**Fix:**
```python
# Add before pivot:
|> filter(fn: (r) => r._field == "value")
```

---

### **Issue 2: Value Access After Pivot**

**Location:** `app/services/realtime_data_db.py` - Line 204

**Current:**
```python
"value": record.values.get("value")  # After pivot
```

**Problem:**
- Pivot ke baad structure change ho jata hai
- Type conflicts ho sakte hain

**Better:**
```python
"value": record.get_value()  # Direct access, no pivot needed
```

---

## 📋 Recommended Code Changes

### **Change 1: `get_realtime_data()` - Remove Pivot**

```python
# Flux query WITHOUT pivot
query = f'''
    from(bucket: "{self.bucket}")
    |> range(start: {range_start})
    |> filter(fn: (r) => r._measurement == "Realtime_Data")
    |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
    |> filter(fn: (r) => r.parameter_name == "{escaped_param_name}")
    |> filter(fn: (r) => r._field == "value")  # ✅ ADD THIS
    |> sort(columns: ["_time"], desc: false)
'''

# Access value directly
for record in table.records:
    data_points.append({
        "timestamp": record.get_time(),
        "value": record.get_value()  # ✅ Direct access
    })
```

### **Change 2: `get_latest_value()` - Remove Pivot**

```python
# Flux query WITHOUT pivot
query = f'''
    from(bucket: "{self.bucket}")
    |> range(start: -7d)
    |> filter(fn: (r) => r._measurement == "Realtime_Data")
    |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
    |> filter(fn: (r) => r.parameter_name == "{escaped_param_name}")
    |> filter(fn: (r) => r._field == "value")  # ✅ ADD THIS
    |> sort(columns: ["_time"], desc: true)
    |> limit(n: 1)
'''

# Access value directly
value = record.get_value()  # ✅ Direct access
```

---

## ⚠️ Why This Matters

1. **Type Conflicts:** `pivot()` operation mixed types handle nahi kar sakta
2. **Performance:** Field filter pehle lagane se faster queries
3. **Reliability:** Direct value access more reliable hai

---

**Last Updated:** January 23, 2026

