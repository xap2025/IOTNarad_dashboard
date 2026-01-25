# 📊 Analytics Page - Step 2: Device Selection & Enabled Parameters Loading

## 🎯 Overview

Yeh document explain karta hai ki Analytics page par device select karne ke baad kaun-se enabled parameters load hote hain aur kaise charts create hote hain.

---

## 🔄 Complete Step 2 Flow

```
User selects device from dropdown
  ↓
analytics-device-selector value changes
  ↓
load_enabled_parameters() callback triggered
  ↓
DeviceConfigDBService initialization
  ↓
Fetch configurations from InfluxDB:
  - get_analog_config()
  - get_digital_config()
  - get_modbus_config()
  - get_can_bus_config()
  ↓
Filter ONLY enabled parameters:
  - Analog: Input channels (4-20mA, 0-10V) with enabled=true
  - Digital: Input channels (NPN, PNP) with enabled=true
  - Modbus: Slave devices with non-empty variable_name
  - Canbus: CAN messages/data mappings with non-empty variable_name
  ↓
Create chart components for each parameter
  ↓
Update UI with charts
```

---

## 📋 Step-by-Step Process

### **Step 1: User Device Selection**

**Component**: `analytics-device-selector` (Dropdown)
**Location**: `app/pages/analytics.py` (line 28-35)

**Kya Hota Hai:**
- User dropdown se device select karta hai
- Device ID (Sr_No) value ke roop mein store hota hai
- Example: `"DEV001"` ya `"12345"`

**Code:**
```python
dcc.Dropdown(
    id='analytics-device-selector',
    options=[...],  # Loaded by load_analytics_device_list()
    value=None,
    placeholder='Select a device...'
)
```

---

### **Step 2: Callback Trigger**

**Callback**: `load_enabled_parameters()`
**File**: `app/pages/analytics.py` (line 185)
**Trigger**: `Input('analytics-device-selector', 'value')`

**Callback Definition:**
```python
@callback(
    [
        Output('analytics-device-store', 'data'),      # Store device_id
        Output('analytics-params-store', 'data'),      # Store enabled_params dict
        Output('analytics-charts-container', 'children'), # Store chart components
    ],
    [
        Input('analytics-device-selector', 'value'),  # Device selection trigger
    ],
    prevent_initial_call=True
)
def load_enabled_parameters(device_id):
    """Load enabled parameters from device configuration"""
```

**Outputs:**
1. **analytics-device-store**: Device ID store hota hai (baad mein use ke liye)
2. **analytics-params-store**: Enabled parameters dictionary store hota hai
   - Format: `{"Parameter Name": "Type"}`
   - Example: `{"Temperature": "Analog", "Switch1": "Digital"}`
3. **analytics-charts-container**: Chart components list (UI mein render hote hain)

---

### **Step 3: Database Service Initialization**

**Service**: `DeviceConfigDBService`
**File**: `app/services/device_config_db.py`

**Code:**
```python
from app.services.device_config_db import DeviceConfigDBService

db_service = DeviceConfigDBService()
```

**Kya Karta Hai:**
- InfluxDB connection establish karta hai
- Database queries execute karne ke liye ready hota hai

---

### **Step 4: Configuration Fetch from Database**

#### **A. Analog Configuration**

**Method**: `get_analog_config(device_id)`
**File**: `app/services/device_config_db.py` (line 622)
**Database Table**: `Device_Config_Analog`

**Query:**
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
  |> filter(fn: (r) => r.device_id == "{device_id}")
  |> pivot(...)
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

**Returned Structure:**
```python
{
    "input_4_20ma": [
        {
            "channel": 1,
            "enabled": True,
            "io_pin": "A0",
            "name": "Temperature",
            "divider": 1.0,
            "multiplier": 1.0
        },
        ...
    ],
    "input_1_10v": [
        {
            "channel": 1,
            "enabled": True,
            "io_pin": "A1",
            "name": "Pressure",
            "divider": 1.0,
            "multiplier": 1.0
        },
        ...
    ],
    "output_0_10v": [...],  # IGNORED for Analytics
    "scan_rate": 1000
}
```

**Important Notes:**
- ✅ **Show**: `input_4_20ma` aur `input_1_10v` channels (sirf inputs)
- ❌ **Ignore**: `output_0_10v` channels (outputs show nahi hote)

---

#### **B. Digital Configuration**

**Method**: `get_digital_config(device_id)`
**File**: `app/services/device_config_db.py` (line 718)
**Database Table**: `Device_Config_Digital`

