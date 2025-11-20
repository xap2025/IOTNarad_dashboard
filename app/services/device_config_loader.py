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

            # Response type is capitalized (e.g., "Analog", "Digital", "Modbus", "Canbus")
            reply_type = str(data.get("type", "")).strip()
            expected_type = self.COMMAND_MAP.get(section, "")
            
            # Handle case-insensitive comparison (normalize both to lowercase for comparison)
            if reply_type.lower() != expected_type.lower():
                logger.debug(f"⚠️ Ignoring reply of type '{reply_type}' for section '{section}' (expected '{expected_type}').")
                return

            response_holder["payload"] = data
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

        return data

