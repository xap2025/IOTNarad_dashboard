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
            # InfluxDB supports: float, int, str, bool
            field_value = parameter_value
            if isinstance(parameter_value, str):
                # Try to convert string to number if possible
                try:
                    # Try float first (handles decimals)
                    if '.' in parameter_value:
                        field_value = float(parameter_value)
                    else:
                        field_value = int(parameter_value)
                except (ValueError, TypeError):
                    # Keep as string if conversion fails
                    field_value = str(parameter_value)
            elif isinstance(parameter_value, bool):
                # InfluxDB supports boolean
                field_value = parameter_value
            elif isinstance(parameter_value, (int, float)):
                field_value = parameter_value
            else:
                # Convert to string for other types
                field_value = str(parameter_value)
            
            # Create Point with measurement "Realtime_Data"
            # Tags: device_id, data_type, parameter_name (for fast filtering)
            # Field: value (the actual data value)
            point = Point("Realtime_Data") \
                .tag("device_id", device_id) \
                .tag("data_type", data_type) \
                .tag("parameter_name", parameter_name) \
                .field("value", field_value) \
                .time(timestamp, WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.debug(f"💾 Saved real-time data: device={device_id}, type={data_type}, param={parameter_name}, value={field_value}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving real-time data: {e}")
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
            
            # Calculate time range
            time_diff = end_time - start_time
            if time_diff.days > 0:
                range_start = f"-{time_diff.days + 1}d"
            elif time_diff.seconds >= 3600:
                range_start = f"-{int(time_diff.seconds / 3600) + 1}h"
            else:
                range_start = f"-{int(time_diff.seconds / 60) + 1}m"
            
            # Flux query to get data points
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: {range_start})
                |> filter(fn: (r) => r._measurement == "Realtime_Data")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> filter(fn: (r) => r.parameter_name == "{escaped_param_name}")
                |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> sort(columns: ["_time"], desc: false)
            '''
            
            logger.debug(f"🔍 Querying real-time data: device={device_id}, param={parameter_name}, range={range_start}")
            
            result = self.query_api.query(org=self.org, query=query)
            
            data_points = []
            for table in result:
                for record in table.records:
                    data_points.append({
                        "timestamp": record.get_time(),
                        "value": record.values.get("value")
                    })
            
            logger.debug(f"✅ Retrieved {len(data_points)} data points for {device_id}/{parameter_name}")
            return data_points
            
        except Exception as e:
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
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -7d)
                |> filter(fn: (r) => r._measurement == "Realtime_Data")
                |> filter(fn: (r) => r.device_id == "{escaped_device_id}")
                |> filter(fn: (r) => r.parameter_name == "{escaped_param_name}")
                |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            for table in result:
                for record in table.records:
                    return record.values.get("value")
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting latest value: {e}")
            return None

