# Load from Device - Implementation Summary

## 📋 Overview

This document explains the **"Load from Device"** functionality that was just implemented, what remains to be done, and how to verify that device-server communication is working correctly.

## 🔄 Recent Updates

**MQTT Topics Updated:**
- **Request Topic:** Changed from `Dev/Config/Read/<Device-ID>` to `Cmd/SConfig/<Device-ID>`
- **Response Topic:** Changed from `Dev/Config/Reply/<Device-ID>` to `Ack/SConfig/<Device-ID>`

**Payload Format Updated:**
- **Request Commands:** Changed from `get_analog_config` to `"Analog"` (capitalized)
- **Response Types:** Changed from `"analog"` to `"Analog"` (capitalized)
- All command and type values are now **capitalized**: `"Analog"`, `"Digital"`, `"Modbus"`, `"Canbus"`

---

## ✅ Completed Work

### 1. **New Service: DeviceConfigLoaderService**

Created `app/services/device_config_loader.py` - A service that handles MQTT communication to request configuration from devices.

**Key Features:**
- Publishes read requests on `Cmd/SConfig/<Device-ID>`
- Subscribes to `Ack/SConfig/<Device-ID>` to receive responses
- Supports all four configuration types: Analog, Digital, MODBUS, CAN Bus
- Includes timeout handling (5 seconds) and error management
- Validates response format before returning

**Command Mapping:**
- **Analog Tab** → `"Analog"`
- **Digital Tab** → `"Digital"`
- **MODBUS Tab** → `"Modbus"`
- **CAN Bus Tab** → `"Canbus"`

### 2. **Load from Device Button Callback**

Added callback in `app/pages/device_config.py` that:
- Detects which tab is active (Analog/Digital/MODBUS/CAN Bus)
- Sends appropriate MQTT command based on active tab
- Receives configuration response from device
- Saves configuration to database (individual section table + merged config)
- Updates UI automatically via `config-reload-trigger`
- Shows success/error messages via toast notification

### 3. **MQTT Topic Structure**

**Request Topic (Server → Device):**
```
Cmd/SConfig/<Device-ID>
```

**Response Topic (Device → Server):**
```
Ack/SConfig/<Device-ID>
```

**Example:**
- Device ID: `TEST78787`
- Request: `Cmd/SConfig/TEST78787`
- Response: `Ack/SConfig/TEST78787`

### 4. **Request/Response Format**

**Server Request Payload:**
```json
{
  "command": "Analog"    // or "Digital", "Modbus", "Canbus"
}
```

**Device Response Payload:**
```json
{
  "type": "Analog",                 // or "Digital", "Modbus", "Canbus"
  "config": {
    // ... configuration JSON matching the section structure
  }
}
```

**Note:** Command and type values are **capitalized** (e.g., "Analog", not "analog").

---

## 🔄 How It Works

### User Workflow

1. **User selects a device** from the dropdown
2. **User navigates to a tab** (Analog/Digital/MODBUS/CAN Bus)
3. **User clicks "Load from Device"** button
4. **System sends MQTT request** to device:
   - Topic: `Cmd/SConfig/<Device-ID>`
   - Payload: `{"command": "Analog"}` (or "Digital", "Modbus", "Canbus")
5. **Device responds** (within 5 seconds):
   - Topic: `Ack/SConfig/<Device-ID>`
   - Payload: `{"type": "Analog", "config": {...}}` (type matches command)
6. **System saves configuration** to database
7. **UI automatically updates** to show loaded configuration
8. **Success message** appears in toast notification

### Technical Flow

```
User Click → Callback Triggered
    ↓
Determine Active Tab → Map to Command
    ↓
DeviceConfigLoaderService.load_section()
    ↓
MQTT: Subscribe to Ack/SConfig/<Device-ID>
    ↓
MQTT: Publish to Cmd/SConfig/<Device-ID>
    ↓
Wait for Response (5s timeout)
    ↓
Validate Response Format
    ↓
Save to Database (Device_Config_<Section>)
    ↓
Rebuild Merged Config → Save to Device_Config
    ↓
Trigger UI Reload → Show Success Message
```

---

## 📝 Tasks Remaining

### 1. **Hardware/Firmware Implementation** ⚠️ **CRITICAL**

The device firmware needs to:

