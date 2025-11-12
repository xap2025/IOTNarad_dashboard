# Device Configuration - InfluxDB Table Structure

## 📊 Current Device_info Table Structure (Reference)

### Measurement: `Device_info`

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| **Sr_No** | Tag | Serial Number (Primary Key) | `TEST78787` |
| **Date_Of_Register** | Field (string) | Registration Date | `2025-11-11` |
| **Device_Name** | Field (string) | Device Name | `Unnamed` |
| **Owner** | Field (string) | Device Owner | `Unassigned` |
| **time** | Timestamp | Record Creation Time | `2025-11-11T12:47:43.798Z` |

### InfluxDB Query Example:
```sql
SELECT *
FROM "Device_info"
WHERE time > now() - interval '96 hour';
```

---

## 🔧 Proposed Device_configuration Table Structure

### Measurement: `Device_configuration`

#### **Option 1: Single Measurement with JSON Field (Recommended for Complex Config)**

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| **Sr_No** | Tag | Serial Number (Links to Device_info) | `TEST78787` |
| **Config_Type** | Tag | Type of Configuration | `analog`, `digital`, `modbus`, `canbus`, `network`, `mqtt` |
| **Config_JSON** | Field (string) | Full Configuration as JSON | `{"channel": 1, "enabled": true, ...}` |
| **Updated_By** | Field (string) | User who updated | `admin` |
| **Version** | Field (integer) | Configuration Version | `1` |
| **time** | Timestamp | Last Update Time | `2025-11-11T12:47:43.798Z` |

**Pros:**
- Simple structure
- Easy to store complex nested configs
- One measurement for all config types

**Cons:**
- JSON parsing needed for queries
- Harder to query specific fields

---

### 📊 Visual Table View for Option 1 (InfluxDB Data Explorer)

#### Measurement: `Device_configuration`

**Table View:**

| Sr_No | Config_Type | Config_JSON | Updated_By | Version | time |
|-------|-------------|------------|------------|---------|------|
| TEST78787 | analog | `{"input_4_20ma":[{"channel":1,"enabled":true,"name":"Temp Sensor","io":"AIN0","div":1.0,"mul":1.0},{"channel":2,"enabled":false,"name":"-","io":"AIN1","div":1.0,"mul":1.0}],"input_1_10v":[{"channel":3,"enabled":true,"name":"Pressure","io":"AIN2","div":1.0,"mul":1.0}],"output_0_10v":[{"channel":1,"enabled":true,"name":"Control","io":"DOUT0","div":1.0,"mul":1.0,"value":0.0}]}` | admin | 1 | 2025-11-11T12:47:43.798Z |
| TEST78787 | digital | `{"npn_input":[{"channel":1,"enabled":true,"name":"Door Sensor","io":"INP1H"},{"channel":2,"enabled":false,"name":"-","io":"INP2H"}],"relay":[{"channel":1,"enabled":true,"name":"Relay 1","io":"RLY1"}]}` | admin | 1 | 2025-11-11T12:47:44.123Z |
| TEST78787 | modbus | `{"enabled":true,"baudrate":9600,"slave_address":1,"data_bits":8,"stop_bits":1,"parity":"none"}` | admin | 1 | 2025-11-11T12:47:44.456Z |
| TEST78787 | canbus | `{"enabled":true,"speed":500,"filter":"0x123"}` | admin | 1 | 2025-11-11T12:47:44.789Z |
| TEST78787 | network | `{"wifi_ssid":"MyNetwork","wifi_password":"***","ip_mode":"dhcp","static_ip":"","gateway":"","subnet":"255.255.255.0","dns":"8.8.8.8"}` | admin | 1 | 2025-11-11T12:47:45.012Z |
| TEST78787 | mqtt | `{"broker":"mqtt.example.com","port":1883,"username":"","password":"","topic_prefix":"iotnarad/devices/TEST78787","publish_interval":5}` | admin | 1 | 2025-11-11T12:47:45.345Z |

**Note:** Config_JSON column mein full JSON string dikhega. InfluxDB Data Explorer mein yeh ek long string ke roop mein dikhega.

---

#### **Expanded View (JSON Parsed - InfluxDB UI mein expand karne par):**

