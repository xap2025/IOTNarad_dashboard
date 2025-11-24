When the Analog tab is active and the user clicks the Send Configuration button, the system sends the Analog configuration JSON.

But from this JSON, please remove these three fields from every channel:

"min_value"

"max_value"

"unit"

from all groups:

input_4_20ma

input_1_10v

output_0_10v

✔ Your updated JSON (after removing min/max/unit)
{
  "type": "Analog",
  "config": {
    "input_4_20ma": [
      {
        "channel": 1,
        "enabled": false,
        "divider": 99,
        "multiplier": 20,
        "io_pin": "AIN0",
        "name": "AIN0"
      },
      {
        "channel": 2,
        "enabled": false,
        "divider": 88,
        "multiplier": 30,
        "io_pin": "AIN1",
        "name": "AIN1"
      }
    ],
    "input_1_10v": [
      {
        "channel": 3,
        "enabled": false,
        "divider": 77,
        "multiplier": 10,
        "io_pin": "AIN2",
        "name": "AIN2"
      },
      {
        "channel": 4,
        "enabled": false,
        "divider": 66,
        "multiplier": 10,
        "io_pin": "AIN3",
        "name": "AIN3"
      }
    ],
    "output_0_10v": [
      {
        "channel": 1,
        "enabled": false,
        "value": 9.0,
        "io_pin": "DOUT0",
        "name": "digitalOutput1"
      },
      {
        "channel": 2,
        "enabled": false,
        "value": 8.0,
        "io_pin": "DOUT1",
        "name": "digitalOutput2"
      }
    ],
    "scan_rate": 2000
  }
}