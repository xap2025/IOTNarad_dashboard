# MQTT Communication Guide: Naman (Device) ↔ Ridhi (Server)

## 📋 Overview

This document explains the MQTT communication between **Naman** (Hardware/Device) and **Ridhi** (Server/Software Dashboard).

**MQTT Broker**: `mqtt:1883` (or configured via `MQTT_BROKER` environment variable)  
**Protocol**: MQTT 3.1.1  
**QoS**: 1 (Quality of Service Level 1 - At least once delivery)

---

## 🎯 Quick Reference Table

| Purpose | Topic Pattern | Publisher | Subscriber | Data Type |
|---------|--------------|-----------|------------|-----------|
| **Device Sensor Data** | `iotnarad/devices/<Device-ID>/data` | Naman | Ridhi | JSON (sensor readings) |
| **Device Status** | `iotnarad/devices/<Device-ID>/status` | Naman | Ridhi | JSON (online/offline) |
| **Device Registration** | `Dev/Init/Reg/<Device-ID>` | Naman | Ridhi | JSON (device info) |
| **Complete Config** | `Dev/Checksum/<Device-ID>` | Ridhi | Naman | JSON (full config) |
| **Request Config** | `Cmd/SConfig/<Device-ID>` | Ridhi | Naman | JSON (command) |
| **Config Reply** | `Ack/SConfig/<Device-ID>` | Naman | Ridhi | JSON (config data) |
| **Send Config** | `Write/DConfig/<Device-ID>` | Ridhi | Naman | JSON (config data) |
| **Config ACK** | `Config/ACK/<Device-ID>` | Naman | Ridhi | JSON (acknowledgment) |
| **Commands** | `iotnarad/devices/<Device-ID>/cmd` | Ridhi | Naman | JSON (command) |
| **Server ACK** | `Dev/Ack/<Device-ID>` | Ridhi | Naman | JSON (acknowledgment) |

---

## 📤 Naman (Device) - What to Publish

### 1. Device Sensor Data
**Topic**: `iotnarad/devices/<Device-ID>/data`  
**QoS**: 1  
**Retain**: false  
**Frequency**: Periodic (e.g., every 5 seconds)

**Payload Example**:
```json
{
  "timestamp": "2025-12-06T17:30:00Z",
  "analog": {
    "input_4_20ma": [
      {"channel": 1, "value": 12.5},
      {"channel": 2, "value": 15.2}
    ],
    "input_1_10v": [
      {"channel": 3, "value": 5.5},
      {"channel": 4, "value": 7.8}
    ]
  },
  "digital": {
    "npn_input": [
      {"channel": 1, "value": true},
      {"channel": 2, "value": false}
    ],
    "relay": [
      {"channel": 1, "value": false}
    ]
  }
}
```

**Purpose**: Send real-time sensor readings and I/O states to the server.

---

### 2. Device Status
**Topic**: `iotnarad/devices/<Device-ID>/status`  
**QoS**: 1  
**Retain**: false  
**Frequency**: On connect/disconnect, or periodic heartbeat

**Payload Example**:
```json
{
  "status": "online",
  "timestamp": "2025-12-06T17:30:00Z",
  "uptime": 3600,
  "firmware_version": "1.0.0"
}
```

**Purpose**: Inform server about device online/offline status.

---

### 3. Device Registration/Initialization
**Topic**: `Dev/Init/Reg/<Device-ID>`  
**QoS**: 1  
**Retain**: false  
**Frequency**: On device boot/startup

**Payload Example**:
```json
{
  "device_id": "ESP32_GW_001",
  "device_type": "esp32_gateway",
  "firmware_version": "1.0.0",
  "mac_address": "AA:BB:CC:DD:EE:FF",
  "ip_address": "192.168.1.100",
  "timestamp": "2025-12-06T17:30:00Z"
}
```

**Purpose**: Register device with server when it first starts or reboots.

---

### 4. Configuration Read Reply
**Topic**: `Ack/SConfig/<Device-ID>`  
**QoS**: 1  
**Retain**: false  
**Frequency**: Only when server requests configuration