**Row 1 - Analog Config:**
```
Sr_No: TEST78787
Config_Type: analog
Config_JSON: {
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
}
Updated_By: admin
Version: 1
time: 2025-11-11T12:47:43.798Z
```

**Row 2 - Digital Config:**
```
Sr_No: TEST78787
Config_Type: digital
Config_JSON: {
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
}
Updated_By: admin
Version: 1
time: 2025-11-11T12:47:44.123Z
```

**Row 3 - Modbus Config:**
```
Sr_No: TEST78787
Config_Type: modbus
Config_JSON: {
  "enabled": true,
  "baudrate": 9600,
  "slave_address": 1,
  "data_bits": 8,
  "stop_bits": 1,
  "parity": "none"
}
Updated_By: admin
Version: 1
time: 2025-11-11T12:47:44.456Z
```

**Row 4 - CAN Bus Config:**
```
Sr_No: TEST78787
Config_Type: canbus
Config_JSON: {
  "enabled": true,
  "speed": 500,
  "filter": "0x123"
}
Updated_By: admin
Version: 1
time: 2025-11-11T12:47:44.789Z
```

---

#### **Filtered View Examples:**

**1. Get All Configs for One Device:**
```
Filter: Sr_No = 'TEST78787'
Result: 6 rows (one for each config type)
```

**2. Get All Analog Configs (All Devices):**
```
Filter: Config_Type = 'analog'
Result: All devices' analog configurations
```

**3. Get Latest Config for a Device:**
```
Filter: Sr_No = 'TEST78787' AND Config_Type = 'modbus'
Sort: time DESC
Limit: 1
Result: Latest modbus config for TEST78787
```

---

#### **InfluxDB Data Explorer UI Appearance:**

**Schema Browser:**
```
Bucket: iot_data_gcp
  └─ Measurement: Device_configuration
      ├─ Fields:
      │   ├─ Config_JSON (string)
      │   ├─ Updated_By (string)
      │   └─ Version (integer)
      └─ Tag Keys:
          ├─ Sr_No
          └─ Config_Type
```

**Table View (Collapsed JSON):**
- Config_JSON column mein long string dikhega
- Click karne par expand ho sakta hai (depends on InfluxDB UI)
- JSON ko manually parse karna padega for specific fields

**Table View (Expanded - if UI supports):**
- JSON formatted dikhega
- Nested structure visible hogi
- Easy to read but still needs parsing for queries

---

#### **Query Examples for Option 1:**

```sql
-- Get all configs for a device
SELECT *
FROM "Device_configuration"
WHERE "Sr_No" = 'TEST78787'
  AND time > now() - interval '1 year'
ORDER BY time DESC;

-- Get latest analog config for a device
SELECT *
FROM "Device_configuration"
WHERE "Sr_No" = 'TEST78787'
  AND "Config_Type" = 'analog'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;

-- Get all modbus configs (all devices)
SELECT *
FROM "Device_configuration"
WHERE "Config_Type" = 'modbus'
  AND time > now() - interval '1 year'
ORDER BY time DESC;
```

**Note:** Specific JSON fields ko query karne ke liye, InfluxDB mein JSON parsing functions use karne padenge (if available) ya application level par parse karna padega.

---

#### **Option 2: Separate Measurements by Config Type (Better for Querying)**

### Measurement: `Device_config_analog`

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| **Sr_No** | Tag | Serial Number | `TEST78787` |
| **Input_Type** | Tag | Input Type | `input_4_20ma`, `input_1_10v`, `output_0_10v` |
| **Channel** | Tag | Channel Number | `1`, `2`, `3`, `4` |
| **Enabled** | Field (boolean) | Channel Enabled | `true`, `false` |
| **Name** | Field (string) | Channel Name | `Temperature Sensor` |
| **IO_Pin** | Field (string) | IO Pin Name | `AIN0`, `AIN1`, `DOUT0` |
| **Div** | Field (float) | Division Factor | `1.0`, `10.0` |
| **Mul** | Field (float) | Multiplication Factor | `1.0`, `2.5` |
| **Value** | Field (float) | Output Value (for outputs) | `0.0`, `5.5` |
| **time** | Timestamp | Last Update Time | `2025-11-11T12:47:43.798Z` |

