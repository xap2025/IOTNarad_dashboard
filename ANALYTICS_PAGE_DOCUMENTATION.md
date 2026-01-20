# Analytics Page Documentation

## 📋 Overview

Analytics Page एक real-time data visualization page है जो device से आने वाले live data को display करता है। यह page dynamically configured parameters को show करता है और उनका historical data graphs के रूप में display करता है।

---

## 🎯 Main Functionality

### 1. **Real-Time Data Collection**
- Device से MQTT topic `RTD/<Device ID>` पर real-time data आता है
- Server `RTD/#` topic पर subscribe करता है
- हर data point database में save होता है
- Data format:
  ```json
  {
    "type": "Analog" | "Digital" | "Modbus" | "Canbus",
    "value": {
      "parameter_name1": value1,
      "parameter_name2": value2,
      ...
    }
  }
  ```

### 2. **Device Selection**
- User device selector dropdown से device choose कर सकता है
- Device list `Device_info` measurement से load होती है
- Format: `{Serial Number} - {Device Name}`

### 3. **Time Range Selection**
- User time range select कर सकता है:
  - Last 1 Hour
  - Last 6 Hours
  - Last 24 Hours
  - Last 7 Days
  - Last 30 Days
  - **Last 6 Months** (new)
  - **Last 1 Year** (new)
- Selected time range के according historical data display होता है

### 4. **Dynamic Parameter Display**
- Analytics page सिर्फ **enabled parameters** show करता है
- Parameters device configuration से automatically load होते हैं:
  - **Analog**: Enabled 4-20mA और 0-10V inputs
  - **Digital**: Enabled NPN/PNP inputs/outputs और relays
  - **Modbus**: Configured slave devices के variable names
  - **CAN Bus**: Configured CAN messages के variable names
- Disabled parameters कभी show नहीं होते

### 5. **Live Value Display**
- हर graph के ऊपर **current/live value** display होता है
- यह value database से latest value fetch करके show करता है
- Format: `Current: {value}`

