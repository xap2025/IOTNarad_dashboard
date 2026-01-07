# Device "Load from Device" Specification

## 📋 Overview

Jab user dashboard mein **"Load from Device"** button click karta hai, device ko configuration data MQTT ke through bhejna hota hai. Ye document hardware team ke liye complete specification hai.

---

## 🔌 MQTT Topics

### Device ko Subscribe karna hai:
```
Cmd/SConfig/<Device-ID>
```
**Example:** `Cmd/SConfig/0x235b`

### Device ko Publish karna hai:
```
Ack/SConfig/<Device-ID>
```
**Example:** `Ack/SConfig/0x235b`

**Important:**
- `<Device-ID>` = Device ka Serial Number (jaisa database mein hai)
- QoS Level: **1** (At least once delivery)
- Retain Flag: **false**

---

## 📤 Server Request Format

Jab server "Load from Device" button click karta hai, device ko yeh message aayega:

**Topic:** `Cmd/SConfig/<Device-ID>`

**Payload:**
```json
{
  "command": "Analog"
}
```

**Possible Commands:**
- `"Analog"` - Analog tab ke liye
- `"Digital"` - Digital tab ke liye
- `"Modbus"` - RS485 MODBUS tab ke liye
- `"Canbus"` - CAN Bus tab ke liye

**Note:** Commands **capitalized** hote hain (first letter capital).

---

## 📥 Device Response Format

Device ko **5 seconds** ke andar response bhejna hai.

**Topic:** `Ack/SConfig/<Device-ID>`

**Payload Structure:**
```json
{
  "type": "Analog",
  "config": {
    // Configuration data (see below for each tab)
  }
}
```

**Important:**
- `type` field **must match** `command` field (capitalized)
- `config` field **must be present** with valid JSON structure
- Response **must be valid JSON**

---

## 📝 Configuration JSON Structures

### 1. Analog Tab

**Request:**
```json
{"command": "Analog"}
```

**Response:**
```json
{
  "type": "Analog",
  "config": {
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
        "name": "Pressure Sensor",
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
        "name": "Voltage Input",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 4,
        "enabled": false,
        "divider": 1,
        "multiplier": 1,
        "io_pin": "AIN3",
        "name": "Current Input",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": true,
        "value": 5.0,
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
        "name": "Motor Control",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "scan_rate": 1000
  }
}
```

**Fields:**
- `input_4_20ma`: Array of 4-20mA input channels (max 2 channels)
- `input_1_10v`: Array of 1-10V input channels (max 2 channels)
- `output_0_10v`: Array of 0-10V output channels (max 2 channels)
- `scan_rate`: Integer (seconds, must be >= 1000)

---

### 2. Digital Tab

**Request:**
```json
{"command": "Digital"}
```

**Response:**
```json
{
  "type": "Digital",
  "config": {
    "npn_input": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "INP1H",
        "name": "Sensor 1"
      },
      {
        "channel": 2,
        "enabled": false,
        "io_pin": "INP2H",
        "name": "Sensor 2"
      },
      {
        "channel": 3,
        "enabled": true,
        "io_pin": "INP3H",
        "name": "Sensor 3"
      },
      {
        "channel": 4,
        "enabled": false,
        "io_pin": "INP4H",
        "name": "Sensor 4"
      }
    ],
    "npn_output": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "OUTL1",
        "name": "Output 1"
      },
      {
        "channel": 2,
        "enabled": false,
        "io_pin": "OUTL2",
        "name": "Output 2"
      },
      {
        "channel": 3,
        "enabled": true,
        "io_pin": "OUTL3",
        "name": "Output 3"
      },
      {
        "channel": 4,
        "enabled": false,
        "io_pin": "OUTL4",
        "name": "Output 4"
      }
    ],
    "pnp_input": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "INP1L",
        "name": "PNP Input 1"
      },
      {
        "channel": 2,
        "enabled": false,
        "io_pin": "INP2L",
        "name": "PNP Input 2"
      },
      {
        "channel": 3,
        "enabled": true,
        "io_pin": "INP3L",
        "name": "PNP Input 3"
      },
      {
        "channel": 4,
        "enabled": false,
        "io_pin": "INP4L",
        "name": "PNP Input 4"
      }
    ],
    "pnp_output": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "OUTH1",
        "name": "PNP Output 1"
      },
      {
        "channel": 2,
        "enabled": false,
        "io_pin": "OUTH2",
        "name": "PNP Output 2"
      },
      {
        "channel": 3,
        "enabled": true,
        "io_pin": "OUTH3",
        "name": "PNP Output 3"
      },
      {
        "channel": 4,
        "enabled": false,
        "io_pin": "OUTH4",
        "name": "PNP Output 4"
      }
    ],
    "relay": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "RLY1",
        "name": "Relay 1"
      },
      {
        "channel": 2,
        "enabled": false,
        "io_pin": "RLY2",
        "name": "Relay 2"
      },
      {
        "channel": 3,
        "enabled": true,
        "io_pin": "RLY3",
        "name": "Relay 3"
      },
      {
        "channel": 4,
        "enabled": false,
        "io_pin": "RLY4",
        "name": "Relay 4"
      }
    ],
    "scan_rate": 1000
  }
}
```