- ✅ **Subscribe** to `Cmd/SConfig/<Device-ID>` topic
- ✅ **Publish** responses to `Ack/SConfig/<Device-ID>` topic
- ✅ **Parse** command payload: `{"command": "Analog"}` (or "Digital", "Modbus", "Canbus")
- ✅ **Respond** with correct format: `{"type": "Analog", "config": {...}}` (type matches command)

**Required Device Behavior:**

| Command | Expected Response Type | Config Structure |
|---------|----------------------|------------------|
| `"Analog"` | `"Analog"` | Analog config JSON (see SAVE_CONFIGURATION_JSON_REFERENCE.md) |
| `"Digital"` | `"Digital"` | Digital config JSON |
| `"Modbus"` | `"Modbus"` | MODBUS config JSON |
| `"Canbus"` | `"Canbus"` | CAN Bus config JSON |

**Note:** All command and type values are **capitalized**.

**Response Time:**
- Device should respond within **5 seconds**
- If device takes longer, increase timeout in `DeviceConfigLoaderService`

### 2. **Testing & Verification**

- [ ] Test with actual hardware device
- [ ] Verify all four tabs (Analog, Digital, MODBUS, CAN Bus)
- [ ] Test timeout handling (device not responding)
- [ ] Test error handling (invalid response format)
- [ ] Verify UI updates correctly after load
- [ ] Confirm database saves correctly

### 3. **Error Handling Enhancements** (Optional)