**Payload Example (Analog)**:
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
        "name": "Temperature"
      }
    ],
    "input_1_10v": [],
    "output_0_10v": [],
    "scan_rate": 2000
  }
}
```

**Payload Example (Digital)**:
```json
{
  "type": "Digital",
  "config": {
    "npn_input": [
      {
        "channel": 1,
        "enabled": true,
        "io_pin": "INP1H",
        "name": "Sensor1"
      }
    ],
    "scan_rate": 1000
  }
}
```

**Payload Example (MODBUS)**:
```json
{
  "type": "Modbus",
  "config": {
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
    "slave_devices": [...]
  }
}
```

**Payload Example (CAN Bus)**:
```json
{
  "type": "Canbus",
  "config": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": 500,
      "identifier_length": "11-bit",
      "can_mode": "Normal"
    },
    "can_messages": [...],
    "data_mapping": [...]
  }
}
```

**Purpose**: Reply to server's configuration read request (`Cmd/SConfig/<Device-ID>`).

---

### 5. Configuration Write Acknowledgment
**Topic**: `Config/ACK/<Device-ID>`  
**QoS**: 1  
**Retain**: false  
**Frequency**: Only when server sends configuration

**Payload Example**:
```json
{
  "Result": "OK"
}
```

**Purpose**: Acknowledge that configuration was received and applied successfully.

---

## 📥 Naman (Device) - What to Subscribe

### 1. Complete Configuration
**Topic**: `Dev/Checksum/<Device-ID>`  
**QoS**: 1  
**Retain**: true (server publishes with retain=true)

**Payload Example**:
```json
{
  "device_id": "ESP32_GW_001",
  "analog": {...},
  "digital": {...},
  "rs485_modbus": {...},
  "can_bus": {...}
}
```

**Purpose**: Receive complete device configuration from server (published when user clicks "Save Configuration" in dashboard).

---

### 2. Configuration Read Request
**Topic**: `Cmd/SConfig/<Device-ID>`  
**QoS**: 1  
**Retain**: false

**Payload Example**:
```json
{
  "command": "Analog"
}
```

**Possible Commands**: `"Analog"`, `"Digital"`, `"Modbus"`, `"Canbus"`

**Purpose**: Server requests specific configuration section. Device should reply on `Ack/SConfig/<Device-ID>`.

---

### 3. Configuration Write Request
**Topic**: `Write/DConfig/<Device-ID>`  
**QoS**: 1  
**Retain**: false

**Payload Example (Analog)**:
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
        "name": "Temperature"
      }
    ],
    "scan_rate": 2000
  }
}
```

**Purpose**: Server sends configuration to device. Device should apply it and reply with ACK on `Config/ACK/<Device-ID>`.

---

### 4. Commands
**Topic**: `iotnarad/devices/<Device-ID>/cmd`  
**QoS**: 1  
**Retain**: false

**Payload Example**:
```json
{
  "command": "restart",
  "params": {},
  "timestamp": "2025-12-06T17:30:00Z"
}
```

**Purpose**: Receive commands from server (e.g., restart, reset, update).

---

### 5. Server Acknowledgments
**Topic**: `Dev/Ack/<Device-ID>`  
**QoS**: 1  
**Retain**: false

**Payload Example**:
```json
{
  "status": "success",
  "message": "Received",
  "timestamp": "2025-12-06T17:30:00Z"
}
```

**Purpose**: Receive acknowledgments from server for device messages.

---

## 📤 Ridhi (Server) - What to Publish

### 1. Complete Configuration
**Topic**: `Dev/Checksum/<Device-ID>`  
**QoS**: 1  
**Retain**: true

**Payload**: Complete device configuration JSON (same as Naman receives)

**Purpose**: Send complete configuration to device when user saves configuration in dashboard.

---

### 2. Configuration Read Request
**Topic**: `Cmd/SConfig/<Device-ID>`  
**QoS**: 1  
**Retain**: false

**Payload**: `{"command": "Analog"}` or `{"command": "Digital"}` etc.

**Purpose**: Request specific configuration section from device (when user clicks "Load from Device").