**Fields:**
- `npn_input`: Array of NPN input channels (max 4 channels)
- `npn_output`: Array of NPN output channels (max 4 channels)
- `pnp_input`: Array of PNP input channels (max 4 channels)
- `pnp_output`: Array of PNP output channels (max 4 channels)
- `relay`: Array of relay channels (max 4 channels)
- `scan_rate`: Integer (seconds, must be >= 1000)

**Note:** Empty arrays allowed (if no channels configured).

---

### 3. RS485 MODBUS Tab

**Request:**
```json
{"command": "Modbus"}
```

**Response:**
```json
{
  "type": "Modbus",
  "config": {
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
        "register_address": "0x4000",
        "data_type": "int16",
        "endianness": "Big Endian",
        "variable_name": "Temperature"
      },
      {
        "index": 1,
        "slave_id": "2",
        "function_code": "0x03",
        "register_address": "0x5000",
        "data_type": "int8",
        "endianness": "Little Endian",
        "variable_name": "Pressure"
      },
      {
        "index": 2,
        "slave_id": "3",
        "function_code": "0x04",
        "register_address": "0x1234",
        "data_type": "float",
        "endianness": "Big Endian",
        "variable_name": "Flow Rate"
      }
    ]
  }
}
```

**Fields:**
- `communication_settings`: Object with baud_rate, data_bits, parity, stop_bits
- `protocol_settings`: Object with mode, role
- `polling_interval_ms`: Integer (milliseconds)
- `slave_devices`: Array of slave device configurations
  - `index`: Integer (0-based, sequential: 0, 1, 2, ...)
  - `slave_id`: String (e.g., "1", "2", "3")
  - `function_code`: String (e.g., "0x03", "0x04")
  - `register_address`: String (e.g., "0x4000", "0x5000")
  - `data_type`: String (e.g., "int8", "int16", "float")
  - `endianness`: String ("Big Endian" or "Little Endian")
  - `variable_name`: String (e.g., "Temperature", "Pressure")

**Important:**
- `slave_devices` array mein **jitne slaves hain, utne entries** honi chahiye
- Agar 5 slaves hain, to 5 entries bhejni hain
- `index` field **must be sequential** (0, 1, 2, 3, 4)

---

### 4. CAN Bus Tab

**Request:**
```json
{"command": "Canbus"}
```

**Response:**
```json
{
  "type": "Canbus",
  "config": {
    "communication_settings": {
      "baud_rate": 500,
      "identifier_length": "11-bit",
      "can_mode": "Normal",
      "filter_mode": "None",
      "filter_id": "0x123",
      "filter_mask": "0x7FF"
    },
    "can_messages": [
      {
        "index": 0,
        "can_id": "0x123",
        "direction": "TX",
        "period_ms": 100,
        "variable_name": "Message Name 1"
      },
      {
        "index": 1,
        "can_id": "0x124",
        "direction": "RX",
        "period_ms": 200,
        "variable_name": "Message Name 2"
      },
      {
        "index": 2,
        "can_id": "0x125",
        "direction": "TX",
        "period_ms": 300,
        "variable_name": "Message Name 3"
      }
    ],
    "data_mapping": [
      {
        "index": 0,
        "can_id": "0x123",
        "byte_position": "Byte 0",
        "data_length": "1 Byte",
        "data_type": "int8",
        "endianness": "Big Endian",
        "variable_name": "Variable Name 1",
        "scale_factor": 1.0,
        "offset": 0.0
      },
      {
        "index": 1,
        "can_id": "0x124",
        "byte_position": "Byte 1",
        "data_length": "2 Bytes",
        "data_type": "int16",
        "endianness": "Little Endian",
        "variable_name": "Variable Name 2",
        "scale_factor": 1.2,
        "offset": 0.5
      },
      {
        "index": 2,
        "can_id": "0x125",
        "byte_position": "Byte 2",
        "data_length": "4 Bytes",
        "data_type": "float",
        "endianness": "Big Endian",
        "variable_name": "Variable Name 3",
        "scale_factor": 1.5,
        "offset": 0.3
      }
    ]
  }
}
```

**Fields:**

**communication_settings:**
- `baud_rate`: Integer (e.g., 125, 250, 500, 1000)
- `identifier_length`: String ("11-bit" or "29-bit")
- `can_mode`: String ("Normal", "Listen", "Loopback")
- `filter_mode`: String ("None", "Accept", "Reject")
- `filter_id`: String (hex format, e.g., "0x123")
- `filter_mask`: String (hex format, e.g., "0x7FF")

