# Device Configuration - JSON Format for Hardware Communication

## 📡 Hardware ko Configuration Bhejne ka Process

Jab aap hardware device ko configuration bhejoge, to MQTT topic par JSON format mein bhejna hoga.

**MQTT Topic Format:** `iotnarad/devices/<SerialNumber>/config`

---

## 🔧 Option 1: Single Measurement with JSON Field

### Database Structure:
- **Measurement:** `Device_configuration`
- **Tags:** `Sr_No`, `Config_Type`
- **Fields:** `Config_JSON` (string), `Updated_By`, `Version`

### Hardware ko JSON Bhejne ka Process:

#### **Step 1: Database se Configuration Fetch Karein**

```python
# Get all configs for a device
query = '''
SELECT *
FROM "Device_configuration"
WHERE "Sr_No" = 'TEST78787'
  AND time > now() - interval '1 year'
ORDER BY time DESC;
'''

# Result: Multiple rows (one per config type)
# Row 1: Config_Type='analog', Config_JSON='{...}'
# Row 2: Config_Type='digital', Config_JSON='{...}'
# Row 3: Config_Type='modbus', Config_JSON='{...}'
# Row 4: Config_Type='canbus', Config_JSON='{...}'
```

#### **Step 2: JSON ko Parse aur Combine Karein**

```python
# Parse each Config_JSON and combine into one structure
configs = {
    'analog': json.loads(row1.Config_JSON),
    'digital': json.loads(row2.Config_JSON),
    'modbus': json.loads(row3.Config_JSON),
    'canbus': json.loads(row4.Config_JSON)
}
```

#### **Step 3: Hardware ko Complete JSON Bhejein**

**MQTT Topic:** `iotnarad/devices/TEST78787/config`

**JSON Payload:**
```json
{
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": true,
        "name": "Temp Sensor",
        "io": "AIN0",
        "div": 1.0,
        "mul": 1.0
      },
      {
        "channel": 2,
        "enabled": false,
        "name": "-",
        "io": "AIN1",
        "div": 1.0,
        "mul": 1.0
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": true,
        "name": "Pressure",
        "io": "AIN2",
        "div": 1.0,
        "mul": 1.0
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": true,
        "name": "Control",
        "io": "DOUT0",
        "div": 1.0,
        "mul": 1.0,
        "value": 0.0
      }
    ]
  },
  "digital": {
    "npn_input": [
      {
        "channel": 1,
        "enabled": true,
        "name": "Door Sensor",
        "io": "INP1H"
      },
      {
        "channel": 2,
        "enabled": false,
        "name": "-",
        "io": "INP2H"
      }
    ],
    "relay": [
      {
        "channel": 1,
        "enabled": true,
        "name": "Relay 1",
        "io": "RLY1"
      }
    ]
  },
  "modbus": {
    "enabled": true,
    "baudrate": 9600,
    "slave_address": 1,
    "data_bits": 8,
    "stop_bits": 1,
    "parity": "none"
  },
  "canbus": {
    "enabled": true,
    "speed": 500,
    "filter": "0x123"
  }
}
```

**Pros:**
- ✅ Simple: Database se directly JSON string fetch karke parse karo
- ✅ One query: Ek device ki sabhi configs ek query mein
- ✅ Easy to combine: Sabhi config types ko combine karke bhejo

**Cons:**
- ⚠️ Parsing needed: Har Config_JSON ko parse karna padega
- ⚠️ Multiple rows: Ek device ke liye multiple rows (6 config types)
- ⚠️ Combine logic: Application mein combine karna padega

---

## 🔧 Option 2: Separate Measurements by Config Type

### Database Structure:
- **Measurements:** `Device_config_analog`, `Device_config_digital`, `Device_config_modbus`, `Device_config_canbus`
- **Tags:** `Sr_No`, `Input_Type`/`IO_Type`, `Channel`
- **Fields:** Individual fields (Enabled, Name, IO_Pin, etc.)

### Hardware ko JSON Bhejne ka Process:

#### **Step 1: Database se Configuration Fetch Karein**

