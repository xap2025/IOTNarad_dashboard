"""
MQTT Client Service
Handles MQTT communication with IoT devices
"""
import os
import json
import logging
import hashlib
import paho.mqtt.client as mqtt
from threading import Thread, Lock
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
        # Use Dev/Init/+ instead of Dev/Init/# to avoid matching Dev/Init/Ack/... messages
        # + matches single level, # matches multiple levels
        self.topic_device_init = os.getenv('MQTT_TOPIC_DEVICE_INIT', 'Dev/Init/+')
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=self.client_id, clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Callbacks
        self.data_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        self.init_callback: Optional[Callable] = None
        
        # Message deduplication: Track recently processed messages
        self._processed_messages: set = set()
        self._message_lock = Lock()
        self._message_ttl = 5.0  # Keep message hash for 5 seconds
        
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
            self.client.subscribe(self.topic_device_init)
            logger.info(f"📡 Subscribed to: {self.topic_device_data}")
            logger.info(f"📡 Subscribed to: {self.topic_device_status}")
            logger.info(f"📡 Subscribed to: {self.topic_device_init}")
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
            
            # Create message hash for deduplication (topic + payload)
            message_hash = hashlib.md5(f"{topic}:{payload}".encode()).hexdigest()
            
            # Check if this exact message was recently processed
            with self._message_lock:
                if message_hash in self._processed_messages:
                    logger.debug(f"🔕 Duplicate message ignored: {topic} (hash: {message_hash[:8]}...)")
                    return
                # Mark as processed
                self._processed_messages.add(message_hash)
                # Clean up old hashes (keep only last 1000 to prevent memory leak)
                if len(self._processed_messages) > 1000:
                    # Remove oldest entries (simple FIFO)
                    self._processed_messages = set(list(self._processed_messages)[-500:])
            
            logger.info(f"📨 Message received on {topic}: {payload[:200]}...")
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to decode JSON message on {topic}: {e}")
                logger.error(f"   Raw payload: {payload}")
                return
            
            # Extract device ID from topic (e.g., iotnarad/devices/esp32_gw_01/data)
            topic_parts = topic.split('/')
            if len(topic_parts) >= 3:
                device_id = topic_parts[2]
            else:
                device_id = 'unknown'
            
            # Route message based on topic
            if topic.startswith('Dev/Init/') and not topic.startswith('Dev/Init/Ack/'):
                # Device initialization message (ignore acknowledgment messages)
                logger.info(f"🔔 Routing to init callback for topic: {topic}")
                if self.init_callback:
                    logger.info(f"✅ Init callback exists, calling...")
                    self.init_callback(topic, data)
                else:
                    logger.warning(f"⚠️ Init callback not registered!")
            elif topic.startswith('Dev/Init/Ack/'):
                # Ignore acknowledgment messages (server's own messages)
                logger.debug(f"🔕 Ignoring acknowledgment message on topic: {topic}")
            elif '/data' in topic and self.data_callback:
                self.data_callback(device_id, data)
            elif '/status' in topic and self.status_callback:
                self.status_callback(device_id, data)
            else:
                logger.warning(f"⚠️ No callback registered for topic: {topic}")
                
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")
            logger.exception("Full error traceback:")
    
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
    
    def set_init_callback(self, callback: Callable):
        """Set callback for device initialization messages"""
        self.init_callback = callback
        logger.info("Device initialization callback registered")
    
    def publish_ack(self, serial_number: str, status: str = "success", message: str = "Received"):
        """
        Publish acknowledgment to device
        
        Args:
            serial_number: Device serial number
            status: Acknowledgment status (default: "success")
            message: Acknowledgment message (default: "Received")
        """
        topic = f"Dev/Init/Ack/{serial_number}"
        payload = {
            "status": status,
            "message": message,
            "timestamp": self._get_timestamp()
        }
        return self.publish(topic, payload, qos=1, retain=False)
    
    def is_connected(self) -> bool:
        """Check if MQTT client is connected"""
        return self.connected
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'