---

### 3. Configuration Write Request
**Topic**: `Write/DConfig/<Device-ID>`  
**QoS**: 1  
**Retain**: false

**Payload**: `{"type": "Analog", "config": {...}}` or similar

**Purpose**: Send configuration to device (when user clicks "Send Configuration").

---

### 4. Commands
**Topic**: `iotnarad/devices/<Device-ID>/cmd`  
**QoS**: 1  
**Retain**: false

**Payload**: `{"command": "...", "params": {...}, "timestamp": "..."}`

**Purpose**: Send commands to device (e.g., restart, reset).

---

### 5. Server Acknowledgments
**Topic**: `Dev/Ack/<Device-ID>`  
**QoS**: 1  
**Retain**: false

**Payload**: `{"status": "success", "message": "...", "timestamp": "..."}`

**Purpose**: Acknowledge device messages (e.g., registration, data).

---

## 📥 Ridhi (Server) - What to Subscribe

### 1. Device Sensor Data
**Topic**: `iotnarad/devices/+/data`  
**QoS**: 1

**Purpose**: Receive real-time sensor readings from all devices.

---

### 2. Device Status
**Topic**: `iotnarad/devices/+/status`  
**QoS**: 1

**Purpose**: Monitor device online/offline status.

---

### 3. Device Registration
**Topic**: `Dev/Init/Reg/#`  
**QoS**: 1

**Purpose**: Receive device registration/initialization messages.

---

### 4. Configuration Read Reply
**Topic**: `Ack/SConfig/<Device-ID>`  
**QoS**: 1

**Purpose**: Receive configuration data from device (reply to `Cmd/SConfig` request).

---

### 5. Configuration Write Acknowledgment
**Topic**: `Config/ACK/<Device-ID>`  
**QoS**: 1

**Purpose**: Receive acknowledgment that device received and applied configuration.

---

### 6. Legacy Config ACK (Backward Compatibility)
**Topic**: `Dev/ConfigACK/#`  
**QoS**: 1

**Purpose**: Legacy topic for configuration acknowledgements (kept for backward compatibility).

---

## 🔄 Communication Flows

### Flow 1: Device Registration
```
1. Naman boots up
2. Naman publishes: Dev/Init/Reg/<Device-ID> → {"device_id": "...", ...}
3. Ridhi receives registration
4. Ridhi publishes: Dev/Ack/<Device-ID> → {"status": "success", ...}
```

### Flow 2: Send Configuration (Server → Device)
```
1. User clicks "Send Configuration" in dashboard
2. Ridhi publishes: Write/DConfig/<Device-ID> → {"type": "Analog", "config": {...}}
3. Naman receives configuration
4. Naman applies configuration
5. Naman publishes: Config/ACK/<Device-ID> → {"Result": "OK"}
6. Ridhi receives ACK and shows success message
```

### Flow 3: Load Configuration (Device → Server)
```
1. User clicks "Load from Device" in dashboard
2. Ridhi publishes: Cmd/SConfig/<Device-ID> → {"command": "Analog"}
3. Naman receives request
4. Naman publishes: Ack/SConfig/<Device-ID> → {"type": "Analog", "config": {...}}
5. Ridhi receives configuration and updates UI
```

### Flow 4: Periodic Data Transmission
```
1. Naman reads sensors every 5 seconds
2. Naman publishes: iotnarad/devices/<Device-ID>/data → {"analog": {...}, ...}
3. Ridhi receives data and saves to InfluxDB
4. Dashboard updates with latest readings
```

### Flow 5: Complete Config Push (Server → Device)
```
1. User clicks "Save Configuration" in dashboard
2. Ridhi saves to database
3. Ridhi publishes: Dev/Checksum/<Device-ID> → {complete config JSON}
4. Naman receives complete configuration (retained message)
5. Naman applies configuration
```

---

## 📝 Important Notes

### 1. Device ID Format
- Device ID is the **Serial Number** (`Sr_No`) from the `Device_info` measurement in InfluxDB
- Example: `ESP32_GW_001`, `0x235b`, `TEST78787`
- Always use the exact device ID in topic names

