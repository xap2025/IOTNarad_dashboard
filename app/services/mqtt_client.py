"""
MQTT Client Service
Handles MQTT communication with IoT devices
"""
import os
import json
import logging
import hashlib
import time
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
        # Device subscribes to: Dev/Checksum/<Device ID>
        # Server publishes to: Dev/Checksum/<Device ID>
        self.topic_device_checksum = os.getenv('MQTT_TOPIC_DEVICE_CHECKSUM', 'Dev/Checksum')
        # Device publishes to: Dev/Init/Reg/<Device ID>
        # Server subscribes to: Dev/Init/Reg/#
        self.topic_device_init_reg = os.getenv('MQTT_TOPIC_DEVICE_INIT_REG', 'Dev/Init/Reg/#')
        self.topic_device_status = os.getenv('MQTT_TOPIC_DEVICE_STATUS', 'iotnarad/devices/+/status')
        # Legacy topic (keep for backward compatibility)
        self.topic_device_config_ack = os.getenv('MQTT_TOPIC_DEVICE_CONFIG_ACK', 'Dev/ConfigACK/#')
        # Device publishes to: Config/ACK/<Device ID> (new format)
        # Server subscribes to: Config/ACK/# (wildcard to receive ACK from any device)
        self.topic_config_ack = os.getenv('MQTT_TOPIC_CONFIG_ACK', 'Config/ACK/#')
        # Device publishes to: Cmd/DConfig/<Device ID>
        # Server subscribes to: Cmd/DConfig/#
        self.topic_device_config_request = os.getenv('MQTT_TOPIC_DEVICE_CONFIG_REQUEST', 'Cmd/DConfig/#')
        # Real-Time Data: Device publishes to: RTD/<Device ID>
        # Server subscribes to: RTD/# (wildcard to receive RTD from any device)
        self.topic_realtime_data = os.getenv('MQTT_TOPIC_REALTIME_DATA', 'RTD/#')
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=self.client_id, clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Callbacks
        self.data_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        self.init_callback: Optional[Callable] = None
        self.config_request_callback: Optional[Callable] = None
        self.realtime_data_callback: Optional[Callable] = None
        
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
            self.client.subscribe(self.topic_device_init_reg)  # Subscribe to device init/registration messages
            self.client.subscribe(self.topic_device_config_ack)  # Subscribe to config acknowledgements (legacy: Dev/ConfigACK/#)
            self.client.subscribe(self.topic_config_ack)  # Subscribe to config acknowledgements (new: Config/ACK/#)
            self.client.subscribe(self.topic_device_config_request)  # Subscribe to device config requests
            self.client.subscribe(self.topic_realtime_data)  # Subscribe to real-time data (RTD/#)
            logger.info(f"📡 Subscribed to: {self.topic_device_data}")
            logger.info(f"📡 Subscribed to: {self.topic_device_status}")
            logger.info(f"📡 Subscribed to: {self.topic_device_init_reg}")
            logger.info(f"📡 Subscribed to: {self.topic_device_config_ack} (legacy)")
            logger.info(f"📡 Subscribed to: {self.topic_config_ack} (new format)")
            logger.info(f"📡 Subscribed to: {self.topic_device_config_request}")
            logger.info(f"📡 Subscribed to: {self.topic_realtime_data} (RTD/#)")
            logger.info(f"✅ MQTT subscriptions complete. Waiting for RTD messages...")
            
            # Log callback registration status
            if self.realtime_data_callback:
                logger.info(f"✅ RTD callback is registered and ready")
            else:
                logger.error(f"❌ RTD callback NOT registered! RTD messages will be lost!")
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
            
            # CRITICAL: Skip deduplication for Dev/Init/Reg/ messages
            # These messages need to go through the callback's deduplication logic
            # which ensures ACK is always sent (even for duplicates)
            skip_dedup = topic.startswith('Dev/Init/Reg/')
            
            if not skip_dedup:
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
            
            # CRITICAL: Log ALL RTD messages for debugging
            if topic.startswith('RTD/'):
                logger.info(f"🔵 RTD MESSAGE DETECTED: Topic={topic}, Payload length={len(payload)}")
            
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
            # IMPORTANT: Check more specific topic first (Dev/Init/Reg/) before general (Dev/Init/)
            if topic.startswith('Dev/Init/Reg/'):
                # Device publishes registration/initialization messages
                # Extract device ID from topic: Dev/Init/Reg/<Device ID>
                device_id = topic.split('/')[-1] if '/' in topic else None
                serial_number = device_id  # Serial number is the device_id in this topic
                logger.info(f"📨 Device Init/Registration received from: {device_id}")
                logger.debug(f"   Topic: {topic}, Payload: {payload[:200]}...")
                
                # Call init callback if set
                # IMPORTANT: Pass parsed JSON data (not raw payload string)
                if self.init_callback:
                    try:
                        self.init_callback(topic, data)  # Pass parsed JSON dict, not raw payload
                    except Exception as e:
                        logger.error(f"❌ Error in init callback: {e}")
                        logger.exception("Full traceback:")
                        # CRITICAL: Even if callback fails, send ACK to device
                        # Extract serial number from topic or payload
                        ack_serial = serial_number
                        if not ack_serial and isinstance(data, dict):
                            ack_serial = data.get('SerialNumber', 'unknown')
                        if ack_serial and ack_serial != 'unknown':
                            logger.warning(f"⚠️ Sending error ACK due to callback exception: {ack_serial}")
                            try:
                                # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                                time.sleep(3.0)
                                self.publish_ack(
                                    ack_serial,
                                    status="error",
                                    message=f"Server error processing registration: {str(e)}"
                                )
                            except Exception as ack_error:
                                logger.error(f"❌ Failed to send error ACK: {ack_error}")
                        else:
                            logger.error(f"❌ Cannot send ACK: serial number not found in topic or payload")
            elif topic.startswith('Dev/Init/'):
                # Device initialization message (other Dev/Init/ topics)
                logger.info(f"🔔 Routing to init callback for topic: {topic}")
                if self.init_callback:
                    logger.info(f"✅ Init callback exists, calling...")
                    # Extract serial number from topic if possible: Dev/Init/<SerialNumber>
                    topic_parts = topic.split('/')
                    serial_number = topic_parts[2] if len(topic_parts) >= 3 else None
                    try:
                        self.init_callback(topic, data)
                    except Exception as e:
                        logger.error(f"❌ Error in init callback: {e}")
                        logger.exception("Full traceback:")
                        # CRITICAL: Even if callback fails, send ACK to device
                        ack_serial = serial_number
                        if not ack_serial and isinstance(data, dict):
                            ack_serial = data.get('SerialNumber', 'unknown')
                        if ack_serial and ack_serial != 'unknown':
                            logger.warning(f"⚠️ Sending error ACK due to callback exception: {ack_serial}")
                            try:
                                # Wait 3 seconds to ensure hardware has time to subscribe to ACK topic
                                time.sleep(3.0)
                                self.publish_ack(
                                    ack_serial,
                                    status="error",
                                    message=f"Server error processing registration: {str(e)}"
                                )
                            except Exception as ack_error:
                                logger.error(f"❌ Failed to send error ACK: {ack_error}")
                        else:
                            logger.error(f"❌ Cannot send ACK: serial number not found in topic or payload")
                else:
                    logger.warning(f"⚠️ Init callback not registered!")
            
            elif topic.startswith('Cmd/DConfig/'):
                # Device requests configuration
                # Topic format: Cmd/DConfig/<Device ID>
                device_id = topic.split('/')[-1] if '/' in topic else None
                logger.info(f"📥 Device config request received from: {device_id}")
                logger.debug(f"   Topic: {topic}, Payload: {payload[:200]}...")
                
                # Call config request callback if set
                if self.config_request_callback:
                    try:
                        self.config_request_callback(topic, data, device_id)
                    except Exception as e:
                        logger.error(f"❌ Error in config request callback: {e}")
                        logger.exception("Full traceback:")
                else:
                    logger.warning(f"⚠️ Config request callback not registered!")
            
            elif topic.startswith('Config/ACK/'):
                # Configuration acknowledgement from hardware (new format)
                # Topic format: Config/ACK/<Device ID>
                ack_device_id = topic.split('/')[-1] if '/' in topic else device_id
                logger.info(f"✅ Configuration ACK received from device {ack_device_id}")
                logger.info(f"   Topic: {topic}, Payload: {payload[:200]}...")
                # Extract result from payload
                try:
                    if "Result" in data or "result" in data:
                        result = data.get("Result") or data.get("result")
                        logger.info(f"   ACK Result: {result}")
                except:
                    pass
                # You can add a callback for config acknowledgements here if needed
            elif topic.startswith('Dev/ConfigACK/') or topic.startswith('Dev/Checksum/'):
                # Configuration acknowledgement from hardware (legacy format)
                logger.info(f"✅ Configuration acknowledgement received from: {device_id}")
                logger.info(f"   Topic: {topic}, Payload: {payload[:200]}...")
                # Extract device ID from topic (e.g., Dev/ConfigACK/TEST78787)
                ack_device_id = topic.split('/')[-1] if '/' in topic else device_id
                # You can add a callback for config acknowledgements here if needed
            elif topic.startswith('RTD/'):
                # Real-Time Data: Device publishes to RTD/<Device ID>
                # Extract device ID from topic: RTD/<Device ID>
                rtd_device_id = topic.split('/')[-1] if '/' in topic else 'unknown'
                logger.info(f"📊 Real-time data received from device: {rtd_device_id}")
                logger.info(f"   Topic: {topic}")
                logger.info(f"   Payload preview: {payload[:500]}...")
                
                # Log data type for debugging
                if isinstance(data, dict):
                    data_type = data.get('type', 'Unknown')
                    values_count = len(data.get('value', {})) if isinstance(data.get('value'), dict) else 0
                    logger.info(f"   Data Type: '{data_type}', Values count: {values_count}")
                else:
                    logger.warning(f"   ⚠️ Data is not a dict: {type(data)}")
                
                # Call real-time data callback if set
                if self.realtime_data_callback:
                    logger.info(f"   ✅ Real-time data callback exists, calling...")
                    try:
                        self.realtime_data_callback(rtd_device_id, data)
                        logger.info(f"   ✅ Real-time data callback completed successfully")
                    except Exception as e:
                        logger.error(f"❌ Error in real-time data callback: {e}")
                        logger.exception("Full traceback:")
                else:
                    logger.error(f"❌ Real-time data callback not registered! Data will be lost!")
                    logger.error(f"   Please check if mqtt_service.set_realtime_data_callback() was called")
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
        Publish device configuration to Dev/Checksum/<Device ID>
        Device subscribes to this topic to receive configuration updates
        
        Args:
            device_id: Device Serial Number (Sr_No) from Device_info measurement
            config: Configuration dictionary
        """
        topic = f"{self.topic_device_checksum}/{device_id}"
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
    
    def set_config_request_callback(self, callback: Callable):
        """Set callback for device configuration requests"""
        self.config_request_callback = callback
        logger.info("Device config request callback registered")
    
    def set_realtime_data_callback(self, callback: Callable):
        """Set callback for real-time data messages (RTD/#)"""
        self.realtime_data_callback = callback
        logger.info("Real-time data callback registered")
    
    def publish_ack(self, serial_number: str, status: str = "success", message: str = "Received"):
        """
        Publish acknowledgment to device
        
        Args:
            serial_number: Device serial number
            status: Acknowledgment status (default: "success")
            message: Acknowledgment message (default: "Received")
        """
        topic = f"Dev/Ack/{serial_number}"
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
