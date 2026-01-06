"""
Device Configuration Database Service
Saves device configurations to InfluxDB

IMPORTANT: Using Self-Hosted InfluxDB 2.x
- Supports Flux queries via Python client
- Local instance running via Docker
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
        # Self-Hosted InfluxDB 2.x Configuration
        self.url = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
        self.token = os.getenv('INFLUXDB_TOKEN', '')
        self.org = os.getenv('INFLUXDB_ORG', 'iotnarad')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'iotnarad-bucket')
        
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org, timeout=30000)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            self.connected = True
            logger.info(f"✅ Device Config DB Service connected to InfluxDB: {self.url}")
            logger.info(f"   Database: Self-Hosted InfluxDB 2.x")
            logger.info(f"   Bucket: {self.bucket}, Org: {self.org}")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Failed to connect Device Config DB Service to InfluxDB: {e}")
    
    def save_device_config(self, device_id: str, config: Dict[str, Any]) -> bool:
        """
        Save device configuration to InfluxDB
        
        Args:
            device_id: Device Serial Number (Sr_No) from Device_info measurement
            config: Complete device configuration dictionary
            
        Returns:
            Success status
        """
        # Validate device_id
        if not device_id or not device_id.strip():
            logger.error("❌ Cannot save device config: device_id is empty or None")
            return False
            
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot save device config.")
            return False
        
        try:
            timestamp = datetime.utcnow()
            
            # Save complete configuration as JSON in a field
            config_json = json.dumps(config, ensure_ascii=False)
            
            # Create Point with measurement "Device_Config"
            # Note: metadata has been removed, config only contains device_id and sections
            point = Point("Device_Config") \
                .tag("device_id", device_id) \
                .field("config_json", config_json) \
                .time(timestamp, WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.info(f"✅ Device configuration saved for: {device_id}")
            logger.info(f"   Measurement: Device_Config (merged JSON only)")
            logger.info(f"   Timestamp: {timestamp.isoformat()}")
            
            # NOTE: Individual sections are saved via save_config_sections_only() 
            # This method ONLY saves the merged complete JSON to Device_Config
            # DO NOT save individual sections here to avoid duplicate entries
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving device config to InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return False
    
    def save_config_sections_only(self, device_id: str, config: Dict[str, Any]) -> bool:
        """
        Save only individual configuration sections to their respective tables
        Does NOT save to Device_Config measurement
        
        Used by individual "Save Configuration" buttons in each tab
        
        Args:
            device_id: Device Serial Number (Sr_No)
            config: Configuration dictionary (can be partial)
            
        Returns:
            Success status
        """
        # Validate device_id
        if not device_id or not device_id.strip():
            logger.error("❌ Cannot save device config sections: device_id is empty or None")
            return False
            
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot save device config sections.")
            return False
        
        try:
            timestamp = datetime.utcnow()
            
            # Save ONLY the sections that are provided in the config (not all sections)
            # This ensures we only save the specific tab's data when called from individual save buttons
            if "analog" in config:
                self._save_analog_config(device_id, config.get("analog", {}), timestamp)
            if "digital" in config:
                self._save_digital_config(device_id, config.get("digital", {}), timestamp)
            if "rs485_modbus" in config:
                self._save_modbus_config(device_id, config.get("rs485_modbus", {}), timestamp)
            if "can_bus" in config:
                self._save_can_bus_config(device_id, config.get("can_bus", {}), timestamp)
            
            logger.info(f"✅ Device configuration sections saved for: {device_id} (no Device_Config)")
            logger.info(f"   Saved to individual tables only")
            logger.info(f"   Timestamp: {timestamp.isoformat()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving device config sections to InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return False
    
    def _save_analog_config(self, device_id: str, analog_config: Dict[str, Any], timestamp: datetime):
        """Save analog configuration as separate points"""
        # Ensure device_id is valid
        if not device_id or not device_id.strip():
            logger.warning("⚠️ Cannot save analog config: device_id is empty or None")
            return
            
        if not analog_config:
            return
        
        try:
            # Get scan_rate from analog_config top level (applies to all channels)
            scan_rate = analog_config.get("scan_rate", 1000)
            
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
                    .field("scan_rate", scan_rate) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save 0-10V inputs (input_1_10v - renamed but still uses same channel type)
            for channel in analog_config.get("input_1_10v", []):
                point = Point("Device_Config_Analog") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "input_1_10v") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", channel.get("io_pin", ""))) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("divider", channel.get("divider", 1)) \
                    .field("multiplier", channel.get("multiplier", 1)) \
                    .field("scan_rate", scan_rate) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save 0-10V outputs
            output_0_10v_list = analog_config.get("output_0_10v", [])
            logger.info(f"🔍 STEP: Saving output_0_10v channels - count: {len(output_0_10v_list)} for device {device_id}")
            logger.info(f"🔍 DEBUG: Full analog_config keys: {list(analog_config.keys())}")
            logger.info(f"🔍 DEBUG: analog_config.get('output_0_10v'): {analog_config.get('output_0_10v', 'KEY_NOT_FOUND')}")
            logger.info(f"🔍 DEBUG: output_0_10v_list type: {type(output_0_10v_list)}, contents: {output_0_10v_list}")
            
            if not output_0_10v_list:
                logger.error(f"❌ CRITICAL: output_0_10v list is EMPTY for device {device_id}!")
                logger.error(f"❌ Full analog_config: {analog_config}")
                logger.error(f"❌ analog_config.get('output_0_10v'): {analog_config.get('output_0_10v', 'KEY_NOT_FOUND')}")
            else:
                logger.info(f"✅ Found {len(output_0_10v_list)} output_0_10v channels to save")
                
                # Collect all points first for batch write
                output_points = []
                
                for idx, channel in enumerate(output_0_10v_list):
                    try:
                        channel_num = channel.get("channel", "")
                        channel_value = channel.get("value", 0.0)
                        channel_name = channel.get("name", "")
                        channel_io_pin = channel.get("io_pin", "")
                        channel_enabled = channel.get("enabled", False)
                        
                        logger.info(f"🔍 Processing output channel {idx+1}/{len(output_0_10v_list)} - channel: {channel_num}, value: {channel_value}, name: {channel_name}, io_pin: {channel_io_pin}, enabled: {channel_enabled}")
                        
                        # Ensure value is valid
                        # Note: We store values as integers (millivolts) to match existing schema
                        # and preserve precision: 5.5V = 5500 mV, 0.0V = 0 mV, 10.0V = 10000 mV
                        # Self-Hosted InfluxDB 2.x supports both integer and float types
                        try:
                            float_value = float(channel_value)
                            # Validate range: 0.0 to 10.0 volts
                            if float_value < 0.0:
                                float_value = 0.0
                                logger.warning(f"⚠️ Channel {channel_num} - value < 0, clamping to 0.0V")
                            elif float_value > 10.0:
                                float_value = 10.0
                                logger.warning(f"⚠️ Channel {channel_num} - value > 10.0, clamping to 10.0V")
                            
                            # Convert to integer by multiplying by 1000 (millivolts)
                            # Use round() to handle floating point precision issues
                            # This preserves precision: 5.5V = 5500 mV, 0.0V = 0 mV, 10.0V = 10000 mV
                            int_value = int(round(float_value * 1000))
                            logger.info(f"✅ Channel {channel_num} - value converted: {float_value}V = {int_value}mV (integer)")
                        except (ValueError, TypeError) as ve:
                            logger.error(f"❌ Cannot convert value '{channel_value}' to float for channel {channel_num}: {ve}")
                            int_value = 0  # Default to 0 mV (0.0V)
                        
                        # Create InfluxDB point
                        # Use integer type for 'value' field to match existing schema
                        point = Point("Device_Config_Analog") \
                            .tag("device_id", device_id) \
                            .tag("channel_type", "output_0_10v") \
                            .tag("channel", str(channel_num)) \
                            .tag("io_pin", str(channel_io_pin)) \
                            .tag("name", str(channel_name)) \
                            .field("enabled", bool(channel_enabled)) \
                            .field("value", int_value) \
                            .field("scan_rate", int(scan_rate)) \
                            .time(timestamp, WritePrecision.NS)
                        
                        output_points.append(point)
                        logger.info(f"✅ Channel {channel_num} - point created successfully, added to batch (batch size: {len(output_points)})")
                        
                    except Exception as channel_error:
                        logger.error(f"❌ Error creating point for output channel {channel_num}: {channel_error}")
                        logger.exception(f"Full traceback for output channel {channel_num}:")
                        # Continue with next channel instead of stopping
                        continue
                
                # Batch write all output points at once
                if output_points:
                    try:
                        logger.info(f"🔍 Writing {len(output_points)} output_0_10v points to InfluxDB...")
                        self.write_api.write(bucket=self.bucket, org=self.org, record=output_points)
                        logger.info(f"✅ Successfully batch-saved {len(output_points)} output_0_10v channels to Device_Config_Analog for device {device_id}")
                        
                        # Log details of each saved channel (using the original channel data, not Point object)
                        for idx, channel in enumerate(output_0_10v_list):
                            channel_num = channel.get("channel", "")
                            channel_value = channel.get("value", 0.0)
                            logger.info(f"✅ Saved output_0_10v: channel={channel_num}, value={channel_value}V ({int(round(float(channel_value) * 1000))}mV)")
                    except Exception as write_error:
                        logger.error(f"❌ CRITICAL: Failed to write output_0_10v points to InfluxDB: {write_error}")
                        logger.exception("Full traceback for batch write error:")
                        raise  # Re-raise to ensure caller knows save failed
                else:
                    logger.warning(f"⚠️ No output points to write (output_points list is empty)")
            
            logger.debug(f"✅ Analog config saved for device: {device_id}")
            
        except Exception as e:
            logger.error(f"❌ Error saving analog config for device {device_id}: {e}")
            logger.exception("Full traceback for analog config save error:")
            # Re-raise exception to ensure caller knows save failed
            raise
    
    def _save_digital_config(self, device_id: str, digital_config: Dict[str, Any], timestamp: datetime):
        """Save digital configuration as separate points"""
        # Ensure device_id is valid
        if not device_id or not device_id.strip():
            logger.warning("⚠️ Cannot save digital config: device_id is empty or None")
            return
            
        if not digital_config:
            return
        
        try:
            # Get scan_rate from digital_config top level (applies to all channels)
            scan_rate = digital_config.get("scan_rate", 1000)
            
            # Save NPN inputs
            # NOTE: Only saving UI-visible parameters: enabled, channel, io_pin, name, scan_rate
            # Removed: pullup, debounce_ms (not in UI)
            for channel in digital_config.get("npn_input", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "npn_input") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("scan_rate", scan_rate) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save NPN outputs
            # NOTE: Only saving UI-visible parameters: enabled, channel, io_pin, name, scan_rate
            # Removed: initial_state (not in UI)
            for channel in digital_config.get("npn_output", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "npn_output") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("scan_rate", scan_rate) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save PNP inputs
            # NOTE: Only saving UI-visible parameters: enabled, channel, io_pin, name, scan_rate
            # Removed: pullup, debounce_ms (not in UI)
            for channel in digital_config.get("pnp_input", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "pnp_input") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("scan_rate", scan_rate) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save PNP outputs
            # NOTE: Only saving UI-visible parameters: enabled, channel, io_pin, name, scan_rate
            # Removed: initial_state (not in UI)
            for channel in digital_config.get("pnp_output", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "pnp_output") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("scan_rate", scan_rate) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            # Save relays
            # NOTE: Only saving UI-visible parameters: enabled, channel, io_pin, name, scan_rate
            # Removed: initial_state (not in UI)
            for channel in digital_config.get("relay", []):
                point = Point("Device_Config_Digital") \
                    .tag("device_id", device_id) \
                    .tag("channel_type", "relay") \
                    .tag("channel", str(channel.get("channel", ""))) \
                    .tag("io_pin", channel.get("io_pin", "")) \
                    .tag("name", channel.get("name", "")) \
                    .field("enabled", channel.get("enabled", False)) \
                    .field("scan_rate", scan_rate) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.debug(f"✅ Digital config saved for device: {device_id}")
            
        except Exception as e:
            logger.error(f"Error saving digital config: {e}")
    
    def _save_modbus_config(self, device_id: str, modbus_config: Dict[str, Any], timestamp: datetime):
        """Save MODBUS configuration"""
        # Ensure device_id is valid
        if not device_id or not device_id.strip():
            logger.warning("⚠️ Cannot save MODBUS config: device_id is empty or None")
            return
            
        if not modbus_config:
            logger.warning("⚠️ Cannot save MODBUS config: modbus_config is empty or None")
            return
        
        # Debug logging
        logger.info(f"🔍 _save_modbus_config called for device: {device_id}")
        logger.info(f"   Config keys: {list(modbus_config.keys())}")
        logger.info(f"   Communication settings: {modbus_config.get('communication_settings')}")
        logger.info(f"   Protocol settings: {modbus_config.get('protocol_settings')}")
        logger.info(f"   Polling interval: {modbus_config.get('polling_interval_ms')}")
        logger.info(f"   Slave devices count: {len(modbus_config.get('slave_devices', []))}")
        
        try:
            # Extract values with detailed logging
            comm_settings = modbus_config.get("communication_settings", {})
            protocol_settings = modbus_config.get("protocol_settings", {})
            
            baud_rate = comm_settings.get("baud_rate", 9600)
            data_bits = comm_settings.get("data_bits", 8)
            parity = comm_settings.get("parity", "None")
            stop_bits = comm_settings.get("stop_bits", 1)
            mode = protocol_settings.get("mode", "RTU")
            role = protocol_settings.get("role", "Master")
            polling_interval = modbus_config.get("polling_interval_ms", 1000)
            
            logger.info(f"🔍 Extracted values for saving:")
            logger.info(f"   Baud Rate: {baud_rate}")
            logger.info(f"   Data Bits: {data_bits}")
            logger.info(f"   Parity: {parity}")
            logger.info(f"   Stop Bits: {stop_bits}")
            logger.info(f"   Mode: {mode}")
            logger.info(f"   Role: {role}")
            logger.info(f"   Polling Interval: {polling_interval}")
            
            # Save MODBUS settings
            point = Point("Device_Config_MODBUS") \
                .tag("device_id", device_id) \
                .tag("config_type", "settings") \
                .field("enabled", modbus_config.get("enabled", False)) \
                .field("baud_rate", baud_rate) \
                .field("data_bits", data_bits) \
                .field("parity", parity) \
                .field("stop_bits", stop_bits) \
                .field("mode", mode) \
                .field("role", role) \
                .field("polling_interval_ms", polling_interval) \
                .time(timestamp, WritePrecision.NS)
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.info(f"✅ MODBUS settings point written to database")
            
            # Save slave devices
            slave_devices_list = modbus_config.get("slave_devices", [])
            logger.info(f"💾 Saving {len(slave_devices_list)} slave device(s) to database for device {device_id}")
            
            for idx, slave in enumerate(slave_devices_list):
                slave_id = str(slave.get("slave_id", ""))
                slave_index = slave.get("index", idx)
                
                # CRITICAL: Log each slave being saved
                logger.debug(f"   Saving slave [{idx}]: Index={slave_index}, Slave ID={slave_id}, "
                           f"Register={slave.get('register_address')}, Var={slave.get('variable_name')}")
                
                point = Point("Device_Config_MODBUS") \
                    .tag("device_id", device_id) \
                    .tag("config_type", "slave_device") \
                    .tag("slave_id", slave_id) \
                    .tag("function_code", str(slave.get("function_code", ""))) \
                    .tag("register_address", str(slave.get("register_address", ""))) \
                    .tag("data_type", str(slave.get("data_type", ""))) \
                    .tag("endianness", str(slave.get("endianness", ""))) \
                    .tag("variable_name", str(slave.get("variable_name", ""))) \
                    .field("index", slave_index) \
                    .field("register_count", slave.get("register_count", 1)) \
                    .time(timestamp, WritePrecision.NS)
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.info(f"✅ MODBUS: Saved {len(slave_devices_list)} slave device(s) to database")
            
            logger.debug(f"✅ MODBUS config saved for device: {device_id}")
            
        except Exception as e:
            logger.error(f"Error saving MODBUS config: {e}")
    
    def _save_can_bus_config(self, device_id: str, can_bus_config: Dict[str, Any], timestamp: datetime):
        """Save CAN Bus configuration"""
        # Ensure device_id is valid
        if not device_id or not device_id.strip():
            logger.warning("⚠️ Cannot save CAN Bus config: device_id is empty or None")
            return
            
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
            device_id: Device Serial Number (Sr_No) from Device_info measurement
            
        Returns:
            Device configuration dictionary or None
        """
        if not self.connected:
            return None
        
        try:
            # Flux query for Self-Hosted InfluxDB 2.x
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
            # Flux query for Self-Hosted InfluxDB 2.x - Get distinct device IDs
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
    
    def get_analog_config(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get latest analog configuration from Device_Config_Analog table"""
        if not self.connected or not device_id or not device_id.strip():
            return None
        
        try:
            # Escape device_id for Flux query (replace backslashes and quotes)
            escaped_device_id = device_id.replace('\\', '\\\\').replace('"', '\\"')
            
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config_Analog")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> pivot(rowKey: ["_time", "channel_type", "channel", "io_pin", "name"], columnKey: ["_field"], valueColumn: "_value")
                |> group(columns: ["channel_type", "channel", "io_pin", "name"])
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            logger.debug(f"🔍 Executing analog config query for device_id: {device_id}")
            result = self.query_api.query(org=self.org, query=query)
            
            input_4_20ma = []
            input_1_10v = []
            output_0_10v = []
            scan_rate = 1000
            
            for table in result:
                for record in table.records:
                    channel_type = record.values.get("channel_type", "")
                    channel = record.values.get("channel", "")
                    io_pin = record.values.get("io_pin", "")
                    name = record.values.get("name", "")
                    enabled = record.values.get("enabled", False)
                    divider = record.values.get("divider", 1.0)
                    multiplier = record.values.get("multiplier", 1.0)
                    scan_rate_val = record.values.get("scan_rate", 1000)
                    value = record.values.get("value", 0.0)
                    
                    scan_rate = scan_rate_val  # All channels have same scan_rate
                    
                    channel_data = {
                        "channel": int(channel) if channel else 0,
                        "enabled": enabled,
                        "io_pin": io_pin,
                        "name": name
                    }
                    
                    if channel_type == "input_4_20ma":
                        channel_data["divider"] = divider
                        channel_data["multiplier"] = multiplier
                        input_4_20ma.append(channel_data)
                    elif channel_type == "input_1_10v":
                        channel_data["divider"] = divider
                        channel_data["multiplier"] = multiplier
                        input_1_10v.append(channel_data)
                    elif channel_type == "output_0_10v":
                        # Convert integer value (millivolts) back to float (volts)
                        # IMPORTANT: In InfluxDB, value is stored as integer (millivolts)
                        # We convert back to float (volts) for UI display
                        # 5500 mV = 5.5V, 0 mV = 0.0V, 10000 mV = 10.0V
                        try:
                            if value is None:
                                channel_data["value"] = 0.0
                            elif isinstance(value, int):
                                # Value is in millivolts, convert to volts
                                channel_data["value"] = float(value) / 1000.0
                            elif isinstance(value, float):
                                # Already in volts (shouldn't happen, but handle it)
                                channel_data["value"] = float(value)
                            else:
                                # Try to convert to int first, then to float
                                int_val = int(float(value)) if value else 0
                                channel_data["value"] = float(int_val) / 1000.0
                            logger.debug(f"✅ Loaded output_0_10v channel {channel}: {value} mV = {channel_data['value']} V")
                        except (ValueError, TypeError) as ve:
                            logger.error(f"❌ Error converting value for output channel {channel}: {value} - {ve}")
                            channel_data["value"] = 0.0  # Default to 0.0V
                        output_0_10v.append(channel_data)
            
            if not input_4_20ma and not input_1_10v and not output_0_10v:
                return None
            
            return {
                "input_4_20ma": input_4_20ma,
                "input_1_10v": input_1_10v,
                "output_0_10v": output_0_10v,
                "scan_rate": scan_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting analog config for device_id '{device_id}': {e}")
            logger.exception("Full traceback:")
            return None
    
    def get_digital_config(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get latest digital configuration from Device_Config_Digital table"""
        if not self.connected or not device_id or not device_id.strip():
            return None
        
        try:
            # Escape device_id for Flux query (replace backslashes and quotes)
            escaped_device_id = device_id.replace('\\', '\\\\').replace('"', '\\"')
            
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config_Digital")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> pivot(rowKey: ["_time", "channel_type", "channel", "io_pin", "name"], columnKey: ["_field"], valueColumn: "_value")
                |> group(columns: ["channel_type", "channel", "io_pin", "name"])
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            logger.debug(f"🔍 Executing digital config query for device_id: {device_id}")
            result = self.query_api.query(org=self.org, query=query)
            
            npn_input = []
            npn_output = []
            pnp_input = []
            pnp_output = []
            relay = []
            scan_rate = 1000
            
            for table in result:
                for record in table.records:
                    channel_type = record.values.get("channel_type", "")
                    channel = record.values.get("channel", "")
                    io_pin = record.values.get("io_pin", "")
                    name = record.values.get("name", "")
                    enabled = record.values.get("enabled", False)
                    # NOTE: Removed pullup, debounce_ms, initial_state - these are not in UI
                    scan_rate_val = record.values.get("scan_rate", 1000)
                    
                    scan_rate = scan_rate_val
                    
                    # Only include UI-visible parameters
                    channel_data = {
                        "channel": int(channel) if channel else 0,
                        "enabled": enabled,
                        "io_pin": io_pin,
                        "name": name
                    }
                    
                    if channel_type == "npn_input":
                        npn_input.append(channel_data)
                    elif channel_type == "npn_output":
                        npn_output.append(channel_data)
                    elif channel_type == "pnp_input":
                        pnp_input.append(channel_data)
                    elif channel_type == "pnp_output":
                        pnp_output.append(channel_data)
                    elif channel_type == "relay":
                        relay.append(channel_data)
            
            if not npn_input and not npn_output and not pnp_input and not pnp_output and not relay:
                return None
            
            config = {
                "npn_input": npn_input,
                "npn_output": npn_output,
                "pnp_input": pnp_input,
                "pnp_output": pnp_output,
                "relay": relay
            }
            
            # Add scan_rate if available
            if scan_rate:
                config["scan_rate"] = scan_rate
            
            return config
            
        except Exception as e:
            logger.error(f"Error getting digital config for device_id '{device_id}': {e}")
            logger.exception("Full traceback:")
            return None
    
    def get_modbus_config(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get latest MODBUS configuration from Device_Config_MODBUS table
        
        CRITICAL: This must retrieve ALL slave devices, not just one.
        The query separates settings (limit to 1) from slave devices (get all).
        """
        if not self.connected or not device_id or not device_id.strip():
            return None
        
        try:
            # Escape device_id for Flux query (replace backslashes and quotes)
            escaped_device_id = device_id.replace('\\', '\\\\').replace('"', '\\"')
            
            # Query 1: Get latest settings (only 1 record needed)
            settings_query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> filter(fn: (r) => r.config_type == "settings")
                |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            # Query 2: Get ALL slave devices from the latest save
            # CRITICAL FIX: The old query grouped by config_type and limited to 1, which only returned 1 slave device
            # New strategy: All slave devices are saved with the SAME timestamp in one save operation
            # We need to get ALL slave devices from the latest timestamp, not just 1 per slave_id
            # 
            # Approach: 
            # 1. Find the latest timestamp for any MODBUS config
            # 2. Get ALL slave devices from that timestamp (they all have the same timestamp)
            # 3. Group by slave_id and get latest for each (handles multiple saves)
            #    BUT: If all slaves are from same timestamp, we get all of them
            
            # First, find the latest timestamp
            latest_timestamp_query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            # Get latest timestamp
            latest_timestamp_result = self.query_api.query(org=self.org, query=latest_timestamp_query)
            latest_timestamp = None
            for table in latest_timestamp_result:
                for record in table.records:
                    latest_timestamp = record.get_time()
                    break
            
            # Query ALL slave devices from the latest save
            # CRITICAL FIX: The old query grouped by config_type and limited to 1, which only returned 1 slave device
            # New strategy: Group by slave_id (not config_type) to get latest version of each unique slave
            # Since all slaves are saved with the same timestamp in one save, grouping by slave_id gets all of them
            # 
            # IMPORTANT: This query groups by slave_id and gets the latest for each
            # If user saves 5 slaves, we get all 5 (one per unique slave_id)
            # If user saves 1 slave later, we get that 1 (but previous 4 are still in DB with older timestamp)
            # So we need to get ALL slaves from the LATEST timestamp, not just latest per slave_id
            #
            # Better approach: Get all slave devices, sort by timestamp, get the latest timestamp,
            # then filter to only slaves from that timestamp
            slave_devices_query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config_MODBUS")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> filter(fn: (r) => r.config_type == "slave_device")
                |> pivot(rowKey: ["_time", "slave_id"], columnKey: ["_field"], valueColumn: "_value")
                |> sort(columns: ["_time"], desc: true)
                |> group(columns: ["slave_id"])
                |> limit(n: 1)
            '''
            
            logger.debug(f"🔍 Executing MODBUS config queries for device_id: {device_id}")
            
            # Execute settings query
            settings_result = self.query_api.query(org=self.org, query=settings_query)
            settings = {}
            
            for table in settings_result:
                for record in table.records:
                    settings = {
                        "enabled": record.values.get("enabled", False),
                        "communication_settings": {
                            "baud_rate": record.values.get("baud_rate", 9600),
                            "data_bits": record.values.get("data_bits", 8),
                            "parity": record.values.get("parity", "None"),
                            "stop_bits": record.values.get("stop_bits", 1)
                        },
                        "protocol_settings": {
                            "mode": record.values.get("mode", "RTU"),
                            "role": record.values.get("role", "Master")
                        },
                        "polling_interval_ms": record.values.get("polling_interval_ms", 1000)
                    }
                    break  # Only need first record (latest)
            
            # Execute slave devices query - get ALL slave devices
            # CRITICAL: Since we don't group by slave_id, we get all records sorted by time
            # We need to find the latest timestamp and get ALL slaves from that timestamp
            slave_devices_result = self.query_api.query(org=self.org, query=slave_devices_query)
            slave_devices = []
            latest_slave_timestamp = None
            
            # First pass: Collect all slave devices and find the latest timestamp
            all_slave_records = []
            for table in slave_devices_result:
                for record in table.records:
                    record_time = record.get_time()
                    if latest_slave_timestamp is None or record_time > latest_slave_timestamp:
                        latest_slave_timestamp = record_time
                    all_slave_records.append({
                        "time": record_time,
                        "index": record.values.get("index", 0),
                        "slave_id": record.values.get("slave_id", "1"),
                        "function_code": record.values.get("function_code", "0x03"),
                        "register_address": record.values.get("register_address", "0"),
                        "data_type": record.values.get("data_type", "int8"),
                        "endianness": record.values.get("endianness", "Big Endian"),
                        "variable_name": record.values.get("variable_name", ""),
                        "register_count": record.values.get("register_count", 1)
                    })
            
            logger.debug(f"   Found {len(all_slave_records)} total slave record(s), latest timestamp: {latest_slave_timestamp}")
            
            # Second pass: Filter to only slaves from the latest timestamp
            # This ensures we get ALL slaves from the latest save operation
            # All slaves are saved with the same timestamp, so we get all of them
            # CRITICAL: Use a larger time window (5 seconds) to handle any timestamp precision issues
            if latest_slave_timestamp:
                from datetime import timedelta
                time_window = timedelta(seconds=5)  # 5 second window for timestamp precision
                for record in all_slave_records:
                    time_diff = abs(record["time"] - latest_slave_timestamp)
                    if time_diff <= time_window:
                        slave_devices.append({
                            "index": record["index"],
                            "slave_id": record["slave_id"],
                            "function_code": record["function_code"],
                            "register_address": record["register_address"],
                            "data_type": record["data_type"],
                            "endianness": record["endianness"],
                            "variable_name": record["variable_name"],
                            "register_count": record["register_count"]
                        })
                logger.debug(f"   Filtered to {len(slave_devices)} slave(s) from latest timestamp {latest_slave_timestamp}")
                logger.debug(f"   Slave IDs from latest save: {[s.get('slave_id') for s in slave_devices]}")
            else:
                # Fallback: Use all records if no timestamp found
                for record in all_slave_records:
                    slave_devices.append({
                        "index": record["index"],
                        "slave_id": record["slave_id"],
                        "function_code": record["function_code"],
                        "register_address": record["register_address"],
                        "data_type": record["data_type"],
                        "endianness": record["endianness"],
                        "variable_name": record["variable_name"],
                        "register_count": record["register_count"]
                    })
                logger.debug(f"   No timestamp found, using all {len(slave_devices)} slave record(s)")
            
            # Sort slave devices by index to ensure correct order
            slave_devices.sort(key=lambda x: x.get("index", 0))
            
            logger.info(f"✅ MODBUS config loaded: {len(slave_devices)} slave device(s) found for device {device_id}")
            if len(slave_devices) > 0:
                logger.debug(f"   Slave IDs: {[s.get('slave_id') for s in slave_devices]}")
                logger.debug(f"   Indices: {[s.get('index') for s in slave_devices]}")
                if latest_slave_timestamp:
                    logger.debug(f"   Latest timestamp: {latest_slave_timestamp}")
            
            if not settings:
                return None
            
            settings["slave_devices"] = slave_devices
            return settings
            
        except Exception as e:
            logger.error(f"Error getting MODBUS config for device_id '{device_id}': {e}")
            logger.exception("Full traceback:")
            return None
    
    def get_can_bus_config(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get latest CAN Bus configuration from Device_Config_CANBus table"""
        if not self.connected or not device_id or not device_id.strip():
            return None
        
        try:
            # Escape device_id for Flux query (replace backslashes and quotes)
            escaped_device_id = device_id.replace('\\', '\\\\').replace('"', '\\"')
            
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_Config_CANBus")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> pivot(rowKey: ["_time", "config_type"], columnKey: ["_field"], valueColumn: "_value")
                |> group(columns: ["config_type"])
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            logger.debug(f"🔍 Executing CAN Bus config query for device_id: {device_id}")
            result = self.query_api.query(org=self.org, query=query)
            
            settings = {}
            can_messages = []
            data_mapping = []
            
            for table in result:
                for record in table.records:
                    config_type = record.values.get("config_type", "")
                    
                    if config_type == "settings":
                        settings = {
                            "enabled": record.values.get("enabled", False),
                            "communication_settings": {
                                "baud_rate": record.values.get("baud_rate", 125),
                                "identifier_length": record.values.get("identifier_length", "11-bit"),
                                "can_mode": record.values.get("can_mode", "Normal"),
                                "filter_mode": record.values.get("filter_mode", "None"),
                                "filter_id": record.values.get("filter_id", "0x123"),
                                "filter_mask": record.values.get("filter_mask", "0x7FF")
                            }
                        }
                    elif config_type == "can_message":
                        can_messages.append({
                            "index": record.values.get("index", 0),
                            "can_id": record.values.get("can_id", "0x123"),
                            "direction": record.values.get("direction", "TX"),
                            "period_ms": record.values.get("period_ms", 100),
                            "variable_name": record.values.get("variable_name", ""),
                            "data_length": record.values.get("data_length", 8)
                        })
                    elif config_type == "data_mapping":
                        data_mapping.append({
                            "index": record.values.get("index", 0),
                            "can_id": record.values.get("can_id", "0x123"),
                            "byte_position": record.values.get("byte_position", "Byte 0"),
                            "data_length": record.values.get("data_length", "1 Byte"),
                            "data_type": record.values.get("data_type", "int8"),
                            "endianness": record.values.get("endianness", "Big Endian"),
                            "variable_name": record.values.get("variable_name", ""),
                            "scale_factor": record.values.get("scale_factor", 1.0),
                            "offset": record.values.get("offset", 0.0)
                        })
            
            if not settings:
                return None
            
            settings["can_messages"] = can_messages
            settings["data_mapping"] = data_mapping
            return settings
            
        except Exception as e:
            logger.error(f"Error getting CAN Bus config for device_id '{device_id}': {e}")
            logger.exception("Full traceback:")
            return None
    
    def get_complete_config_from_tables(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete configuration by combining data from all individual tables
        This is used when a user saves one section - we need to rebuild the complete config
        """
        if not device_id or not device_id.strip():
            return None
        
        analog_config = self.get_analog_config(device_id)
        digital_config = self.get_digital_config(device_id)
        modbus_config = self.get_modbus_config(device_id)
        can_bus_config = self.get_can_bus_config(device_id)
        
        # Build complete config
        complete_config = {
            "device_id": device_id
        }
        
        if analog_config:
            complete_config["analog"] = analog_config
        if digital_config:
            complete_config["digital"] = digital_config
        if modbus_config:
            complete_config["rs485_modbus"] = modbus_config
        if can_bus_config:
            complete_config["can_bus"] = can_bus_config
        
        # Return None if no config found
        if len(complete_config) == 1:  # Only device_id
            return None
        
        return complete_config
    
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

