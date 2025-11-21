"""
Device Config Sender Service
Sends configuration to devices over MQTT when user clicks
'Send Configuration' on the dashboard.
"""
import os
import json
import logging
from threading import Event

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class DeviceConfigSenderService:
    """Utility to send configuration sections to a device via MQTT."""

    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER", "mqtt")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.keepalive = 60

    def send_config(self, device_id: str, config_type: str, config_data: dict, timeout: float = 5.0):
        """
        Send a specific configuration section to the device and wait for ACK.

        Args:
            device_id: Target device serial number.
            config_type: One of ['Analog', 'Digital', 'Modbus', 'Canbus'].
            config_data: Configuration dictionary for the section.
            timeout: Seconds to wait for device ACK.

        Returns:
            bool: True if ACK received, False otherwise.

        Raises:
            ValueError: If config_type is invalid.
            TimeoutError: If no ACK is received before timeout.
        """
        if config_type not in ["Analog", "Digital", "Modbus", "Canbus"]:
            raise ValueError(f"Unsupported config type '{config_type}' for config send.")

        write_topic = f"Write/DConfig/{device_id}"
        ack_topic = f"Config/ACK/{device_id}"

        event = Event()
        ack_received = {"received": False, "result": None}

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info(f"📡 Connected to MQTT for config send: {device_id} ({config_type})")
                # Subscribe to ACK topic for this specific device
                client.subscribe(ack_topic)
                logger.info(f"📡 Subscribed to ACK topic: {ack_topic}")
            else:
                logger.error(f"❌ Failed to connect to MQTT broker (rc={rc}) for send request.")

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode("utf-8")
                data = json.loads(payload)
                
                # Check if this is an ACK message
                if "Result" in data or "result" in data:
                    result = data.get("Result") or data.get("result")
                    ack_received["received"] = True
                    ack_received["result"] = result
                    logger.info(f"✅ ACK received from device {device_id}: {result}")
                    event.set()
            except Exception as exc:
                logger.error(f"❌ Failed to parse ACK reply: {exc}")

        client = mqtt.Client(clean_session=True)
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(self.broker, self.port, self.keepalive)
        client.loop_start()

        # Build payload with type and config
        payload = {
            "type": config_type,
            "config": config_data
        }
        message = json.dumps(payload)
        logger.info(f"📤 Sending {config_type} config to {device_id} on {write_topic}")
        logger.debug(f"📤 Payload: {message[:200]}...")
        
        result = client.publish(write_topic, message, qos=1, retain=False)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error(f"❌ Failed to publish config message. Return code: {result.rc}")
            client.loop_stop()
            client.disconnect()
            return False

        # Wait for ACK
        received = event.wait(timeout)
        client.loop_stop()
        client.disconnect()

        if not received:
            logger.warning(f"⚠️ No ACK received from device {device_id} within {timeout}s.")
            return False

        # Check if ACK result is OK
        if ack_received.get("result") == "OK" or ack_received.get("result") == "ok":
            logger.info(f"✅ Configuration sent successfully to device {device_id}")
            return True
        else:
            logger.warning(f"⚠️ Device {device_id} sent ACK with result: {ack_received.get('result')}")
            return False

