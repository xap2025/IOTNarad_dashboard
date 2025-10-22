"""
MQTT Client Service
Handles MQTT communication with IoT devices
"""
import os
import json
import logging
import paho.mqtt.client as mqtt
from threading import Thread
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)


class MQTTClientService:
    """
    MQTT Client Service for IoT device communication
    Handles pub/sub operations with Mosquitto broker
    """
    
    def __init__(self):
        self.broker = os.getenv('MQTT_BROKER', 'mqtt')
        self.port = int(os.getenv('MQTT_PORT', 1883))
        self.client_id = f"iotnarad-dashboard-{os.getpid()}"
        
        # MQTT Topics
        self.topic_device_data = os.getenv('MQTT_TOPIC_DEVICE_DATA', 'iotnarad/devices/+/data')
        self.topic_device_config = os.getenv('MQTT_TOPIC_DEVICE_CONFIG', 'iotnarad/devices/+/config')
        self.topic_device_status = os.getenv('MQTT_TOPIC_DEVICE_STATUS', 'iotnarad/devices/+/status')
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=self.client_id, clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Callbacks
        self.data_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        self.connected = False
        logger.info(f"MQTT Client initialized: {self.client_id}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connected to MQTT Broker: {self.broker}:{self.port}")
            
            # Subscribe to topics
            self.client.subscribe(self.topic_device_data)
            self.client.subscribe(self.topic_device_status)
            logger.info(f"📡 Subscribed to: {self.topic_device_data}")
            logger.info(f"📡 Subscribed to: {self.topic_device_status}")
        else:
            self.connected = False
            logger.error(f"❌ Failed to connect to MQTT Broker. Return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠️ Unexpected disconnection from MQTT Broker. Code: {rc}")
        else:
            logger.info("Disconnected from MQTT Broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"📨 Message received on {topic}: {payload[:100]}...")
            
            # Parse JSON payload
            data = json.loads(payload)
            
            # Extract device ID from topic (e.g., iotnarad/devices/esp32_gw_01/data)
            topic_parts = topic.split('/')
            if len(topic_parts) >= 3:
                device_id = topic_parts[2]
            else:
                device_id = 'unknown'
            
            # Route message based on topic
            if '/data' in topic and self.data_callback:
                self.data_callback(device_id, data)
            elif '/status' in topic and self.status_callback:
                self.status_callback(device_id, data)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def start(self):
        """Start MQTT client in background thread"""
        try:
            logger.info(f"🚀 Connecting to MQTT Broker: {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, keepalive=60)
            
            # Start network loop in background thread
            thread = Thread(target=self.client.loop_forever, daemon=True)
            thread.start()
            
            logger.info("MQTT Client thread started")
        except Exception as e:
            logger.error(f"Failed to start MQTT client: {e}")
    
    def stop(self):
        """Stop MQTT client"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT Client stopped")
        except Exception as e:
            logger.error(f"Error stopping MQTT client: {e}")
    
    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 1, retain: bool = False):
        """
        Publish message to MQTT topic
        
        Args:
            topic: MQTT topic
            payload: Dictionary payload to publish
            qos: Quality of Service (0, 1, or 2)
            retain: Retain message flag
        """
        try:
            if not self.connected:
                logger.warning("MQTT client not connected. Cannot publish message.")
                return False
            
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=qos, retain=retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📤 Published to {topic}: {message[:100]}...")
                return True
            else:
                logger.error(f"Failed to publish message. Return code: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False
    
    def publish_config(self, device_id: str, config: Dict[str, Any]):
        """
        Publish device configuration
        
        Args:
            device_id: Device identifier
            config: Configuration dictionary
        """
        topic = f"iotnarad/devices/{device_id}/config"
        return self.publish(topic, config, qos=1, retain=True)
    
    def publish_command(self, device_id: str, command: str, params: Dict[str, Any] = None):
        """
        Publish command to device
        
        Args:
            device_id: Device identifier
            command: Command name
            params: Command parameters
        """
        topic = f"iotnarad/devices/{device_id}/cmd"
        payload = {
            'command': command,
            'params': params or {},
            'timestamp': self._get_timestamp()
        }
        return self.publish(topic, payload, qos=1)
    
    def set_data_callback(self, callback: Callable):
        """Set callback for device data messages"""
        self.data_callback = callback
        logger.info("Data callback registered")
    
    def set_status_callback(self, callback: Callable):
        """Set callback for device status messages"""
        self.status_callback = callback
        logger.info("Status callback registered")
    
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self.connected
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
