# IOTNarad Dashboard 🚀

**Professional IoT Device Management Platform**

A comprehensive dashboard for managing and monitoring ESP32-based IoT devices with real-time data visualization, device configuration, and MQTT communication.

---

## 🏗️ Architecture

```
IoT Devices → Mosquitto MQTT → Docker App → InfluxDB Cloud → Dashboard
     ↓              ↓                ↓              ↓              ↓
  Sensors    Local Broker      GCP VM App   Cloud Database  Plotly Dash
                (GCP VM)         (GCP VM)                    + WebSocket
```

## ✨ Features

### 🔐 **Secure Authentication**
- Admin login with fixed credentials
- Session-based authentication
- Secure password handling

### 📊 **Real-time Analytics**
- Live sensor data visualization
- Temperature, humidity, voltage, current monitoring
- Interactive Plotly charts
- Time-range selection (1h, 6h, 24h, 7d, 30d)

### ⚙️ **Device Configuration**
- **Analog I/O**: 4-20mA, 1-10V, 0-10V
- **Digital I/O**: NPN, PNP, Relays
- **Communication**: WiFi, MQTT, Modbus RTU, CAN Bus
- Save configurations to server (ESP32 memory-efficient)
- Push config to devices via MQTT

### 📡 **Communication**
- MQTT pub/sub with Mosquitto
- WebSocket with Flask-SocketIO for real-time updates
- No data loss with proper buffering
- Handles multiple devices simultaneously

### 💾 **Data Storage**
- InfluxDB Cloud for time-series data
- Local device configuration storage
- Data export/import capabilities

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- InfluxDB Cloud account (optional, can use local)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd IOTNarad_dashboard
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
```

**Important Settings:**
```env
# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=iotnarad@2025

# MQTT Settings
MQTT_BROKER=mqtt
MQTT_PORT=1883

# InfluxDB Cloud (or use local)
INFLUXDB_URL=https://your-cloud-url.com
INFLUXDB_TOKEN=your-token-here
INFLUXDB_ORG=your-org
INFLUXDB_BUCKET=iotnarad-bucket
```

### 3. Start with Docker Compose
```bash
docker-compose up -d
```

### 4. Access the Dashboard
Open your browser and navigate to:
```
http://localhost:8050
```

**Login Credentials:**
- Username: `admin`
- Password: `iotnarad@2025`

---

## 📁 Project Structure

```
IOTNarad_dashboard/
├── app/
│   ├── main.py                 # Main application entry point
│   ├── pages/                  # Dashboard pages
│   │   ├── login.py           # Login page
│   │   ├── dashboard.py       # Main dashboard
│   │   ├── device_config.py   # Device configuration
│   │   └── analytics.py       # Analytics & charts
│   └── services/              # Backend services
│       ├── mqtt_client.py     # MQTT communication
│       ├── influx.py          # InfluxDB integration
│       └── device_config.py   # Config management
├── infra/
│   └── mosquitto/
│       └── mosquitto.conf     # MQTT broker config
├── data/
│   └── configs/               # Device configurations
├── docker-compose.yml         # Docker services
├── Dockerfile                 # App container
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🔧 Configuration

### Device Configuration

1. **Login** to the dashboard
2. Navigate to **Devices** tab
3. Select your device from the dropdown
4. Configure settings in tabs:
   - **⚡ Analog**: Current/voltage inputs and outputs
   - **🔢 Digital**: NPN, PNP, relay controls
   - **📡 Communication**: Network, MQTT, Modbus, CAN Bus
5. Click **Save Configuration**
6. Configuration is automatically pushed to device via MQTT

### MQTT Topics

**Device Data (from IoT devices):**
```
iotnarad/devices/{device_id}/data
```

**Device Configuration (to IoT devices):**
```
iotnarad/devices/{device_id}/config
```

**Device Status:**
```
iotnarad/devices/{device_id}/status
```

### Sample MQTT Message from Device

```json
{
  "device_id": "esp32_gw_01",
  "timestamp": "2025-10-08T10:30:00Z",
  "temperature": 25.5,
  "humidity": 60.2,
  "voltage_ain0": 5.2,
  "current_ain1": 12.5,
  "digital_inputs": [true, false, true, false],
  "digital_outputs": [false, true, false, true]
}
```

---

## 🐳 Docker Services

### Services Overview

| Service | Port | Description |
|---------|------|-------------|
| **app** | 8050 | Dash dashboard + Flask-SocketIO |
| **mqtt** | 1883, 9001 | Mosquitto MQTT broker |
| **influxdb** | 8086 | InfluxDB (local, optional) |

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Restart app only
docker-compose restart app
```

---

## 🧪 Development

### Local Development (without Docker)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env
```

3. **Run MQTT broker (separate terminal):**
```bash
docker run -p 1883:1883 -p 9001:9001 eclipse-mosquitto:2
```

4. **Run the app:**
```bash
python -m app.main
```

### Testing MQTT

Use the provided PowerShell script:
```powershell
.\tools\mqtt_publish.ps1
```

Or use `mosquitto_pub`:
```bash
mosquitto_pub -h localhost -t "iotnarad/devices/esp32_gw_01/data" \
  -m '{"temperature": 25.5, "humidity": 60.2}'
```

---

## 📊 InfluxDB Setup

### Option 1: Use InfluxDB Cloud (Recommended for Production)

1. Sign up at [InfluxDB Cloud](https://www.influxdata.com/products/influxdb-cloud/)
2. Create a bucket: `iotnarad-bucket`
3. Generate an API token
4. Update `.env` with your credentials

### Option 2: Use Local InfluxDB (Development)

Local InfluxDB is included in `docker-compose.yml`:
```yaml
INFLUXDB_URL=http://influxdb:8086
```

Access InfluxDB UI: `http://localhost:8086`

---

## 🎨 UI Features

### Modern Design
- **Color Theme**: Purple gradient (#667eea to #764ba2)
- **Responsive Layout**: Works on desktop and mobile
- **Icons**: Font Awesome for professional look
- **Animations**: Smooth transitions and hover effects

### Navigation
- **Sidebar**: Easy access to all sections
- **Tabs**: Organized device configuration
- **Real-time Updates**: WebSocket for instant data

---

## 🔒 Security

- Session-based authentication
- Environment variable configuration
- MQTT can be secured with TLS (update mosquitto.conf)
- InfluxDB token-based authentication

---

## 🐛 Troubleshooting

### Dashboard not accessible
```bash
# Check if app is running
docker-compose ps

# Check logs
docker-compose logs app
```

### MQTT connection issues
```bash
# Check MQTT broker
docker-compose logs mqtt

# Test connection
mosquitto_sub -h localhost -t "iotnarad/#" -v
```

### InfluxDB not storing data
- Verify InfluxDB credentials in `.env`
- Check InfluxDB logs: `docker-compose logs influxdb`
- Ensure bucket exists

---

## 📝 TODO / Roadmap

- [ ] User management (multiple users)
- [ ] Device alerts and notifications
- [ ] Email/SMS notifications
- [ ] Data export (CSV, Excel)
- [ ] Mobile app integration
- [ ] Dashboard customization
- [ ] Historical data comparison
- [ ] Predictive analytics

---

## 👨‍💻 Development Team

**IOTNarad** - Professional IoT Solutions

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 🆘 Support

For support, please contact:
- Email: support@iotnarad.com
- GitHub Issues: [Create an issue](https://github.com/iotnarad/dashboard/issues)

---

**Happy Monitoring! 🎉**