**can_messages:** Array of CAN message configurations
- `index`: Integer (0-based, sequential: 0, 1, 2, ...)
- `can_id`: String (hex format, e.g., "0x123")
- `direction`: String ("TX" or "RX")
- `period_ms`: Integer (milliseconds)
- `variable_name`: String (e.g., "Message Name 1")

**data_mapping:** Array of data mapping configurations
- `index`: Integer (0-based, sequential: 0, 1, 2, ...)
- `can_id`: String (hex format, e.g., "0x123")
- `byte_position`: String (e.g., "Byte 0", "Byte 1", ..., "Byte 7")
- `data_length`: String (e.g., "1 Byte", "2 Bytes", "4 Bytes", "8 Bytes")
- `data_type`: String (e.g., "int8", "uint8", "int16", "uint16", "int32", "uint32", "float")
- `endianness`: String ("Big Endian" or "Little Endian")
- `variable_name`: String (e.g., "Variable Name 1")
- `scale_factor`: Float (e.g., 1.0, 1.2, 1.5)
- `offset`: Float (e.g., 0.0, 0.5, 0.3)

**Important:**
- `can_messages` array mein **jitne messages hain, utne entries** honi chahiye
- `data_mapping` array mein **jitne mappings hain, utne entries** honi chahiye
- Agar 5 CAN messages hain, to 5 entries bhejni hain
- Agar 3 data mappings hain, to 3 entries bhejni hain
- `index` field **must be sequential** (0, 1, 2, 3, 4)

---

## ⚠️ Important Notes

### 1. Response Time
- Device ko **5 seconds** ke andar response bhejna **must** hai
- Agar timeout ho jata hai, server error show karega

### 2. Type Matching
- Response ka `type` field **must match** request ka `command` field
- Example: Request `{"command": "Analog"}` → Response `{"type": "Analog", ...}`

### 3. Config Field
- `config` field **must be present** in response
- `config` field **must be a valid JSON object** (not null, not empty string)

### 4. Array Handling
- Arrays empty ho sakti hain (e.g., `"slave_devices": []`)
- Arrays mein **jitne items hain, utne entries** bhejni hain
- **No extra fields** - sirf wahi fields bhejni hain jo UI mein hain

### 5. Field Types
- **Integers:** `baud_rate`, `data_bits`, `stop_bits`, `polling_interval_ms`, `period_ms`, `index`, `channel`
- **Floats:** `value`, `scale_factor`, `offset`
- **Strings:** `slave_id`, `function_code`, `register_address`, `can_id`, `variable_name`, etc.
- **Booleans:** `enabled`

### 6. Case Sensitivity
- Field names **case-sensitive** hain
- `"type"` (lowercase) not `"Type"`
- `"config"` (lowercase) not `"Config"`
- Values case-sensitive hain (e.g., `"TX"` not `"tx"`)

---

## 📋 Quick Reference Table

| Tab | Command | Response Type | Key Arrays |
|-----|---------|--------------|------------|
| **Analog** | `"Analog"` | `"Analog"` | `input_4_20ma`, `input_1_10v`, `output_0_10v` |
| **Digital** | `"Digital"` | `"Digital"` | `npn_input`, `npn_output`, `pnp_input`, `pnp_output`, `relay` |
| **RS485 MODBUS** | `"Modbus"` | `"Modbus"` | `slave_devices` |
| **CAN Bus** | `"Canbus"` | `"Canbus"` | `can_messages`, `data_mapping` |

---

## 🧪 Testing Example

### Step 1: Subscribe to Request Topic
```bash
mosquitto_sub -h mqtt -p 1883 -t "Cmd/SConfig/0x235b" -v
```

### Step 2: When Request Received
Server se aayega:
```
Cmd/SConfig/0x235b {"command":"Analog"}
```

### Step 3: Device Response
Device ko bhejna hai:
```bash
mosquitto_pub -h mqtt -p 1883 -t "Ack/SConfig/0x235b" -m '{"type":"Analog","config":{"input_4_20ma":[{"channel":1,"enabled":true,"divider":100,"multiplier":1,"io_pin":"AIN0","name":"Temperature","min_value":4,"max_value":20,"unit":"mA"}],"input_1_10v":[],"output_0_10v":[],"scan_rate":1000}}'
```

---

## ✅ Checklist for Hardware Team

- [ ] Device subscribes to `Cmd/SConfig/<Device-ID>` topic
- [ ] Device publishes to `Ack/SConfig/<Device-ID>` topic
- [ ] Device parses `{"command": "..."}` payload correctly
- [ ] Device responds within 5 seconds
- [ ] Response format: `{"type": "...", "config": {...}}`
- [ ] `type` field matches `command` field (capitalized)
- [ ] All required fields present in `config`
- [ ] Arrays contain correct number of entries (based on device configuration)
- [ ] Field types correct (int, float, string, bool)
- [ ] JSON is valid and parseable

---

**Last Updated:** 2026-01-07
**Status:** ✅ Complete specification for hardware team

