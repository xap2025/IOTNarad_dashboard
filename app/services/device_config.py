"""
Device Configuration Service
Handles device configuration storage and retrieval
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class DeviceConfigService:
    """
    Device Configuration Service
    Stores device configurations in JSON files
    (In production, this could use a database like PostgreSQL or MongoDB)
    """
    
    def __init__(self, config_dir: str = 'data/configs'):
        """
        Initialize Device Configuration Service
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Device config directory: {self.config_dir.absolute()}")
        
        # Default configuration template
        self.default_config = {
            'network': {
                'wifi_ssid': '',
                'wifi_password': '',
                'ip_mode': 'dhcp',
                'static_ip': '',
                'gateway': '',
                'subnet': '255.255.255.0',
                'dns': '8.8.8.8'
            },
            'mqtt': {
                'broker': 'mqtt',
                'port': 1883,
                'username': '',
                'password': '',
                'topic_prefix': 'iotnarad/devices',
                'publish_interval': 5
            },
            'analog': {
                'input_4_20ma': [
                    {'channel': 1, 'enabled': False, 'div': 1, 'mul': 1, 'name': '-', 'io': 'AIN0'},
                    {'channel': 2, 'enabled': False, 'div': 1, 'mul': 1, 'name': '-', 'io': 'AIN1'}
                ],
                'input_1_10v': [
                    {'channel': 3, 'enabled': False, 'div': 1, 'mul': 1, 'name': 'AIN2', 'io': 'AIN2', 'scan_rate': 1000, 'min_value': 0, 'max_value': 10},
                    {'channel': 4, 'enabled': False, 'div': 1, 'mul': 1, 'name': 'AIN3', 'io': 'AIN3', 'scan_rate': 1000, 'min_value': 0, 'max_value': 10}
                ],
                'output_0_10v': [
                    {'channel': 1, 'enabled': False, 'value': 0.0, 'name': '-', 'io': 'DOUT0'},
                    {'channel': 2, 'enabled': False, 'value': 0.0, 'name': '-', 'io': 'DOUT1'}
                ]
            },
            'digital': {
                'npn_input': [
                    {'channel': 1, 'enabled': False, 'name': '-', 'io': 'INP1H'},
                    {'channel': 2, 'enabled': False, 'name': '-', 'io': 'INP2H'},
                    {'channel': 3, 'enabled': False, 'name': '-', 'io': 'INP3H'},
                    {'channel': 4, 'enabled': False, 'name': '-', 'io': 'INP4H'}
                ],
                'npn_output': [
                    {'channel': 1, 'enabled': False, 'name': '-', 'io': 'OUTL1'},
                    {'channel': 2, 'enabled': False, 'name': '-', 'io': 'OUTL2'},
                    {'channel': 3, 'enabled': False, 'name': '-', 'io': 'OUTL3'},
                    {'channel': 4, 'enabled': False, 'name': '-', 'io': 'OUTL4'}
                ],
                'pnp_input': [
                    {'channel': 1, 'enabled': False, 'name': '-', 'io': 'INP1L'},
                    {'channel': 2, 'enabled': False, 'name': '-', 'io': 'INP2L'},
                    {'channel': 3, 'enabled': False, 'name': '-', 'io': 'INP3L'},
                    {'channel': 4, 'enabled': False, 'name': '-', 'io': 'INP4L'}
                ],
                'pnp_output': [
                    {'channel': 1, 'enabled': False, 'name': '-', 'io': 'OUTH1'},
                    {'channel': 2, 'enabled': False, 'name': '-', 'io': 'OUTH2'},
                    {'channel': 3, 'enabled': False, 'name': '-', 'io': 'OUTH3'},
                    {'channel': 4, 'enabled': False, 'name': '-', 'io': 'OUTH4'}
                ],
                'relay': [
                    {'channel': 1, 'enabled': False, 'name': '-', 'io': 'RLY1'},
                    {'channel': 2, 'enabled': False, 'name': '-', 'io': 'RLY2'},
                    {'channel': 3, 'enabled': False, 'name': '-', 'io': 'RLY3'},
                    {'channel': 4, 'enabled': False, 'name': '-', 'io': 'RLY4'}
                ]
            },
            'communication': {
                'modbus': {
                    'enabled': False,
                    'baudrate': 9600,
                    'slave_address': 1,
                    'data_bits': 8,
                    'stop_bits': 1,
                    'parity': 'none'
                },
                'canbus': {
                    'enabled': False,
                    'speed': 500,
                    'filter': ''
                }
            },
            'metadata': {
                'device_name': '',
                'device_type': 'esp32_gateway',
                'location': '',
                'description': '',
                'created_at': '',
                'updated_at': ''
            }
        }
    
    def _get_config_path(self, device_id: str) -> Path:
        """Get configuration file path for a device"""
        return self.config_dir / f"{device_id}.json"
    
    def save_device_config(self, device_id: str, config: Dict[str, Any]) -> bool:
        """
        Save device configuration
        
        Args:
            device_id: Device identifier
            config: Configuration dictionary
            
        Returns:
            Success status
        """
        try:
            config_path = self._get_config_path(device_id)
            
            # Update timestamp
            from datetime import datetime
            if 'metadata' not in config:
                config['metadata'] = {}
            
            config['metadata']['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            
            if not config['metadata'].get('created_at'):
                config['metadata']['created_at'] = config['metadata']['updated_at']
            
            # Write to file
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Configuration saved for device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving device config: {e}")
            return False
    
    def load_device_config(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Load device configuration
        
        Args:
            device_id: Device identifier
            
        Returns:
            Configuration dictionary or None if not found
        """
        try:
            config_path = self._get_config_path(device_id)
            
            if not config_path.exists():
                logger.info(f"No config found for device {device_id}, returning default")
                return self.get_default_config(device_id)
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"📄 Configuration loaded for device: {device_id}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading device config: {e}")
            return None
    
    def get_default_config(self, device_id: str) -> Dict[str, Any]:
        """
        Get default configuration for a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            Default configuration dictionary
        """
        from datetime import datetime
        config = self.default_config.copy()
        
        # Set device-specific defaults
        config['metadata']['device_name'] = device_id
        config['metadata']['created_at'] = datetime.utcnow().isoformat() + 'Z'
        config['metadata']['updated_at'] = config['metadata']['created_at']
        config['mqtt']['topic_prefix'] = f"iotnarad/devices/{device_id}"
        
        return config
    
    def delete_device_config(self, device_id: str) -> bool:
        """
        Delete device configuration
        
        Args:
            device_id: Device identifier
            
        Returns:
            Success status
        """
        try:
            config_path = self._get_config_path(device_id)
            
            if config_path.exists():
                config_path.unlink()
                logger.info(f"🗑️ Configuration deleted for device: {device_id}")
                return True
            else:
                logger.warning(f"No config file found for device: {device_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting device config: {e}")
            return False
    
    def list_devices(self) -> List[str]:
        """
        List all devices with saved configurations
        
        Returns:
            List of device IDs
        """
        try:
            devices = []
            for config_file in self.config_dir.glob('*.json'):
                device_id = config_file.stem
                devices.append(device_id)
            
            logger.debug(f"Found {len(devices)} device configurations")
            return sorted(devices)
            
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return []
    
    def export_config(self, device_id: str, export_path: str) -> bool:
        """
        Export device configuration to a file
        
        Args:
            device_id: Device identifier
            export_path: Path to export file
            
        Returns:
            Success status
        """
        try:
            config = self.load_device_config(device_id)
            if not config:
                return False
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📦 Configuration exported to: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return False
    
    def import_config(self, device_id: str, import_path: str) -> bool:
        """
        Import device configuration from a file
        
        Args:
            device_id: Device identifier
            import_path: Path to import file
            
        Returns:
            Success status
        """
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                logger.error(f"Import file not found: {import_path}")
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update device ID in metadata
            if 'metadata' not in config:
                config['metadata'] = {}
            config['metadata']['device_name'] = device_id
            
            return self.save_device_config(device_id, config)
            
        except Exception as e:
            logger.error(f"Error importing config: {e}")
            return False