**Query:**
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -365d)
  |> filter(fn: (r) => r._measurement == "Device_Config_Digital")
  |> filter(fn: (r) => r.device_id == "{device_id}")
  |> pivot(...)
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
```

**Returned Structure:**
```python
{
    "npn_input": [
        {
            "channel": 1,
            "enabled": True,
            "io_pin": "D2",
            "name": "Switch1"
        },
        ...
    ],
    "pnp_input": [
        {
            "channel": 1,
            "enabled": True,
            "io_pin": "D3",
            "name": "Sensor1"
        },
        ...
    ],
    "npn_output": [...],  # IGNORED for Analytics
    "pnp_output": [...],  # IGNORED for Analytics
    "relay": [...],       # IGNORED for Analytics
    "scan_rate": 1000
}
```

**Important Notes:**
- ✅ **Show**: `npn_input` aur `pnp_input` channels (sirf inputs)
- ❌ **Ignore**: `npn_output`, `pnp_output`, aur `relay` (outputs show nahi hote)

---

#### **C. Modbus Configuration**

**Method**: `get_modbus_config(device_id)`
**File**: `app/services/device_config_db.py` (line 801)
**Database Table**: `Device_Config_MODBUS`

**Query Strategy:**
1. **Settings Query**: Latest communication settings (baud_rate, parity, etc.)
2. **Slave Devices Query**: ALL slave devices from latest timestamp

**Returned Structure:**
```python
{
    "enabled": True,
    "communication_settings": {
        "baud_rate": 9600,
        "data_bits": 8,
        "parity": "None",
        "stop_bits": 1
    },
    "protocol_settings": {
        "mode": "RTU",
        "role": "Master"
    },
    "polling_interval_ms": 1000,
    "slave_devices": [
        {
            "index": 0,
            "slave_id": "1",
            "function_code": "0x03",
            "register_address": "40001",
            "data_type": "int16",
            "endianness": "Big Endian",
            "variable_name": "Temperature",  # ✅ Used for Analytics
            "register_count": 1
        },
        {
            "index": 1,
            "slave_id": "1",
            "function_code": "0x03",
            "register_address": "40002",
            "data_type": "int16",
            "endianness": "Big Endian",
            "variable_name": "Pressure",     # ✅ Used for Analytics
            "register_count": 1
        },
        ...
    ]
}
```

**Important Notes:**
- ✅ **Show**: `slave_devices` array mein se har slave ka `variable_name` (agar non-empty hai)
- ❌ **Ignore**: Empty `variable_name` wale slaves show nahi hote
- **Format**: Variable name exactly as configured (spaces preserved)

---

#### **D. CAN Bus Configuration**

**Method**: `get_can_bus_config(device_id)`
**File**: `app/services/device_config_db.py` (line 992)
**Database Table**: `Device_Config_CANBus`

**Query Strategy:**
1. **Settings Query**: Latest communication settings (baud_rate, CAN mode, etc.)
2. **CAN Messages Query**: ALL CAN messages from latest timestamp
3. **Data Mapping Query**: ALL data mappings from latest timestamp

**Returned Structure:**
```python
{
    "enabled": True,
    "communication_settings": {
        "baud_rate": 125,
        "identifier_length": "11-bit",
        "can_mode": "Normal",
        ...
    },
    "can_messages": [
        {
            "index": 0,
            "can_id": "0x123",
            "direction": "TX",
            "period_ms": 100,
            "variable_name": "Temperature",  # ✅ Used for Analytics
            "data_length": 8
        },
        ...
    ],
    "data_mapping": [
        {
            "index": 0,
            "can_id": "0x123",
            "byte_position": "Byte 0",
            "data_length": "1 Byte",
            "data_type": "int8",
            "endianness": "Big Endian",
            "variable_name": "Pressure",     # ✅ Used for Analytics
            "scale_factor": 1.0,
            "offset": 0.0
        },
        ...
    ]
}
```

**Important Notes:**
- ✅ **Show**: 
  - `can_messages` array mein se har message ka `variable_name` (agar non-empty hai)
  - `data_mapping` array mein se har mapping ka `variable_name` (agar non-empty hai)
- ❌ **Ignore**: Empty `variable_name` wale messages/mappings show nahi hote

---

### **Step 5: Filter Enabled Parameters**

**Code Location**: `app/pages/analytics.py` (line 201-279)

**Process:**

#### **A. Analog Parameters Filtering**

```python
if analog_config:
    # 4-20mA inputs (ONLY INPUTS)
    input_4_20ma_list = analog_config.get('input_4_20ma', [])
    for channel in input_4_20ma_list:
        if channel.get('enabled', False):  # ✅ Check enabled flag
            name = channel.get('name', f"Channel {channel.get('channel', '?')}")
            enabled_params[name] = 'Analog'  # Add to enabled params
    
    # 0-10V inputs (ONLY INPUTS)
    input_1_10v_list = analog_config.get('input_1_10v', [])
    for channel in input_1_10v_list:
        if channel.get('enabled', False):  # ✅ Check enabled flag
            name = channel.get('name', f"Channel {channel.get('channel', '?')}")
            enabled_params[name] = 'Analog'  # Add to enabled params
    
    # NOTE: output_0_10v channels are IGNORED
