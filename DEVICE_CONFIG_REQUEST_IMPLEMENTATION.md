# Device Configuration Request Feature - Implementation

## 🎯 Feature Overview

Device can now request configuration from the server via MQTT. When device sends a request, server responds with the requested configuration.

---

## 📋 MQTT Topics

### Server Side:
- **Subscribe**: `Cmd/DConfig/#` - Listen for device config requests
- **Publish**: `Ack/DConfig/<Device ID>` - Send configuration to device

### Device Side:
- **Publish**: `Cmd/DConfig/<Device ID>` - Request configuration
- **Subscribe**: `Ack/DConfig/<Device ID>` - Receive configuration

---

## 🔄 Message Flow

### 1. Device Request

**Topic**: `Cmd/DConfig/<Device ID>`

**Payload Example**:
```json
{
  "command": "Digital"
}
```

**Supported Commands**:
- `"Analog"` - Request Analog tab configuration
- `"Digital"` - Request Digital tab configuration
- `"Modbus"` - Request RS485/Modbus tab configuration
- `"Canbus"` - Request CAN Bus tab configuration

---

### 2. Server Response

**Topic**: `Ack/DConfig/<Device ID>`

**Payload Format** (Same as Send Configuration):
```json
{
  "type": "Digital",
  "config": {
    "npn_input": [...],
    "npn_output": [...],
    "pnp_input": [...],
    "pnp_output": [...],
    "relay": [...],
    "scan_rate": 1000
  }
}
```

---

## 🏗️ Implementation Details

### Files Created/Modified:

1. **`app/services/device_config_provider.py`** (NEW)
   - Service to handle device config requests
   - Loads config from database
   - Publishes to `Ack/DConfig/<Device ID>`

2. **`app/services/mqtt_client.py`** (MODIFIED)
   - Added subscription to `Cmd/DConfig/#`
   - Added `set_config_request_callback()` method
   - Added message routing for `Cmd/DConfig/` topics

3. **`app/main.py`** (MODIFIED)
   - Initialized `DeviceConfigDBService` and `DeviceConfigProviderService`
   - Created `on_device_config_request()` callback
   - Registered callback with MQTT service

---

## 📝 Code Structure

### DeviceConfigProviderService

**Methods**:
- `handle_config_request(device_id, command)` - Main handler
- `_get_empty_config(config_type)` - Returns empty config structure

**Command Mapping**:
```python
{
    "Analog": "analog",
    "Digital": "digital",
    "Modbus": "modbus",
    "Canbus": "can"
}
```

**Flow**:
1. Receive request with command
2. Normalize command (case-insensitive)
3. Load config from database using appropriate method:
   - `get_analog_config(device_id)`
   - `get_digital_config(device_id)`
   - `get_modbus_config(device_id)`
   - `get_can_bus_config(device_id)`
4. Build JSON payload with `type` and `config`
5. Publish to `Ack/DConfig/<Device ID>`

---

## 🧪 Testing

### Test 1: Request Digital Configuration

**Device publishes**:
```bash
Topic: Cmd/DConfig/8C4B14BA7950
Payload: {"command": "Digital"}
```

**Expected Server Logs**:
```
📥 Device config request received on topic: Cmd/DConfig/8C4B14BA7950
   Device ID: 8C4B14BA7950, Payload: {'command': 'Digital'}
📥 Device 8C4B14BA7950 requested Digital configuration
📤 Sending Digital config to device 8C4B14BA7950 on Ack/DConfig/8C4B14BA7950
✅ Digital configuration sent successfully to device 8C4B14BA7950
```

**Device receives**:
```bash
Topic: Ack/DConfig/8C4B14BA7950
Payload: {
  "type": "Digital",
  "config": {
    "npn_input": [...],
    "npn_output": [...],
    ...
  }
}
```

---

### Test 2: Request Analog Configuration

**Device publishes**:
```bash
Topic: Cmd/DConfig/8C4B14BA7950
Payload: {"command": "Analog"}
```

**Expected**: Server sends Analog configuration

---

### Test 3: Request Modbus Configuration

**Device publishes**:
```bash
Topic: Cmd/DConfig/8C4B14BA7950
Payload: {"command": "Modbus"}
```

**Expected**: Server sends Modbus configuration

---

### Test 4: Request CAN Bus Configuration

**Device publishes**:
```bash
Topic: Cmd/DConfig/8C4B14BA7950
Payload: {"command": "Canbus"}
```

**Expected**: Server sends CAN Bus configuration

---

### Test 5: Invalid Command

**Device publishes**:
```bash
Topic: Cmd/DConfig/8C4B14BA7950
Payload: {"command": "Invalid"}
```

**Expected**: Server logs error, no config sent

---

### Test 6: No Configuration Found

**Device publishes**:
```bash
Topic: Cmd/DConfig/8C4B14BA7950
Payload: {"command": "Digital"}
```

**If no config in database**:
- Server sends empty config structure
- Logs warning message

---

## 🔍 Monitoring

### Subscribe to Topics for Testing

**Monitor device requests**:
```bash
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Cmd/DConfig/#" -v
```

**Monitor server responses**:
```bash
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Ack/DConfig/#" -v
```

---

## 📊 Error Handling

### Invalid Command
- Logs error: `❌ Invalid command '...' from device ...`
- Returns `False`
- No config sent

### Database Error
- Logs error with full traceback
- Returns `False`
- No config sent

### No Configuration Found
- Logs warning: `⚠️ No ... configuration found for device ...`
- Sends empty config structure
- Returns `True`

### MQTT Publish Failure
- Logs error: `❌ Failed to send ... configuration to device ...`
- Returns `False`

---

## ✅ Summary

### Features Implemented:
- ✅ Server subscribes to `Cmd/DConfig/#`
- ✅ Device can request config via `Cmd/DConfig/<Device ID>`
- ✅ Server loads config from database
- ✅ Server publishes config to `Ack/DConfig/<Device ID>`
- ✅ Supports all 4 config types: Analog, Digital, Modbus, Canbus
- ✅ Error handling and logging
- ✅ Empty config fallback if no config found

### Next Steps:
1. Test with hardware device
2. Verify config format matches "Send Configuration" format
3. Monitor logs for any issues

---

**Status**: ✅ **IMPLEMENTATION COMPLETE**

**Files**:
- ✅ `app/services/device_config_provider.py` - NEW
- ✅ `app/services/mqtt_client.py` - MODIFIED
- ✅ `app/main.py` - MODIFIED

