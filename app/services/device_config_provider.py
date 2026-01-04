"""
Device Config Provider Service
Handles device requests for configuration via MQTT
"""
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DeviceConfigProviderService:
    """Service to provide device configurations when requested via MQTT"""
    
    def __init__(self, mqtt_service, db_service):
        """
        Initialize the service
        
        Args:
            mqtt_service: MQTTClientService instance
            db_service: DeviceConfigDBService instance
        """
        self.mqtt_service = mqtt_service
        self.db_service = db_service
        
        # Command to config type mapping
        self.command_map = {
            "Analog": "analog",
            "Digital": "digital",
            "Modbus": "modbus",
            "Canbus": "can"
        }
    
    def handle_config_request(self, device_id: str, command: str) -> bool:
        """
        Handle device configuration request
        
        Args:
            device_id: Device ID requesting configuration
            command: Configuration type requested ("Analog", "Digital", "Modbus", "Canbus")
            
        Returns:
            bool: True if config sent successfully, False otherwise
        """
        try:
            # Normalize command (case-insensitive)
            command_normalized = command.strip().capitalize()
            
            # Map command to config type
            config_type = self.command_map.get(command_normalized)
            if not config_type:
                logger.error(f"❌ Invalid command '{command}' from device {device_id}")
                return False
            
            logger.info(f"📥 Device {device_id} requested {command_normalized} configuration")
            
            # Load configuration from database
            config_data = None
            if config_type == "analog":
                config_data = self.db_service.get_analog_config(device_id)
            elif config_type == "digital":
                config_data = self.db_service.get_digital_config(device_id)
            elif config_type == "modbus":
                config_data = self.db_service.get_modbus_config(device_id)
            elif config_type == "can":
                config_data = self.db_service.get_can_bus_config(device_id)
            
            if not config_data:
                logger.info(f"ℹ️ No {command_normalized} configuration found for device {device_id}. Sending default UI configuration.")
                # Send default UI config instead of empty arrays
                config_data = self._get_empty_config(config_type)
            
            # Build JSON payload (same format as Send Configuration)
            payload = {
                "type": command_normalized,
                "config": config_data
            }
            
            # Publish to Ack/DConfig/<Device ID>
            ack_topic = f"Ack/DConfig/{device_id}"
            message = json.dumps(payload)
            
            logger.info(f"📤 Sending {command_normalized} config to device {device_id} on {ack_topic}")
            logger.debug(f"📤 Payload: {message[:200]}...")
            
            success = self.mqtt_service.publish(ack_topic, payload, qos=1, retain=False)
            
            if success:
                logger.info(f"✅ {command_normalized} configuration sent successfully to device {device_id}")
            else:
                logger.error(f"❌ Failed to send {command_normalized} configuration to device {device_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error handling config request for device {device_id}, command '{command}': {e}")
            logger.exception("Full traceback:")
            return False
    
    def _get_empty_config(self, config_type: str) -> Dict[str, Any]:
        """Return default UI configuration structure for the given type (matches UI defaults)"""
        if config_type == "analog":
            return {
                "input_4_20ma": [
                    {"channel": 1, "enabled": False, "divider": 1, "multiplier": 1, "io_pin": "AIN0", "name": "AIN0"},
                    {"channel": 2, "enabled": False, "divider": 1, "multiplier": 1, "io_pin": "AIN1", "name": "AIN1"}
                ],
                "input_1_10v": [
                    {"channel": 3, "enabled": False, "divider": 1, "multiplier": 1, "io_pin": "AIN2", "name": "AIN2"},
                    {"channel": 4, "enabled": False, "divider": 1, "multiplier": 1, "io_pin": "AIN3", "name": "AIN3"}
                ],
                "output_0_10v": [
                    {"channel": 1, "enabled": False, "value": 0.0, "io_pin": "DOUT0", "name": "DOUT0"},
                    {"channel": 2, "enabled": False, "value": 0.0, "io_pin": "DOUT1", "name": "DOUT1"}
                ],
                "scan_rate": 1000
            }
        elif config_type == "digital":
            return {
                "npn_input": [
                    {"channel": 1, "enabled": False, "io_pin": "INP1H", "name": "-"},
                    {"channel": 2, "enabled": False, "io_pin": "INP2H", "name": "-"},
                    {"channel": 3, "enabled": False, "io_pin": "INP3H", "name": "-"},
                    {"channel": 4, "enabled": False, "io_pin": "INP4H", "name": "-"}
                ],
                "npn_output": [
                    {"channel": 1, "enabled": False, "io_pin": "OUTL1", "name": "-"},
                    {"channel": 2, "enabled": False, "io_pin": "OUTL2", "name": "-"},
                    {"channel": 3, "enabled": False, "io_pin": "OUTL3", "name": "-"},
                    {"channel": 4, "enabled": False, "io_pin": "OUTL4", "name": "-"}
                ],
                "pnp_input": [
                    {"channel": 1, "enabled": False, "io_pin": "INP1L", "name": "-"},
                    {"channel": 2, "enabled": False, "io_pin": "INP2L", "name": "-"},
                    {"channel": 3, "enabled": False, "io_pin": "INP3L", "name": "-"},
                    {"channel": 4, "enabled": False, "io_pin": "INP4L", "name": "-"}
                ],
                "pnp_output": [
                    {"channel": 1, "enabled": False, "io_pin": "OUTH1", "name": "-"},
                    {"channel": 2, "enabled": False, "io_pin": "OUTH2", "name": "-"},
                    {"channel": 3, "enabled": False, "io_pin": "OUTH3", "name": "-"},
                    {"channel": 4, "enabled": False, "io_pin": "OUTH4", "name": "-"}
                ],
                "relay": [
                    {"channel": 1, "enabled": False, "io_pin": "RLY1", "name": "-"},
                    {"channel": 2, "enabled": False, "io_pin": "RLY2", "name": "-"},
                    {"channel": 3, "enabled": False, "io_pin": "RLY3", "name": "-"},
                    {"channel": 4, "enabled": False, "io_pin": "RLY4", "name": "-"}
                ],
                "scan_rate": 1000
            }
        elif config_type == "modbus":
            return {
                "communication_settings": {
                    "baud_rate": "9600",
                    "data_bits": "8",
                    "parity": "None",
                    "stop_bits": "1"
                },
                "protocol_settings": {
                    "mode": "RTU",
                    "role": "Master"
                },
                "slave_devices": [],
                "polling_interval": 1000
            }
        elif config_type == "can":
            return {
                "can_settings": {
                    "baud_rate": "125",
                    "identifier_length": "11-bit",
                    "can_mode": "Normal",
                    "filter_mode": "None",
                    "filter_id": "0x123",
                    "filter_mask": "0x7FF"
                },
                "messages": []
            }
        else:
            return {}