```

**Filtering Rules:**
- ✅ **Include**: Channels jahan `enabled == True`
- ❌ **Exclude**: Channels jahan `enabled == False`
- ❌ **Exclude**: Output channels (`output_0_10v`)

**Example:**
```python
# Input channels
input_4_20ma = [
    {"channel": 1, "enabled": True, "name": "Temperature"},   # ✅ Included
    {"channel": 2, "enabled": False, "name": "Humidity"},    # ❌ Excluded
    {"channel": 3, "enabled": True, "name": "Pressure"}      # ✅ Included
]

# Result:
enabled_params = {
    "Temperature": "Analog",
    "Pressure": "Analog"
}
```

---

#### **B. Digital Parameters Filtering**

```python
if digital_config:
    # NPN inputs (ONLY INPUTS)
    npn_input_list = digital_config.get('npn_input', [])
    for channel in npn_input_list:
        if channel.get('enabled', False):  # ✅ Check enabled flag
            name = channel.get('name', f"NPN_IN_{channel.get('channel', '?')}")
            enabled_params[name] = 'Digital'
    
    # PNP inputs (ONLY INPUTS)
    pnp_input_list = digital_config.get('pnp_input', [])
    for channel in pnp_input_list:
        if channel.get('enabled', False):  # ✅ Check enabled flag
            name = channel.get('name', f"PNP_IN_{channel.get('channel', '?')}")
            enabled_params[name] = 'Digital'
    
    # NOTE: npn_output, pnp_output, relay are IGNORED
```

**Filtering Rules:**
- ✅ **Include**: NPN/PNP input channels jahan `enabled == True`
- ❌ **Exclude**: NPN/PNP input channels jahan `enabled == False`
- ❌ **Exclude**: Output channels (`npn_output`, `pnp_output`)
- ❌ **Exclude**: Relays (`relay`)

**Example:**
```python
# Input channels
npn_input = [
    {"channel": 1, "enabled": True, "name": "Switch1"},   # ✅ Included
    {"channel": 2, "enabled": False, "name": "Switch2"},   # ❌ Excluded
]

pnp_input = [
    {"channel": 1, "enabled": True, "name": "Sensor1"}     # ✅ Included
]

# Result:
enabled_params = {
    "Switch1": "Digital",
    "Sensor1": "Digital"
}
```

---

#### **C. Modbus Parameters Filtering**

```python
if modbus_config:
    slave_devices = modbus_config.get('slave_devices', [])
    for slave in slave_devices:
        var_name = slave.get('variable_name', '')
        if var_name:  # ✅ Check if non-empty
            clean_var_name = var_name.strip()  # Remove extra spaces
            enabled_params[clean_var_name] = 'Modbus'
        else:
            logger.warning(f"⚠️ Modbus slave device has empty variable_name")
```

**Filtering Rules:**
- ✅ **Include**: Slave devices jahan `variable_name` non-empty hai
- ❌ **Exclude**: Slave devices jahan `variable_name` empty hai
- **Format**: Variable name exactly as configured (spaces preserved, but trimmed)

**Example:**
```python
slave_devices = [
    {
        "slave_id": "1",
        "register_address": "40001",
        "variable_name": "Temperature",      # ✅ Included
        ...
    },
    {
        "slave_id": "1",
        "register_address": "40002",
        "variable_name": "",                  # ❌ Excluded (empty)
        ...
    },
    {
        "slave_id": "2",
        "register_address": "40001",
        "variable_name": "  Pressure  ",      # ✅ Included (trimmed to "Pressure")
        ...
    }
]

# Result:
enabled_params = {
    "Temperature": "Modbus",
    "Pressure": "Modbus"
}
```

---

#### **D. CAN Bus Parameters Filtering**

```python
if can_bus_config:
    # CAN Messages
    can_messages = can_bus_config.get('can_messages', [])
    for msg in can_messages:
        var_name = msg.get('variable_name', '')
        if var_name:  # ✅ Check if non-empty
            enabled_params[var_name] = 'Canbus'
    
    # Data Mappings
    data_mapping = can_bus_config.get('data_mapping', [])
    for mapping in data_mapping:
        var_name = mapping.get('variable_name', '')
        if var_name:  # ✅ Check if non-empty
            enabled_params[var_name] = 'Canbus'
