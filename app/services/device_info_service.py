"""
Device Info Service
Handles device registration and information storage in InfluxDB

IMPORTANT: Using Self-Hosted InfluxDB 2.x
- Supports Flux queries via Python client
- Local instance running via Docker
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class DeviceInfoService:
    """
    Device Info Service
    Manages device registration and information in InfluxDB
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
            logger.info(f"✅ Device Info Service connected to InfluxDB: {self.url}")
            logger.info(f"   Database: Self-Hosted InfluxDB 2.x")
            logger.info(f"   Bucket: {self.bucket}, Org: {self.org}")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Failed to connect Device Info Service to InfluxDB: {e}")
    
    def check_serial_number_exists(self, serial_number: str) -> bool:
        """
        Check if serial number already exists in database
        
        Args:
            serial_number: Device serial number
            
        Returns:
            True if exists, False otherwise
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot check serial number.")
            return False
        
        try:
            # Flux query for Self-Hosted InfluxDB 2.x
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_info")
                |> filter(fn: (r) => r.Sr_No == "{serial_number}")
                |> limit(n: 1)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            # Check if any records found
            for table in result:
                for record in table.records:
                    logger.info(f"✅ Serial number '{serial_number}' already exists in database")
                    return True
            
            logger.info(f"ℹ️ Serial number '{serial_number}' not found in database (new device)")
            return False
            
        except Exception as e:
            logger.error(f"Error checking serial number: {e}")
            return False
    
    def register_device(self, serial_number: str, owner: Optional[str] = None) -> bool:
        """
        Register a new device in the database
        
        Args:
            serial_number: Device serial number
            owner: Optional owner/user ID. Defaults to 'admin' when not provided.
            
        Returns:
            True if registered successfully, False otherwise
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot register device.")
            return False
        
        try:
            # Validate serial number
            if not serial_number or serial_number.upper() == "ACK" or len(serial_number) < 3:
                logger.warning(f"⚠️ Invalid serial number rejected: '{serial_number}'")
                return False
            
            # Check if already exists (first check)
            if self.check_serial_number_exists(serial_number):
                logger.info(f"ℹ️ Device with serial number '{serial_number}' already registered. This is expected for duplicate messages.")
                return True  # Return True because device is already registered (success case)
            
            # Get current date
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
            timestamp = datetime.utcnow()
            # Owner defaults to "admin" if not provided
            owner_value = owner.strip() if owner and isinstance(owner, str) else "admin"
            
            # Create point for Device_info measurement
            # Owner is a TAG (not field) for efficient filtering by user
            point = Point("Device_info") \
                .tag("Sr_No", serial_number) \
                .tag("Owner", owner_value) \
                .field("Date_Of_Register", current_date) \
                .field("Device_Name", "Unnamed") \
                .time(timestamp, WritePrecision.NS)
            
            # CRITICAL: Double-check right before write to prevent race condition
            # Even with in-memory dedup, multiple threads might reach here
            # This is the final defense against duplicates
            if self.check_serial_number_exists(serial_number):
                logger.info(f"ℹ️ Device with serial number '{serial_number}' was registered by another process. This is expected for concurrent messages.")
                return True  # Return True because device is already registered (success case)
            
            # Write to InfluxDB
            try:
                logger.info(f"📝 Writing device to InfluxDB: {serial_number}")
                logger.info(f"   Bucket: {self.bucket}, Org: {self.org}")
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
                logger.info(f"✅ Write operation completed for: {serial_number}")
                
                # Final verification: Check again after write to ensure it was written
                # Small delay to allow InfluxDB to commit
                import time
                time.sleep(0.05)  # 50ms delay for InfluxDB to commit
                
                # Verify write succeeded
                if not self.check_serial_number_exists(serial_number):
                    logger.warning(f"⚠️ Write completed but device '{serial_number}' not found in database. This may be a timing issue.")
            except Exception as write_error:
                logger.error(f"❌ Failed to write device to InfluxDB: {write_error}")
                logger.error(f"   Bucket: {self.bucket}, Org: {self.org}")
                raise
            
            logger.info(f"✅ Device registered successfully!")
            logger.info(f"   Serial Number: {serial_number}")
            logger.info(f"   Measurement: Device_info")
            logger.info(f"   Owner: {owner_value}")
            logger.info(f"   Date of Register: {current_date}")
            logger.info(f"   Device Name: Unnamed")
            return True
            
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            logger.exception("Full error traceback:")
            return False
    
    def get_device_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """
        Get device information by serial number
        
        Args:
            serial_number: Device serial number
            
        Returns:
            Device information dictionary or None
        """
        if not self.connected:
            return None
        
        try:
            # Flux query for Self-Hosted InfluxDB 2.x
            # Owner is a TAG, so it's accessible directly (no pivot needed for tags)
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "Device_info")
                |> filter(fn: (r) => r.Sr_No == "{serial_number}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            for table in result:
                for record in table.records:
                    # Owner is a TAG, accessible from record.values
                    # After pivot, fields are also in record.values
                    return {
                        'Sr_No': record.values.get('Sr_No'),
                        'Owner': record.values.get('Owner', 'Unassigned'),  # TAG - accessible before/after pivot
                        'Date_Of_Register': record.values.get('Date_Of_Register', ''),
                        'Device_Name': record.values.get('Device_Name', 'Unnamed'),
                        'timestamp': record.get_time().isoformat()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return None
    
    def list_all_devices(self) -> list:
        """
        List all registered devices
        
        Returns:
            List of serial numbers
        """
        if not self.connected:
            return []
        
        try:
            # Flux query for Self-Hosted InfluxDB 2.x
            query = f'''
                import "influxdata/influxdb/schema"
                
                schema.tagValues(
                  bucket: "{self.bucket}",
                  tag: "Sr_No",
                  predicate: (r) => r._measurement == "Device_info",
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
    
    def get_all_devices_info(self, owner_filter: Optional[str] = None, is_admin: bool = False) -> List[Dict[str, Any]]:
        """
        Get all devices with their information in a single optimized query
        
        Args:
            owner_filter: Optional owner name to filter devices. If None, returns all devices.
                         If provided, only returns devices where Owner == owner_filter.
            is_admin: If True, ignore owner_filter and return all devices (admin sees all)
        
        Returns:
            List of device info dictionaries with Sr_No, Device_Name, Owner, etc.
        """
        if not self.connected:
            return []
        
        try:
            # Build query with optional owner filter
            # Owner is a TAG, so we can filter it directly BEFORE pivot (more efficient)
            # CRITICAL FIX: Group FIRST, then sort, then limit, then pivot, then keep
            # This matches the working query structure from InfluxDB UI
            if is_admin or not owner_filter:
                # Admin or no filter - get all devices
                query = f'''
                    from(bucket: "{self.bucket}")
                    |> range(start: -365d)
                    |> filter(fn: (r) => r._measurement == "Device_info")
                    |> group(columns: ["Sr_No", "Owner"])
                    |> sort(columns: ["_time"], desc: true)
                    |> limit(n: 1)
                    |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                    |> keep(columns: ["_time", "Sr_No", "Owner", "Device_Name", "Date_Of_Register"])
                '''
            else:
                # Filter by owner - Owner is a TAG, so filter BEFORE pivot (more efficient)
                query = f'''
                    from(bucket: "{self.bucket}")
                    |> range(start: -365d)
                    |> filter(fn: (r) => r._measurement == "Device_info")
                    |> filter(fn: (r) => r.Owner == "{owner_filter}")
                    |> group(columns: ["Sr_No", "Owner"])
                    |> sort(columns: ["_time"], desc: true)
                    |> limit(n: 1)
                    |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
                    |> keep(columns: ["_time", "Sr_No", "Owner", "Device_Name", "Date_Of_Register"])
                '''
            
            logger.info(f"🔍 Executing Flux query for devices info (owner_filter: '{owner_filter}', is_admin: {is_admin})")
            logger.info(f"   Bucket: {self.bucket}, Org: {self.org}")
            logger.debug(f"   Query:\n{query}")
            
            result = self.query_api.query(org=self.org, query=query)
            logger.info(f"   Query executed successfully, processing results...")
            
            # Process results
            devices = []
            seen_serials = set()
            table_count = 0
            record_count = 0
            
            for table in result:
                table_count += 1
                logger.debug(f"   Processing table {table_count}, columns: {table.columns}")
                for record in table.records:
                    record_count += 1
                    logger.debug(f"   Record {record_count} - values: {record.values if hasattr(record, 'values') else 'N/A'}")
                    
                    # Sr_No is a tag (in group key), so get it from record.values
                    sr_no = None
                    if hasattr(record, 'values') and record.values:
                        sr_no = record.values.get('Sr_No')
                    if not sr_no:
                        # Also try getting from record directly (for tags in group key)
                        sr_no = getattr(record, 'Sr_No', None)
                    if not sr_no:
                        logger.warning(f"   ⚠️ Could not extract Sr_No from record {record_count}")
                        continue
                    
                    if sr_no in seen_serials:
                        logger.debug(f"   Skipping duplicate device: {sr_no}")
                        continue
                    
                    seen_serials.add(sr_no)
                    
                    # Owner is a TAG (in group key), accessible from record.values
                    owner = None
                    if hasattr(record, 'values') and record.values:
                        owner = record.values.get('Owner')
                    if not owner:
                        # Also try getting from record directly (for tags in group key)
                        owner = getattr(record, 'Owner', None)
                    if not owner:
                        owner = 'Unassigned'
                        logger.warning(f"   ⚠️ Could not extract Owner from record {record_count}, defaulting to 'Unassigned'")
                    
                    logger.debug(f"   Device found: Sr_No={sr_no}, Owner={owner}")
                    
                    # Double-check owner filter (in case filter didn't work in Flux)
                    # This shouldn't be needed if Owner is a tag, but keeping as safety check
                    if not is_admin and owner_filter and owner != owner_filter:
                        logger.debug(f"   Skipping device {sr_no} - Owner '{owner}' != filter '{owner_filter}'")
                        continue
                    
                    device_name = record.values.get('Device_Name', 'Unnamed') if hasattr(record, 'values') and record.values else 'Unnamed'
                    date_of_register = record.values.get('Date_Of_Register', '') if hasattr(record, 'values') and record.values else ''
                    
                    devices.append({
                        'Sr_No': sr_no,
                        'Device_Name': device_name,
                        'Owner': owner,
                        'Date_Of_Register': date_of_register,
                        'timestamp': record.get_time().isoformat() if record.get_time() else datetime.utcnow().isoformat()
                    })
            
            logger.info(f"   Processed {table_count} tables, {record_count} records, {len(devices)} unique devices")
            
            logger.info(f"✅ Found {len(devices)} devices in database (owner_filter: {owner_filter}, is_admin: {is_admin})")
            
            # Sort by Serial Number
            return sorted(devices, key=lambda x: x['Sr_No'])
            
        except Exception as e:
            logger.error(f"Error getting all devices info: {e}")
            logger.exception("Full error traceback:")
            # Fallback: use individual queries if optimized query fails
            try:
                serial_numbers = self.list_all_devices()
                devices = []
                for sr_no in serial_numbers:
                    device_info = self.get_device_info(sr_no)
                    if device_info:
                        # Apply owner filter in fallback too
                        if not is_admin and owner_filter:
                            if device_info.get('Owner') != owner_filter:
                                continue
                        devices.append(device_info)
                return sorted(devices, key=lambda x: x.get('Sr_No', ''))
            except Exception as fallback_error:
                logger.error(f"Fallback query also failed: {fallback_error}")
                return []
    
    def delete_device_records(self, serial_number: str) -> bool:
        """
        Delete all records for a device by serial number
        
        Args:
            serial_number: Device serial number
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot delete device records.")
            return False
        
        try:
            from influxdb_client import DeleteApi
            from datetime import timedelta
            
            delete_api = DeleteApi(self.client)
            
            # Delete all entries for this device in the last 365 days
            start_time = datetime.utcnow() - timedelta(days=365)
            stop_time = datetime.utcnow()
            
            # Create delete predicate - Sr_No is a TAG
            predicate = f'_measurement="Device_info" AND Sr_No="{serial_number}"'
            
            delete_api.delete(
                start=start_time,
                stop=stop_time,
                predicate=predicate,
                bucket=self.bucket,
                org=self.org
            )
            
            logger.info(f"✅ All records deleted for device '{serial_number}'")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting device records: {e}")
            logger.exception("Full error traceback:")
            return False
    
    def assign_device_to_user(self, serial_number: str, new_owner: str, device_name: str) -> bool:
        """
        Assign device to a user by deleting old records and creating new one
        
        IMPORTANT: This method deletes ALL old records for the device first,
        then creates a new record with updated Owner, Device_Name, and Date_Of_Register.
        Date_Of_Register is set to current date when device is assigned to user.
        This prevents duplicate entries in the database.
        
        Args:
            serial_number: Device serial number
            new_owner: New owner/user ID
            device_name: Device name
            
        Returns:
            True if assigned successfully, False otherwise
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot assign device.")
            return False
        
        try:
            # Step 1: Verify device exists before assignment
            device_info = self.get_device_info(serial_number)
            if not device_info:
                logger.warning(f"Device with serial number '{serial_number}' not found")
                return False
            
            # Step 2: Delete all old records for this device
            logger.info(f"🗑️ Deleting old records for device '{serial_number}'...")
            delete_success = self.delete_device_records(serial_number)
            if not delete_success:
                logger.error(f"Failed to delete old records for device '{serial_number}'")
                return False
            
            # Step 3: Create new record with updated information
            # Date_Of_Register = current date (when device is assigned to user)
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
            timestamp = datetime.utcnow()
            
            # Create new point with updated Owner, Device_Name, and Date_Of_Register
            point = Point("Device_info") \
                .tag("Sr_No", serial_number) \
                .tag("Owner", new_owner) \
                .field("Date_Of_Register", current_date) \
                .field("Device_Name", device_name) \
                .time(timestamp, WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.info(f"✅ Device assigned successfully!")
            logger.info(f"   Serial Number: {serial_number}")
            logger.info(f"   New Owner: {new_owner}")
            logger.info(f"   Device Name: {device_name}")
            logger.info(f"   Date of Register (updated to assignment date): {current_date}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning device: {e}")
            logger.exception("Full error traceback:")
            return False
    
    def update_device_info(self, serial_number: str, owner: str = None, device_name: str = None) -> bool:
        """
        Update device information
        
        Args:
            serial_number: Device serial number
            owner: Owner name (optional)
            device_name: Device name (optional)
            
        Returns:
            True if updated successfully
        """
        if not self.connected:
            return False
        
        try:
            # Get existing device info
            device_info = self.get_device_info(serial_number)
            if not device_info:
                logger.warning(f"Device with serial number '{serial_number}' not found")
                return False
            
            # Use existing values if not provided
            new_owner = owner if owner is not None else device_info.get('Owner', 'Unassigned')
            new_device_name = device_name if device_name is not None else device_info.get('Device_Name', 'Unnamed')
            date_of_register = device_info.get('Date_Of_Register', datetime.utcnow().strftime("%Y-%m-%d"))
            
            # Create updated point
            # Owner is a TAG (not field) for efficient filtering by user
            point = Point("Device_info") \
                .tag("Sr_No", serial_number) \
                .tag("Owner", new_owner) \
                .field("Date_Of_Register", date_of_register) \
                .field("Device_Name", new_device_name) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.info(f"✅ Device info updated for serial number: {serial_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating device info: {e}")
            return False
    
    def user_has_assigned_devices(self, user_id: str) -> bool:
        """
        Check if a user has any devices assigned to them
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user has assigned devices, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            # Get all devices for this user
            devices = self.get_all_devices_info(owner_filter=user_id, is_admin=False)
            
            if devices and len(devices) > 0:
                logger.info(f"✅ User '{user_id}' has {len(devices)} device(s) assigned")
                return True
            
            logger.info(f"ℹ️ User '{user_id}' has no devices assigned")
            return False
            
        except Exception as e:
            logger.error(f"Error checking assigned devices for user '{user_id}': {e}")
            # Return True on error to be safe (prevent deletion if check fails)
            return True
    
    def is_connected(self) -> bool:
        """Check if InfluxDB client is connected"""
        return self.connected
    
    def close(self):
        """Close InfluxDB client connection"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logger.info("Device Info Service client closed")
        except Exception as e:
            logger.error(f"Error closing Device Info Service client: {e}")

