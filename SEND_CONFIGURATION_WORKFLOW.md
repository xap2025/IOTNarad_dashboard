# Send Configuration Button - Complete Workflow

## Overview

When you click the **"Send Configuration"** button on any tab (Analog, Digital, RS485 MODBUS, or CAN Bus), the system **sends the configuration directly to the device via MQTT**. 

**Important:** The configuration is **NOT saved to the database** when you click "Send Configuration". It is sent directly to the device only.

---

## Step-by-Step Workflow

### Step 1: User Clicks "Send Configuration" Button

- User selects a device from the "Select Device" dropdown
- User configures settings in the active tab (Analog/Digital/MODBUS/CAN Bus)
- User clicks the **"Send Configuration"** button

### Step 2: Validation

The system validates:
- ✅ Device is selected (serial number exists)
- ✅ Active tab is valid (Analog, Digital, MODBUS, or CAN Bus)
- ✅ All required UI inputs are available

If validation fails → Error message is shown, process stops.

### Step 3: Read UI Values

The system reads all current values from the UI inputs:

#### For **Analog Tab:**
- Input channels: enabled, divider, multiplier, name
- Output channels: enabled, value, name
- Scan rate

#### For **Digital Tab:**
- NPN Input: enabled, name (4 channels)
- NPN Output: enabled, name (4 channels)
- PNP Input: enabled, name (4 channels)
- PNP Output: enabled, name (4 channels)
- Relay: enabled, name (4 channels)
- Scan rate

#### For **RS485 MODBUS Tab:**
- Communication Settings: baud rate, data bits, parity, stop bits
- Protocol Settings: mode, role
- Polling interval
- Slave Devices: all rows from the table (slave_id, function_code, register_address, data_type, endianness, variable_name)

#### For **CAN Bus Tab:**
- Communication Settings: baud rate, identifier length, CAN mode, filter mode, filter ID, filter mask
- CAN Messages: all rows from the messages table
- Data Mappings: all rows from the data mapping table

### Step 4: Build JSON Configuration

The system uses `ConfigJSONBuilder` to convert UI values into JSON:

**Location:** `app/services/config_json_builder.py`

**Methods used:**
- `build_analog_config()` - for Analog tab
- `build_digital_config()` - for Digital tab
- `build_modbus_config()` - for MODBUS tab
- `build_can_bus_config()` - for CAN Bus tab

**JSON Structure Created:**

```json
{
  "type": "Analog",  // or "Digital", "Modbus", "Canbus"
  "config": {
    // Configuration data based on active tab
  }
}
```

**Special Processing:**

1. **Analog Tab:**
   - Removes `min_value`, `max_value`, and `unit` fields from all channels before sending
   - These fields are only for UI display, not needed by device

2. **Digital Tab:**
   - Removes `pullup`, `debounce_ms` (from inputs)
   - Removes `initial_state` (from outputs and relays)
   - Only sends fields available in UI: `channel`, `enabled`, `io_pin`, `name`

3. **MODBUS Tab:**
   - Includes all communication settings, protocol settings, polling interval, and slave devices

4. **CAN Bus Tab:**
   - Includes all communication settings, CAN messages, and data mappings

### Step 5: Send via MQTT

The system uses `DeviceConfigSenderService` to send the JSON to the device:

**Location:** `app/services/device_config_sender.py`

**MQTT Topics:**
- **Publish Topic:** `Write/DConfig/<Device-ID>`
- **Subscribe Topic (for ACK):** `Config/ACK/<Device-ID>`

**MQTT Payload:**
```json
{
  "type": "Analog",
  "config": {
    // Configuration data
  }
}
```

**Process:**
1. Connect to MQTT broker
2. Subscribe to ACK topic: `Config/ACK/<Device-ID>`
3. Publish configuration to: `Write/DConfig/<Device-ID>`
4. Wait for ACK from device (timeout: 5 seconds)
5. Disconnect from MQTT broker

