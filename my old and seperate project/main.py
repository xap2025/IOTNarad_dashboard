# main.py
import sys
from dash import Dash, html, dcc, page_container
import dash_bootstrap_components as dbc
import warnings
from influxdb_client.client.warnings import MissingPivotFunction
from flask import Flask
from flask_socketio import SocketIO
import os

# Import the config
from config import SOCKETIO_CORS, SOCKETIO_ASYNC_MODE, SOCKETIO_PING_TIMEOUT, SOCKETIO_PING_INTERVAL

# Initialize the Flask server and Dash app
server = Flask(__name__)
app = Dash(__name__, server=server, use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           suppress_callback_exceptions=True)

# SocketIO setup - MUST BE GLOBAL
# SocketIO setup - MUST BE GLOBAL
socketio = SocketIO(server,
                   cors_allowed_origins=SOCKETIO_CORS,
                   async_mode=SOCKETIO_ASYNC_MODE,
                   ping_timeout=SOCKETIO_PING_TIMEOUT,
                   ping_interval=SOCKETIO_PING_INTERVAL,
                   logger=True,
                   engineio_logger=True)
# Disable InfluxDB pivot warning
warnings.simplefilter("ignore", MissingPivotFunction)

# Main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id="session-store", storage_type="session"),
    page_container
])

# Import and start backend services
from singleMQTT import start_backend_services

# Start backend services only once
start_backend_services()  # Moved outside of __main__

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8071))  # Changed to 8071
    print(f"Starting server on port {port}")
    socketio.run(server, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)