```python
# Get analog config
analog_query = '''
SELECT *
FROM "Device_config_analog"
WHERE "Sr_No" = 'TEST78787'
  AND time > now() - interval '1 year'
ORDER BY "Input_Type", "Channel";
'''

# Get digital config
digital_query = '''
SELECT *
FROM "Device_config_digital"
WHERE "Sr_No" = 'TEST78787'
  AND time > now() - interval '1 year'
ORDER BY "IO_Type", "Channel";
'''

# Get modbus config
modbus_query = '''
SELECT *
FROM "Device_config_modbus"
WHERE "Sr_No" = 'TEST78787'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;
'''

# Get canbus config
canbus_query = '''
SELECT *
FROM "Device_config_canbus"
WHERE "Sr_No" = 'TEST78787'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;
'''
```

#### **Step 2: Rows ko Group aur Structure Karein**

```python
# Analog: Group by Input_Type
analog_config = {
    "input_4_20ma": [],
    "input_1_10v": [],
    "output_0_10v": []
}

for row in analog_rows:
    if row.Input_Type == "input_4_20ma":
        analog_config["input_4_20ma"].append({
            "channel": row.Channel,
            "enabled": row.Enabled,
            "name": row.Name,
            "io": row.IO_Pin,
            "div": row.Div,
            "mul": row.Mul,
            "value": row.Value if hasattr(row, 'Value') else None
        })
    # ... similar for other input types

# Digital: Group by IO_Type
digital_config = {
    "npn_input": [],
    "npn_output": [],
    "pnp_input": [],
    "pnp_output": [],
    "relay": []
}

for row in digital_rows:
    digital_config[row.IO_Type].append({
        "channel": row.Channel,
        "enabled": row.Enabled,
        "name": row.Name,
        "io": row.IO_Pin
    })

# Modbus: Single row
modbus_config = {
    "enabled": modbus_row.Enabled,
    "baudrate": modbus_row.Baudrate,
    "slave_address": modbus_row.Slave_Address,
    "data_bits": modbus_row.Data_Bits,
    "stop_bits": modbus_row.Stop_Bits,
    "parity": modbus_row.Parity
}

# CAN Bus: Single row
canbus_config = {
    "enabled": canbus_row.Enabled,
    "speed": canbus_row.Speed,
    "filter": canbus_row.Filter
}
```

#### **Step 3: Hardware ko Complete JSON Bhejein**

**MQTT Topic:** `iotnarad/devices/TEST78787/config`

**JSON Payload (Same as Option 1):**
```json
{
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": true,
        "name": "Temp Sensor",
        "io": "AIN0",
        "div": 1.0,
        "mul": 1.0
      }
    ],
    "input_1_10v": [...],
    "output_0_10v": [...]
  },
  "digital": {
    "npn_input": [...],
    "relay": [...]
  },
  "modbus": {
    "enabled": true,
    "baudrate": 9600,
    "slave_address": 1,
    "data_bits": 8,
    "stop_bits": 1,
    "parity": "none"
  },
  "canbus": {
    "enabled": true,
    "speed": 500,
    "filter": "0x123"
  }
}
```

**Pros:**
- ✅ Direct fields: No JSON parsing needed
- ✅ Easy filtering: Specific channels/types ko easily filter kar sakte hain
- ✅ Better queries: SQL-like queries for specific fields

**Cons:**
- ⚠️ Multiple queries: 4 separate queries (analog, digital, modbus, canbus)
- ⚠️ Grouping logic: Rows ko group karke structure banana padega
- ⚠️ More complex: More code to combine different measurements

---

## 📊 Comparison Table

| Aspect | Option 1 (Single Measurement) | Option 2 (Separate Measurements) |
|--------|-------------------------------|----------------------------------|
| **Database Queries** | 1 query (all configs) | 4 queries (one per type) |
| **JSON Parsing** | Required (parse Config_JSON) | Not required (direct fields) |
| **Data Combination** | Simple (just parse JSONs) | Complex (group rows by type) |
| **Code Complexity** | Low (simple parsing) | Medium (grouping logic) |
| **Query Performance** | Fast (one query) | Slower (multiple queries) |
| **Hardware JSON** | Same for both | Same for both |
| **Flexibility** | Easy to add new config types | Need new measurement for new type |
| **Filtering** | Limited (JSON parsing needed) | Easy (direct field queries) |

---

## 💡 Recommendation for Hardware Communication

### **Option 1 (Single Measurement) - Better for Hardware Communication**

