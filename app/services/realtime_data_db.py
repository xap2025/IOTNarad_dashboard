"""
Real-Time Data Database Service
Saves real-time device data from RTD/# MQTT topic to InfluxDB

IMPORTANT: Using Self-Hosted InfluxDB 2.x
- Supports Flux queries via Python client
- Local instance running via Docker
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


logger = logging.getLogger(__name__)


class RealtimeDataDBService:
    """
    Real-Time Data Database Service
    Saves real-time device data to InfluxDB
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
            logger.info(f"✅ Real-Time Data DB Service connected to InfluxDB: {self.url}")
            logger.info(f"   Database: Self-Hosted InfluxDB 2.x")
            logger.info(f"   Bucket: {self.bucket}, Org: {self.org}")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Failed to connect Real-Time Data DB Service to InfluxDB: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected
    
    def save_realtime_data(self, device_id: str, data_type: str, parameter_name: str, parameter_value: Any, timestamp: Optional[datetime] = None) -> bool:
        """
        Save real-time data point to InfluxDB
        
        Args:
            device_id: Device Serial Number (Sr_No)
            data_type: Type of data (Analog, Digital, Modbus, Canbus)
            parameter_name: Name of the parameter (e.g., "current", "voltage", "Conductivity")
            parameter_value: Value of the parameter (can be string, number, boolean)
            timestamp: Optional timestamp (defaults to current UTC time)
            
        Returns:
            Success status
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot save real-time data.")
            return False
        
        if not device_id or not device_id.strip():
            logger.warning("⚠️ Cannot save real-time data: device_id is empty")
            return False
        
        if not parameter_name or not parameter_name.strip():
            logger.warning("⚠️ Cannot save real-time data: parameter_name is empty")
            return False
        
        try:
            # Use provided timestamp or current UTC time
            if timestamp is None:
                timestamp = datetime.utcnow()
            
            # Convert value to appropriate type for InfluxDB
            # CRITICAL: InfluxDB does not allow field type conflicts in the same measurement
            # We need to convert all values to numeric types (int/float) to avoid conflicts
            # Boolean values will be converted to integers (true=1, false=0)
            field_value = parameter_value
            
            if isinstance(parameter_value, bool):
                # Convert boolean to integer to avoid type conflicts
                # true = 1, false = 0
                field_value = 1 if parameter_value else 0
                logger.info(f"   ✅ Converted boolean {parameter_value} to integer {field_value} for Digital data")
            elif isinstance(parameter_value, str):
                # Try to convert string to number if possible
                try:
                    # Try float first (handles decimals)
                    if '.' in parameter_value:
                        field_value = float(parameter_value)
                    else:
                        field_value = int(parameter_value)
                    logger.debug(f"   Converted string '{parameter_value}' to number {field_value}")
                except (ValueError, TypeError):
                    # If conversion fails, we have a problem - InfluxDB doesn't like mixed types
                    # Try to convert to a numeric representation
                    logger.warning(f"⚠️ Cannot convert string '{parameter_value}' to number. Using 0 as fallback.")
                    field_value = 0
            elif isinstance(parameter_value, (int, float)):
                # Already numeric - use as is
                field_value = parameter_value
            else:
                # For other types, try to convert to number
                logger.warning(f"⚠️ Unknown value type {type(parameter_value)}: {parameter_value}. Converting to 0.")
                field_value = 0
            
            # Create Point with measurement "Realtime_Data"
            # Tags: device_id, data_type, parameter_name (for fast filtering)
            # Field: value (the actual data value)
            point = Point("Realtime_Data") \
                .tag("device_id", device_id) \
                .tag("data_type", data_type) \
                .tag("parameter_name", parameter_name) \
                .field("value", field_value) \
                .time(timestamp, WritePrecision.NS)
            
            logger.info(f"💾 Writing to InfluxDB: device={device_id}, type={data_type}, param={parameter_name}, value={field_value} (type: {type(field_value)})")
            logger.debug(f"   Point tags: device_id={device_id}, data_type={data_type}, parameter_name={parameter_name}")
            logger.debug(f"   Point field: value={field_value}")
            logger.debug(f"   Timestamp: {timestamp}")
            
            # Write to InfluxDB
            try:
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
                logger.info(f"✅ Successfully wrote to InfluxDB: {device_id}/{data_type}/{parameter_name}")
                return True
            except Exception as write_error:
                error_msg = str(write_error)
                
                # Check for type conflict error (422 Unprocessable Entity)
                if "422" in error_msg or "type conflict" in error_msg.lower() or "field type conflict" in error_msg.lower():
                    logger.error(f"❌ TYPE CONFLICT: Cannot save {device_id}/{data_type}/{parameter_name} = {field_value}")
                    logger.error(f"   Reason: Database has existing records with different type (boolean vs integer)")
                    logger.error(f"   Solution: Delete old records from InfluxDB for this parameter, or use different measurement")
                    logger.error(f"   Query to fix: DELETE FROM Realtime_Data WHERE device_id='{device_id}' AND parameter_name='{parameter_name}'")
                    # Don't log full traceback for type conflicts - it's expected
                else:
                    logger.error(f"❌ InfluxDB write error: {write_error}")
                    logger.error(f"   Device: {device_id}, Type: {data_type}, Param: {parameter_name}, Value: {field_value}")
                    logger.exception("Full write error traceback:")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error saving real-time data: {e}")
            logger.error(f"   Device: {device_id}, Type: {data_type}, Param: {parameter_name}, Value: {parameter_value}")
            logger.exception("Full error traceback:")
            return False
    
    def get_realtime_data(self, device_id: str, parameter_name: str, start_time: datetime, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get real-time data for a specific device and parameter within a time range
        
        Args:
            device_id: Device Serial Number
            parameter_name: Name of the parameter
            start_time: Start time for query
            end_time: End time for query (defaults to current time)
            
        Returns:
            List of data points with timestamp and value
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot query real-time data.")
            return []
        
        if not device_id or not device_id.strip():
            return []
        
        if end_time is None:
            end_time = datetime.utcnow()
        
        try:
            # Escape device_id and parameter_name for Flux query
            escaped_device_id = device_id.replace('\\', '\\\\').replace('"', '\\"')
            escaped_param_name = parameter_name.replace('\\', '\\\\').replace('"', '\\"')
            
            # Convert datetime to RFC3339 format for Flux query (absolute time)
            # Flux requires RFC3339 format: "2006-01-02T15:04:05Z"
            # Using absolute time ensures we get data from the exact time range, even if device is off
            start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Flux query with absolute time range
            # CRITICAL: Simple query without type filtering to avoid TSM panic
            # If type conflict occurs, error will be caught and empty results returned
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: {start_time_str}, stop: {end_time_str})
                |> filter(fn: (r) => r._measurement == "Realtime_Data")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> filter(fn: (r) => r.parameter_name == "{escaped_param_name}")
                |> filter(fn: (r) => r._field == "value")
                |> sort(columns: ["_time"], desc: false)
            '''
            
            logger.info(f"🔍 Querying real-time data: device={device_id}, param='{parameter_name}', start={start_time_str}, end={end_time_str}")
            logger.debug(f"   Query: {query}")
            
            result = self.query_api.query(org=self.org, query=query)
            
            data_points = []
            for table in result:
                for record in table.records:
                    # Get value directly from _value field (no pivot needed)
                    value = record.get_value()
                    data_points.append({
                        "timestamp": record.get_time(),
                        "value": value
                    })
            
            logger.info(f"✅ Retrieved {len(data_points)} data points for {device_id}/{parameter_name}")
            if len(data_points) > 0:
                logger.debug(f"   Sample: timestamp={data_points[0].get('timestamp')}, value={data_points[0].get('value')}")
            return data_points
            
        except Exception as e:
            error_msg = str(e)
            # Check if this is the type conversion panic error
            if "IntegerValue" in error_msg and "BooleanValue" in error_msg:
                logger.warning(f"⚠️ Type conflict detected for {device_id}/{parameter_name}. "
                             f"This parameter has mixed Boolean/Integer values in database. "
                             f"Returning empty results. Consider cleaning up database records.")
                # Return empty list instead of crashing
                return []
            else:
                logger.error(f"❌ Error querying real-time data: {e}")
                logger.exception("Full error traceback:")
                return []
    
    def get_latest_value(self, device_id: str, parameter_name: str) -> Optional[Any]:
        """
        Get the latest value for a specific device and parameter
        
        Args:
            device_id: Device Serial Number
            parameter_name: Name of the parameter
            
        Returns:
            Latest value or None if not found
        """
        if not self.connected:
            return None
        
        try:
            # Escape for Flux query
            escaped_device_id = device_id.replace('\\', '\\\\').replace('"', '\\"')
            escaped_param_name = parameter_name.replace('\\', '\\\\').replace('"', '\\"')
            
            # Query latest value (last 7 days, get most recent)
            # CRITICAL: Simple query without type filtering to avoid TSM panic
            # If type conflict occurs, error will be caught and None returned
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -7d)
                |> filter(fn: (r) => r._measurement == "Realtime_Data")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> filter(fn: (r) => r.parameter_name == "{escaped_param_name}")
                |> filter(fn: (r) => r._field == "value")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            logger.info(f"🔍 Querying latest value: device={device_id}, param='{parameter_name}'")
            logger.debug(f"   Query: {query}")
            
            result = self.query_api.query(org=self.org, query=query)
            
            record_count = 0
            for table in result:
                for record in table.records:
                    record_count += 1
                    # Get value directly from _value field (no pivot needed)
                    value = record.get_value()
                    # Note: Values are stored as integers (boolean true=1, false=0)
                    # Return as-is, let the UI layer handle display conversion
                    logger.info(f"✅ Found latest value for {device_id}/{parameter_name}: {value} (type: {type(value)})")
                    return value
            
            logger.warning(f"⚠️ No latest value found for {device_id}/{parameter_name} (checked {record_count} records)")
            return None
            
        except Exception as e:
            error_msg = str(e)
            # Check if this is the type conversion panic error
            if "IntegerValue" in error_msg and "BooleanValue" in error_msg:
                logger.warning(f"⚠️ Type conflict detected for {device_id}/{parameter_name}. "
                             f"This parameter has mixed Boolean/Integer values in database. "
                             f"Returning None. Consider cleaning up database records.")
                # Return None instead of crashing
                return None
            else:
                logger.error(f"❌ Error getting latest value: {e}")
                logger.exception("Full error traceback:")
                return None

