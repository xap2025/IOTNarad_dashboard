# 📊 IOTNarad Dashboard - Project Summary

## 🎯 Project Overview

**IOTNarad Dashboard** is a comprehensive IoT device management platform built with:
- **Frontend:** Dash (Plotly) + Bootstrap
- **Backend:** Flask + Flask-SocketIO
- **Database:** InfluxDB Cloud Serverless (v3) - **SQL queries required**
- **MQTT:** Mosquitto broker
- **Deployment:** Docker Compose

---

## ✅ Current Status

### Core Features: **COMPLETE** ✅
- ✅ User authentication & management
- ✅ Device registration via MQTT
- ✅ Device configuration (Analog, Digital, MODBUS, CAN Bus)
- ✅ Real-time data visualization
- ✅ Email service (OAuth2 + App Password)
- ✅ Password reset & change
- ✅ Profile management

### SQL Requirement: **IMPLEMENTED** ✅
- ✅ All service files updated with SQL comments
- ✅ SQL equivalent documented for all queries
- ✅ Documentation files created

---

## 📁 Project Structure

```
IOTNarad_dashboard/
├── app/                          # Main application
│   ├── main.py                  # Entry point
│   ├── pages/                   # Dash pages
│   └── services/                # Business logic
├── assets/                      # Static files
├── infra/                       # Infrastructure configs
├── tools/                       # Utility scripts
├── docker-compose.yml           # Docker services
├── Dockerfile                   # App container
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables (not in Git)
```

---

## 🔧 Key Services

| Service | Purpose | Database |
|---------|---------|----------|
| `user_service.py` | User management | InfluxDB (SQL) |
| `device_info_service.py` | Device registration | InfluxDB (SQL) |
| `device_config_db.py` | Config storage | InfluxDB (SQL) |
| `influx.py` | Time-series data | InfluxDB (SQL) |
| `mqtt_client.py` | MQTT communication | N/A |
| `email_service.py` | Email sending | N/A |
| `oee_service.py` | OEE calculations | N/A |

---

## 📊 Database Tables (Measurements)

1. **User_info** - User accounts
2. **Device_info** - Registered devices
3. **Device_Config** - Device configurations
4. **Device_Config_Analog** - Analog I/O
5. **Device_Config_Digital** - Digital I/O
6. **Device_Config_MODBUS** - MODBUS settings
7. **Device_Config_CANBus** - CAN Bus settings
8. **device_data** - Sensor time-series data

---

## 🚀 Quick Commands

### Start Application:
```bash
docker compose up -d --build
```

### View Logs:
```bash
docker compose logs -f app
```

### Test Device Init:
```powershell
.\test_mqtt_publish.ps1
```

### View Database:
```bash
python VIEW_ALL_TABLES.py
```

---

## 📚 Essential Documentation

1. **`IMPORTANT_SQL_REQUIREMENT.md`** - SQL requirement reminder
2. **`SQL_QUERIES_REFERENCE.md`** - SQL queries guide
3. **`DEVICE_INIT_GUIDE.md`** - Device initialization
4. **`PROJECT_REVIEW.md`** - Complete project review

---

## ⚠️ Important Reminders

1. **SQL Queries:** Always use SQL in InfluxDB Cloud UI
2. **Time Range:** Use `interval '1 year'` for all queries
3. **Environment:** Never commit `.env` file
4. **MQTT Topics:** Follow documented topic structure

---

## ✅ Project Health: **EXCELLENT**

All systems operational and documented.