**Reasons:**
1. ✅ **Faster:** Ek query mein sabhi configs mil jayengi
2. ✅ **Simpler Code:** JSON parse karke directly combine karo
3. ✅ **Less Database Calls:** 1 query vs 4 queries
4. ✅ **Same Output:** Dono options mein hardware ko same JSON format milega

**Implementation Example:**
```python
def get_device_config_for_hardware(serial_number):
    # Single query
    query = f'''
    SELECT "Config_Type", "Config_JSON"
    FROM "Device_configuration"
    WHERE "Sr_No" = '{serial_number}'
      AND time > now() - interval '1 year'
    ORDER BY time DESC;
    '''
    
    results = query_api.query(query)
    
    # Combine configs
    config = {}
    for row in results:
        config_type = row.Config_Type
        config_json = json.loads(row.Config_JSON)
        config[config_type] = config_json
    
    return config  # Ready to send to hardware
```

---

### **Option 2 (Separate Measurements) - Better for Querying/Analytics**

**Reasons:**
1. ✅ **Better Queries:** Specific channels/types ko easily query kar sakte hain
2. ✅ **No Parsing:** Direct field access
3. ✅ **Analytics:** Easy to analyze which channels are enabled across devices
4. ✅ **Filtering:** Easy filtering by channel, type, etc.

**Use Case:** Agar aapko analytics chahiye (e.g., "kitne devices mein channel 1 enabled hai"), to Option 2 better hai.

---

## 🎯 Final Recommendation

### **For Hardware Communication: Option 1**
- Ek query mein sabhi configs
- Simple JSON parsing
- Fast response time
- Less code complexity

### **For Analytics/Reporting: Option 2**
- Better querying capabilities
- Direct field access
- Easy filtering and aggregation

### **Hybrid Approach (Best of Both):**
1. **Store in Option 2 format** (separate measurements) for querying
2. **Cache in Option 1 format** (combined JSON) for hardware communication
3. **When sending to hardware:** Use cached JSON (fast)
4. **When querying/analyzing:** Use separate measurements (flexible)

---

## 📝 Code Example: Hardware ko Config Bhejna

### Option 1 Implementation:

```python
def send_config_to_hardware(serial_number):
    # Fetch all configs
    query = f'''
    SELECT "Config_Type", "Config_JSON"
    FROM "Device_configuration"
    WHERE "Sr_No" = '{serial_number}'
      AND time > now() - interval '1 year'
    ORDER BY time DESC;
    '''
    
    results = query_api.query(query)
    
    # Combine into single JSON
    hardware_config = {}
    for row in results:
        config_type = row.Config_Type
        config_data = json.loads(row.Config_JSON)
        hardware_config[config_type] = config_data
    
    # Send via MQTT
    topic = f"iotnarad/devices/{serial_number}/config"
    mqtt_client.publish(topic, hardware_config)
    
    return hardware_config
```

### Option 2 Implementation:

```python
def send_config_to_hardware(serial_number):
    # Fetch analog config
    analog_rows = query_analog_config(serial_number)
    analog_config = group_analog_rows(analog_rows)
    
    # Fetch digital config
    digital_rows = query_digital_config(serial_number)
    digital_config = group_digital_rows(digital_rows)
    
    # Fetch modbus config
    modbus_row = query_modbus_config(serial_number)
    modbus_config = row_to_dict(modbus_row)
    
    # Fetch canbus config
    canbus_row = query_canbus_config(serial_number)
    canbus_config = row_to_dict(canbus_row)
    
    # Combine
    hardware_config = {
        "analog": analog_config,
        "digital": digital_config,
        "modbus": modbus_config,
        "canbus": canbus_config
    }
    
    # Send via MQTT
    topic = f"iotnarad/devices/{serial_number}/config"
    mqtt_client.publish(topic, hardware_config)
    
    return hardware_config
```

---

## 🔍 Summary

**Hardware ko JSON bhejne ke liye:**
- **Option 1:** Simple, fast, ek query
- **Option 2:** Complex, multiple queries, but better for analytics

**Final JSON format dono options mein same hoga** - hardware ko koi difference nahi padega.

**Recommendation:** 
- Agar **primary use case hardware communication** hai → **Option 1**
- Agar **primary use case analytics/reporting** hai → **Option 2**
- Agar **dono chahiye** → **Hybrid approach** (store Option 2, cache Option 1)