```

**Filtering Rules:**
- ✅ **Include**: CAN messages jahan `variable_name` non-empty hai
- ✅ **Include**: Data mappings jahan `variable_name` non-empty hai
- ❌ **Exclude**: Empty `variable_name` wale messages/mappings

**Example:**
```python
can_messages = [
    {
        "can_id": "0x123",
        "variable_name": "Temperature",      # ✅ Included
        ...
    },
    {
        "can_id": "0x124",
        "variable_name": "",                  # ❌ Excluded
        ...
    }
]

data_mapping = [
    {
        "can_id": "0x123",
        "byte_position": "Byte 0",
        "variable_name": "Pressure",          # ✅ Included
        ...
    }
]

# Result:
enabled_params = {
    "Temperature": "Canbus",
    "Pressure": "Canbus"
}
```

---

### **Step 6: Create Chart Components**

**Code Location**: `app/pages/analytics.py` (line 284-312)

**Process:**

```python
charts = []
if enabled_params:
    rows = []
    current_row = []
    
    for idx, (param_name, param_type) in enumerate(enabled_params.items()):
        chart_id = f"chart-{param_name}"
        chart_col = create_parameter_chart(param_name, param_type, chart_id)
        current_row.append(chart_col)
        
        # Create row every 3 charts
        if len(current_row) == 3 or idx == len(enabled_params) - 1:
            rows.append(dbc.Row(current_row, className='mb-4'))
            current_row = []
    
    charts = rows
else:
    charts = [
        dbc.Alert("No enabled parameters found...", color="info")
    ]
```

**Chart Component Creation:**

**Function**: `create_parameter_chart()`
**File**: `app/pages/analytics.py` (line 71)

**Kya Banata Hai:**
- Chart card component (Bootstrap card)
- Parameter name display (with icon based on type)
- Live value container (initially "No value")
- Plotly graph component (initially empty)

**Chart Layout:**
- **3 charts per row** (Bootstrap grid: `md=4`)
- **Icons aur colors** data type ke according:
  - Analog: ⚡ Purple (`#8b5cf6`)
  - Digital: 🔄 Green (`#10b981`)
  - Modbus: 🔌 Blue (`#3b82f6`)
  - Canbus: 🚌 Orange (`#f59e0b`)

**Example Output:**
```python
[
    dbc.Row([
        create_parameter_chart("Temperature", "Analog", "chart-Temperature"),
        create_parameter_chart("Pressure", "Analog", "chart-Pressure"),
        create_parameter_chart("Switch1", "Digital", "chart-Switch1")
    ]),
    dbc.Row([
        create_parameter_chart("ModbusVar1", "Modbus", "chart-ModbusVar1")
    ])
]
```

---

### **Step 7: Update UI**

**Outputs:**
1. **analytics-device-store**: Device ID store hota hai
2. **analytics-params-store**: Enabled parameters dictionary store hota hai
3. **analytics-charts-container**: Chart components render hote hain

**Result:**
- Charts UI mein display hote hain
- Har chart ke liye:
  - Parameter name (with icon)
  - Live value display (initially "No value")
  - Empty graph (data baad mein load hoga)

---

## 📊 Complete Example

### **Input: Device Selection**
```
Device ID: "DEV001"
```

### **Step 1: Database Queries**

**Analog Config:**
```python
{
    "input_4_20ma": [
        {"channel": 1, "enabled": True, "name": "Temperature"},
        {"channel": 2, "enabled": False, "name": "Humidity"}
    ],
    "input_1_10v": [
        {"channel": 1, "enabled": True, "name": "Pressure"}
    ],
    "output_0_10v": [
        {"channel": 1, "enabled": True, "name": "Output1"}  # Ignored
    ]
}
```

**Digital Config:**
```python
{
    "npn_input": [
        {"channel": 1, "enabled": True, "name": "Switch1"}
    ],
    "pnp_input": [
        {"channel": 1, "enabled": True, "name": "Sensor1"}
    ],
    "npn_output": [
        {"channel": 1, "enabled": True, "name": "LED1"}  # Ignored
    ]
}
```

**Modbus Config:**
```python
{
    "slave_devices": [
        {"variable_name": "ModbusVar1", ...},
        {"variable_name": "", ...},  # Ignored
        {"variable_name": "ModbusVar2", ...}
    ]
}
```

