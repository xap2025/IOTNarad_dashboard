On my Device page, I have three buttons:
1.	Save Configuration


2.	Load from Device


3.	Reset to Default


Now I want to add the proper functionality for the Load from Device button.
Required Functionality: Load from Device
When the user clicks the Load from Device button:
•	It should request the configuration directly from the device using MQTT.


•	The selected device is determined by the Select Device dropdown.


•	The configuration loaded depends on the active tab (Analog, Digital, Modbus, CAN Bus).


Example Workflow
If the user is on:
•	Device → Analog tab
 Clicking Load from Device should request the Analog configuration from the device and then display it in the Analog UI.


If the user is on:
•	Device → Digital tab
 Clicking Load from Device should fetch the Digital configuration and show it in the Digital UI.


Same logic for:
•	RS485 MODBUS


•	CAN Bus


Only the payload changes, not the topic.
________________________________________
✅ Server ↔ Device Configuration Exchange (Simple Explanation)
There are only two MQTT topics for configuration exchange:
________________________________________
🟩 1. Server → Device (Read Request Topic)
Topic:
Cmd/SConfig/<Device ID>


•	The Server publishes on this topic


•	The Device subscribes to this topic


________________________________________
🟩 2. Device → Server (Reply Topic)
Topic:
Dev/Config/Reply/<Device-ID>


•	The Device publishes on this topic


•	The Server subscribes to this topic


________________________________________
⭐ Important Note
Analog, Digital, Modbus, CAN — all use the same two topics.
 They do NOT require separate topics.
Only the payload (JSON command) is different.
________________________________________
🟦 Commands Sent by Server (Requests)
A. Get Analog Configuration
Topic:
Cmd/SConfig/<Device ID>

Payload:
{
"command":"Analog"
}
________________________________________
B. Get Digital Configuration
Topic:
Cmd/SConfig/<Device ID>

Payload:
{
"command":"Digital"
}

________________________________________


C. Get Modbus Configuration
Topic:
Cmd/SConfig/<Device ID>

Payload:
{
"command":"Modbus"
}

________________________________________
D. Get CAN Bus Configuration
Topic:
Cmd/SConfig/<Device ID>

Payload:
{
"command":"Canbus"
}

________________________________________

🟧 Device Replies (Same Topic for All)
Device always responds on:
Ack/SConfig/<Device ID>

Example Replies:
Analog Reply
{
"type":"Analog",
"config":{
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

Digital Reply
{
"type":"Digital",
"config":{
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

Modbus Reply
{
"type":"Modbus",
"config":{
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



CAN Bus Reply
{
"type":"Canbus",
"config":{}
}
For example 👍

{
"type":"Canbus",
"config":{
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

________________________________________
🟩 Final Summary — Server
✔ Server SUBSCRIBES to:
Ack/SConfig/#

✔ Server PUBLISHES to:
Cmd/SConfig/<Device ID>

________________________________________
🟩 Final Summary — Device
✔ Device SUBSCRIBES to:
Cmd/SConfig/<Device ID>

✔ Device PUBLISHES to:
Ack/SConfig/<Device ID>

Note: Make sure that whatever JSON the device sends, it should be visible and displayed correctly in the UI.

