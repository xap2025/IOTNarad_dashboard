# How to Save Device Configuration as JSON

## Overview
Yeh guide explain karta hai ki kaise sabhi device configurations (Analog, Digital, RS485 MODBUS, CAN Bus) ko collect karke JSON format mein save kiya jaye.

## Step-by-Step Implementation

### Step 1: Collect Form Data from Dash UI

Device configuration page se sabhi form data collect karna hoga. Ye data Dash callbacks ke through collect hota hai.

### Step 2: Build JSON Structure

`ConfigJSONBuilder` class use karke JSON structure build karein.

### Step 3: Save to File/Database

`DeviceConfigService` use karke configuration save karein.

---

## Implementation in `device_config.py`

### 1. Import Required Modules

```python
from app.services.config_json_builder import ConfigJSONBuilder
from app.services.device_config import DeviceConfigService
from dash import Input, Output, State, ALL, callback
```

### 2. Update Save Configuration Callback

```python
@callback(
    Output('config-save-toast', 'is_open'),
    Output('config-save-toast', 'children'),
    Input('save-config-btn', 'n_clicks'),
    # Analog Input States
    State({'type': 'analog-input-enable', 'index': ALL}, 'value'),
    State({'type': 'analog-input-div', 'index': ALL}, 'value'),
    State({'type': 'analog-input-mul', 'index': ALL}, 'value'),
    State({'type': 'analog-input-name', 'index': ALL}, 'value'),
    # Analog Output States
    State({'type': 'analog-output-enable', 'index': ALL}, 'value'),
    State({'type': 'analog-output-value', 'index': ALL}, 'value'),
    State({'type': 'analog-output-name', 'index': ALL}, 'value'),
    # Digital States (NPN Input)
    State({'type': 'npn-input-enable', 'index': ALL}, 'value'),
    State({'type': 'npn-input-name', 'index': ALL}, 'value'),
    # Digital States (NPN Output)
    State({'type': 'npn-output-enable', 'index': ALL}, 'value'),
    State({'type': 'npn-output-name', 'index': ALL}, 'value'),
    # Digital States (PNP Input)
    State({'type': 'pnp-input-enable', 'index': ALL}, 'value'),
    State({'type': 'pnp-input-name', 'index': ALL}, 'value'),
    # Digital States (PNP Output)
    State({'type': 'pnp-output-enable', 'index': ALL}, 'value'),
    State({'type': 'pnp-output-name', 'index': ALL}, 'value'),
    # Digital States (Relay)
    State({'type': 'relay-enable', 'index': ALL}, 'value'),
    State({'type': 'relay-name', 'index': ALL}, 'value'),
    # MODBUS States
    State('modbus-baud-rate', 'value'),
    State('modbus-data-bits', 'value'),
    State('modbus-parity', 'value'),
    State('modbus-stop-bits', 'value'),
    State('modbus-mode', 'value'),
    State('modbus-role', 'value'),
    State('modbus-polling-interval', 'value'),
    State('modbus-devices-store', 'data'),
    # CAN Bus States
    State('can-baud-rate', 'value'),
    State('can-identifier-length', 'value'),
    State('can-mode', 'value'),
    State('can-filter-mode', 'value'),
    State('can-filter-id', 'value'),
    State('can-filter-mask', 'value'),
    State('can-messages-store', 'data'),
    State('can-data-mapping-store', 'data'),
    # Device Selection
    State('device-selector', 'value'),
    prevent_initial_call=True
)
def save_configuration(
    n_clicks,
    # Analog Input
    analog_input_enable, analog_input_div, analog_input_mul, analog_input_name,
    # Analog Output
    analog_output_enable, analog_output_value, analog_output_name,
    # Digital NPN Input
    npn_input_enable, npn_input_name,
    # Digital NPN Output
    npn_output_enable, npn_output_name,
    # Digital PNP Input
    pnp_input_enable, pnp_input_name,
    # Digital PNP Output
    pnp_output_enable, pnp_output_name,
    # Digital Relay
    relay_enable, relay_name,
    # MODBUS
    modbus_baud_rate, modbus_data_bits, modbus_parity, modbus_stop_bits,
    modbus_mode, modbus_role, modbus_polling_interval, modbus_devices_store,
    # CAN Bus
    can_baud_rate, can_identifier_length, can_mode, can_filter_mode,
    can_filter_id, can_filter_mask, can_messages_store, can_data_mapping_store,
    # Device
    device_id
):
    """Save device configuration to JSON"""
    if not n_clicks:
        return False, ""
    
    try:
        builder = ConfigJSONBuilder()
        config_service = DeviceConfigService()
        
        # Build Analog Config
        # 4-20mA Input (channels 1-2)
        input_4_20ma_data = []
        for idx in range(2):
            input_4_20ma_data.append({
                "channel": idx + 1,
                "enabled": analog_input_enable[idx] if idx < len(analog_input_enable) else False,
                "divider": analog_input_div[idx] if idx < len(analog_input_div) else 1,
                "multiplier": analog_input_mul[idx] if idx < len(analog_input_mul) else 1,
                "io_pin": f"AIN{idx}",
                "name": analog_input_name[idx] if idx < len(analog_input_name) else "-"
            })
        
        # 1-10V Input (channels 3-4)
        input_1_10v_data = []
        for idx in range(2):
            input_1_10v_data.append({
                "channel": idx + 3,
                "enabled": analog_input_enable[idx + 2] if idx + 2 < len(analog_input_enable) else False,
                "divider": analog_input_div[idx + 2] if idx + 2 < len(analog_input_div) else 1,
                "multiplier": analog_input_mul[idx + 2] if idx + 2 < len(analog_input_mul) else 1,
                "io_pin": f"AIN{idx + 2}",
                "name": analog_input_name[idx + 2] if idx + 2 < len(analog_input_name) else "-"
            })
        
        # 0-10V Output
        output_0_10v_data = []
        for idx in range(2):
            output_0_10v_data.append({
                "channel": idx + 1,
                "enabled": analog_output_enable[idx] if idx < len(analog_output_enable) else False,
                "value": analog_output_value[idx] if idx < len(analog_output_value) else 0.0,
                "io_pin": f"DOUT{idx}",
                "name": analog_output_name[idx] if idx < len(analog_output_name) else "-"
            })
        
        analog_config = builder.build_analog_config(
            input_4_20ma_data,
            input_1_10v_data,
            output_0_10v_data
        )
        
        # Build Digital Config
        npn_input_data = []
        for idx in range(4):
            npn_input_data.append({
                "channel": idx + 1,
                "enabled": npn_input_enable[idx] if idx < len(npn_input_enable) else False,
                "io_pin": f"INP{idx + 1}H",
                "name": npn_input_name[idx] if idx < len(npn_input_name) else "-"
            })
        
        npn_output_data = []
        for idx in range(4):
            npn_output_data.append({
                "channel": idx + 1,
                "enabled": npn_output_enable[idx] if idx < len(npn_output_enable) else False,
                "io_pin": f"OUTL{idx + 1}",
                "name": npn_output_name[idx] if idx < len(npn_output_name) else "-"
            })
        
        pnp_input_data = []
        for idx in range(4):
            pnp_input_data.append({
                "channel": idx + 1,
                "enabled": pnp_input_enable[idx] if idx < len(pnp_input_enable) else False,
                "io_pin": f"INP{idx + 1}L",
                "name": pnp_input_name[idx] if idx < len(pnp_input_name) else "-"
            })
        
        pnp_output_data = []
        for idx in range(4):
            pnp_output_data.append({
                "channel": idx + 1,
                "enabled": pnp_output_enable[idx] if idx < len(pnp_output_enable) else False,
                "io_pin": f"OUTH{idx + 1}",
                "name": pnp_output_name[idx] if idx < len(pnp_output_name) else "-"
            })
        
        relay_data = []
        for idx in range(4):
            relay_data.append({
                "channel": idx + 1,
                "enabled": relay_enable[idx] if idx < len(relay_enable) else False,
                "io_pin": f"RLY{idx + 1}",
                "name": relay_name[idx] if idx < len(relay_name) else "-"
            })
        
        digital_config = builder.build_digital_config(
            npn_input_data,
            npn_output_data,
            pnp_input_data,
            pnp_output_data,
            relay_data
        )
        
        # Build MODBUS Config
        modbus_config = None
        if modbus_devices_store:
            modbus_config = builder.build_modbus_config(
                baud_rate=modbus_baud_rate or "9600",
                data_bits=modbus_data_bits or "8",
                parity=modbus_parity or "None",
                stop_bits=modbus_stop_bits or "1",
                mode=modbus_mode or "RTU",
                role=modbus_role or "Master",
                polling_interval=modbus_polling_interval or 1000,
                slave_devices=modbus_devices_store
            )
        
        # Build CAN Bus Config
        can_bus_config = None
        if can_messages_store and can_data_mapping_store:
            can_bus_config = builder.build_can_bus_config(
                baud_rate=can_baud_rate or "125",
                identifier_length=can_identifier_length or "11-bit",
                can_mode=can_mode or "Normal",
                filter_mode=can_filter_mode or "None",
                filter_id=can_filter_id or "0x123",
                filter_mask=can_filter_mask or "0x7FF",
                can_messages=can_messages_store,
                data_mappings=can_data_mapping_store
            )
        
        # Build Complete Config
        complete_config = builder.build_complete_config(
            device_id=device_id or "esp32_gw_01",
            device_name=device_id or "ESP32-Gateway-01",
            analog_config=analog_config,
            digital_config=digital_config,
            modbus_config=modbus_config,
            can_bus_config=can_bus_config
        )
        
        # Save Configuration
        success = config_service.save_device_config(device_id or "esp32_gw_01", complete_config)
        
        if success:
            return True, f"✅ Configuration saved successfully for {device_id}"
        else:
            return True, f"❌ Error saving configuration for {device_id}"
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving configuration: {e}")
        return True, f"❌ Error: {str(e)}"
```

