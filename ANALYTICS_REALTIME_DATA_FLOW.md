# 📊 Analytics Page - Real-Time Data Flow Explanation

## 🎯 Overview

Yeh document explain karta hai ki Analytics page par real-time data kaha aur kaise save hota hai, aur kaun-kaun se callbacks trigger hote hain.

---

## 🔄 Complete Data Flow

```
Device (Hardware) 
  ↓
MQTT Topic: RTD/<Device ID>
  ↓
MQTT Broker receives message
  ↓
MQTT Client Service (_on_message callback)
  ↓
on_realtime_data_received() callback (main.py)
  ↓
RealtimeDataDBService.save_realtime_data()
  ↓
InfluxDB Database (Self-Hosted)
  ↓
Analytics Page (5-second interval)
  ↓
update_analytics_charts() callback
  ↓
RealtimeDataDBService.get_realtime_data()
  ↓
UI Charts Update
```

---

## 💾 Data Save Kaha Hota Hai?

### **Database: InfluxDB 2.x (Self-Hosted)**

- **Location**: Docker container (`influxdb:8086`)
- **Bucket**: `iotnarad-bucket`
- **Organization**: `iotnarad`
- **Measurement**: `Realtime_Data`

### **Data Structure:**

```python
Point("Realtime_Data")
  .tag("device_id", device_id)           # Device Serial Number
  .tag("data_type", data_type)            # Analog/Digital/Modbus/Canbus
  .tag("parameter_name", parameter_name)   # Parameter name (e.g., "current", "voltage")
  .field("value", field_value)            # Actual numeric value
  .time(timestamp, WritePrecision.NS)     # Timestamp
```

**Example:**
- `device_id`: "DEV001"
- `data_type`: "Analog"
- `parameter_name`: "Temperature"
- `value`: 25.5
- `timestamp`: 2024-01-15T10:30:45.123456789Z

---

## 🔧 Kaun-Se Callbacks Trigger Hote Hain?

### **1. MQTT Message Receive Callback**

**File**: `app/services/mqtt_client.py`
**Function**: `_on_message()`
**Line**: ~103

**Kya Karta Hai:**
- MQTT broker se message receive karta hai
- Topic check karta hai (`RTD/<Device ID>`)
- Device ID extract karta hai
- `realtime_data_callback` ko call karta hai

**Code:**
```python
elif topic.startswith('RTD/'):
    rtd_device_id = topic.split('/')[-1]
    if self.realtime_data_callback:
        self.realtime_data_callback(rtd_device_id, data)
```

---

### **2. Real-Time Data Processing Callback**

**File**: `app/main.py`
**Function**: `on_realtime_data_received()`
**Line**: ~1227

**Kya Karta Hai:**
1. **Data Extract**: `type` aur `value` extract karta hai
2. **Data Normalize**: Data type ko normalize karta hai (Analog/Digital/Modbus/Canbus)
3. **Timestamp Generate**: Current UTC timestamp banata hai
4. **Database Save**: Har parameter ko InfluxDB mein save karta hai
5. **Logging**: Success/failure log karta hai

**Important Steps:**
```python
# Step 1: Extract data
data_type = data.get('type', 'Unknown')
values = data.get('value', {})

# Step 2: Normalize type
normalized_type = data_type.strip()
# Converts: "analog" → "Analog", "digital" → "Digital"

# Step 3: Save each parameter
for parameter_name, parameter_value in values.items():
    realtime_data_db_service.save_realtime_data(
        device_id=device_id,
        data_type=normalized_type,
        parameter_name=clean_param_name,
        parameter_value=parameter_value,
        timestamp=timestamp
    )
```

**Callback Registration:**
```python
# Line 1337 in main.py
mqtt_service.set_realtime_data_callback(on_realtime_data_received)
```

---

### **3. Database Save Service**

**File**: `app/services/realtime_data_db.py`
**Function**: `save_realtime_data()`
**Line**: ~50

**Kya Karta Hai:**
1. **Value Conversion**: 
   - Boolean → Integer (true=1, false=0)
   - String → Number (if possible)
   - Mixed types ko handle karta hai

2. **InfluxDB Point Create**:
   - Tags: `device_id`, `data_type`, `parameter_name`
   - Field: `value` (numeric)
   - Timestamp: UTC time with nanosecond precision

3. **Write to Database**:
   - Synchronous write API use karta hai
   - Error handling aur retry logic

