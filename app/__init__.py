from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

load_dotenv()


def create_flask_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "secret")
    return app


socketio = SocketIO(async_mode="eventlet", cors_allowed_origins="*")

