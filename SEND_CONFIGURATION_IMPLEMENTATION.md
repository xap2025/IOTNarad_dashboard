# Send Configuration - Implementation Summary

## 📋 Overview

This document explains the **"Send Configuration"** functionality that was just implemented. This feature allows users to send configuration from the server to devices via MQTT, based on the active tab (Analog, Digital, MODBUS, or CAN Bus).

---

## ✅ Completed Work

### 1. **Button Renamed and Updated**

**Changed:**
- ❌ **Old:** "Reset to Default" button
- ✅ **New:** "Send Configuration" button

**UI Updates:**
- Button ID: `reset-config-btn` → `send-config-btn`
- Button text: "Reset to Default" → "Send Configuration"
- Button icon: `fa-undo` → `fa-paper-plane`
- Button color: `warning` (yellow) → `success` (green)
- Button position: Now appears next to "Load from Device" button

**Location:** `app/pages/device_config.py` (line ~91-94)

### 2. **New Service: DeviceConfigSenderService**

Created `app/services/device_config_sender.py` - A service that handles MQTT communication to send configuration to devices.

**Key Features:**
- Publishes configuration on `Write/DConfig/<Device-ID>`
- Subscribes to `Config/ACK/<Device-ID>` to receive acknowledgments
- Supports all four configuration types: Analog, Digital, MODBUS, CAN Bus
- Includes timeout handling (5 seconds) and error management
- Validates ACK response format before returning

**Method:**
```python
send_config(device_id, config_type, config_data, timeout=5.0)
```

**Parameters:**
- `device_id`: Device serial number
- `config_type`: One of `"Analog"`, `"Digital"`, `"Modbus"`, `"Canbus"`
- `config_data`: Configuration dictionary for the section
- `timeout`: Seconds to wait for device ACK (default: 5.0)

**Returns:**
- `True` if ACK received with `"Result": "OK"`
- `False` if timeout or invalid ACK

### 3. **Send Configuration Callback**

Added callback in `app/pages/device_config.py` that:
- Detects which tab is active (Analog/Digital/MODBUS/CAN Bus)
- Reads all configuration values from the active tab's UI
- Builds configuration JSON using `ConfigJSONBuilder`
- Sends configuration to device via MQTT
- Waits for device acknowledgment
- Shows success/error messages via toast notification

**Callback Function:** `send_configuration_to_device()`

**Inputs:**
- Button click: `send-config-btn`
- Active tab: `config-tabs.active_tab`
- Device selection: `device-selector.value`
- All tab states (Analog, Digital, MODBUS, CAN Bus)

**Outputs:**
- Toast visibility: `config-save-toast.is_open`
- Toast message: `config-save-toast.children`

### 4. **MQTT Topic Structure**

**Send Topic (Server → Device):**
```
Write/DConfig/<Device-ID>
```

**ACK Topic (Device → Server):**
```
Config/ACK/<Device-ID>
```

**Example:**
- Device ID: `TEST78787`
- Send: `Write/DConfig/TEST78787`
- ACK: `Config/ACK/TEST78787`

### 5. **Request/Response Format**

**Server Send Payload:**
```json
{
  "type": "Analog",    // or "Digital", "Modbus", "Canbus"
  "config": {
    // ... configuration JSON matching the section structure
  }
}
```

**Device ACK Payload:**
```json
{
  "Result": "OK"
}
```

---

## 🔄 How It Works

### User Workflow

1. **User selects a device** from the dropdown
2. **User navigates to a tab** (Analog/Digital/MODBUS/CAN Bus)
3. **User configures settings** in the active tab
4. **User clicks "Send Configuration"** button
5. **System reads active tab** and builds configuration JSON
6. **System sends MQTT message** to device:
   - Topic: `Write/DConfig/<Device-ID>`
   - Payload: `{"type": "<section>", "config": {...}}`
7. **Device receives config** and applies settings
8. **Device sends ACK** (within 5 seconds):
   - Topic: `Config/ACK/<Device-ID>`
   - Payload: `{"Result": "OK"}`
9. **System receives ACK** and shows success message
10. **If no ACK received**, system shows warning message

### Technical Flow

```
User Click → Callback Triggered
    ↓
Determine Active Tab → Read UI State Values
    ↓
Build Config JSON (ConfigJSONBuilder)
    ↓
DeviceConfigSenderService.send_config()
    ↓
MQTT: Subscribe to Config/ACK/<Device-ID>
    ↓
MQTT: Publish to Write/DConfig/<Device-ID>
    ↓
Wait for ACK (5s timeout)
    ↓
Validate ACK Response
    ↓
Show Success/Warning Message
```

---

## 📝 Configuration Payloads (Tab-wise)

### 🔹 Analog Configuration

