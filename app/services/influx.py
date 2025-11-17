"""
InfluxDB Service
Handles time-series data storage and retrieval

IMPORTANT: Using Self-Hosted InfluxDB 2.x
- Supports Flux queries via Python client
- Local instance running via Docker
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class InfluxDBService:
    """
    InfluxDB Service for time-series data storage
    Uses Self-Hosted InfluxDB 2.x
    """
    
    def __init__(self):
        # Self-Hosted InfluxDB 2.x Configuration
        self.url = os.getenv('INFLUXDB_URL', 'http://influxdb:8086')
        self.token = os.getenv('INFLUXDB_TOKEN', '')
        self.org = os.getenv('INFLUXDB_ORG', 'iotnarad')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'iotnarad-bucket')
        
        # Initialize client
        try:
            self.client = InfluxDBClient(
                url=self.url,
                token=self.token,
                org=self.org,
                timeout=30000
            )
            
            # Get write and query APIs
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            
            self.connected = True
            logger.info(f"✅ Connected to InfluxDB: {self.url}")
            logger.info(f"📊 Using bucket: {self.bucket}")
            
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Failed to connect to InfluxDB: {e}")
            logger.warning("InfluxDB operations will be disabled")
    
    def write_device_data(self, device_id: str, data: Dict[str, Any]) -> bool:
        """
        Write device data to InfluxDB
        
        Args:
            device_id: Device identifier
            data: Data dictionary with sensor readings
            
        Returns:
            Success status
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot write data.")
            return False
        
        try:
            # Get timestamp from data or use current time
            timestamp = data.get('timestamp', datetime.utcnow())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Create point with device as measurement
            point = Point("device_data") \
                .tag("device_id", device_id) \
                .tag("device_type", data.get('device_type', 'esp32'))
            
            # Add fields from data
            for key, value in data.items():
                if key not in ['timestamp', 'device_id', 'device_type']:
                    # Skip non-numeric values for now
                    if isinstance(value, (int, float)):
                        point = point.field(key, float(value))
                    elif isinstance(value, bool):
                        point = point.field(key, value)
                    elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                        # Try to convert string numbers
                        try:
                            point = point.field(key, float(value))
                        except ValueError:
                            pass
            
            # Set timestamp
            point = point.time(timestamp, WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.debug(f"💾 Data written to InfluxDB for device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}")
            return False
    
    def get_device_data(self, device_id: str, time_range: str = '1h') -> List[Dict[str, Any]]:
        """
        Query device data from InfluxDB
        
        Args:
            device_id: Device identifier
            time_range: Time range (e.g., '1h', '6h', '24h', '7d')
            
        Returns:
            List of data points
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot query data.")
            return []
        
        try:
            # Flux query for Self-Hosted InfluxDB 2.x
            query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: -{time_range})
              |> filter(fn: (r) => r["_measurement"] == "device_data")
              |> filter(fn: (r) => r["device_id"] == "{device_id}")
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
            
            # Execute query
            tables = self.query_api.query(query, org=self.org)
            
            # Convert to list of dictionaries
            results = []
            for table in tables:
                for record in table.records:
                    data_point = {
                        'timestamp': record.get_time().isoformat(),
                        'device_id': record.values.get('device_id'),
                    }
                    
                    # Add all field values
                    for key, value in record.values.items():
                        if key not in ['_start', '_stop', '_time', '_measurement', 'device_id', 'device_type', 'result', 'table']:
                            data_point[key] = value
                    
                    results.append(data_point)
            
            logger.debug(f"📈 Retrieved {len(results)} data points for device: {device_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error querying InfluxDB: {e}")
            return []
    
    def get_latest_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get latest data point for a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            Latest data point or None
        """
        if not self.connected:
            return None
        
        try:
            query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: -1h)
              |> filter(fn: (r) => r["_measurement"] == "device_data")
              |> filter(fn: (r) => r["device_id"] == "{device_id}")
              |> last()
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
            
            tables = self.query_api.query(query, org=self.org)
            
            for table in tables:
                for record in table.records:
                    data_point = {
                        'timestamp': record.get_time().isoformat(),
                        'device_id': record.values.get('device_id'),
                    }
                    
                    for key, value in record.values.items():
                        if key not in ['_start', '_stop', '_time', '_measurement', 'device_id', 'device_type', 'result', 'table']:
                            data_point[key] = value
                    
                    return data_point
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest data: {e}")
            return None
    
    def get_device_list(self) -> List[str]:
        """
        Get list of all devices that have sent data
        
        Returns:
            List of device IDs
        """
        if not self.connected:
            return []
        
        try:
            query = f'''
            import "influxdata/influxdb/schema"
            
            schema.tagValues(
              bucket: "{self.bucket}",
              tag: "device_id",
              predicate: (r) => r._measurement == "device_data",
              start: -30d
            )
            '''
            
            tables = self.query_api.query(query, org=self.org)
            
            devices = []
            for table in tables:
                for record in table.records:
                    devices.append(record.get_value())
            
            logger.debug(f"Found {len(devices)} devices in InfluxDB")
            return devices
            
        except Exception as e:
            logger.error(f"Error getting device list: {e}")
            return []
    
    def delete_device_data(self, device_id: str, start_time: datetime, stop_time: datetime) -> bool:
        """
        Delete device data within a time range
        
        Args:
            device_id: Device identifier
            start_time: Start time
            stop_time: Stop time
            
        Returns:
            Success status
        """
        if not self.connected:
            return False
        
        try:
            delete_api = self.client.delete_api()
            
            predicate = f'_measurement="device_data" AND device_id="{device_id}"'
            
            delete_api.delete(
                start_time,
                stop_time,
                predicate,
                bucket=self.bucket,
                org=self.org
            )
            
            logger.info(f"🗑️ Deleted data for device {device_id} from {start_time} to {stop_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting data: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if InfluxDB client is connected"""
        return self.connected
    
    def close(self):
        """Close InfluxDB client connection"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logger.info("InfluxDB client closed")
        except Exception as e:
            logger.error(f"Error closing InfluxDB client: {e}")