**Code:**
```python
# Convert boolean to integer for Digital data
if isinstance(parameter_value, bool):
    field_value = 1 if parameter_value else 0

# Create Point
point = Point("Realtime_Data") \
    .tag("device_id", device_id) \
    .tag("data_type", data_type) \
    .tag("parameter_name", parameter_name) \
    .field("value", field_value) \
    .time(timestamp, WritePrecision.NS)

# Write to InfluxDB
self.write_api.write(bucket=self.bucket, org=self.org, record=point)
```

---

### **4. Analytics Page Update Callbacks**

#### **A. Device Status Update**

**File**: `app/pages/analytics.py`
**Function**: `update_device_status()`
**Line**: ~340

**Trigger**: 
- `analytics-refresh-interval` (har 5 seconds)
- `analytics-device-store` (device change par)

**Kya Karta Hai:**
- Device ka status check karta hai (Running/Not Running)
- Last 1 hour mein data hai ya nahi check karta hai
- Status badge update karta hai

**Code:**
```python
@callback(
    Output('device-status-container', 'children'),
    [
        Input('analytics-refresh-interval', 'n_intervals'),
        Input('analytics-device-store', 'data'),
    ]
)
def update_device_status(n_intervals, device_id):
    # Query InfluxDB for data in last 1 hour
    # Return "Running" or "Not Running" badge
```

---

#### **B. Charts Update (Main Callback)**

**File**: `app/pages/analytics.py`
**Function**: `update_analytics_charts()`
**Line**: ~419

**Trigger**: 
- `analytics-refresh-interval` (har 5 seconds) ⏱️
- `analytics-time-range-selector` (time range change)
- `analytics-device-store` (device change)
- `analytics-params-store` (parameters change)

**Kya Karta Hai:**
1. **Time Range Calculate**: User-selected time range (1h, 6h, 24h, etc.)
2. **Data Fetch**: Har parameter ke liye historical data fetch karta hai
3. **Latest Value Fetch**: Har parameter ka latest value fetch karta hai
4. **Charts Create**: Plotly graphs banata hai
5. **Live Values Update**: Current values display karta hai

**Code Flow:**
```python
@callback(
    [
        Output({'type': 'analytics-chart', 'parameter': ALL}, 'figure'),
        Output({'type': 'live-value-container', 'parameter': ALL}, 'children'),
    ],
    [
        Input('analytics-refresh-interval', 'n_intervals'),  # ⏱️ Har 5 seconds
        Input('analytics-time-range-selector', 'value'),
        Input('analytics-device-store', 'data'),
        Input('analytics-params-store', 'data'),
    ]
)
def update_analytics_charts(n_intervals, time_range, device_id, enabled_params):
    # Step 1: Calculate time range
    start_time = end_time - timedelta(hours=1)  # For '1h'
    
    # Step 2: Fetch historical data
    for param_name in enabled_params:
        data_points = db_service.get_realtime_data(
            device_id=device_id,
            parameter_name=param_name,
            start_time=start_time,
            end_time=end_time
        )
        
        # Step 3: Fetch latest value
        latest_value = db_service.get_latest_value(
            device_id=device_id,
            parameter_name=param_name
        )
        
        # Step 4: Create chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=values))
        
        # Step 5: Update live value display
        live_value_display = html.Span(latest_value)
```

---

### **5. Database Query Service**

**File**: `app/services/realtime_data_db.py`

#### **A. Get Historical Data**

**Function**: `get_realtime_data()`
**Line**: ~198

**Kya Karta Hai:**
- Flux query banata hai InfluxDB ke liye
- Time range ke according data fetch karta hai
- Data points return karta hai (timestamp + value)

