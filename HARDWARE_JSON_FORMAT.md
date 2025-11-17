# 📡 Hardware JSON Format - Device_Config_Analog

यह document hardware engineers के लिए है, जो **exact JSON structure** दिखाता है जो MQTT के through hardware को भेजा जाता है।

---

## 🔄 Data Flow

```
UI (Dash) 
  ↓
Build JSON (ConfigJSONBuilder)
  ↓
Save to InfluxDB (Device_Config_Analog)
  ↓
Retrieve & Merge All Sections
  ↓
Publish via MQTT to Hardware
  ↓
Topic: Dev/Checksum/<Device ID>
```

---

## 📊 Complete JSON Structure (MQTT Payload)

जब कोई भी tab (Analog/Digital/RS485/CAN Bus) में "Save Configuration" button click होता है, तो **complete merged JSON** hardware को भेजा जाता है:

```json
{
  "device_id": "TEST88888",
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": false,
        "divider": 1,
        "multiplier": 1,
        "io_pin": "AIN0",
        "name": "AIN0",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      },
      {
        "channel": 2,
        "enabled": true,
        "divider": 10,
        "multiplier": 1,
        "io_pin": "AIN1",
        "name": "Temperature Sensor",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": true,
        "divider": 1,
        "multiplier": 1,
        "io_pin": "AIN2",
        "name": "AIN2",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 4,
        "enabled": false,
        "divider": 100,
        "multiplier": 1,
        "io_pin": "AIN3",
        "name": "Pressure Sensor",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": true,
        "value": 5.5,
        "io_pin": "DOUT0",
        "name": "DOUT0",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 2,
        "enabled": false,
        "value": 0.0,
        "io_pin": "DOUT1",
        "name": "Valve Control",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "scan_rate": 1000
  },
  "digital": {
    "scan_rate": 1000,
    "npn_input": [...],
    "npn_output": [...],
    "pnp_input": [...],
    "pnp_output": [...],
    "relay": [...]
  },
  "rs485_modbus": {
    "enabled": true,
    "communication_settings": {...},
    "protocol_settings": {...},
    "polling_interval_ms": 1000,
    "slave_devices": [...]
  },
  "can_bus": {
    "enabled": true,
    "communication_settings": {...},
    "can_messages": [...],
    "data_mapping": [...]
  }
}
```

---

## 📋 Analog Section - Detailed Structure

### 1. Input 4-20mA (`input_4_20ma`)

```json
{
  "input_4_20ma": [
    {
      "channel": 1,              // Channel number (1 or 2)
      "enabled": true,           // Boolean: Channel enabled/disabled
      "divider": 10,             // Integer: Divider value (1, 10, 100, etc.)
      "multiplier": 1,           // Integer: Multiplier value
      "io_pin": "AIN0",          // String: Physical IO pin name
      "name": "Temperature",     // String: User-defined name/label
      "min_value": 4,            // Integer: Minimum value (always 4 for 4-20mA)
      "max_value": 20,           // Integer: Maximum value (always 20 for 4-20mA)
      "unit": "mA"               // String: Unit (always "mA")
    }
  ]
}
```

**Important Notes:**
- `channel`: 1-2 (चैनल 1 और 2 के लिए)
- `enabled`: `true` = channel active, `false` = channel disabled
- `divider`: 1, 10, 100, 1000, etc.
- `multiplier`: 1, 10, 50, etc.
- `min_value`: हमेशा `4` (4-20mA range)
- `max_value`: हमेशा `20` (4-20mA range)

---

### 2. Input 0-10V (`input_1_10v`)

```json
{
  "input_1_10v": [
    {
      "channel": 3,              // Channel number (3 or 4)
      "enabled": true,           // Boolean: Channel enabled/disabled
      "divider": 1,              // Integer: Divider value
      "multiplier": 1,           // Integer: Multiplier value
      "io_pin": "AIN2",          // String: Physical IO pin name (AIN2 or AIN3)
      "name": "Pressure Sensor", // String: User-defined name/label
      "min_value": 0,            // Integer: Minimum value (always 0 for 0-10V)
      "max_value": 10,           // Integer: Maximum value (always 10 for 0-10V)
      "unit": "V"                // String: Unit (always "V")
    }
  ]
}
```

**Important Notes:**
- `channel`: 3-4 (चैनल 3 और 4 के लिए)
- `min_value`: हमेशा `0` (0-10V range)
- `max_value`: हमेशा `10` (0-10V range)

---

### 3. Output 0-10V (`output_0_10v`) ⚡ **KEY SECTION**

```json
{
  "output_0_10v": [
    {
      "channel": 1,              // Channel number (1 or 2)
      "enabled": true,           // Boolean: Channel enabled/disabled
      "value": 5.5,              // Float: Output voltage value (0.0 to 10.0 volts)
      "io_pin": "DOUT0",         // String: Physical IO pin name (DOUT0 or DOUT1)
      "name": "Valve Control",   // String: User-defined name/label
      "min_value": 0,            // Integer: Minimum value (always 0)
      "max_value": 10,           // Integer: Maximum value (always 10)
      "unit": "V"                // String: Unit (always "V")
    },
    {
      "channel": 2,
      "enabled": false,
      "value": 0.0,
      "io_pin": "DOUT1",
      "name": "DOUT1",
      "min_value": 0,
      "max_value": 10,
      "unit": "V"
    }
  ]
}
```