---

## Data Collection from Stores

### MODBUS Devices Store
MODBUS devices store se data directly collect hota hai:

```python
# Store data format:
modbus_devices_store = [
    {
        "index": 0,
        "slave_id": "1",
        "function_code": "0x03",
        "register_addr": "0",
        "data_type": "int8",
        "endianness": "Big Endian",
        "var_name": "Variable Name"
    },
    # ... more devices
]
```

### CAN Bus Messages Store
CAN Bus messages store se data directly collect hota hai:

```python
# Store data format:
can_messages_store = [
    {
        "index": 0,
        "can_id": "0x123",
        "direction": "TX",
        "period": "100",
        "var_name": "Message Name"
    },
    # ... more messages
]
```

### CAN Bus Data Mapping Store
CAN Bus data mapping store se data directly collect hota hai:

```python
# Store data format:
can_data_mapping_store = [
    {
        "index": 0,
        "can_id": "0x123",
        "byte_pos": "Byte 0",
        "data_len": "1 Byte",
        "data_type": "int8",
        "endianness": "Big Endian",
        "var_name": "Variable Name",
        "scale": "1",
        "offset": "0"
    },
    # ... more mappings
]
```

---

## Complete Example

### Example: Save Configuration with All Sections

```python
from app.services.config_json_builder import ConfigJSONBuilder
from app.services.device_config import DeviceConfigService

builder = ConfigJSONBuilder()
config_service = DeviceConfigService()

# 1. Build Analog Config
analog_config = builder.build_analog_config(
    input_4_20ma_data=[
        {"channel": 1, "enabled": True, "divider": 100, "multiplier": 1, 
         "io_pin": "AIN0", "name": "Temperature"}
    ],
    input_1_10v_data=[
        {"channel": 3, "enabled": True, "divider": 1000, "multiplier": 1, 
         "io_pin": "AIN2", "name": "Flow Meter"}
    ],
    output_0_10v_data=[
        {"channel": 1, "enabled": True, "value": 5.0, 
         "io_pin": "DOUT0", "name": "Valve Control"}
    ]
)

# 2. Build Digital Config
digital_config = builder.build_digital_config(
    npn_input_data=[
        {"channel": 1, "enabled": True, "io_pin": "INP1H", "name": "Start Button"}
    ],
    npn_output_data=[
        {"channel": 1, "enabled": True, "io_pin": "OUTL1", "name": "Motor Control"}
    ],
    pnp_input_data=[],
    pnp_output_data=[],
    relay_data=[
        {"channel": 1, "enabled": True, "io_pin": "RLY1", "name": "Main Power Relay"}
    ]
)

# 3. Build MODBUS Config
modbus_config = builder.build_modbus_config(
    baud_rate="9600",
    data_bits="8",
    parity="None",
    stop_bits="1",
    mode="RTU",
    role="Master",
    polling_interval=1000,
    slave_devices=[
        {
            "index": 0,
            "slave_id": "1",
            "function_code": "0x03",
            "register_addr": "0",
            "data_type": "int16",
            "endianness": "Big Endian",
            "var_name": "Temperature"
        }
    ]
)

# 4. Build CAN Bus Config
can_bus_config = builder.build_can_bus_config(
    baud_rate="500",
    identifier_length="11-bit",
    can_mode="Normal",
    filter_mode="Accept",
    filter_id="0x123",
    filter_mask="0x7FF",
    can_messages=[
        {
            "index": 0,
            "can_id": "0x123",
            "direction": "TX",
            "period": "100",
            "var_name": "Engine Speed"
        }
    ],
    data_mappings=[
        {
            "index": 0,
            "can_id": "0x123",
            "byte_pos": "Byte 0",
            "data_len": "1 Byte",
            "data_type": "int8",
            "endianness": "Big Endian",
            "var_name": "Speed Low",
            "scale": "1",
            "offset": "0"
        }
    ]
)

# 5. Build Complete Config
complete_config = builder.build_complete_config(
    device_id="esp32_gw_01",
    device_name="ESP32-Gateway-01",
    analog_config=analog_config,
    digital_config=digital_config,
    modbus_config=modbus_config,
    can_bus_config=can_bus_config,
    location="Production Line 1",
    description="Main gateway for production monitoring"
)

# 6. Save Configuration
success = config_service.save_device_config("esp32_gw_01", complete_config)

if success:
    print("✅ Configuration saved successfully!")
    # Print JSON
    print(builder.to_json(complete_config))
else:
    print("❌ Error saving configuration")
```

---

## File Location

Saved configurations are stored in:
```
data/configs/{device_id}.json
```

Example: `data/configs/esp32_gw_01.json`

---

## Next Steps

1. **Update `device_config.py`** - Add the save configuration callback with all State inputs
2. **Test** - Test saving configuration for each device type
3. **Load Configuration** - Implement load functionality to populate forms from saved JSON
4. **MQTT Integration** - Send configuration to devices via MQTT after saving
5. **Validation** - Add validation for form data before saving

---

## Notes

- **All arrays** can have multiple entries (slave devices, CAN messages, etc.)
- **Enabled flags** control whether a channel/device is active
- **Index fields** are used for array ordering (0-based)
- **Hex values** (CAN ID, Filter ID) should be in string format with "0x" prefix
- **Timestamps** are automatically generated in ISO 8601 format
- **Empty/unused channels** should have `enabled: false` and `name: "-"`