**Query Example:**
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "Realtime_Data")
  |> filter(fn: (r) => r.device_id == "DEV001")
  |> filter(fn: (r) => r.parameter_name == "Temperature")
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: false)
```

---

#### **B. Get Latest Value**

**Function**: `get_latest_value()`
**Line**: ~269

**Kya Karta Hai:**
- Last 7 days mein se latest value fetch karta hai
- Single value return karta hai (most recent)

**Query Example:**
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "Realtime_Data")
  |> filter(fn: (r) => r.device_id == "DEV001")
  |> filter(fn: (r) => r.parameter_name == "Temperature")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

---

## ⏱️ Timing & Intervals

### **Current Implementation:**

1. **MQTT Data Arrival**: 
   - **Immediate**: Jaise hi device se data aata hai
   - **No delay**: Direct database save

2. **Analytics Page Update**:
   - **Interval**: 5 seconds (fixed)
   - **Component**: `dcc.Interval(id='analytics-refresh-interval', interval=5000)`
   - **Trigger**: Har 5 seconds automatically

3. **Device Status Check**:
   - **Interval**: 5 seconds (same as charts)
   - **Check**: Last 1 hour mein data hai ya nahi

---

## 📋 Callback Summary Table

| Callback | File | Trigger | Purpose |
|----------|------|---------|---------|
| `_on_message()` | `mqtt_client.py` | MQTT message receive | MQTT message parse aur callback call |
| `on_realtime_data_received()` | `main.py` | MQTT RTD topic | Data process aur database save |
| `save_realtime_data()` | `realtime_data_db.py` | Called by `on_realtime_data_received()` | InfluxDB mein data write |
| `update_device_status()` | `analytics.py` | 5-second interval | Device status badge update |
| `update_analytics_charts()` | `analytics.py` | 5-second interval | Charts aur live values update |
| `get_realtime_data()` | `realtime_data_db.py` | Called by `update_analytics_charts()` | Historical data fetch |
| `get_latest_value()` | `realtime_data_db.py` | Called by `update_analytics_charts()` | Latest value fetch |

---

## 🔍 Important Notes

### **1. Data Type Conversion:**
- **Digital Data**: Boolean values (true/false) ko integers (1/0) mein convert kiya jata hai
- **Analog Data**: Numeric values as-is save hote hain
- **String Values**: Number mein convert kiye jaate hain (if possible)

### **2. Parameter Name Matching:**
- Parameter names ko **exactly match** karna chahiye
- Extra spaces remove kiye jaate hain: `parameter_name.strip()`
- Database mein jo name save hai, wahi UI mein dikhna chahiye

### **3. Time Range:**
- User time range select kar sakta hai (1h, 6h, 24h, 7d, 30d, 6m, 1y)
- Charts automatically update hote hain selected range ke according

### **4. Error Handling:**
- Database connection errors handle kiye jaate hain
- Type conflicts (422 errors) automatically resolve kiye jaate hain
- Failed saves log kiye jaate hain

---

## 🚀 Future Improvements (Not Yet Implemented)

### **Event-Based Updates:**
- Currently: Fixed 5-second interval
- Planned: SocketIO events se immediate updates
- Status: Documentation mein mentioned hai, but code mein implement nahi hai

**Planned Flow:**
```
MQTT Data → Database Save → SocketIO Event → Immediate UI Update
```

**Current Flow:**
```
MQTT Data → Database Save → Wait 5 seconds → UI Update
```

---

## 📝 Example Logs

### **When Data Arrives:**

```
📊 Real-time data received from device: DEV001
   Full Payload: {"type": "Analog", "value": {"Temperature": 25.5}}
   Data Type: 'Analog'
   Values count: 1
💾 Attempting to save RTD: device=DEV001, type=Analog, param='Temperature', value=25.5
✅ Successfully saved RTD: DEV001/Analog/Temperature = 25.5
✅ Processed 1 real-time data parameters from device DEV001
   Saved: 1, Failed: 0
```

### **When Analytics Updates:**

```
🔄 Analytics callback triggered: n_intervals=10, device_id=DEV001, enabled_params_count=3
🔍 Fetching data for parameter: 'Temperature' (device: DEV001, type: Analog)
   Historical data points: 60
   Latest value: 25.5 (type: <class 'float'>)
✅ Updated 3 charts for device DEV001
```

---

## ✅ Summary

1. **Data Save**: InfluxDB mein `Realtime_Data` measurement mein save hota hai
2. **MQTT Callback**: `on_realtime_data_received()` data receive karta hai
3. **Database Service**: `save_realtime_data()` InfluxDB mein write karta hai
4. **Analytics Updates**: Har 5 seconds `update_analytics_charts()` trigger hota hai
5. **Data Fetch**: `get_realtime_data()` aur `get_latest_value()` database se data fetch karte hain
6. **UI Update**: Charts aur live values automatically update hote hain

**Current Update Frequency**: 5 seconds (fixed interval)
**Data Storage**: InfluxDB (Self-Hosted)
**Data Format**: Time-series data with tags (device_id, data_type, parameter_name)

