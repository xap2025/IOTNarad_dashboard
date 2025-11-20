# Save Configuration JSON Reference

This document summarizes what happens inside each **Save Configuration** callback for the Analog, Digital, RS485 MODBUS, and CAN Bus tabs in `app/pages/device_config.py`. Every tab:

- Builds a section-specific JSON payload with `ConfigJSONBuilder` (`app/services/config_json_builder.py`).
- Persists only that section via `DeviceConfigDBService.save_config_sections_only`.
- Rebuilds the merged config (`device_id` + all sections currently stored) and saves it to `Device_Config`, then publishes to MQTT if enabled.

The snippets below show the exact fields that the UI produces for the hardware team.

---

## Analog Tab

When `save-analog-config-btn` fires, we collect the 4 input channels and 2 output channels, validate the values, and build:

```
{
  "device_id": "<serial_number>",
  "analog": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": <bool>,
        "divider": <int>,
        "multiplier": <int>,
        "io_pin": "AIN0",
        "name": "<label>",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      },
      {
        "channel": 2,
        "enabled": <bool>,
        "divider": <int>,
        "multiplier": <int>,
        "io_pin": "AIN1",
        "name": "<label>",
        "min_value": 4,
        "max_value": 20,
        "unit": "mA"
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": <bool>,
        "divider": <int>,
        "multiplier": <int>,
        "io_pin": "AIN2",
        "name": "<label>",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 4,
        "enabled": <bool>,
        "divider": <int>,
        "multiplier": <int>,
        "io_pin": "AIN3",
        "name": "<label>",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": <bool>,
        "value": <float>,   // e.g., 5.0
        "io_pin": "DOUT0",
        "name": "<label>",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      },
      {
        "channel": 2,
        "enabled": <bool>,
        "value": <float>,
        "io_pin": "DOUT1",
        "name": "<label>",
        "min_value": 0,
        "max_value": 10,
        "unit": "V"
      }
    ],
    "scan_rate": <int>   // must be >= 1000 (seconds)
  }
}
```

- Channel order is fixed, and empty names are auto-replaced with their IO pin.
- `value` is always serialized as a float; `0.0` is valid.

---

## Digital Tab

`save-digital-config-btn` collects five channel groups (4 entries each) plus the digital scan rate and builds:

```
{
  "device_id": "<serial_number>",
  "digital": {
    "npn_input": [
      {
        "channel": <1-4>,
        "enabled": <bool>,
        "io_pin": "INP{channel}H",
        "name": "<label>",
        "pullup": true,
        "debounce_ms": 50
      }
      // ...four channels total
    ],
    "npn_output": [
      {
        "channel": <1-4>,
        "enabled": <bool>,
        "io_pin": "OUTL{channel}",
        "name": "<label>",
        "initial_state": false
      }
    ],
    "pnp_input": [
      {
        "channel": <1-4>,
        "enabled": <bool>,
        "io_pin": "INP{channel}L",
        "name": "<label>",
        "pullup": false,
        "debounce_ms": 50
      }
    ],
    "pnp_output": [
      {
        "channel": <1-4>,
        "enabled": <bool>,
        "io_pin": "OUTH{channel}",
        "name": "<label>",
        "initial_state": false
      }
    ],
    "relay": [
      {
        "channel": <1-4>,
        "enabled": <bool>,
        "io_pin": "RLY{channel}",
        "name": "<label>",
        "initial_state": false
      }
    ],
    "scan_rate": <int>   // must be >= 1000 (seconds)
  }
}
```

All names default to their IO pin if left blank. Pull-up, debounce, and initial state values are currently hard-coded defaults from the builder.

---

## RS485 MODBUS Tab

`save-modbus-config-btn` produces:

```
{
  "device_id": "<serial_number>",
  "rs485_modbus": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": <int>,      // e.g., 9600
      "data_bits": <int>,      // e.g., 8
      "parity": "<None|Even|Odd>",
      "stop_bits": <int>       // e.g., 1
    },
    "protocol_settings": {
      "mode": "<RTU|ASCII|TCP>",
      "role": "<Master|Slave>"
    },
    "polling_interval_ms": <int>,   // default 1000
    "slave_devices": [
      {
        "index": <0-based>,
        "slave_id": "<string>",
        "function_code": "<e.g., 0x03>",
        "register_address": "<string>",
        "data_type": "<int8|int16|float...>",
        "endianness": "<Big Endian|Little Endian>",
        "variable_name": "<label>",
        "register_count": 1
      }
      // ...one entry per device row in the UI
    ]
  }
}
```

Values are forced to strings to preserve user formatting (hex prefixes, etc.). The UI store (`modbus-devices-store`) is copied directly into `slave_devices` with these keys.

---

## CAN Bus Tab

`save-canbus-config-btn` uses the CAN form + the two Dash stores (`can-messages-store`, `can-data-mapping-store`) to build:

```
{
  "device_id": "<serial_number>",
  "can_bus": {
    "enabled": true,
    "communication_settings": {
      "baud_rate": <int>,             // e.g., 500
      "identifier_length": "<11-bit|29-bit>",
      "can_mode": "<Normal|Listen|Loopback>",
      "filter_mode": "<None|Accept|Reject>",
      "filter_id": "<hex string>",    // default "0x000"
      "filter_mask": "<hex string>"   // default "0x000"
    },
    "can_messages": [
      {
        "index": <0-based>,
        "can_id": "<hex string>",
        "direction": "<TX|RX>",
        "period_ms": <int>,
        "variable_name": "<label>",
        "data_length": 8               // fixed
      }
      // ...one entry per message row
    ],
    "data_mapping": [
      {
        "index": <0-based>,
        "can_id": "<hex string>",
        "byte_position": "<Byte 0..7>",
        "data_length": "<1 Byte|2 Bytes|...>",
        "data_type": "<int8|uint16|float...>",
        "endianness": "<Big Endian|Little Endian>",
        "variable_name": "<label>",
        "scale_factor": <float>,
        "offset": <float>
      }
      // ...one entry per data-mapping row
    ]
  }
}
```

The stores already contain `scale`, `offset`, etc.; they are cast to floats before serialization.

---

## Notes for Firmware

- After any tab save, the merged JSON (`device_id` + sections that exist) is written to `Device_Config` and published via MQTT. Firmware should subscribe to the device-specific topic to receive the updated payload.
- All numeric fields are typed (`int` or `float`) before serialization to keep the JSON deterministic.
- Channel ordering is stable: indexes always match the physical IO numbering even if the UI hides channels.

Share this file with hardware/firmware teams so they can mirror the exact structure when parsing configuration updates coming from the dashboard.

