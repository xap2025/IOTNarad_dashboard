"""
Configuration JSON Builder
Helper functions to build device configuration JSON from Dash form data
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class ConfigJSONBuilder:
    """Build device configuration JSON from form data"""
    
    @staticmethod
    def build_analog_config(
        input_4_20ma_data: List[Dict],
        input_1_10v_data: List[Dict],
        output_0_10v_data: List[Dict],
        scan_rate: int = 1000
    ) -> Dict[str, Any]:
        """
        Build analog configuration section
        
        Args:
            input_4_20ma_data: List of 4-20mA input channel data
            input_1_10v_data: List of 1-10V input channel data
            output_0_10v_data: List of 0-10V output channel data
            scan_rate: Scan rate in seconds (default: 1000)
            
        Returns:
            Analog configuration dictionary
        """
        return {
            "input_4_20ma": [
                {
                    "channel": item.get("channel", idx + 1),
                    "enabled": item.get("enabled", False),
                    "divider": item.get("divider", 1),
                    "multiplier": item.get("multiplier", 1),
                    "io_pin": item.get("io_pin", f"AIN{idx}"),
                    "name": item.get("name", "-"),
                    "min_value": 4,
                    "max_value": 20,
                    "unit": "mA"
                }
                for idx, item in enumerate(input_4_20ma_data)
            ],
            "input_1_10v": [
                {
                    "channel": item.get("channel", idx + 3),
                    "enabled": item.get("enabled", False),
                    "divider": item.get("divider", 1),
                    "multiplier": item.get("multiplier", 1),
                    "io_pin": item.get("io_pin", f"AIN{idx + 2}"),
                    "name": item.get("name", item.get("io_pin", f"AIN{idx + 2}")) if item.get("name") else item.get("io_pin", f"AIN{idx + 2}"),
                    "min_value": 0,
                    "max_value": 10,
                    "unit": "V"
                }
                for idx, item in enumerate(input_1_10v_data)
            ],
            "output_0_10v": [
                {
                    "channel": item.get("channel", idx + 1),
                    "enabled": item.get("enabled", False),
                    "value": item.get("value", 0.0),
                    "io_pin": item.get("io_pin", f"DOUT{idx}"),
                    "name": item.get("name", "-"),
                    "min_value": 0,
                    "max_value": 10,
                    "unit": "V"
                }
                for idx, item in enumerate(output_0_10v_data)
            ],
            "scan_rate": scan_rate
        }
    
    @staticmethod
    def build_digital_config(
        npn_input_data: List[Dict],
        npn_output_data: List[Dict],
        pnp_input_data: List[Dict],
        pnp_output_data: List[Dict],
        relay_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Build digital configuration section
        
        Args:
            npn_input_data: List of NPN input channel data
            npn_output_data: List of NPN output channel data
            pnp_input_data: List of PNP input channel data
            pnp_output_data: List of PNP output channel data
            relay_data: List of relay channel data
            
        Returns:
            Digital configuration dictionary
        """
        return {
            "npn_input": [
                {
                    "channel": item.get("channel", idx + 1),
                    "enabled": item.get("enabled", False),
                    "io_pin": item.get("io_pin", f"INP{idx + 1}H"),
                    "name": item.get("name", "-")
                }
                for idx, item in enumerate(npn_input_data)
            ],
            "npn_output": [
                {
                    "channel": item.get("channel", idx + 1),
                    "enabled": item.get("enabled", False),
                    "io_pin": item.get("io_pin", f"OUTL{idx + 1}"),
                    "name": item.get("name", "-")
                }
                for idx, item in enumerate(npn_output_data)
            ],
            "pnp_input": [
                {
                    "channel": item.get("channel", idx + 1),
                    "enabled": item.get("enabled", False),
                    "io_pin": item.get("io_pin", f"INP{idx + 1}L"),
                    "name": item.get("name", "-")
                }
                for idx, item in enumerate(pnp_input_data)
            ],
            "pnp_output": [
                {
                    "channel": item.get("channel", idx + 1),
                    "enabled": item.get("enabled", False),
                    "io_pin": item.get("io_pin", f"OUTH{idx + 1}"),
                    "name": item.get("name", "-")
                }
                for idx, item in enumerate(pnp_output_data)
            ],
            "relay": [
                {
                    "channel": item.get("channel", idx + 1),
                    "enabled": item.get("enabled", False),
                    "io_pin": item.get("io_pin", f"RLY{idx + 1}"),
                    "name": item.get("name", "-")
                }
                for idx, item in enumerate(relay_data)
            ]
        }
    
    @staticmethod
    def build_modbus_config(
        baud_rate: str,
        data_bits: str,
        parity: str,
        stop_bits: str,
        mode: str,
        role: str,
        polling_interval: int,
        slave_devices: List[Dict]
    ) -> Dict[str, Any]:
        """
        Build RS485 MODBUS configuration section
        
        Args:
            baud_rate: Baud rate (e.g., "9600")
            data_bits: Data bits (e.g., "8")
            parity: Parity ("None", "Even", "Odd")
            stop_bits: Stop bits (e.g., "1")
            mode: MODBUS mode ("RTU", "ASCII", "TCP")
            role: MODBUS role ("Master", "Slave")
            polling_interval: Polling interval in milliseconds
            slave_devices: List of slave device configurations from store
            
        Returns:
            MODBUS configuration dictionary
        """
        return {
            "communication_settings": {
                "baud_rate": int(baud_rate),
                "data_bits": int(data_bits),
                "parity": parity,
                "stop_bits": int(stop_bits)
            },
            "protocol_settings": {
                "mode": mode,
                "role": role
            },
            "polling_interval_ms": polling_interval,
            "slave_devices": [
                {
                    "index": device.get("index", idx),
                    "slave_id": str(device.get("slave_id", "1")),
                    "function_code": str(device.get("function_code", "0x03")),
                    "register_address": str(device.get("register_addr", "0")),
                    "data_type": str(device.get("data_type", "int8")),
                    "endianness": str(device.get("endianness", "Big Endian")),
                    "variable_name": str(device.get("var_name", "Variable Name"))
                }
                for idx, device in enumerate(slave_devices)
            ]
        }
    
    @staticmethod
    def build_can_bus_config(
        baud_rate: str,
        identifier_length: str,
        can_mode: str,
        filter_mode: str,
        filter_id: str,
        filter_mask: str,
        can_messages: List[Dict],
        data_mappings: List[Dict]
    ) -> Dict[str, Any]:
        """
        Build CAN Bus configuration section
        
        Args:
            baud_rate: Baud rate (e.g., "125", "250", "500", "1000")
            identifier_length: Identifier length ("11-bit" or "29-bit")
            can_mode: CAN mode ("Normal", "Listen", "Loopback")
            filter_mode: Filter mode ("None", "Accept", "Reject")
            filter_id: Filter ID (hex format, e.g., "0x123")
            filter_mask: Filter mask (hex format, e.g., "0x7FF")
            can_messages: List of CAN message configurations from store
            data_mappings: List of data mapping configurations from store
            
        Returns:
            CAN Bus configuration dictionary
        """
        return {
            "communication_settings": {
                "baud_rate": int(baud_rate),
                "identifier_length": identifier_length,
                "can_mode": can_mode,
                "filter_mode": filter_mode,
                "filter_id": filter_id,
                "filter_mask": filter_mask
            },
            "can_messages": [
                {
                    "index": message.get("index", idx),
                    "can_id": str(message.get("can_id", "0x123")),
                    "direction": str(message.get("direction", "TX")),
                    # CRITICAL: Support both field names - new format (period_ms) and old format (period)
                    "period_ms": int(message.get("period_ms") if "period_ms" in message and message.get("period_ms") is not None else (message.get("period", 100) if message.get("period") is not None else 100)),
                    # CRITICAL: Support both field names - new format (variable_name) and old format (var_name)
                    "variable_name": str(message.get("variable_name") if "variable_name" in message and message.get("variable_name") else (message.get("var_name", "Message Name")))
                    # Removed "data_length": 8 - not in UI
                }
                for idx, message in enumerate(can_messages)
            ],
            "data_mapping": [
                {
                    "index": mapping.get("index", idx),
                    "can_id": str(mapping.get("can_id", "0x123")),
                    # CRITICAL: Support both field names - new format (byte_position) and old format (byte_pos)
                    "byte_position": str(mapping.get("byte_position") if "byte_position" in mapping and mapping.get("byte_position") else (mapping.get("byte_pos", "Byte 0"))),
                    # CRITICAL: Support both field names - new format (data_length) and old format (data_len)
                    "data_length": str(mapping.get("data_length") if "data_length" in mapping and mapping.get("data_length") else (mapping.get("data_len", "1 Byte"))),
                    "data_type": str(mapping.get("data_type", "int8")),
                    "endianness": str(mapping.get("endianness", "Big Endian")),
                    # CRITICAL: Support both field names - new format (variable_name) and old format (var_name)
                    "variable_name": str(mapping.get("variable_name") if "variable_name" in mapping and mapping.get("variable_name") else (mapping.get("var_name", "Variable Name"))),
                    # CRITICAL: Support both field names - new format (scale_factor) and old format (scale)
                    "scale_factor": float(mapping.get("scale_factor") if "scale_factor" in mapping and mapping.get("scale_factor") is not None else (mapping.get("scale", 1.0) if mapping.get("scale") is not None else 1.0)),
                    "offset": float(mapping.get("offset", 0.0) if mapping.get("offset") is not None else 0.0)
                }
                for idx, mapping in enumerate(data_mappings)
            ]
        }
    
    @staticmethod
    def build_complete_config(
        device_id: str,
        device_name: str,
        analog_config: Dict[str, Any],
        digital_config: Dict[str, Any],
        modbus_config: Optional[Dict[str, Any]] = None,
        can_bus_config: Optional[Dict[str, Any]] = None,
        mqtt_config: Optional[Dict[str, Any]] = None,
        network_config: Optional[Dict[str, Any]] = None,
        location: str = "",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Build complete device configuration JSON
        
        Args:
            device_id: Device ID
            device_name: Device name
            analog_config: Analog configuration
            digital_config: Digital configuration
            modbus_config: MODBUS configuration (optional)
            can_bus_config: CAN Bus configuration (optional)
            mqtt_config: MQTT configuration (optional)
            network_config: Network configuration (optional)
            location: Device location (optional)
            description: Device description (optional)
            
        Returns:
            Complete device configuration dictionary
        """
        now = datetime.utcnow().isoformat() + 'Z'
        
        config = {
            "device_id": device_id,
            "metadata": {
                "device_name": device_name,
                "device_type": "esp32_gateway",
                "location": location,
                "description": description,
                "created_at": now,
                "updated_at": now,
                "version": "1.0.0"
            },
            "analog": analog_config,
            "digital": digital_config
        }
        
        if modbus_config:
            config["rs485_modbus"] = modbus_config
        
        if can_bus_config:
            config["can_bus"] = can_bus_config
        
        if mqtt_config:
            config["mqtt"] = mqtt_config
        else:
            config["mqtt"] = {
                "broker": "mqtt",
                "port": 1883,
                "username": "",
                "password": "",
                "topic_prefix": f"iotnarad/devices/{device_id}",
                "publish_interval": 5,
                "qos": 1,
                "retain": False
            }
        
        if network_config:
            config["network"] = network_config
        else:
            config["network"] = {
                "wifi_ssid": "",
                "wifi_password": "",
                "ip_mode": "dhcp",
                "static_ip": "",
                "gateway": "",
                "subnet": "255.255.255.0",
                "dns": "8.8.8.8"
            }
        
        return config
    
    @staticmethod
    def to_json(config: Dict[str, Any], indent: int = 2) -> str:
        """
        Convert configuration dictionary to JSON string
        
        Args:
            config: Configuration dictionary
            indent: JSON indentation (default: 2)
            
        Returns:
            JSON string
        """
        return json.dumps(config, indent=indent, ensure_ascii=False)


# Example usage
if __name__ == "__main__":
    builder = ConfigJSONBuilder()
    
    # Example: Build analog config
    analog_config = builder.build_analog_config(
        input_4_20ma_data=[
            {"channel": 1, "enabled": True, "divider": 100, "multiplier": 1, "io_pin": "AIN0", "name": "Temperature"},
            {"channel": 2, "enabled": False, "divider": 1, "multiplier": 1, "io_pin": "AIN1", "name": "-"}
        ],
        input_1_10v_data=[
            {"channel": 3, "enabled": True, "divider": 1000, "multiplier": 1, "io_pin": "AIN2", "name": "Flow Meter"}
        ],
        output_0_10v_data=[
            {"channel": 1, "enabled": True, "value": 5.0, "io_pin": "DOUT0", "name": "Valve Control"}
        ]
    )
    
    # Example: Build MODBUS config
    modbus_config = builder.build_modbus_config(
        baud_rate="9600",
        data_bits="8",
        parity="None",
        stop_bits="1",
        mode="RTU",
        role="Master",
        polling_interval=1000,
        slave_devices=[
            {"index": 0, "slave_id": "1", "function_code": "0x03", "register_addr": "0", 
             "data_type": "int16", "endianness": "Big Endian", "var_name": "Temperature"},
            {"index": 1, "slave_id": "1", "function_code": "0x03", "register_addr": "1", 
             "data_type": "int16", "endianness": "Big Endian", "var_name": "Pressure"}
        ]
    )
    
    # Example: Build complete config
    complete_config = builder.build_complete_config(
        device_id="esp32_gw_01",
        device_name="ESP32-Gateway-01",
        analog_config=analog_config,
        digital_config={
            "npn_input": [],
            "npn_output": [],
            "pnp_input": [],
            "pnp_output": [],
            "relay": []
        },
        modbus_config=modbus_config
    )
    
    # Print JSON
    print(builder.to_json(complete_config))

