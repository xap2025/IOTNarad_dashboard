"""
Device Configuration Database Service
Saves device configurations to InfluxDB

IMPORTANT: Using InfluxDB Cloud Serverless (v3) - SQL queries required
Note: Python client's query_api uses Flux, but documentation should show SQL equivalents
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class DeviceConfigDBService:
    """
    Device Configuration Database Service
    Saves device configurations to InfluxDB using Point structure
    """
    
    def __init__(self):
        # InfluxDB Configuration
        self.url = os.getenv('INFLUXDB_URL', 'https://us-east-1-1.aws.cloud2.influxdata.com')
        self.token = os.getenv('INFLUXDB_TOKEN', 'T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA==')
        self.org = os.getenv('INFLUXDB_ORG', 'iot-narad-gcp')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'iot_data_gcp')
        
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org, timeout=30000)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            self.connected = True
            logger.info(f"✅ Device Config DB Service connected to InfluxDB: {self.url}")
            logger.info(f"   Bucket: {self.bucket}, Org: {self.org}")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Failed to connect Device Config DB Service to InfluxDB: {e}")
    
    def save_device_config(self, device_id: str, config: Dict[str, Any]) -> bool:
        """
        Save device configuration to InfluxDB
        
        Args:
            device_id: Device identifier (e.g., "esp32_gw_01")
            config: Complete device configuration dictionary
            
        Returns:
            Success status
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot save device config.")
            return False
        
        try:
            timestamp = datetime.utcnow()
            
            # Save complete configuration as JSON in a field
            config_json = json.dumps(config, ensure_ascii=False)
            
            # Create Point with measurement "Device_Config"
            point = Point("Device_Config") \
                .tag("device_id", device_id) \
                .tag("device_name", config.get("metadata", {}).get("device_name", device_id)) \
                .tag("device_type", config.get("metadata", {}).get("device_type", "esp32_gateway")) \
                .tag("location", config.get("metadata", {}).get("location", "")) \
                .field("config_json", config_json) \
                .field("version", config.get("metadata", {}).get("version", "1.0.0")) \
                .time(timestamp, WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.info(f"✅ Device configuration saved for: {device_id}")
            logger.info(f"   Measurement: Device_Config")
            logger.info(f"   Timestamp: {timestamp.isoformat()}")
            
            # Also save individual sections for easier querying
            self._save_analog_config(device_id, config.get("analog", {}), timestamp)
            self._save_digital_config(device_id, config.get("digital", {}), timestamp)
            self._save_modbus_config(device_id, config.get("rs485_modbus", {}), timestamp)
            self._save_can_bus_config(device_id, config.get("can_bus", {}), timestamp)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving device config to InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return False
    
    def _save_analog_config(self, device_id: str, analog_config: Dict[str, Any], timestamp: datetime):
        """Save analog configuration as separate points"""
        if not analog_config:
            return
        
        try:
            # Save 4-20mA inputs
            for channel in analog_config.get("input_4_20ma", []):
                point = Point("Device_Config_Analog") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "input_4_20ma") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("divider", channel.get("divider", 1)) \
                    .field("multiplier", channel.get("multiplier", 1)) \
                    .field("min_value", channel.get("min_value", 4)) \
                    .field("max_value", channel.get("max_value", 20)) \
                    .field("unit", channel.get("unit", "mA")) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save 1-10V inputs
            for channel in analog_config.get("input_1_10v", []):
                point = Point("Device_Config_Analog") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "input_1_10v") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("divider", channel.get("divider", 1)) \
                    .field("multiplier", channel.get("multiplier", 1)) \
                    .field("min_value", channel.get("min_value", 1)) \
                    .field("max_value", channel.get("max_value", 10)) \
                    .field("unit", channel.get("unit", "V")) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save 0-10V outputs
            for channel in analog_config.get("output_0_10v", []):
                point = Point("Device_Config_Analog") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "output_0_10v") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("value", channel.get("value", 0.0)) \
                    .field("min_value", channel.get("min_value", 0)) \
                    .field("max_value", channel.get("max_value", 10)) \
                    .field("unit", channel.get("unit", "V")) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.debug(f"✅ Analog config saved for device: {device_id}")
            
        except Exception as e:
            logger.error(f"Error saving analog config: {e}")
    
    def _save_digital_config(self, device_id: str, digital_config: Dict[str, Any], timestamp: datetime):
        """Save digital configuration as separate points"""
        if not digital_config:
            return
        
        try:
            # Save NPN inputs
            for channel in digital_config.get("npn_input", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "npn_input") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("pullup", channel.get("pullup", True)) \
                    .field("debounce_ms", channel.get("debounce_ms", 50)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save NPN outputs
            for channel in digital_config.get("npn_output", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "npn_output") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("initial_state", channel.get("initial_state", False)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save PNP inputs
            for channel in digital_config.get("pnp_input", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "pnp_input") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("pullup", channel.get("pullup", False)) \
                    .field("debounce_ms", channel.get("debounce_ms", 50)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save PNP outputs
            for channel in digital_config.get("pnp_output", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "pnp_output") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("initial_state", channel.get("initial_state", False)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save relays
            for channel in digital_config.get("relay", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "relay") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("initial_state", channel.get("initial_state", False)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.debug(f"✅ Digital config saved for device: {device_id}")
            
        except Exception as e:
            logger.error(f"Error saving digital config: {e}")
    
    def _save_modbus_config(self, device_id: str, modbus_config: Dict[str, Any], timestamp: datetime):
        """Save MODBUS configuration"""
        if not modbus_config or not modbus_config.get("enabled"):
            return
        
        try:
            # Save MODBUS settings
            point = Point("Device_Config_MODBUS") \
                .tag("device_id", device_id) \
                .tag("config_type", "settings") \
                .field("enabled", modbus_config.get("enabled", False)) \
                .field("baud_rate", modbus_config.get("communication_settings", {}).get("baud_rate", 9600)) \
                .field("data_bits", modbus_config.get("communication_settings", {}).get("data_bits", 8)) \
                .field("parity", modbus_config.get("communication_settings", {}).get("parity", "None")) \
                .field("stop_bits", modbus_config.get("communication_settings", {}).get("stop_bits", 1)) \
                .field("mode", modbus_config.get("protocol_settings", {}).get("mode", "RTU")) \
                .field("role", modbus_config.get("protocol_settings", {}).get("role", "Master")) \
                .field("polling_interval_ms", modbus_config.get("polling_interval_ms", 1000)) \
                .time(timestamp, WritePrecision.NS)
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save slave devices
            for slave in modbus_config.get("slave_devices", []):
                point = Point("Device_Config_MODBUS") \
                    .tag("device_id", device_id) \
                    .tag("config_type", "slave_device") \
                    .tag("slave_id", str(slave.get("slave_id", ""))) \
                    .tag("function_code", str(slave.get("function_code", ""))) \
                    .tag("register_address", str(slave.get("register_address", ""))) \
                    .tag("data_type", str(slave.get("data_type", ""))) \
                    .tag("endianness", str(slave.get("endianness", ""))) \
                    .tag("variable_name", str(slave.get("variable_name", ""))) \
                    .field("index", slave.get("index", 0)) \
                    .field("register_count", slave.get("register_count", 1)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.debug(f"✅ MODBUS config saved for device: {device_id}")
            
        except Exception as e:
            logger.error(f"Error saving MODBUS config: {e}")
    
    def _save_can_bus_config(self, device_id: str, can_bus_config: Dict[str, Any], timestamp: datetime):
        """Save CAN Bus configuration"""
        if not can_bus_config or not can_bus_config.get("enabled"):
            return
        
        try:
            # Save CAN Bus settings
            comm_settings = can_bus_config.get("communication_settings", {})
            point = Point("Device_Config_CANBus") \
                .tag("device_id", device_id) \
                .tag("config_type", "settings") \
                .field("enabled", can_bus_config.get("enabled", False)) \
                .field("baud_rate", comm_settings.get("baud_rate", 125)) \
                .field("identifier_length", comm_settings.get("identifier_length", "11-bit")) \
                .field("can_mode", comm_settings.get("can_mode", "Normal")) \
                .field("filter_mode", comm_settings.get("filter_mode", "None")) \
                .field("filter_id", comm_settings.get("filter_id", "0x123")) \
                .field("filter_mask", comm_settings.get("filter_mask", "0x7FF")) \
                .time(timestamp, WritePrecision.NS)
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save CAN messages
            for message in can_bus_config.get("can_messages", []):
                point = Point("Device_Config_CANBus") \
                    .tag("device_id", device_id) \
                    .tag("config_type", "can_message") \
                    .tag("can_id", str(message.get("can_id", ""))) \
                    .tag("direction", str(message.get("direction", ""))) \
                    .tag("variable_name", str(message.get("variable_name", ""))) \
                    .field("index", message.get("index", 0)) \
                    .field("period_ms", message.get("period_ms", 100)) \
                    .field("data_length", message.get("data_length", 8)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save data mappings
            for mapping in can_bus_config.get("data_mapping", []):
                point = Point("Device_Config_CANBus") \
                    .tag("device_id", device_id) \
                    .tag("config_type", "data_mapping") \
                    .tag("can_id", str(mapping.get("can_id", ""))) \
                    .tag("byte_position", str(mapping.get("byte_position", ""))) \
                    .tag("data_type", str(mapping.get("data_type", ""))) \
                    .tag("endianness", str(mapping.get("endianness", ""))) \
                    .tag("variable_name", str(mapping.get("variable_name", ""))) \
                    .field("index", mapping.get("index", 0)) \
                    .field("data_length", str(mapping.get("data_length", ""))) \
                    .field("scale_factor", mapping.get("scale_factor", 1.0)) \
                    .field("offset", mapping.get("offset", 0.0)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.debug(f"✅ CAN Bus config saved for device: {device_id}")
            
        except Exception as e:
            logger.error(f"Error saving CAN Bus config: {e}")
    
    def get_device_config(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get latest device configuration from InfluxDB
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device configuration dictionary or None
        """
        if not self.connected:
            return None
        
        try:
            # NOTE: SQL equivalent: SELECT * FROM "Device_Config" WHERE "device_id" = '{device_id}' AND time > now() - interval '1 year' ORDER BY time DESC LIMIT 1
            # Using Flux here due to Python client limitation
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config")
                |> filter(fn: (r) => r.device_id == "{device_id}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            for table in result:
                for record in table.records:
                    config_json = record.get_value()
                    if config_json:
                        return json.loads(config_json)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting device config: {e}")
            return None
    
    def list_devices(self) -> List[str]:
        """Get list of all devices with configurations"""
        if not self.connected:
            return []
        
        try:
            # NOTE: SQL equivalent: SELECT DISTINCT "device_id" FROM "Device_Config" WHERE time > now() - interval '1 year' ORDER BY "device_id"
            query = f'''
                import "influxdata/influxdb/schema"
                
                schema.tagValues(
                  bucket: "{self.bucket}",
                  tag: "device_id",
                  predicate: (r) => r._measurement == "Device_Config",
                  start: -365d
                )
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            devices = []
            for table in result:
                for record in table.records:
                    devices.append(record.get_value())
            
            return list(set(devices))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return []
    
    def is_connected(self) -> bool:
        """Check if InfluxDB client is connected"""
        return self.connected
    
    def close(self):
        """Close InfluxDB client connection"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logger.info("Device Config DB Service client closed")
        except Exception as e:
            logger.error(f"Error closing Device Config DB Service client: {e}")