### Step 6: Wait for Device Acknowledgment

The system waits for the device to send an ACK message:

**Expected ACK Format:**
```json
{
  "Result": "OK"
}
```

**ACK Handling:**
- ✅ If ACK received with `Result: "OK"` → Success message shown
- ⚠️ If ACK received with other result → Warning message shown
- ❌ If no ACK received within 5 seconds → Warning message shown

### Step 7: Show Result to User

**Success Message:**
```
✅ Sent! [Config Type] configuration sent to device [Serial Number] and acknowledged.
```

**Warning Message:**
```
⚠️ Warning: Configuration sent to [Serial Number] but no ACK received. Device may not have applied the configuration.
```

**Error Message:**
```
❌ Error: Failed to send configuration: [Error details]
```

---

## Important Points

### ❌ What "Send Configuration" Does NOT Do:

1. **Does NOT save to database** - Configuration is sent directly to device only
2. **Does NOT update UI** - UI values remain unchanged
3. **Does NOT trigger config reload** - No automatic refresh of UI from database

### ✅ What "Send Configuration" Does:

1. ✅ Reads current UI values
2. ✅ Builds JSON configuration
3. ✅ Sends JSON to device via MQTT
4. ✅ Waits for device acknowledgment
5. ✅ Shows success/error message to user

---

## Comparison: "Save Configuration" vs "Send Configuration"

| Feature | Save Configuration | Send Configuration |
|---------|-------------------|-------------------|
| **Saves to Database** | ✅ Yes | ❌ No |
| **Sends to Device** | ❌ No | ✅ Yes |
| **Updates UI** | ✅ Yes (reloads from DB) | ❌ No |
| **Device Acknowledgment** | ❌ Not required | ✅ Required (waits 5s) |
| **MQTT Topic** | N/A | `Write/DConfig/<Device-ID>` |
| **Use Case** | Store configuration for later | Apply configuration immediately |

---

## Workflow Diagram

```
User clicks "Send Configuration"
         ↓
Validate device selection & active tab
         ↓
Read all UI values from active tab
         ↓
Build JSON using ConfigJSONBuilder
         ↓
Remove unwanted fields (if any)
         ↓
Connect to MQTT broker
         ↓
Subscribe to ACK topic: Config/ACK/<Device-ID>
         ↓
Publish to: Write/DConfig/<Device-ID>
         ↓
Wait for ACK (timeout: 5 seconds)
         ↓
Disconnect from MQTT
         ↓
Show success/error message to user
```

---

## Code Flow

**Main Callback:** `app/pages/device_config.py` → `send_configuration_to_device()`

**Services Used:**
1. `ConfigJSONBuilder` (`app/services/config_json_builder.py`)
   - Builds JSON from UI values
   
2. `DeviceConfigSenderService` (`app/services/device_config_sender.py`)
   - Handles MQTT connection
   - Publishes configuration
   - Waits for ACK

---

## Testing

To test "Send Configuration":

1. Select a device from dropdown
2. Configure settings in any tab
3. Click "Send Configuration"
4. Check server logs for MQTT publish/ACK messages
5. Verify device receives and applies configuration

**Expected Log Messages:**
```
📡 Connected to MQTT for config send: [device-id] ([config-type])
📡 Subscribed to ACK topic: Config/ACK/[device-id]
📤 Sending [config-type] config to [device-id] on Write/DConfig/[device-id]
✅ ACK received from device [device-id]: OK
✅ Configuration sent successfully to device [device-id]
```

---

## Summary

**"Send Configuration" button:**
- ✅ Sends configuration **directly to device** via MQTT
- ❌ Does **NOT save to database**
- ✅ Waits for device acknowledgment
- ✅ Shows success/error message

**If you want to save configuration:**
- Use **"Save Configuration"** button instead
- This saves to database but does NOT send to device

**If you want both:**
- Click **"Save Configuration"** first (saves to DB)
- Then click **"Send Configuration"** (sends to device)

