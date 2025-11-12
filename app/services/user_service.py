"""
User Service for managing user data in InfluxDB

IMPORTANT: Using InfluxDB Cloud Serverless (v3) - SQL queries required
Note: Python client's query_api uses Flux, but documentation should show SQL equivalents
"""
import os
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)

class UserService:
    """Service for managing user data in InfluxDB"""
    
    def __init__(self):
        self.url = os.getenv('INFLUXDB_URL', 'https://us-east-1-1.aws.cloud2.influxdata.com')
        self.token = os.getenv('INFLUXDB_TOKEN', 'T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA==')
        self.org = os.getenv('INFLUXDB_ORG', 'iot-narad-gcp')
        self.bucket = os.getenv('INFLUXDB_BUCKET', 'iot_data_gcp')
        
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org, timeout=30000)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()
            # IMPORTANT: InfluxDB Cloud Serverless (v3) uses SQL, not Flux
            # Note: Python client's query_api uses Flux, but we document SQL equivalents
            self.connected = True
            logger.info(f"✅ User Service connected to InfluxDB: {self.url}")
            logger.info(f"   Database: InfluxDB Cloud Serverless (v3) - SQL queries required")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Failed to connect User Service to InfluxDB: {e}")

    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user in InfluxDB"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot create user.")
            return False
        
        try:
            # Log incoming data for debugging
            logger.info(f"Creating user with data: {user_data}")
            
            # Validate required fields
            required_fields = ["Company_Name", "User_Id", "Email_Id", "Phone_No", "User_Type", "Password"]
            missing_fields = [field for field in required_fields if not user_data.get(field)]
            if missing_fields:
                logger.error(f"Missing required fields: {missing_fields}")
                return False
            
            # Create point with User_info measurement
            point = Point("User_info") \
                .tag("Company_Name", user_data.get("Company_Name", "")) \
                .tag("Email_Id", user_data.get("Email_Id", "")) \
                .tag("Phone_No", user_data.get("Phone_No", "")) \
                .tag("User_Id", user_data.get("User_Id", "")) \
                .tag("User_Type", user_data.get("User_Type", "")) \
                .tag("status", user_data.get("Status", "active")) \
                .field("Password", user_data.get("Password", "")) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.info(f"✅ User '{user_data.get('User_Id')}' successfully created in InfluxDB.")
            logger.info(f"   Measurement: User_info")
            logger.info(f"   Bucket: {self.bucket}")
            logger.info(f"   Org: {self.org}")
            return True
            
        except KeyError as e:
            logger.error(f"Missing required field in user_data: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating user in InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return False

    def get_user_by_id_and_phone(self, user_id: str, phone_no: str) -> Optional[Dict[str, Any]]:
        """Get user by User ID and Phone Number for password reset"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot get user.")
            return None
        
        try:
            # NOTE: SQL equivalent: SELECT * FROM "User_info" WHERE "User_Id" = '{user_id}' AND "Phone_No" = '{phone_no}' AND time > now() - interval '1 year' ORDER BY time DESC LIMIT 1
            # Using Flux here due to Python client limitation
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "User_info")
                |> filter(fn: (r) => r.User_Id == "{user_id}")
                |> filter(fn: (r) => r.Phone_No == "{phone_no}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            for table in result:
                for record in table.records:
                    return {
                        'User_Id': record.values.get('User_Id'),
                        'Company_Name': record.values.get('Company_Name'),
                        'Email_Id': record.values.get('Email_Id'),
                        'Phone_No': record.values.get('Phone_No'),
                        'User_Type': record.values.get('User_Type'),
                        'status': record.values.get('status'),
                        'Password': record.get_value()  # Get field value, not field name
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID and phone in InfluxDB: {e}")
            return None

    def get_all_user_entries(self, user_id: str) -> list:
        """Get all entries for a user ID (for password reset)"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot get user entries.")
            return []
        
        try:
            # Flux query with 1 year time range
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "User_info")
                |> filter(fn: (r) => r.User_Id == "{user_id}")
                |> sort(columns: ["_time"], desc: true)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            entries = []
            
            for table in result:
                for record in table.records:
                    entries.append({
                        'User_Id': record.values.get('User_Id'),
                        'Company_Name': record.values.get('Company_Name'),
                        'Email_Id': record.values.get('Email_Id'),
                        'Phone_No': record.values.get('Phone_No'),
                        'User_Type': record.values.get('User_Type'),
                        'status': record.values.get('status'),
                        'Password': record.get_value(),  # Get field value, not field name
                        'timestamp': record.get_time()
                    })
            
            return entries
            
        except Exception as e:
            logger.error(f"Error getting all user entries in InfluxDB: {e}")
            return []

    def delete_all_user_entries(self, user_id: str) -> bool:
        """Delete all entries for a user ID"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot delete user entries.")
            return False
        
        try:
            # InfluxDB delete API requires delete predicate
            from influxdb_client import DeleteApi
            
            delete_api = DeleteApi(self.client)
            
            # Delete all entries for this user ID in the last 365 days
            from datetime import timedelta
            start_time = datetime.utcnow() - timedelta(days=365)
            stop_time = datetime.utcnow()
            
            # Create delete predicate
            predicate = f'_measurement="User_info" AND User_Id="{user_id}"'
            
            delete_api.delete(
                start=start_time,
                stop=stop_time,
                predicate=predicate,
                bucket=self.bucket,
                org=self.org
            )
            
            logger.info(f"✅ All entries deleted for user '{user_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user entries in InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return False

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change password for logged-in user:
        1. Verify current password
        2. Get all old entries for user_id
        3. Delete all old entries
        4. Save all entries again with new password
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot change password.")
            return False
        
        # Validate input
        if not user_id or not current_password or not new_password:
            logger.warning("Missing required fields for password change")
            return False
        
        # Verify current password first
        user = self.authenticate_user(user_id, current_password)
        if not user:
            logger.warning(f"Current password verification failed for user '{user_id}'")
            return False
        
        try:
            # Get all entries for this user
            all_entries = self.get_all_user_entries(user_id)
            if not all_entries:
                logger.warning(f"No entries found for user '{user_id}'")
                return False
            
            logger.info(f"Found {len(all_entries)} entries for user '{user_id}'")
            
            # Delete all old entries
            delete_success = self.delete_all_user_entries(user_id)
            if not delete_success:
                logger.error(f"Failed to delete old entries for user '{user_id}'")
                return False
            
            # Save all entries again with new password
            # Use the most recent entry's data but with new password
            latest_entry = all_entries[0]  # Get first entry (most recent)
            
            point = Point("User_info") \
                .tag("Company_Name", latest_entry.get("Company_Name", "")) \
                .tag("Email_Id", latest_entry.get("Email_Id", "")) \
                .tag("Phone_No", latest_entry.get("Phone_No", "")) \
                .tag("User_Id", latest_entry.get("User_Id", "")) \
                .tag("User_Type", latest_entry.get("User_Type", "")) \
                .tag("status", latest_entry.get("status", "active")) \
                .field("Password", new_password) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.info(f"✅ Password changed successfully for user '{user_id}'")
            logger.info(f"   New password saved in database")
            
            return True
            
        except Exception as e:
            logger.error(f"Error changing password in InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return False

    def reset_password(self, user_id: str, phone_no: str, new_password: str) -> bool:
        """Reset password for a user:
        1. Get all old entries for user_id
        2. Delete all old entries
        3. Save all entries again with new password
        """
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot reset password.")
            return False
        
        try:
            # Step 1: Verify user exists with matching phone number
            user = self.get_user_by_id_and_phone(user_id, phone_no)
            if not user:
                logger.warning(f"User '{user_id}' with phone '{phone_no}' not found")
                return False
            
            # Step 2: Get all entries for this user
            all_entries = self.get_all_user_entries(user_id)
            if not all_entries:
                logger.warning(f"No entries found for user '{user_id}'")
                return False
            
            logger.info(f"Found {len(all_entries)} entries for user '{user_id}'")
            
            # Step 3: Delete all old entries
            delete_success = self.delete_all_user_entries(user_id)
            if not delete_success:
                logger.error(f"Failed to delete old entries for user '{user_id}'")
                return False
            
            # Step 4: Save all entries again with new password
            # Use the most recent entry's data but with new password
            latest_entry = all_entries[0]  # Get first entry (most recent)
            
            point = Point("User_info") \
                .tag("Company_Name", latest_entry.get("Company_Name", "")) \
                .tag("Email_Id", latest_entry.get("Email_Id", "")) \
                .tag("Phone_No", latest_entry.get("Phone_No", "")) \
                .tag("User_Id", latest_entry.get("User_Id", "")) \
                .tag("User_Type", latest_entry.get("User_Type", "")) \
                .tag("status", latest_entry.get("status", "active")) \
                .field("Password", new_password) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            logger.info(f"✅ Password reset successful for user '{user_id}'")
            logger.info(f"   New password saved in database")
            logger.info(f"   Email will be sent to: {latest_entry.get('Email_Id')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting password in InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return False

    def _execute_flux_query(self, flux_query: str) -> List[Dict[str, Any]]:
        """Execute Flux query and return records as list of dictionaries
        Note: In Flux, each record represents a field-value pair, so we need to group by time
        """
        try:
            result = self.query_api.query(org=self.org, query=flux_query)
            
            # Group records by time to combine all fields for the same timestamp
            records_by_time = {}
            
            for table in result:
                for record in table.records:
                    time_key = str(record.get_time())
                    
                    if time_key not in records_by_time:
                        records_by_time[time_key] = {
                            'User_Id': record.values.get('User_Id'),
                            'Company_Name': record.values.get('Company_Name'),
                            'Email_Id': record.values.get('Email_Id'),
                            'Phone_No': record.values.get('Phone_No'),
                            'User_Type': record.values.get('User_Type'),
                            'status': record.values.get('status'),
                            'Password': None,
                            'time': record.get_time()
                        }
                    
                    # Add field value if it's Password
                    if record.get_field() == 'Password':
                        records_by_time[time_key]['Password'] = record.get_value()
            
            # Convert to list sorted by time (descending)
            records = list(records_by_time.values())
            records.sort(key=lambda x: x['time'], reverse=True)
            
            return records
            
        except Exception as e:
            logger.error(f"Error executing Flux query: {e}")
            logger.exception("Full error traceback:")
            return []

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Check if user ID already exists - Using Flux query with 1 year range"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot check user.")
            return None
        
        try:
            # Flux query with 1 year time range (as suggested for InfluxDB Cloud Serverless)
            flux_query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "User_info")
                |> filter(fn: (r) => r.User_Id == "{user_id}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            logger.info(f"Executing Flux query for user: {user_id}")
            records = self._execute_flux_query(flux_query)
            
            if records and len(records) > 0:
                return records[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking user in InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return None

    def authenticate_user(self, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with user_id and password - checks latest entry"""
        # STRICT VALIDATION: Return None immediately if not connected
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot authenticate user.")
            return None
        
        # STRICT VALIDATION: Check for None or empty strings
        if user_id is None or password is None:
            logger.warning("Authentication failed: User ID or Password is None")
            return None
        
        # STRICT VALIDATION: Check for empty strings
        if not user_id or not password:
            logger.warning("Authentication failed: User ID or Password is empty")
            return None
        
        # Trim whitespace
        user_id = user_id.strip()
        password = password.strip()
        
        # STRICT VALIDATION: Check again after trimming
        if not user_id or not password:
            logger.warning("Authentication failed: User ID or Password is empty after trimming")
            return None
        
        try:
            # Flux query with 1 year time range - Get latest entry
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "User_info")
                |> filter(fn: (r) => r.User_Id == "{user_id}")
                |> sort(columns: ["_time"], desc: true)
                |> limit(n: 1)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            # Check if any records found
            found_record = False
            for table in result:
                for record in table.records:
                    found_record = True
                    # Get field value, not field name
                    stored_password = record.get_value()
                    
                    # Debug: Log what we're comparing
                    logger.info(f"🔍 Authentication attempt for User ID: {user_id}")
                    logger.info(f"   Field name: {record.get_field()}")
                    logger.info(f"   Stored password value: {repr(stored_password)}")
                    logger.info(f"   Input password value: {repr(password)}")
                    
                    # Compare passwords strictly - handle string conversion
                    stored_pwd_str = str(stored_password) if stored_password is not None else ""
                    input_pwd_str = str(password) if password else ""
                    
                    if stored_pwd_str == input_pwd_str and stored_pwd_str:
                        logger.info(f"✅ Authentication successful for User ID: {user_id}")
                        return {
                            'User_Id': record.values.get('User_Id'),
                            'Company_Name': record.values.get('Company_Name'),
                            'Email_Id': record.values.get('Email_Id'),
                            'Phone_No': record.values.get('Phone_No'),
                            'User_Type': record.values.get('User_Type'),
                            'status': record.values.get('status')
                        }
                    else:
                        # Debug logging
                        logger.warning(f"❌ Password mismatch for User ID: {user_id}")
                        logger.debug(f"   Stored password length: {len(stored_pwd_str)}")
                        logger.debug(f"   Input password length: {len(input_pwd_str)}")
                        logger.debug(f"   Passwords match: {stored_pwd_str == input_pwd_str}")
                        return None
            
            # No record found - STRICT: Always return None
            if not found_record:
                logger.warning(f"❌ User ID '{user_id}' not found in database")
                return None
            
            # If we reach here, record was found but password didn't match
            # (already returned None above)
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user in InfluxDB: {e}")
            logger.exception("Full error traceback:")
            return None

    def get_all_users(self) -> list:
        """Get all users from InfluxDB"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot get users.")
            return []
        
        try:
            # Flux query with 1 year time range
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -365d)
                |> filter(fn: (r) => r._measurement == "User_info")
                |> sort(columns: ["_time"], desc: true)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            users = []
            
            for table in result:
                for record in table.records:
                    users.append({
                        'User_Id': record.values.get('User_Id'),
                        'Company_Name': record.values.get('Company_Name'),
                        'Email_Id': record.values.get('Email_Id'),
                        'Phone_No': record.values.get('Phone_No'),
                        'User_Type': record.values.get('User_Type'),
                        'status': record.values.get('status'),
                        'created_at': record.get_time()
                    })
            
            return users
            
        except Exception as e:
            logger.error(f"Error getting users from InfluxDB: {e}")
            return []

    def delete_user(self, user_id: str) -> bool:
        """Delete a user from InfluxDB"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot delete user.")
            return False
        
        try:
            # Note: InfluxDB doesn't support direct deletion by tags
            # This would require a more complex approach or using delete API
            logger.warning(f"Delete user functionality not implemented for InfluxDB. User ID: {user_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting user from InfluxDB: {e}")
            return False

    def close(self):
        """Close InfluxDB connection"""
        if self.connected:
            self.client.close()
            self.connected = False
            logger.info("User Service connection closed.")