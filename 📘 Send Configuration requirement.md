📘 Device Configuration – “Send Configuration” Workflow (Full Explanation & Clean Version)

My Device page has three buttons:

Save Configuration

Load from Device

Reset to Default

You want to rename “Reset to Default” → “Send Configuration”, and implement the proper logic for sending configuration from Server → Device via MQTT.

Below is the complete phrased version.

1️⃣ Button Rename

Rename the existing button:

❌ Reset to Default
✔️ Send Configuration

2️⃣ Required Functionality — Send Configuration Button
Step 1: User selects device

The user selects a Device ID from the Select Device dropdown.

Step 2: User configures settings

Based on the active tab, the user sets configuration values:

If they are on Analog → configure Analog parameters

If they are on Digital → configure Digital parameters

If they are on MODBUS → configure Modbus parameters

If they are on CAN Bus → configure CAN parameters

Step 3: When user clicks “Send Configuration”

The server must:

Read the currently active tab

Convert the tab values into a JSON configuration object

Publish that JSON to the device via MQTT

Topic used:

Write/DConfig/<Device ID>


The device will receive this configuration and apply it.

3️⃣ Server → Device MQTT Flow
Server PUBLISHES configuration to:
Write/DConfig/<Device ID>

The payload structure depends on the active tab:
4️⃣ Configuration Payloads (Tab-wise)
🔹 Analog Configuration (When Analog tab is active)
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

🔹 Digital Configuration
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

🔹 MODBUS Configuration
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
    "slave_devices": [
      {
        "index": 0,
        "slave_id": "1",
        "function_code": "0x03",
        "register_address": "1000",
        "data_type": "int16",
        "endianness": "Little Endian",
        "variable_name": "Temp1",
        "register_count": 1
      }
    ]
  }
}

🔹 CAN Bus Configuration
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

5️⃣ Device → Server (ACK Response)

After receiving the config, the device sends back an acknowledgment.

Device PUBLISHES:
Config/ACK/<Device ID>

Example Payload:
{ "Result": "OK" }


This tells the server:

Configuration received successfully

No error occurred

6️⃣ Server listens for ACK

The server listens on:

Config/ACK/#


Meaning:
“Listen to ACK from any device.”

7️⃣ Full Send Configuration Flow (Summary)
User → Clicks Send Configuration
↓
Server → Reads active tab and builds JSON config
↓
Server publishes config to → Write/DConfig/<DeviceID>
↓
Device receives config and applies settings
↓
Device publishes ACK to → Config/ACK/<DeviceID>
↓
Server listens on → Config/ACK/# and confirms success

8️⃣ One-Line Summary for IT Team

Server sends configuration using → Write/DConfig/<DeviceID>
Device confirms success using → Config/ACK/<DeviceID>
Server listens to all ACKs on → Config/ACK/#