When **Analog tab** is active, sends:
```json
{
  "type": "Analog",
  "config": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": true,
        "divider": 1,
        "multiplier": 1,
        "io_pin": "AIN0",
        "name": "Channel 1",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      }
    ],
    "input_1_10v": [...],
    "output_0_10v": [...],
    "scan_rate": 1000
  }
}
```

### 🔹 Digital Configuration

When **Digital tab** is active, sends:
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

### 🔹 MODBUS Configuration

When **MODBUS tab** is active, sends:
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

### 🔹 CAN Bus Configuration

When **CAN Bus tab** is active, sends:
```json
{
  "type": "Canbus",
  "config": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": 500,
      "identifier_length": "11-bit",
      "can_mode": "Normal",
      "filter_mode": "None",
      "filter_id": "0x000",
      "filter_mask": "0x000"
    },
    "can_messages": [...],
    "data_mapping": [...]
  }
}
```

---

## 🔍 Tasks Remaining

### 1. **Hardware/Firmware Implementation** ⚠️ **CRITICAL**

The device firmware needs to:

- ✅ **Subscribe** to `Write/DConfig/<Device-ID>` topic
- ✅ **Parse** configuration payload: `{"type": "<section>", "config": {...}}`
- ✅ **Apply** configuration settings to device
- ✅ **Publish** ACK response to `Config/ACK/<Device-ID>` topic
- ✅ **ACK payload format:** `{"Result": "OK"}`

**Required Device Behavior:**

| Config Type | Device Should | ACK Response |
|-------------|---------------|--------------|
| `"Analog"` | Apply analog I/O settings | `{"Result": "OK"}` |
| `"Digital"` | Apply digital I/O settings | `{"Result": "OK"}` |
| `"Modbus"` | Apply MODBUS settings | `{"Result": "OK"}` |
| `"Canbus"` | Apply CAN Bus settings | `{"Result": "OK"}` |

**Response Time:**
- Device should send ACK within **5 seconds**
- If device takes longer, increase timeout in `DeviceConfigSenderService`

### 2. **Testing & Verification**

- [ ] Test with actual hardware device
- [ ] Verify all four tabs (Analog, Digital, MODBUS, CAN Bus)
- [ ] Test timeout handling (device not responding)
- [ ] Test error handling (invalid ACK format)
- [ ] Verify device applies configuration correctly
- [ ] Confirm ACK messages are received

### 3. **Error Handling Enhancements** (Optional)