### 2. QoS Levels
- **QoS 1** is used for all topics (At least once delivery)
- Ensures messages are delivered, but may be duplicated
- Server implements deduplication to handle duplicate messages

### 3. Retain Flag
- **Retain = true**: Only for `Dev/Checksum/<Device-ID>` (complete config)
  - Ensures device receives latest config even if it was offline
- **Retain = false**: For all other topics (data, commands, ACKs)

### 4. JSON Payload Format
- All payloads are **JSON strings**
- Use `json.dumps()` when publishing
- Use `json.loads()` when receiving
- Always validate JSON before processing

### 5. Timeout Handling
- Server waits **5 seconds** for replies (config read/write)
- Device should reply within 5 seconds
- If timeout occurs, server shows error message

### 6. Error Handling
- Device should validate received configuration before applying
- If invalid, device can send ACK with `{"Result": "ERROR"}` or `{"Result": "FAIL"}`
- Server handles errors gracefully and shows user-friendly messages

### 7. Topic Wildcards
- Server uses `+` wildcard for subscribing to multiple devices:
  - `iotnarad/devices/+/data` - All devices' data
  - `iotnarad/devices/+/status` - All devices' status
- Server uses `#` wildcard for device registration:
  - `Dev/Init/Reg/#` - All device registrations

---

## 🎯 Summary for Hardware Team

### Naman (Device) Must:

**Subscribe to:**
- ✅ `Dev/Checksum/<Device-ID>` - Receive complete config
- ✅ `Cmd/SConfig/<Device-ID>` - Receive config read requests
- ✅ `Write/DConfig/<Device-ID>` - Receive config write requests
- ✅ `iotnarad/devices/<Device-ID>/cmd` - Receive commands
- ✅ `Dev/Ack/<Device-ID>` - Receive server ACKs

**Publish to:**
- ✅ `iotnarad/devices/<Device-ID>/data` - Send sensor data
- ✅ `iotnarad/devices/<Device-ID>/status` - Send status updates
- ✅ `Dev/Init/Reg/<Device-ID>` - Register on boot
- ✅ `Ack/SConfig/<Device-ID>` - Reply to config read requests
- ✅ `Config/ACK/<Device-ID>` - Acknowledge config write requests

**Key Points:**
- Use **QoS 1** for all topics
- Reply to `Cmd/SConfig` within 5 seconds
- Send ACK to `Write/DConfig` within 5 seconds
- Use exact device ID in all topic names
- All payloads must be valid JSON

---

## 🎯 Summary for Software Team

### Ridhi (Server) Does:

**Subscribes to:**
- ✅ `iotnarad/devices/+/data` - Receive all devices' data
- ✅ `iotnarad/devices/+/status` - Receive all devices' status
- ✅ `Dev/Init/Reg/#` - Receive device registrations
- ✅ `Ack/SConfig/<Device-ID>` - Receive config read replies
- ✅ `Config/ACK/<Device-ID>` - Receive config write ACKs
- ✅ `Dev/ConfigACK/#` - Legacy config ACKs

**Publishes to:**
- ✅ `Dev/Checksum/<Device-ID>` - Send complete config (retain=true)
- ✅ `Cmd/SConfig/<Device-ID>` - Request config from device
- ✅ `Write/DConfig/<Device-ID>` - Send config to device
- ✅ `iotnarad/devices/<Device-ID>/cmd` - Send commands
- ✅ `Dev/Ack/<Device-ID>` - Send ACKs to device

**Key Points:**
- Uses wildcards (`+`, `#`) for subscribing to multiple devices
- Implements message deduplication
- Waits 5 seconds for device replies
- Handles timeouts gracefully
- All topics use QoS 1

---

## 📚 Related Files

- **MQTT Client Service**: `app/services/mqtt_client.py`
- **Config Loader Service**: `app/services/device_config_loader.py`
- **Config Sender Service**: `app/services/device_config_sender.py`
- **Device Config Page**: `app/pages/device_config.py`

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-06  
**Author**: IOTNarad Dashboard Documentation

