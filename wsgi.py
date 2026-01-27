# wsgi.py - Gunicorn Entry Point for Production Deployment
# This file is used when running the app with Gunicorn (production)
# Example: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:8050 wsgi:application

# ✅ Must monkey patch FIRST (required for Socket.IO with eventlet)
from gevent import monkey
monkey.patch_all()

# Import Flask server and SocketIO from main app
from app.main import server as application
from app.main import socketio

# Global flag to ensure MQTT services start only once
# This prevents multiple MQTT connections when Gunicorn spawns multiple workers
if not hasattr(application, '_backend_services_started'):
    # Import MQTT service
    from app.services.mqtt_client import mqtt_client_service
    
    # Start MQTT service
    if mqtt_client_service:
        try:
            mqtt_client_service.start()
            print("✅ MQTT service started from wsgi.py")
        except Exception as e:
            print(f"⚠️ Error starting MQTT service from wsgi.py: {e}")
    
    application._backend_services_started = True  # Mark as started

# Gunicorn will use this 'application' object
# SocketIO is also exported for compatibility
__all__ = ['application', 'socketio']