**Example Data:**
```
Sr_No: TEST78787
Input_Type: input_4_20ma
Channel: 1
Enabled: true
Name: Temperature Sensor
IO_Pin: AIN0
Div: 1.0
Mul: 1.0
time: 2025-11-11T12:47:43.798Z
```

---

### Measurement: `Device_config_digital`

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| **Sr_No** | Tag | Serial Number | `TEST78787` |
| **IO_Type** | Tag | IO Type | `npn_input`, `npn_output`, `pnp_input`, `pnp_output`, `relay` |
| **Channel** | Tag | Channel Number | `1`, `2`, `3`, `4` |
| **Enabled** | Field (boolean) | Channel Enabled | `true`, `false` |
| **Name** | Field (string) | Channel Name | `Door Sensor` |
| **IO_Pin** | Field (string) | IO Pin Name | `INP1H`, `OUTL1`, `RLY1` |
| **time** | Timestamp | Last Update Time | `2025-11-11T12:47:43.798Z` |

**Example Data:**
```
Sr_No: TEST78787
IO_Type: npn_input
Channel: 1
Enabled: true
Name: Door Sensor
IO_Pin: INP1H
time: 2025-11-11T12:47:43.798Z
```

---

### Measurement: `Device_config_modbus`

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| **Sr_No** | Tag | Serial Number | `TEST78787` |
| **Enabled** | Field (boolean) | Modbus Enabled | `true`, `false` |
| **Baudrate** | Field (integer) | Baud Rate | `9600`, `19200`, `38400` |
| **Slave_Address** | Field (integer) | Slave Address | `1`, `2`, `3` |
| **Data_Bits** | Field (integer) | Data Bits | `8` |
| **Stop_Bits** | Field (integer) | Stop Bits | `1`, `2` |
| **Parity** | Field (string) | Parity | `none`, `even`, `odd` |
| **time** | Timestamp | Last Update Time | `2025-11-11T12:47:43.798Z` |

**Example Data:**
```
Sr_No: TEST78787
Enabled: true
Baudrate: 9600
Slave_Address: 1
Data_Bits: 8
Stop_Bits: 1
Parity: none
time: 2025-11-11T12:47:43.798Z
```

---

### Measurement: `Device_config_canbus`

| Column Name | Type | Description | Example |
|------------|------|-------------|---------|
| **Sr_No** | Tag | Serial Number | `TEST78787` |
| **Enabled** | Field (boolean) | CAN Bus Enabled | `true`, `false` |
| **Speed** | Field (integer) | CAN Speed | `500`, `250`, `1000` |
| **Filter** | Field (string) | CAN Filter | `0x123`, `0x456` |
| **time** | Timestamp | Last Update Time | `2025-11-11T12:47:43.798Z` |

**Example Data:**
```
Sr_No: TEST78787
Enabled: true
Speed: 500
Filter: 0x123
time: 2025-11-11T12:47:43.798Z
```

---

## 📋 InfluxDB Query Examples

### Get All Analog Config for a Device:
```sql
SELECT *
FROM "Device_config_analog"
WHERE "Sr_No" = 'TEST78787'
  AND time > now() - interval '1 year'
ORDER BY time DESC;
```

### Get All Digital Inputs for a Device:
```sql
SELECT *
FROM "Device_config_digital"
WHERE "Sr_No" = 'TEST78787'
  AND "IO_Type" = 'npn_input'
  AND time > now() - interval '1 year'
ORDER BY "Channel";
```

### Get Modbus Config for a Device:
```sql
SELECT *
FROM "Device_config_modbus"
WHERE "Sr_No" = 'TEST78787'
  AND time > now() - interval '1 year'
ORDER BY time DESC
LIMIT 1;
```

### Get All Configurations for a Device (All Types):
```sql
-- Analog
SELECT * FROM "Device_config_analog" WHERE "Sr_No" = 'TEST78787' AND time > now() - interval '1 year';

-- Digital
SELECT * FROM "Device_config_digital" WHERE "Sr_No" = 'TEST78787' AND time > now() - interval '1 year';

-- Modbus
SELECT * FROM "Device_config_modbus" WHERE "Sr_No" = 'TEST78787' AND time > now() - interval '1 year';

-- CAN Bus
SELECT * FROM "Device_config_canbus" WHERE "Sr_No" = 'TEST78787' AND time > now() - interval '1 year';
```

