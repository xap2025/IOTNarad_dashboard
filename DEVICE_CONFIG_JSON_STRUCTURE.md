# Device Configuration JSON Structure

## Overview
Ye document sabhi device configurations (Analog, Digital, RS485 MODBUS, CAN Bus) ke liye complete JSON structure explain karta hai.

## Complete JSON Structure

### 1. Root Level Fields

```json
{
  "device_id": "esp32_gw_01",
  "metadata": { ... },
  "analog": { ... },
  "digital": { ... },
  "rs485_modbus": { ... },
  "can_bus": { ... },
  "mqtt": { ... },
  "network": { ... }
}
```

---

## 2. Metadata Section

```json
{
  "metadata": {
    "device_name": "ESP32-Gateway-01",
    "device_type": "esp32_gateway",
    "location": "Production Line 1",
    "description": "Main gateway for production monitoring",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T14:45:00Z",
    "version": "1.0.0"
  }
}
```

**Fields:**
- `device_name`: Device ka naam
- `device_type`: Device type (esp32_gateway, etc.)
- `location`: Device location
- `description`: Device description
- `created_at`: Creation timestamp (ISO 8601)
- `updated_at`: Last update timestamp (ISO 8601)
- `version`: Configuration version

---

## 3. Analog Configuration

### 3.1 Input 4-20mA

```json
{
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
      }
    ]
  }
}
```

**Fields:**
- `channel`: Channel number (1, 2, 3, ...)
- `enabled`: Enable/disable flag (true/false)
- `divider`: Divider value for scaling
- `multiplier`: Multiplier value for scaling
- `io_pin`: IO pin name (AIN0, AIN1, etc.)
- `name`: Channel name/label
- `min_value`: Minimum value (4 mA)
- `max_value`: Maximum value (20 mA)
- `unit`: Unit of measurement (mA)

### 3.2 Input 1-10V

```json
{
  "input_1_10v": [
    {
      "channel": 3,
      "enabled": true,
      "divider": 1000,
      "multiplier": 1,
      "io_pin": "AIN2",
      "name": "Flow Meter",
      "min_value": 1,
      "max_value": 10,
      "unit": "V"
    }
  ]
}
```

**Fields:** Same as 4-20mA, but `unit` is "V" and `min_value`/`max_value` are 1-10V

### 3.3 Output 0-10V

```json
{
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
    }
  ]
}
```

**Fields:**
- `value`: Current output value (0.0 to 10.0)
- Other fields same as input sections

---

## 4. Digital Configuration

### 4.1 NPN Input

```json
{
  "digital": {
    "npn_input": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "INP1H",
        "name": "Start Button",
        "pullup": true,
        "debounce_ms": 50
      }
    ]
  }
}
```

**Fields:**
- `channel`: Channel number
- `enabled`: Enable/disable flag
- `io_pin`: IO pin name (INP1H, INP2H, etc.)
- `name`: Channel name
- `pullup`: Pullup resistor enabled (true/false)
- `debounce_ms`: Debounce time in milliseconds

### 4.2 NPN Output

```json
{
  "npn_output": [
    {
      "channel": 1,
      "enabled": true,
      "io_pin": "OUTL1",
      "name": "Motor Control",
      "initial_state": false
    }
  ]
}
```

**Fields:**
- `initial_state`: Initial output state (true/false)
- Other fields same as input

### 4.3 PNP Input/Output

Same structure as NPN, but with different IO pins:
- PNP Input: `INP1L`, `INP2L`, etc.
- PNP Output: `OUTH1`, `OUTH2`, etc.

### 4.4 Relay

```json
{
  "relay": [
    {
      "channel": 1,
      "enabled": true,
      "io_pin": "RLY1",
      "name": "Main Power Relay",
      "initial_state": false
    }
  ]
}
```

**Fields:** Same as digital output

---

## 5. RS485 MODBUS Configuration

```json
{
  "rs485_modbus": {
    "enabled": true,
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
        "register_address": "0",
        "data_type": "int16",
        "endianness": "Big Endian",
        "variable_name": "Temperature",
        "register_count": 1
      }
    ]
  }
}
```

### Communication Settings
- `baud_rate`: 9600, 19200, 38400, 57600, 115200
- `data_bits`: 7 or 8
- `parity`: "None", "Even", "Odd"
- `stop_bits`: 1 or 2

### Protocol Settings
- `mode`: "RTU", "ASCII", "TCP"
- `role`: "Master" or "Slave"

### Slave Devices
- `index`: Device index (0, 1, 2, ...)
- `slave_id`: MODBUS slave ID (1-247)
- `function_code`: "0x01", "0x02", "0x03", "0x04", "0x05", "0x06", "0x0F", "0x10"
- `register_address`: Register address (decimal or hex)
- `data_type`: "int8", "uint8", "int16", "uint16", "int32", "uint32", "float32", "float64"
- `endianness`: "Big Endian" or "Little Endian"
- `variable_name`: Variable name for this register
- `register_count`: Number of registers to read (optional)