Consider adding:
- Retry mechanism (if device doesn't send ACK)
- Better error messages for specific failure cases
- Loading indicator during MQTT send
- Cancel button to abort pending sends

---

## 🧪 Verification & Testing Guide

### Prerequisites

1. **MQTT Broker Running**
   - Default: `mqtt` (hostname) on port `1883`
   - Or set via environment: `MQTT_BROKER` and `MQTT_PORT`

2. **MQTT Client Tools Installed**
   - **mosquitto-clients** package (Linux/Mac)
   - **Mosquitto** for Windows
   - Or use any MQTT client (MQTT.fx, MQTT Explorer, etc.)

### Method 1: Monitor MQTT Messages in Terminal

#### Step 1: Subscribe to Send Topic (Server → Device)

Open **Terminal 1** and subscribe to see what the server sends:

```bash
# Subscribe to all device config sends
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Write/DConfig/#" -v

# Or subscribe to specific device (replace TEST78787 with your device ID)
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Write/DConfig/TEST78787" -v
```

**Expected Output When Server Sends Config:**
```
Write/DConfig/TEST78787 {"type":"Analog","config":{"input_4_20ma":[...],"input_1_10v":[...],"output_0_10v":[...],"scan_rate":1000}}
```

#### Step 2: Subscribe to ACK Topic (Device → Server)

Open **Terminal 2** and subscribe to see what the device responds:

```bash
# Subscribe to all device ACKs
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Config/ACK/#" -v

# Or subscribe to specific device
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Config/ACK/TEST78787" -v
```

**Expected Output When Device Responds:**
```
Config/ACK/TEST78787 {"Result":"OK"}
```

#### Step 3: Test Send Configuration

1. **Open Dashboard** in browser
2. **Navigate to:** Devices → Select Device → Analog Tab
3. **Configure settings** in the Analog tab
4. **Click "Send Configuration"** button
5. **Watch Terminal 1:** Should show config message
6. **Watch Terminal 2:** Should show ACK message (if device is connected)

### Method 2: Manual MQTT Testing (Simulate Device ACK)

If you want to test the server-side logic without a real device:

#### Step 1: Subscribe to Send Topic

```bash
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "Write/DConfig/#" -v
```

#### Step 2: Manually Send ACK (Simulate Device)

In another terminal, when you see a config message, manually publish an ACK:

```bash
# Example: Send ACK for device TEST78787
docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t "Config/ACK/TEST78787" -m '{"Result":"OK"}'
```

**Note:** Replace `TEST78787` with your actual device ID.

### Method 3: Monitor All MQTT Traffic

To see **all** MQTT messages (useful for debugging):

```bash
# Subscribe to all topics (wildcard)
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -p 1883 -t "#" -v
```

**Warning:** This will show a lot of messages. Use filters if needed.

### Method 4: Check Server Logs

The server logs MQTT activity. Check application logs for:

```
📤 Sending Analog config to TEST78787 on Write/DConfig/TEST78787
✅ ACK received from device TEST78787: OK
✅ Configuration sent successfully to device TEST78787
```

---

## 🔍 Troubleshooting

### Issue: "No ACK received from device"

**Possible Causes:**
1. Device not connected to MQTT broker
2. Device not subscribed to `Write/DConfig/<Device-ID>`
3. Device not publishing to `Config/ACK/<Device-ID>`
4. Network connectivity issues
5. Device processing time > 5 seconds

**Solutions:**
- Check device MQTT connection status
- Verify device is subscribed to correct topic: `Write/DConfig/<Device-ID>`
- Verify device publishes to correct topic: `Config/ACK/<Device-ID>`
- Increase timeout in `DeviceConfigSenderService` if needed
- Check MQTT broker logs

### Issue: "Device sent ACK with invalid result"

**Possible Causes:**
1. Device ACK missing `"Result"` field
2. Device ACK has `"Result"` value other than `"OK"` or `"ok"`
3. ACK payload format is incorrect

**Solutions:**
- Verify device ACK format matches specification: `{"Result": "OK"}`
- Check device firmware code
- Review ACK in MQTT monitor (Terminal 2)

### Issue: "Device not found"

**Possible Causes:**
1. Device ID not selected in dropdown
2. Device not in database
3. User doesn't have permission to access device

**Solutions:**
- Select device from dropdown before clicking Send
- Verify device exists in `Device_info` table
- Check user permissions (device ownership)

### Issue: "MQTT client not connected"

**Possible Causes:**
1. MQTT broker not running
2. Incorrect broker host/port
3. Network connectivity issues

**Solutions:**
- Check MQTT broker status: `docker ps` (if using Docker)
- Verify `MQTT_BROKER` and `MQTT_PORT` environment variables
- Test broker connection: `docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -p 1883 -t test -m "test"`

---

## 📚 Related Documentation

- **LOAD_FROM_DEVICE_IMPLEMENTATION.md** - How to load configuration from device
- **SAVE_CONFIGURATION_JSON_REFERENCE.md** - JSON structure for each configuration section
- **CONFIG_JSON_SUMMARY.md** - Overview of configuration system
- **MQTT_AND_DATABASE_REFERENCE.md** - MQTT topic reference

---

## 🎯 Quick Test Checklist

Use this checklist to verify everything works:

- [ ] MQTT broker is running and accessible
- [ ] Device is connected to MQTT broker
- [ ] Device subscribes to `Write/DConfig/<Device-ID>`
- [ ] Device publishes to `Config/ACK/<Device-ID>`
- [ ] Server can publish to `Write/DConfig/<Device-ID>` (test with mosquitto_pub)
- [ ] Server can subscribe to `Config/ACK/<Device-ID>` (test with mosquitto_sub)
- [ ] Send Configuration button works in Analog tab
- [ ] Send Configuration button works in Digital tab
- [ ] Send Configuration button works in MODBUS tab
- [ ] Send Configuration button works in CAN Bus tab
- [ ] Success message appears when ACK received
- [ ] Warning message appears when no ACK received
- [ ] Device applies configuration correctly

---

## 🔄 Comparison: Send vs Save vs Load

| Feature | Save Configuration | Load from Device | Send Configuration |
|---------|-------------------|------------------|-------------------|
| **Direction** | Server → Database | Device → Server | Server → Device |
| **Action** | Saves to DB | Fetches from device | Sends to device |
| **MQTT Topic** | N/A (DB only) | `Cmd/SConfig/<ID>` | `Write/DConfig/<ID>` |
| **UI Update** | Yes (auto-reload) | Yes (auto-reload) | No (config already in UI) |
| **ACK Required** | No | No | Yes (`Config/ACK/<ID>`) |
| **Use Case** | Save current UI state | Get device's current config | Push config to device |

**Workflow Example:**
1. **Load from Device** → Get current device config → Shows in UI
2. **User modifies** settings in UI
3. **Save Configuration** → Saves to database
4. **Send Configuration** → Pushes to device → Device applies

---

## 📞 Support

If you encounter issues:

1. **Check MQTT Messages:** Use terminal monitoring (Method 1)
2. **Check Server Logs:** Look for error messages
3. **Test Manually:** Use mosquitto_pub/sub to test MQTT communication
4. **Verify Device:** Ensure device firmware is correctly implemented
5. **Check ACK Format:** Verify device sends `{"Result": "OK"}`

---

**Last Updated:** Implementation completed for Send Configuration functionality
**Status:** ✅ Server-side complete | ⚠️ Device firmware implementation required

