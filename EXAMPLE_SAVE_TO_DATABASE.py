"""
Example: Save Device Configuration to InfluxDB Database
Yeh example dikhata hai ki kaise device configuration ko database mein save karein
"""
from app.services.device_config_db import DeviceConfigDBService
from app.services.config_json_builder import ConfigJSONBuilder
import json


def example_save_complete_config():
    """Example: Complete device configuration save karein"""
    
    # Initialize services
    db_service = DeviceConfigDBService()
    builder = ConfigJSONBuilder()
    
    # Check connection
    if not db_service.is_connected():
        print("❌ InfluxDB not connected!")
        return
    
    print("✅ InfluxDB connected successfully!")
    
    # 1. Build Analog Configuration
    analog_config = builder.build_analog_config(
        input_4_20ma_data=[
            {
                "channel": 1,
                "enabled": True,
                "divider": 100,
                "multiplier": 1,
                "io_pin": "AIN0",
                "name": "Temperature Sensor"
            },
            {
                "channel": 2,
                "enabled": False,
                "divider": 1,
                "multiplier": 1,
                "io_pin": "AIN1",
                "name": "-"
            }
        ],
        input_1_10v_data=[
            {
                "channel": 3,
                "enabled": True,
                "divider": 1000,
                "multiplier": 1,
                "io_pin": "AIN2",
                "name": "Flow Meter"
            }
        ],
        output_0_10v_data=[
            {
                "channel": 1,
                "enabled": True,
                "value": 5.0,
                "io_pin": "DOUT0",
                "name": "Valve Control"
            }
        ]
    )
    
    # 2. Build Digital Configuration
    digital_config = builder.build_digital_config(
        npn_input_data=[
            {
                "channel": 1,
                "enabled": True,
                "io_pin": "INP1H",
                "name": "Start Button"
            }
        ],
        npn_output_data=[
            {
                "channel": 1,
                "enabled": True,
                "io_pin": "OUTL1",
                "name": "Motor Control"
            }
        ],
        pnp_input_data=[],
        pnp_output_data=[],
        relay_data=[
            {
                "channel": 1,
                "enabled": True,
                "io_pin": "RLY1",
                "name": "Main Power Relay"
            }
        ]
    )
    
    # 3. Build MODBUS Configuration
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
            },
            {
                "index": 1,
                "slave_id": "1",
                "function_code": "0x03",
                "register_addr": "1",
                "data_type": "int16",
                "endianness": "Big Endian",
                "var_name": "Pressure"
            }
        ]
    )
    
    # 4. Build CAN Bus Configuration
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
    
    # 5. Build Complete Configuration
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
    
    # 6. Save to Database
    print("\n💾 Saving configuration to database...")
    success = db_service.save_device_config("esp32_gw_01", complete_config)
    
    if success:
        print("✅ Configuration saved successfully!")
        print(f"   Device ID: esp32_gw_01")
        print(f"   Measurement: Device_Config")
        print(f"   Bucket: {db_service.bucket}")
        print(f"   Org: {db_service.org}")
    else:
        print("❌ Error saving configuration")
    
    # 7. Verify by loading back
    print("\n🔍 Verifying saved configuration...")
    loaded_config = db_service.get_device_config("esp32_gw_01")
    
    if loaded_config:
        print("✅ Configuration loaded successfully!")
        print(f"   Device Name: {loaded_config['metadata']['device_name']}")
        print(f"   Analog Inputs (4-20mA): {len(loaded_config['analog']['input_4_20ma'])}")
        print(f"   Analog Inputs (1-10V): {len(loaded_config['analog']['input_1_10v'])}")
        print(f"   Analog Outputs: {len(loaded_config['analog']['output_0_10v'])}")
        print(f"   MODBUS Slaves: {len(loaded_config.get('rs485_modbus', {}).get('slave_devices', []))}")
        print(f"   CAN Messages: {len(loaded_config.get('can_bus', {}).get('can_messages', []))}")
    else:
        print("❌ Configuration not found")
    
    # 8. List all devices
    print("\n📋 Listing all devices...")
    devices = db_service.list_devices()
    print(f"Found {len(devices)} devices:")
    for device_id in devices:
        print(f"  - {device_id}")


def example_save_minimal_config():
    """Example: Minimal device configuration save karein"""
    
    db_service = DeviceConfigDBService()
    builder = ConfigJSONBuilder()
    
    if not db_service.is_connected():
        print("❌ InfluxDB not connected!")
        return
    
    # Build minimal config
    config = builder.build_complete_config(
        device_id="esp32_gw_02",
        device_name="ESP32-Gateway-02",
        analog_config=builder.build_analog_config([], [], []),
        digital_config=builder.build_digital_config([], [], [], [], [])
    )
    
    # Save to database
    success = db_service.save_device_config("esp32_gw_02", config)
    
    if success:
        print("✅ Minimal configuration saved!")
    else:
        print("❌ Error saving configuration")


def example_print_config_json():
    """Example: Configuration JSON print karein"""
    
    builder = ConfigJSONBuilder()
    
    # Build config
    config = builder.build_complete_config(
        device_id="esp32_gw_01",
        device_name="ESP32-Gateway-01",
        analog_config=builder.build_analog_config([], [], []),
        digital_config=builder.build_digital_config([], [], [], [], [])
    )
    
    # Print JSON
    print("📄 Configuration JSON:")
    print(builder.to_json(config, indent=2))


if __name__ == "__main__":
    print("=" * 60)
    print("Device Configuration Database Example")
    print("=" * 60)
    
    # Run example
    example_save_complete_config()
    
    # Uncomment to run other examples
    # example_save_minimal_config()
    # example_print_config_json()
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)