Consider adding:
- Retry mechanism (if device doesn't respond)
- Better error messages for specific failure cases
- Loading indicator during MQTT request
- Cancel button to abort pending requests

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

#### Step 1: Subscribe to Request Topic (Server → Device)

Open **Terminal 1** and subscribe to see what the server sends:

```bash
# Subscribe to all device read requests
mosquitto_sub -h mqtt -p 1883 -t "Cmd/SConfig/+" -v

# Or subscribe to specific device (replace TEST78787 with your device ID)
mosquitto_sub -h mqtt -p 1883 -t "Cmd/SConfig/TEST78787" -v
```

**Expected Output When Server Sends Request:**
```
Cmd/SConfig/TEST78787 {"command":"Analog"}
```

#### Step 2: Subscribe to Response Topic (Device → Server)

Open **Terminal 2** and subscribe to see what the device responds:

```bash
# Subscribe to all device responses
mosquitto_sub -h mqtt -p 1883 -t "Ack/SConfig/+" -v

# Or subscribe to specific device
mosquitto_sub -h mqtt -p 1883 -t "Ack/SConfig/TEST78787" -v
```

**Expected Output When Device Responds:**
```
Ack/SConfig/TEST78787 {"type":"Analog","config":{"input_4_20ma":[...],"input_1_10v":[...],"output_0_10v":[...],"scan_rate":1000}}
```

#### Step 3: Test Load from Device

1. **Open Dashboard** in browser
2. **Navigate to:** Devices → Select Device → Analog Tab
3. **Click "Load from Device"** button
4. **Watch Terminal 1:** Should show request message
5. **Watch Terminal 2:** Should show response message (if device is connected)

### Method 2: Manual MQTT Testing (Simulate Device Response)

If you want to test the server-side logic without a real device:

#### Step 1: Subscribe to Request Topic

```bash
mosquitto_sub -h mqtt -p 1883 -t "Cmd/SConfig/+" -v
```

#### Step 2: Manually Send Response (Simulate Device)

In another terminal, when you see a request, manually publish a response:

```bash
# Example: Respond to analog config request
mosquitto_pub -h mqtt -p 1883 -t "Ack/SConfig/TEST78787" -m '{"type":"Analog","config":{"input_4_20ma":[{"channel":1,"enabled":true,"divider":100,"multiplier":1,"io_pin":"AIN0","name":"Temperature","min_value":4,"max_value":20,"unit":"mA"}],"input_1_10v":[],"output_0_10v":[{"channel":1,"enabled":true,"value":5.0,"io_pin":"DOUT0","name":"Valve Control","min_value":0,"max_value":10,"unit":"V"}],"scan_rate":1000}}'
```

**Note:** The response type must be capitalized: `"Analog"` (not `"analog"`).

**Note:** Replace `TEST78787` with your actual device ID.

### Method 3: Monitor All MQTT Traffic

To see **all** MQTT messages (useful for debugging):

```bash
# Subscribe to all topics (wildcard)
mosquitto_sub -h mqtt -p 1883 -t "#" -v
```

**Warning:** This will show a lot of messages. Use filters if needed.

### Method 4: Check Server Logs

The server logs MQTT activity. Check application logs for:

```
📤 Published to Cmd/SConfig/TEST78787: {"command":"Analog"}
📨 Message received on Ack/SConfig/TEST78787: {"type":"Analog","config":{...}}
✅ Successfully loaded analog configuration from device TEST78787
```

### Method 5: Database Verification (Optional - For Debugging)

**Note:** This is **NOT a required step** in the normal workflow. The system automatically saves configuration to the database and updates the UI. This method is only for **manual verification/debugging** if you want to confirm the data was saved correctly.

**When to use:**
- If you suspect data wasn't saved correctly
- For debugging purposes
- To verify database structure
- To check raw data format

**SQL Queries:**

```sql
-- Check Analog config
SELECT * FROM Device_Config_Analog WHERE device_id = 'TEST78787';

-- Check merged config
SELECT * FROM Device_Config WHERE device_id = 'TEST78787';
```

**Normal Workflow (Automatic):**
1. User clicks "Load from Device" ✅
2. System receives config from device ✅
3. System **automatically saves** to database ✅
4. System **automatically updates** UI ✅
5. Success message appears ✅

**No manual database verification needed!** Method 5 is only if you want to manually inspect the saved data.

---

## 🔍 Troubleshooting

### Issue: "Timeout waiting for device response"

**Possible Causes:**
1. Device not connected to MQTT broker
2. Device not subscribed to `Cmd/SConfig/<Device-ID>`
3. Device not publishing to `Ack/SConfig/<Device-ID>`
4. Network connectivity issues
5. Device processing time > 5 seconds

**Solutions:**
- Check device MQTT connection status
- Verify device is subscribed to correct topic: `Cmd/SConfig/<Device-ID>`
- Verify device publishes to correct topic: `Ack/SConfig/<Device-ID>`
- Increase timeout in `DeviceConfigLoaderService` if needed
- Check MQTT broker logs

### Issue: "Invalid response format"

**Possible Causes:**
1. Device response missing `"type"` field
2. Device response missing `"config"` field
3. Response type doesn't match requested section
4. Config structure doesn't match expected format

**Solutions:**
- Verify device response format matches specification
- Check device firmware code
- Review response in MQTT monitor (Terminal 2)

### Issue: "Device not found"

**Possible Causes:**
1. Device ID not selected in dropdown
2. Device not in database
3. User doesn't have permission to access device

**Solutions:**
- Select device from dropdown before clicking Load
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
- Test broker connection: `mosquitto_pub -h mqtt -p 1883 -t test -m "test"`

---

## 📚 Related Documentation

- **SAVE_CONFIGURATION_JSON_REFERENCE.md** - JSON structure for each configuration section
- **CONFIG_JSON_SUMMARY.md** - Overview of configuration system
- **MQTT_AND_DATABASE_REFERENCE.md** - MQTT topic reference

---

## 🎯 Quick Test Checklist

Use this checklist to verify everything works:

- [ ] MQTT broker is running and accessible
- [ ] Device is connected to MQTT broker
- [ ] Device subscribes to `Cmd/SConfig/<Device-ID>`
- [ ] Device publishes to `Ack/SConfig/<Device-ID>`
- [ ] Server can publish to `Cmd/SConfig/<Device-ID>` (test with mosquitto_pub)
- [ ] Server can subscribe to `Ack/SConfig/<Device-ID>` (test with mosquitto_sub)
- [ ] Load from Device button works in Analog tab
- [ ] Load from Device button works in Digital tab
- [ ] Load from Device button works in MODBUS tab
- [ ] Load from Device button works in CAN Bus tab
- [ ] UI updates correctly after loading
- [ ] Configuration saved to database
- [ ] Success message appears in toast

---

## 📞 Support

If you encounter issues:

1. **Check MQTT Messages:** Use terminal monitoring (Method 1)
2. **Check Server Logs:** Look for error messages
3. **Check Database:** Verify configuration was saved
4. **Test Manually:** Use mosquitto_pub/sub to test MQTT communication
5. **Verify Device:** Ensure device firmware is correctly implemented

---

**Last Updated:** Implementation completed for Load from Device functionality
**Status:** ✅ Server-side complete | ⚠️ Device firmware implementation required