**CAN Bus Config:**
```python
{
    "can_messages": [
        {"variable_name": "CANVar1", ...}
    ],
    "data_mapping": [
        {"variable_name": "CANVar2", ...}
    ]
}
```

### **Step 2: Filter Enabled Parameters**

```python
enabled_params = {
    "Temperature": "Analog",      # From input_4_20ma (enabled=True)
    "Pressure": "Analog",          # From input_1_10v (enabled=True)
    "Switch1": "Digital",          # From npn_input (enabled=True)
    "Sensor1": "Digital",          # From pnp_input (enabled=True)
    "ModbusVar1": "Modbus",        # From slave_devices (non-empty variable_name)
    "ModbusVar2": "Modbus",        # From slave_devices (non-empty variable_name)
    "CANVar1": "Canbus",           # From can_messages (non-empty variable_name)
    "CANVar2": "Canbus"            # From data_mapping (non-empty variable_name)
}
```

### **Step 3: Create Charts**

**Total Charts**: 8
**Layout**: 3 rows (3 + 3 + 2 charts)

**Row 1:**
- Temperature (Analog) ⚡
- Pressure (Analog) ⚡
- Switch1 (Digital) 🔄

**Row 2:**
- Sensor1 (Digital) 🔄
- ModbusVar1 (Modbus) 🔌
- ModbusVar2 (Modbus) 🔌

**Row 3:**
- CANVar1 (Canbus) 🚌
- CANVar2 (Canbus) 🚌

---

## ✅ Summary

### **What Gets Shown:**

1. **Analog Parameters:**
   - ✅ 4-20mA Input channels (enabled)
   - ✅ 0-10V Input channels (enabled)
   - ❌ Output channels (ignored)

2. **Digital Parameters:**
   - ✅ NPN Input channels (enabled)
   - ✅ PNP Input channels (enabled)
   - ❌ Output channels (ignored)
   - ❌ Relays (ignored)

3. **Modbus Parameters:**
   - ✅ Slave devices with non-empty `variable_name`
   - ❌ Empty `variable_name` wale slaves (ignored)

4. **CAN Bus Parameters:**
   - ✅ CAN messages with non-empty `variable_name`
   - ✅ Data mappings with non-empty `variable_name`
   - ❌ Empty `variable_name` wale messages/mappings (ignored)

### **Key Points:**

- **Only Enabled**: Sirf `enabled=True` wale channels show hote hain
- **Only Inputs**: Output channels show nahi hote (Analog/Digital)
- **Non-Empty Names**: Modbus/CAN Bus mein sirf non-empty `variable_name` show hota hai
- **Exact Matching**: Parameter names exactly as configured (spaces preserved)
- **Chart Layout**: 3 charts per row (responsive grid)

---

## 🔍 Debugging

### **Check Logs:**

```
📊 ANALOG: Loading analog config for device DEV001
📊 ANALOG: Found 2 input_4_20ma channel(s)
   Added Analog parameter (4-20mA Input): 'Temperature'
📊 DIGITAL: Loading digital config for device DEV001
📊 DIGITAL: Found 1 NPN input channel(s)
   Added Digital parameter (NPN Input): 'Switch1'
📊 MODBUS: Found 2 slave device(s) in config
   Added Modbus parameter: 'ModbusVar1'
✅ Loaded 3 enabled parameters for device DEV001
   Parameter list: ['Temperature', 'Switch1', 'ModbusVar1']
   Parameter details: {'Temperature': 'Analog', 'Switch1': 'Digital', 'ModbusVar1': 'Modbus'}
```

### **Common Issues:**

1. **No Charts Showing:**
   - Check: Device configuration database mein hai ya nahi
   - Check: Parameters enabled hain ya nahi
   - Check: Variable names non-empty hain ya nahi (Modbus/CAN Bus)

2. **Missing Parameters:**
   - Check: `enabled` flag `True` hai ya nahi
   - Check: Output channels intentionally ignored hote hain
   - Check: Empty `variable_name` wale parameters ignored hote hain

3. **Wrong Parameter Names:**
   - Check: Database mein jo name save hai, wahi UI mein dikhna chahiye
   - Check: Extra spaces trim ho rahe hain (Modbus)

---

## 📝 Code References

- **Callback**: `app/pages/analytics.py` (line 185)
- **Database Service**: `app/services/device_config_db.py`
- **Chart Creation**: `app/pages/analytics.py` (line 71)
- **Configuration Methods**:
  - `get_analog_config()`: Line 622
  - `get_digital_config()`: Line 718
  - `get_modbus_config()`: Line 801
  - `get_can_bus_config()`: Line 992

