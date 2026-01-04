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
                logger.warning(f"⚠️ No {command_normalized} configuration found for device {device_id}")
                # Send empty config instead of failing
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
        """Return empty configuration structure for the given type"""
        if config_type == "analog":
            return {
                "input_4_20ma": [],
                "input_1_10v": [],
                "output_0_10v": [],
                "scan_rate": 1000
            }
        elif config_type == "digital":
            return {
                "npn_input": [],
                "npn_output": [],
                "pnp_input": [],
                "pnp_output": [],
                "relay": [],
                "scan_rate": 1000
            }
        elif config_type == "modbus":
            return {
                "communication_settings": {},
                "protocol_settings": {},
                "slave_devices": [],
                "polling_interval": 1000
            }
        elif config_type == "can":
            return {
                "can_settings": {},
                "messages": []
            }
        else:
            return {}

