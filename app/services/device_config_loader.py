"""
Device Config Loader Service
Fetches live configuration from devices over MQTT when user clicks
'Load from Device' on the dashboard.
"""
import os
import json
import logging
from threading import Event

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class DeviceConfigLoaderService:
    """Utility to request configuration sections from a device via MQTT."""

    COMMAND_MAP = {
        "analog": "Analog",
        "digital": "Digital",
        "modbus": "Modbus",
        "can": "Canbus",
    }

    def __init__(self):
        self.broker = os.getenv("MQTT_BROKER", "mqtt")
        self.port = int(os.getenv("MQTT_PORT", 1883))
        self.keepalive = 60

    def _build_topics(self, device_id: str):
        read_topic = f"Cmd/SConfig/{device_id}"
        reply_topic = f"Ack/SConfig/{device_id}"
        return read_topic, reply_topic

    def load_section(self, device_id: str, section: str, timeout: float = 5.0):
        """
        Request a specific configuration section from the device and wait for reply.

        Args:
            device_id: Target device serial number.
            section: One of ['analog', 'digital', 'modbus', 'can'].
            timeout: Seconds to wait for device reply.

        Returns:
            Dict payload received from device (expects {'type': section, 'config': {...}}).

        Raises:
            ValueError: If section is invalid.
            TimeoutError: If no reply is received before timeout.
            RuntimeError: If reply payload is malformed.
        """
        section = section.lower()
        if section not in self.COMMAND_MAP:
            raise ValueError(f"Unsupported section '{section}' for config load.")

        command = self.COMMAND_MAP[section]
        read_topic, reply_topic = self._build_topics(device_id)

        event = Event()
        response_holder = {}

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info(f"📡 Connected to MQTT for config load: {device_id} ({section})")
                client.subscribe(reply_topic)
            else:
                logger.error(f"❌ Failed to connect to MQTT broker (rc={rc}) for load request.")

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode("utf-8")
                data = json.loads(payload)
            except Exception as exc:
                logger.error(f"❌ Failed to parse config reply: {exc}")
                return

            # Device may send either "type" or "command" field
            # Also check for "status" field to validate response
            reply_type = str(data.get("type", "")).strip()
            if not reply_type:
                # Fallback: check "command" field if "type" is not present
                reply_type = str(data.get("command", "")).strip()
            
            expected_type = self.COMMAND_MAP.get(section, "")
            
            # Handle case-insensitive comparison (normalize both to lowercase for comparison)
            if reply_type.lower() != expected_type.lower():
                logger.debug(f"⚠️ Ignoring reply of type '{reply_type}' for section '{section}' (expected '{expected_type}').")
                return
            
            # Validate that config field exists
            if "config" not in data:
                logger.error(f"❌ Device reply missing 'config' field: {data}")
                return
            
            # Check status if present (optional - some devices send status field)
            status = data.get("status", "").lower()
            if status and status not in ["ok", "success"]:
                logger.warning(f"⚠️ Device returned non-OK status: {status}")
                # Still accept the response if config is present
            
            # Normalize response format to always have "type" field
            normalized_data = {
                "type": expected_type,  # Use expected type (capitalized)
                "config": data.get("config", {})
            }
            
            response_holder["payload"] = normalized_data
            event.set()

        client = mqtt.Client(clean_session=True)
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(self.broker, self.port, self.keepalive)
        client.loop_start()

        payload = {"command": command}
        message = json.dumps(payload)
        logger.info(f"📤 Requesting {section} config from {device_id} on {read_topic}: {message}")
        client.publish(read_topic, message, qos=1, retain=False)

        received = event.wait(timeout)
        client.loop_stop()
        client.disconnect()

        if not received:
            raise TimeoutError(f"No {section} config reply from device {device_id} within {timeout}s.")

        data = response_holder.get("payload")
        if not data or "config" not in data:
            raise RuntimeError(f"Malformed config reply for {section}: {data}")
        
        logger.info(f"✅ Successfully received {section} config from device {device_id}")
        logger.debug(f"📥 Response payload: {json.dumps(data, indent=2)[:500]}...")

        return data