### 6. **Graph Visualization**
- हर parameter का अपना graph होता है
- Graph में:
  - X-axis: Time (selected time range के according)
  - Y-axis: Parameter value
  - Line chart with markers
  - Color coding by data type:
    - **Analog**: Purple (#8b5cf6)
    - **Digital**: Green (#10b981)
    - **Modbus**: Blue (#3b82f6)
    - **CAN Bus**: Orange (#f59e0b)

### 7. **Auto-Refresh**
- Page हर 5 seconds में automatically refresh होता है
- Latest values और graphs update होते हैं

---

## 🗄️ Database Structure

### Measurement: `Realtime_Data`

Real-time data InfluxDB में `Realtime_Data` measurement में save होता है।

#### Tags (Indexed for fast queries):
- `device_id`: Device Serial Number (Sr_No)
- `data_type`: Type of data (Analog, Digital, Modbus, Canbus)
- `parameter_name`: Name of the parameter (e.g., "current", "voltage", "Conductivity")

#### Fields:
- `value`: Actual data value (can be float, int, string, or boolean)

#### Timestamp:
- UTC timestamp when data was received

#### Example Data Points:
```
Measurement: Realtime_Data
Tags:
  device_id: "8C4B144D3274"
  data_type: "Analog"
  parameter_name: "current"
Fields:
  value: 1.23
Time: 2026-01-19T10:30:00Z
```

```
Measurement: Realtime_Data
Tags:
  device_id: "8C4B144D3274"
  data_type: "Modbus"
  parameter_name: "Conductivity"
Fields:
  value: 0
Time: 2026-01-19T10:30:00Z
```

---

## 📊 Data Flow

### 1. **Device → MQTT → Database**
```
Device publishes → RTD/<Device ID>
  ↓
MQTT Broker receives
  ↓
Server subscribes to RTD/#
  ↓
on_realtime_data_received() callback
  ↓
RealtimeDataDBService.save_realtime_data()
  ↓
InfluxDB: Realtime_Data measurement
```

### 2. **Database → Analytics Page**
```
User selects device
  ↓
load_enabled_parameters() callback
  ↓
DeviceConfigDBService.get_*_config()
  ↓
Filter enabled parameters
  ↓
Create dynamic charts
  ↓
update_analytics_charts() callback (every 5 seconds)
  ↓
RealtimeDataDBService.get_realtime_data()
  ↓
Display graphs + live values
```

---

## 🔧 Technical Implementation

### Files Involved:

1. **`app/services/realtime_data_db.py`**
   - `RealtimeDataDBService`: Database operations for real-time data
   - Methods:
     - `save_realtime_data()`: Save data point to InfluxDB
     - `get_realtime_data()`: Query historical data for a parameter
     - `get_latest_value()`: Get most recent value for a parameter

2. **`app/services/mqtt_client.py`**
   - `MQTTClientService`: MQTT communication
   - Subscribes to `RTD/#` topic
   - Routes RTD messages to callback

3. **`app/main.py`**
   - `on_realtime_data_received()`: MQTT callback for RTD data
   - Processes incoming data and saves to database

4. **`app/pages/analytics.py`**
   - `create_analytics_layout()`: Main page layout
   - `load_analytics_device_list()`: Load device dropdown
   - `load_enabled_parameters()`: Load and filter enabled parameters
   - `update_analytics_charts()`: Update graphs with real-time data

---

## 📝 Example Scenarios

### Scenario 1: Analog Data
**Device Configuration:**
- Channel 1 (4-20mA): Enabled, Name: "current"
- Channel 4 (0-10V): Enabled, Name: "voltage"

**Device sends:**
```json
{
  "type": "Analog",
  "value": {
    "current": "1.23",
    "voltage": "51.3"
  }
}
```

**Analytics Page shows:**
- Graph for "current" with live value: 1.23
- Graph for "voltage" with live value: 51.3

### Scenario 2: Modbus Data
**Device Configuration:**
- Slave Device 1: Variable Name: "Conductivity"
- Slave Device 2: Variable Name: "Ph"
- Slave Device 3: Variable Name: "Humidity"
- Slave Device 4: Variable Name: "Air_Temp"

**Device sends:**
```json
{
  "type": "Modbus",
  "value": {
    "Conductivity": 0,
    "Ph": 30,
    "Humidity": 459,
    "Air_Temp": 262
  }
}
```

**Analytics Page shows:**
- 4 graphs (one for each variable)
- Live values: Conductivity=0, Ph=30, Humidity=459, Air_Temp=262

### Scenario 3: Digital Data
**Device Configuration:**
- NPN Input Channel 1: Enabled, Name: "proxy motor"
- NPN Input Channel 2: Enabled, Name: "proxy counter"

**Device sends:**
```json
{
  "type": "Digital",
  "value": {
    "proxy motor": 0,
    "proxy counter": 1
  }
}
```

**Analytics Page shows:**
- Graph for "proxy motor" with live value: 0
- Graph for "proxy counter" with live value: 1

---

## ⚠️ Important Notes

1. **Only Enabled Parameters**: Analytics page सिर्फ enabled/configured parameters show करता है। Disabled parameters कभी display नहीं होते।

2. **Dynamic UI**: Parameters की संख्या के according UI automatically adjust होता है। अगर कोई parameter नहीं है, तो message show होता है।

3. **Real-Time Updates**: Page हर 5 seconds में refresh होता है। Latest values और graphs automatically update होते हैं।

4. **Time Range**: User time range change कर सकता है, और graphs उसी के according historical data show करते हैं।

5. **Database Storage**: सभी real-time data points database में save होते हैं, ताकि historical analysis possible हो।

6. **Data Type Normalization**: 
   - "Modbus" → "Modbus"
   - "Canbus" → "Canbus"
   - Case-insensitive matching

---

## 🐛 Troubleshooting

### Problem: No parameters showing
**Solution**: 
- Check device configuration in Devices tab
- Ensure at least one parameter is enabled
- Verify device ID is correct

### Problem: No data in graphs
**Solution**:
- Check if device is sending data to `RTD/<Device ID>` topic
- Verify MQTT connection
- Check database connection
- Ensure data format is correct: `{"type": "...", "value": {...}}`

### Problem: Live values showing "--"
**Solution**:
- Check if device has sent any data recently
- Verify database has data for selected time range
- Check parameter name matches exactly (case-sensitive)

---

## 📈 Future Enhancements

1. **Alerts/Thresholds**: Set thresholds और alerts when values exceed limits
2. **Export Data**: Download historical data as CSV/Excel
3. **Multiple Devices**: Compare data from multiple devices
4. **Custom Dashboards**: User-defined dashboard layouts
5. **Statistical Analysis**: Min, max, average calculations
6. **Data Aggregation**: Downsampling for long time ranges

---

## 📞 Support

अगर कोई issue हो, तो:
1. Check logs: `app/services/realtime_data_db.py` और `app/main.py`
2. Verify MQTT topic: Device should publish to `RTD/<Device ID>`
3. Check database: Verify data is being saved in `Realtime_Data` measurement
4. Check device configuration: Ensure parameters are enabled in Devices tab

---

**Last Updated**: January 2026

