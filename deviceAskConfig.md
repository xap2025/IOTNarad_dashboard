New Feature: Device Requests Configuration from Server

Now I want to add one more function.

1. How the device will request configuration

When the device needs configuration, it will send an MQTT message to the server.

Topic format:

Cmd/DConfig/<Device ID>


Example:

Cmd/DConfig/8C4B14BA7950


Here, 8C4B14BA7950 is the Device ID.

Payload example:

{
  "command": "Digital"
}


The command tells the server which tab’s configuration the device wants.

Possible command values are:

For Analog tab:

{ "command": "Analog" }


For Digital tab:

{ "command": "Digital" }


For RS485 / Modbus tab:

{ "command": "Modbus" }


For CAN Bus tab:

{ "command": "Canbus" }


All such requests will come on:

Cmd/DConfig/#

2. What the server should do

When the server receives a message on Cmd/DConfig/#:

The server should read the command value.

Based on the command, the server should select only that configuration:

Analog → Analog tab configuration

Digital → Digital tab configuration

Modbus → RS485 / Modbus configuration

Canbus → CAN Bus configuration

The server should send the configuration in the exact same JSON format that is used when the user clicks the Send Configuration button in the UI.

Only the requested tab’s configuration should be sent (not all tabs).

3. MQTT Topics Used
Server

Subscribe:

Cmd/DConfig/#


Publish:

Ack/DConfig/<Device ID>

Device

Publish (request):

Cmd/DConfig/<Device ID>


Subscribe (receive config):

Ack/DConfig/<Device ID>

4. Example Payloads Sent by Server
Digital Configuration (example)
{
  "type": "Digital",
  "config": {
    "npn_input": [
      { "channel": 1, "enabled": true, "io_pin": "INP1H", "name": "proxy_counter" },
      { "channel": 2, "enabled": true, "io_pin": "INP2H", "name": "proxy_ir" },
      { "channel": 3, "enabled": false, "io_pin": "INP3H", "name": "INP3H" },
      { "channel": 4, "enabled": false, "io_pin": "INP4H", "name": "INP4H" }
    ],
    "npn_output": [
      { "channel": 1, "enabled": false, "io_pin": "OUTL1", "name": "OUTL1" },
      { "channel": 2, "enabled": false, "io_pin": "OUTL2", "name": "OUTL2" },
      { "channel": 3, "enabled": false, "io_pin": "OUTL3", "name": "OUTL3" },
      { "channel": 4, "enabled": false, "io_pin": "OUTL4", "name": "OUTL4" }
    ],
    "pnp_input": [],
    "pnp_output": [],
    "relay": [],
    "scan_rate": 1000
  }
}

Analog Configuration (example)
{
  "type": "Analog",
  "config": {
    "input_4_20ma": [
      { "channel": 1, "enabled": false, "divider": 99, "multiplier": 20, "io_pin": "AIN0", "name": "AIN0" },
      { "channel": 2, "enabled": false, "divider": 88, "multiplier": 30, "io_pin": "AIN1", "name": "AIN1" }
    ],
    "input_1_10v": [
      { "channel": 3, "enabled": false, "divider": 77, "multiplier": 10, "io_pin": "AIN2", "name": "AIN2" },
      { "channel": 4, "enabled": false, "divider": 66, "multiplier": 10, "io_pin": "AIN3", "name": "AIN3" }
    ],
    "output_0_10v": [
      { "channel": 1, "enabled": false, "value": 9.0, "io_pin": "DOUT0", "name": "digitalOutput1" },
      { "channel": 2, "enabled": false, "value": 8.0, "io_pin": "DOUT1", "name": "digitalOutput2" }
    ],
    "scan_rate": 2000
  }
}

Modbus Configuration
{
  "type": "Modbus",
  "config": { ... }
}

CAN Bus Configuration
{
  "type": "Canbus",
  "config": { ... }
}

5. Simple Flow Summary

Device asks for a specific configuration using Cmd/DConfig/<Device ID>

Server reads the command (Analog / Digital / Modbus / Canbus)

Server sends only that configuration on Ack/DConfig/<Device ID>

Device receives the configuration and applies it