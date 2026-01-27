# ✅ Must monkey patch FIRST
from gevent import monkey
monkey.patch_all()

from main import server as application
from main import socketio

# Global flag to ensure services start only once
if not hasattr(application, '_backend_services_started'):
    from singleMQTT import start_backend_services
    start_backend_services()
    application._backend_services_started = True  # Mark as started

application  # Gunicorn will use this