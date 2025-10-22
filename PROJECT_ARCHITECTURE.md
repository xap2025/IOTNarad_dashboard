# 📁 IOTNarad Dashboard - Complete Project Architecture

## 🏗️ Project Structure & File Responsibilities

| File/Folder | Purpose | What It Does | Terminal Command After Changes |
|-------------|---------|--------------|-------------------------------|
| **📁 app/** | Main application code | Core Python application | `docker-compose restart app` |
| **📄 app/main.py** | Application entry point | Flask + Dash server, routing, authentication | `docker-compose restart app` |
| **📁 app/pages/** | UI page layouts | Dashboard pages (login, home, analytics, devices) | `docker-compose restart app` |
| **📄 app/pages/login.py** | Login page | Authentication interface, login form | `docker-compose restart app` |
| **📄 app/pages/dashboard.py** | Main dashboard | Sidebar navigation, home page layout | `docker-compose restart app` |
| **📄 app/pages/analytics.py** | Analytics page | Real-time charts, data visualization | `docker-compose restart app` |
| **📄 app/pages/device_config.py** | Device configuration | Device settings, MQTT config | `docker-compose restart app` |
| **📁 app/services/** | Backend services | MQTT, InfluxDB, device config services | `docker-compose restart app` |
| **📄 app/services/mqtt_client.py** | MQTT communication | MQTT pub/sub, device communication | `docker-compose restart app` |
| **📄 app/services/influx.py** | Database service | InfluxDB read/write operations | `docker-compose restart app` |
| **📄 app/services/device_config.py** | Config management | Device configuration storage | `docker-compose restart app` |
| **📁 infra/** | Infrastructure config | Docker service configurations | `docker-compose restart <service>` |
| **📁 infra/mosquitto/** | MQTT broker config | Mosquitto MQTT settings | `docker-compose restart mqtt` |
| **📄 infra/mosquitto/mosquitto.conf** | MQTT configuration | MQTT broker settings, ports | `docker-compose restart mqtt` |
| **📁 infra/influxdb/** | InfluxDB config | Database configuration | `docker-compose restart influxdb` |
| **📄 infra/influxdb/influxdb.conf** | InfluxDB settings | Database configuration | `docker-compose restart influxdb` |
| **📁 data/** | Data storage | Device configurations, logs | No restart needed |
| **📁 data/configs/** | Device configs | JSON configuration files | No restart needed |
| **📄 .env** | Environment variables | Database credentials, MQTT settings | `docker-compose restart app` |
| **📄 .env.example** | Template file | Environment variable template | No restart needed |
| **📄 .env.production** | Production config | Production environment settings | `docker-compose restart app` |
| **📄 requirements.txt** | Python dependencies | Python package list | `docker-compose up -d --build` |
| **📄 Dockerfile** | Container definition | Docker image build instructions | `docker-compose up -d --build` |
| **📄 docker-compose.yml** | Service orchestration | Multi-container setup | `docker-compose down && docker-compose up -d` |
| **📄 docker-compose-fixed.yml** | Fixed compose file | Backup compose configuration | `docker-compose -f docker-compose-fixed.yml up -d` |

---

## 🚀 Terminal Commands by Change Type

### **🔄 Quick Restart Commands**

| Change Type | Command | When to Use |
|-------------|---------|-------------|
| **Python code changes** | `docker-compose restart app` | Any .py file in app/ folder |
| **Page layout changes** | `docker-compose restart app` | Changes in app/pages/ |
| **Service changes** | `docker-compose restart app` | Changes in app/services/ |
| **Environment variables** | `docker-compose restart app` | Changes in .env file |
| **MQTT config** | `docker-compose restart mqtt` | Changes in infra/mosquitto/ |
| **InfluxDB config** | `docker-compose restart influxdb` | Changes in infra/influxdb/ |

### **🔨 Rebuild Commands**

| Change Type | Command | When to Use |
|-------------|---------|-------------|
| **New Python packages** | `docker-compose up -d --build` | Changes in requirements.txt |
| **Dockerfile changes** | `docker-compose up -d --build` | Changes in Dockerfile |
| **Docker compose changes** | `docker-compose down && docker-compose up -d` | Changes in docker-compose.yml |
| **Major code changes** | `docker-compose up -d --build` | Multiple file changes |

### **🧹 Clean Restart Commands**

| Change Type | Command | When to Use |
|-------------|---------|-------------|
| **Complete reset** | `docker-compose down -v && docker-compose up -d --build` | Major issues, fresh start |
| **Clean rebuild** | `docker system prune -f && docker-compose up -d --build` | Docker issues, clean build |
| **Nuclear option** | `docker-compose down -v && docker system prune -a -f && docker-compose up -d --build` | Everything broken |

---

## 📋 File-by-File Change Commands

### **📄 Core Application Files**

```bash
# app/main.py changes
docker-compose restart app

# app/pages/login.py changes  
docker-compose restart app

# app/pages/dashboard.py changes
docker-compose restart app

# app/pages/analytics.py changes
docker-compose restart app

# app/pages/device_config.py changes
docker-compose restart app

# app/services/mqtt_client.py changes
docker-compose restart app

# app/services/influx.py changes
docker-compose restart app

# app/services/device_config.py changes
docker-compose restart app
```

### **⚙️ Configuration Files**

```bash
# .env file changes
docker-compose restart app

# .env.production changes
docker-compose restart app

# requirements.txt changes
docker-compose up -d --build

# Dockerfile changes
docker-compose up -d --build

# docker-compose.yml changes
docker-compose down && docker-compose up -d

# infra/mosquitto/mosquitto.conf changes
docker-compose restart mqtt

# infra/influxdb/influxdb.conf changes
docker-compose restart influxdb
```

### **📁 Data & Static Files**

```bash
# data/configs/ changes (JSON files)
# No restart needed - files are mounted as volumes

# index.html, style.css, script.js changes
# No restart needed - these are static files (not used in production)

# README.md, documentation changes
# No restart needed - documentation only
```

---

## 🎯 Development Workflow Commands

### **Daily Development**

```bash
# Start your day
cd C:\Users\ridhi\IOTNarad_dashboard
docker-compose up -d

# Make changes to Python files
# Edit files in app/ directory

# Apply changes
docker-compose restart app

# Check logs
docker-compose logs app --tail=20

# Test in browser
# Open http://localhost:8050
```

### **Adding New Features**

```bash
# Add new Python packages
# Edit requirements.txt
docker-compose up -d --build

# Add new pages
# Create new file in app/pages/
docker-compose restart app

# Add new services
# Create new file in app/services/
docker-compose restart app
```

### **Configuration Changes**

```bash
# Change database settings
# Edit .env file
docker-compose restart app

# Change MQTT settings
# Edit infra/mosquitto/mosquitto.conf
docker-compose restart mqtt

# Change Docker setup
# Edit docker-compose.yml
docker-compose down && docker-compose up -d
```

---

## 🔍 Quick Reference Commands

### **Status & Monitoring**

```bash
# Check container status
docker ps

# Check all containers
docker ps -a

# View app logs
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f app

# Check service status
docker-compose ps
```

### **Testing Commands**

```bash
# Test MQTT
docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -t "test" -m "hello"

# Test InfluxDB
docker exec -it iotnarad_influxdb influx ping

# Test app health
curl http://localhost:8050
```

### **Cleanup Commands**

```bash
# Stop all services
docker-compose down

# Remove containers
docker-compose down -v

# Clean Docker system
docker system prune -f

# Complete cleanup
docker system prune -a --volumes -f
```

---

## 🚨 Common Scenarios & Commands

### **Scenario 1: Changed Python Code**
```bash
# After editing any .py file in app/
docker-compose restart app
```

### **Scenario 2: Added New Python Package**
```bash
# After editing requirements.txt
docker-compose up -d --build
```

### **Scenario 3: Changed Environment Variables**
```bash
# After editing .env
docker-compose restart app
```

### **Scenario 4: Changed Docker Configuration**
```bash
# After editing docker-compose.yml
docker-compose down && docker-compose up -d
```

### **Scenario 5: Changed MQTT Settings**
```bash
# After editing infra/mosquitto/mosquitto.conf
docker-compose restart mqtt
```

### **Scenario 6: Dashboard Not Loading**
```bash
# Quick fix
docker-compose restart app

# If still not working
docker-compose down && docker-compose up -d --build
```

### **Scenario 7: Complete Reset**
```bash
# Nuclear option
docker-compose down -v
docker system prune -a --volumes -f
docker-compose up -d --build
```

---

## 📱 Batch File Shortcuts

| Batch File | Command | Purpose |
|------------|---------|---------|
| `quick_test.bat` | Interactive menu | Daily testing and debugging |
| `fix_dashboard.bat` | Complete fix | One-click dashboard reset |
| `fix_wsl_docker.bat` | Docker fix | WSL integration issues |
| `test_docker_simple.bat` | Docker test | Basic Docker functionality |
| `run_without_docker.bat` | Python only | Fallback without Docker |

---

## 🎯 Best Practices

### **Development Workflow**
1. **Make changes** to Python files
2. **Run:** `docker-compose restart app`
3. **Check logs:** `docker-compose logs app --tail=10`
4. **Test in browser:** Refresh http://localhost:8050

### **Configuration Changes**
1. **Edit config files** (.env, docker-compose.yml, etc.)
2. **Run appropriate restart command**
3. **Verify services are running:** `docker ps`
4. **Test functionality**

### **Major Changes**
1. **Edit multiple files**
2. **Run:** `docker-compose up -d --build`
3. **Wait for build to complete**
4. **Check all services:** `docker-compose ps`

---

**This table covers every possible change scenario in your project!** 🎉

Save this file for quick reference during development.
