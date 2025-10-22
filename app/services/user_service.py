import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
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
            self.connected = True
            logger.info(f"✅ User Service connected to InfluxDB: {self.url}")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Failed to connect User Service to InfluxDB: {e}")

    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user in InfluxDB"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot create user.")
            return False
        
        try:
            # Create point with User_info measurement
            point = Point("User_info") \
                .tag("Company_Name", user_data["Company_Name"]) \
                .tag("Email_Id", user_data["Email_Id"]) \
                .tag("Phone_No", user_data["Phone_No"]) \
                .tag("User_Id", user_data["User_Id"]) \
                .tag("User_Type", user_data["User_Type"]) \
                .tag("status", user_data.get("status", "active")) \
                .field("Password", user_data["Password"]) \
                .time(datetime.utcnow(), WritePrecision.NS)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            logger.info(f"User '{user_data['User_Id']}' created in InfluxDB.")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user in InfluxDB: {e}")
            return False

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Check if user ID already exists"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot check user.")
            return None
        
        try:
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -30d)
                |> filter(fn: (r) => r._measurement == "User_info")
                |> filter(fn: (r) => r.User_Id == "{user_id}")
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
                        'Password': record.get_field()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking user in InfluxDB: {e}")
            return None

    def authenticate_user(self, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with user_id and password"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot authenticate user.")
            return None
        
        try:
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -30d)
                |> filter(fn: (r) => r._measurement == "User_info")
                |> filter(fn: (r) => r.User_Id == "{user_id}")
                |> limit(n: 1)
            '''
            
            result = self.query_api.query(org=self.org, query=query)
            
            for table in result:
                for record in table.records:
                    stored_password = record.get_field()
                    if stored_password == password:
                        return {
                            'User_Id': record.values.get('User_Id'),
                            'Company_Name': record.values.get('Company_Name'),
                            'Email_Id': record.values.get('Email_Id'),
                            'Phone_No': record.values.get('Phone_No'),
                            'User_Type': record.values.get('User_Type'),
                            'status': record.values.get('status')
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user in InfluxDB: {e}")
            return None

    def get_all_users(self) -> list:
        """Get all users from InfluxDB"""
        if not self.connected:
            logger.warning("InfluxDB not connected. Cannot get users.")
            return []
        
        try:
            query = f'''
                from(bucket: "{self.bucket}")
                |> range(start: -30d)
                |> filter(fn: (r) => r._measurement == "User_info")
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