---

## 🎯 Recommended Approach

**Option 2 (Separate Measurements)** is recommended because:
1. ✅ Easy to query specific config types
2. ✅ Better performance (no JSON parsing)
3. ✅ Clear structure for hardware engineers
4. ✅ Easy to filter by channel, type, etc.
5. ✅ Can track history of each config type separately

---

## 📊 Visual Table View (InfluxDB Data Explorer)

### Device_config_analog Table View:
```
| Sr_No      | Input_Type   | Channel | Enabled | Name              | IO_Pin | Div  | Mul  | time                    |
|------------|--------------|---------|---------|-------------------|--------|------|------|-------------------------|
| TEST78787  | input_4_20ma | 1       | true    | Temperature Sensor| AIN0   | 1.0  | 1.0  | 2025-11-11T12:47:43.798Z|
| TEST78787  | input_4_20ma | 2       | false   | -                 | AIN1   | 1.0  | 1.0  | 2025-11-11T12:47:43.798Z|
| TEST78787  | input_1_10v  | 3       | true    | Pressure Sensor   | AIN2   | 1.0  | 1.0  | 2025-11-11T12:47:43.798Z|
| TEST78787  | output_0_10v | 1       | true    | Control Output    | DOUT0  | 1.0  | 1.0  | 0.0  | 2025-11-11T12:47:43.798Z|
```

### Device_config_digital Table View:
```
| Sr_No      | IO_Type   | Channel | Enabled | Name        | IO_Pin | time                    |
|------------|-----------|---------|---------|-------------|--------|-------------------------|
| TEST78787  | npn_input | 1       | true    | Door Sensor | INP1H  | 2025-11-11T12:47:43.798Z|
| TEST78787  | npn_input | 2       | false   | -           | INP2H  | 2025-11-11T12:47:43.798Z|
| TEST78787  | relay     | 1       | true    | Relay 1     | RLY1   | 2025-11-11T12:47:43.798Z|
```

### Device_config_modbus Table View:
```
| Sr_No      | Enabled | Baudrate | Slave_Address | Data_Bits | Stop_Bits | Parity | time                    |
|------------|---------|----------|----------------|-----------|------------|--------|-------------------------|
| TEST78787  | true    | 9600     | 1              | 8         | 1          | none   | 2025-11-11T12:47:43.798Z|
```

### Device_config_canbus Table View:
```
| Sr_No      | Enabled | Speed | Filter | time                    |
|------------|---------|-------|--------|-------------------------|
| TEST78787  | true    | 500   | 0x123  | 2025-11-11T12:47:43.798Z|
```

---

## 🔗 Relationship with Device_info

- **Device_info.Sr_No** = **Device_config_*.Sr_No** (Foreign Key relationship)
- One device can have multiple configuration records (one per channel/type)
- Each configuration update creates a new timestamped record (history tracking)

---

## 💡 Implementation Notes

1. **Tags vs Fields:**
   - **Tags**: Sr_No, Input_Type, IO_Type, Channel (for filtering/indexing)
   - **Fields**: Enabled, Name, IO_Pin, Div, Mul, Value (actual data)

2. **Time Series:**
   - Each configuration change creates a new record with new timestamp
   - Latest config = `ORDER BY time DESC LIMIT 1`

3. **Query Performance:**
   - Use tags for filtering (faster)
   - Use fields for data retrieval

4. **Data Retention:**
   - Keep all history for audit trail
   - Or use retention policy to auto-delete old configs

---

## 📝 Summary

**4 Separate Measurements:**
1. `Device_config_analog` - Analog I/O configurations
2. `Device_config_digital` - Digital I/O configurations  
3. `Device_config_modbus` - RS485 Modbus configurations
4. `Device_config_canbus` - CAN Bus configurations

**Common Structure:**
- `Sr_No` as Tag (links to Device_info)
- Type-specific tags for filtering
- Configuration fields as data
- `time` for versioning/history

This structure makes it easy for hardware engineers to:
- Query specific device configurations
- Filter by channel, type, etc.
- Track configuration history
- Export configurations for device programming

