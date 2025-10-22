@echo off
echo ==========================================
echo  Running IOTNarad Dashboard Without Docker
echo ==========================================
echo.

echo [1/3] Installing Python dependencies...
pip install dash flask flask-socketio paho-mqtt influxdb-client python-dotenv dash-bootstrap-components plotly pandas eventlet gunicorn werkzeug
echo.

echo [2/3] Creating data directory...
if not exist "data\configs" mkdir "data\configs"
echo.

echo [3/3] Starting dashboard...
echo Dashboard will start at: http://localhost:8050
echo Login: admin / iotnarad@2025
echo.
echo Press Ctrl+C to stop the dashboard
echo.

python -m app.main