**Important Notes:**
- `channel`: 1-2 (चैनल 1 और 2 के लिए)
- `value`: **Float type** - Output voltage (0.0 to 10.0 volts)
  - Examples: `0.0`, `5.5`, `10.0`, `7.3`, etc.
  - **IMPORTANT:** Database में यह **integer (millivolts)** में store होता है (5500 mV = 5.5V), लेकिन JSON में **float (volts)** में convert होकर भेजा जाता है
- `enabled`: `true` = output channel active, `false` = disabled
- `io_pin`: `"DOUT0"` (channel 1) या `"DOUT1"` (channel 2)

---

### 4. Scan Rate (`scan_rate`)

```json
{
  "scan_rate": 1000              // Integer: Scan rate in seconds (minimum 1000)
}
```

**Important Notes:**
- **Global parameter** - सभी analog channels (inputs और outputs) के लिए same value
- Minimum value: `1000` seconds
- यह सभी analog channels के लिए apply होता है

---

## 🔄 Value Storage & Conversion

### Database (InfluxDB):
- `value` field: **Integer type** (millivolts)
- Example: `5500` = 5.5V, `0` = 0.0V, `10000` = 10.0V

### JSON (MQTT Payload):
- `value` field: **Float type** (volts)
- Example: `5.5` = 5.5V, `0.0` = 0.0V, `10.0` = 10.0V

**Conversion Formula:**
```
Database (mV) → JSON (V): value_volts = value_millivolts / 1000.0
JSON (V) → Database (mV): value_millivolts = int(round(value_volts * 1000))
```

---

## 📡 MQTT Topic & Message Format

### Topic Pattern:
```
Dev/Checksum/<Device ID>
```

### Example:
```
Topic: Dev/Checksum/TEST88888
```

### Message Format:
```json
{
  "device_id": "TEST88888",
  "analog": { ... },
  "digital": { ... },
  "rs485_modbus": { ... },
  "can_bus": { ... }
}
```

### Message Properties:
- **QoS**: 1 (At least once delivery)
- **Retain**: False
- **Encoding**: UTF-8 JSON

---

## 📋 Complete Example (Real-World)

```json
{
  "device_id": "NAD-6625",
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": true,
        "divider": 100,
        "multiplier": 1,
        "io_pin": "AIN0",
        "name": "Temperature Sensor",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      },
      {
        "channel": 2,
        "enabled": false,
        "divider": 1,
        "multiplier": 1,
        "io_pin": "AIN1",
        "name": "AIN1",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": true,
        "divider": 500,
        "multiplier": 1,
        "io_pin": "AIN2",
        "name": "Pressure Sensor",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 4,
        "enabled": false,
        "divider": 1,
        "multiplier": 100,
        "io_pin": "AIN3",
        "name": "AIN3",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": true,
        "value": 5.5,
        "io_pin": "DOUT0",
        "name": "Valve Control",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 2,
        "enabled": false,
        "value": 0.0,
        "io_pin": "DOUT1",
        "name": "DOUT1",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "scan_rate": 2000
  }
}
```

---

## ✅ Hardware Implementation Checklist

Hardware engineer को निम्नलिखित implement करना होगा:

1. ✅ **MQTT Subscribe**: Topic `Dev/Checksum/<Device ID>` पर subscribe करें
2. ✅ **JSON Parsing**: Incoming JSON message parse करें
3. ✅ **Analog Configuration**:
   - `analog.input_4_20ma[]` - 4-20mA inputs process करें
   - `analog.input_1_10v[]` - 0-10V inputs process करें
   - `analog.output_0_10v[]` - 0-10V outputs set करें ⚡
   - `analog.scan_rate` - Scan rate apply करें
4. ✅ **Output Value**: `output_0_10v[].value` को **float (volts)** के रूप में read करें
5. ✅ **Channel Enable**: `enabled: false` वाले channels को skip करें
6. ✅ **Acknowledgment**: Config receive करने के बाद `Dev/ConfigACK/<Device ID>` topic पर acknowledgment भेजें

---

## 🎯 Key Points for Hardware

1. **Value Type**: `output_0_10v[].value` हमेशा **float (decimal)** में आएगा
   - Range: `0.0` to `10.0` volts
   - Example: `5.5` = 5.5 volts, `0.0` = 0 volts
2. **Channel Numbers**: 
   - Input 4-20mA: Channels 1, 2
   - Input 0-10V: Channels 3, 4
   - Output 0-10V: Channels 1, 2
3. **Scan Rate**: Global parameter, सभी analog channels के लिए same
4. **IO Pins**: Physical pin names (`AIN0`, `AIN1`, `AIN2`, `AIN3`, `DOUT0`, `DOUT1`)

---

## 📞 Support

अगर hardware implementation में कोई confusion हो, तो:
1. इस document को reference करें
2. Actual JSON message logs check करें
3. MQTT topic `Dev/Checksum/<Device ID>` पर subscribe करके live messages देखें

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-17  
**Status**: ✅ Active

