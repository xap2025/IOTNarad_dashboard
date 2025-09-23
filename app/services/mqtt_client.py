import os
import threading
from typing import Optional
import paho.mqtt.client as mqtt
from flask_socketio import emit
from app import socketio


class MqttService:
    def __init__(self):
        self._client: Optional[mqtt.Client] = None
        self._thread: Optional[threading.Thread] = None

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        topic = os.getenv("MQTT_TOPIC_SUB", "devices/+/uplink")
        client.subscribe(topic, qos=1)

    def _on_message(self, client, userdata, msg):
        socketio.emit("mqtt_message", {"topic": msg.topic, "payload": msg.payload.decode(errors="ignore")})

    def start(self):
        if self._thread and self._thread.is_alive():
            return

        def _run():
            host = os.getenv("MQTT_BROKER_HOST", "localhost")
            port = int(os.getenv("MQTT_BROKER_PORT", 1883))
            username = os.getenv("MQTT_USERNAME")
            password = os.getenv("MQTT_PASSWORD")

            self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            if username:
                self._client.username_pw_set(username, password)
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message
            self._client.connect(host, port, keepalive=60)
            self._client.loop_forever()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()


mqtt_service = MqttService()

