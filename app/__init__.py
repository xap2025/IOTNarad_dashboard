from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

load_dotenv()


def create_flask_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "secret")
    # Initialize SocketIO with the app regardless of how the server starts (gunicorn or python)
    socketio.init_app(app)

    # Lazy-start MQTT client on first HTTP request to avoid issues with gunicorn import timing
    try:
        from app.services.mqtt_client import mqtt_service

        @app.before_first_request
        def _start_mqtt_background():
            mqtt_service.start()
    except Exception:
        # Avoid import errors breaking app creation; logs will show if MQTT fails later
        pass

    return app


socketio = SocketIO(async_mode="eventlet", cors_allowed_origins="*")