---

## 6. CAN Bus Configuration

```json
{
  "can_bus": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": 500,
      "identifier_length": "11-bit",
      "can_mode": "Normal",
      "filter_mode": "Accept",
      "filter_id": "0x123",
      "filter_mask": "0x7FF"
    },
    "can_messages": [
      {
        "index": 0,
        "can_id": "0x123",
        "direction": "TX",
        "period_ms": 100,
        "variable_name": "Engine Speed",
        "data_length": 8
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
        "variable_name": "Speed Low",
        "scale_factor": 1.0,
        "offset": 0.0
      }
    ]
  }
}
```

### Communication Settings
- `baud_rate`: 125, 250, 500, 1000 (kbps)
- `identifier_length`: "11-bit" or "29-bit"
- `can_mode`: "Normal", "Listen", "Loopback"
- `filter_mode`: "None", "Accept", "Reject"
- `filter_id`: Filter CAN ID (hex format, e.g., "0x123")
- `filter_mask`: Filter mask (hex format, e.g., "0x7FF")

### CAN Messages
- `index`: Message index (0, 1, 2, ...)
- `can_id`: CAN message ID (hex format)
- `direction`: "TX" (Transmit) or "RX" (Receive)
- `period_ms`: Message period in milliseconds
- `variable_name`: Variable name for this message
- `data_length`: Data length in bytes (typically 8)

### Data Mapping
- `index`: Mapping index (0, 1, 2, ...)
- `can_id`: CAN message ID (hex format)
- `byte_position`: "Byte 0" to "Byte 7"
- `data_length`: "1 Byte", "2 Bytes", "4 Bytes", "8 Bytes"
- `data_type`: "int8", "uint8", "int16", "uint16", "int32", "uint32", "float32", "float64"
- `endianness`: "Big Endian" or "Little Endian"
- `variable_name`: Variable name for this byte/bytes
- `scale_factor`: Scaling factor (float)
- `offset`: Offset value (float)

---

## 7. MQTT Configuration

```json
{
  "mqtt": {
    "broker": "mqtt",
    "port": 1883,
    "username": "",
    "password": "",
    "topic_prefix": "iotnarad/devices/esp32_gw_01",
    "publish_interval": 5,
    "qos": 1,
    "retain": false
  }
}
```

**Fields:**
- `broker`: MQTT broker hostname/IP
- `port`: MQTT port (usually 1883)
- `username`: MQTT username (optional)
- `password`: MQTT password (optional)
- `topic_prefix`: Topic prefix for this device
- `publish_interval`: Publish interval in seconds
- `qos`: Quality of Service (0, 1, or 2)
- `retain`: Retain messages (true/false)

---

## 8. Network Configuration

```json
{
  "network": {
    "wifi_ssid": "Production_WiFi",
    "wifi_password": "********",
    "ip_mode": "dhcp",
    "static_ip": "",
    "gateway": "",
    "subnet": "255.255.255.0",
    "dns": "8.8.8.8"
  }
}
```

**Fields:**
- `wifi_ssid`: WiFi SSID
- `wifi_password`: WiFi password
- `ip_mode`: "dhcp" or "static"
- `static_ip`: Static IP address (if ip_mode is "static")
- `gateway`: Gateway IP address
- `subnet`: Subnet mask
- `dns`: DNS server IP

---

## Usage Example

### Saving Configuration

```python
from app.services.device_config import DeviceConfigService

config_service = DeviceConfigService()

config = {
    "device_id": "esp32_gw_01",
    "metadata": { ... },
    "analog": { ... },
    "digital": { ... },
    "rs485_modbus": { ... },
    "can_bus": { ... },
    "mqtt": { ... },
    "network": { ... }
}

success = config_service.save_device_config("esp32_gw_01", config)
```

### Loading Configuration

```python
config = config_service.load_device_config("esp32_gw_01")
if config:
    print(f"Device: {config['metadata']['device_name']}")
    print(f"Analog channels: {len(config['analog']['input_4_20ma'])}")
    print(f"MODBUS slaves: {len(config['rs485_modbus']['slave_devices'])}")
```

---

## Notes

1. **All arrays** (input_4_20ma, slave_devices, can_messages, etc.) can have **multiple entries**
2. **Enabled flags** control whether a channel/device is active
3. **Index fields** are used for array ordering (0-based)
4. **Hex values** (CAN ID, Filter ID) should be in string format with "0x" prefix
5. **Timestamps** should be in ISO 8601 format with 'Z' suffix for UTC
6. **Empty/unused channels** should have `enabled: false` and `name: "-"`

---

## File Location

Configuration files are stored in: `data/configs/{device_id}.json`

Example: `data/configs/esp32_gw_01.json`

