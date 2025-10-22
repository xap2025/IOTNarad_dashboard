# 🧪 IOTNarad Dashboard - Testing Guide

## ✅ Quick Test on Your Laptop (Windows)

### **Prerequisites Verified:**
- ✅ Docker Desktop installed (v28.4.0)
- ✅ Docker Compose available (v2.39.2)
- ✅ Python installed (v3.12.0)
- ✅ .env file configured with InfluxDB Cloud credentials

---

## 🚀 Method 1: Quick Docker Test (RECOMMENDED)

### **Step 1: Open PowerShell/Command Prompt**
```powershell
# Navigate to project directory (if not already there)
cd C:\Users\ridhi\IOTNarad_dashboard
```

### **Step 2: Create data directory**
```powershell
mkdir -p data\configs
```

### **Step 3: Start all services**
```powershell
docker-compose up -d --build
```

This will:
- Build the app container
- Start MQTT broker (Mosquitto)
- Start InfluxDB (local, optional)
- Start the dashboard app

### **Step 4: Wait 30 seconds for services to start**
```powershell
# Check container status
docker ps
```

You should see 3 containers running:
- `iotnarad_app`
- `iotnarad_mqtt`
- `iotnarad_influxdb`

### **Step 5: View logs to verify**
```powershell
# View app logs
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f app
```

Look for these messages:
```
✅ Connected to MQTT Broker: mqtt:1883
✅ Connected to InfluxDB: https://us-east-1-1.aws.cloud2.influxdata.com
🚀 Starting IOTNarad Dashboard on 0.0.0.0:8050
```

### **Step 6: Open Dashboard in Browser**
1. Open your browser (Chrome, Edge, Firefox)
2. Go to: **http://localhost:8050**
3. Login with:
   - **Username:** `admin`
   - **Password:** `iotnarad@2025`

### **Step 7: Test the Dashboard**

#### **Test Login Page:**
- ✅ Beautiful gradient background
- ✅ Login form appears
- ✅ Can enter credentials

#### **Test Home Page:**
- ✅ Sidebar navigation works
- ✅ Stats cards display (24 devices, 1,542 msg/hour, etc.)
- ✅ System status shows (MQTT, InfluxDB, WebSocket)

#### **Test Analytics Page:**
- ✅ Click "Analytics" in sidebar
- ✅ Time range selector works (1h, 6h, 24h, 7d, 30d)
- ✅ Charts display (Temperature, Humidity, Voltage, Current)
- ✅ Digital I/O status shows
- ✅ Activity log displays

#### **Test Devices Page:**
- ✅ Click "Devices" in sidebar
- ✅ Device dropdown shows ESP32 gateways
- ✅ Tabs work (Analog, Digital, Communication)
- ✅ Tables display correctly
- ✅ Input fields are editable
- ✅ Checkboxes work

---

## 🔧 Method 2: Test MQTT Communication

### **Open a new terminal and test MQTT publishing:**

```powershell
# Publish test data to MQTT
docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -t "iotnarad/devices/esp32_gw_01/data" -m '{"device_id":"esp32_gw_01","temperature":25.5,"humidity":60.2,"voltage_ain0":5.2,"current_ain1":12.5}'
```

### **Check if data appears:**
1. Go to Analytics page
2. Charts should update with new data (if real-time updates work)
3. Check app logs: `docker-compose logs app`

---

## 📊 Method 3: Test InfluxDB Connection

### **Verify data is being stored:**

```powershell
# Check app logs for InfluxDB writes
docker-compose logs app | findstr "InfluxDB"
```

You should see:
```
✅ Connected to InfluxDB: https://us-east-1-1.aws.cloud2.influxdata.com
💾 Data written to InfluxDB for device: esp32_gw_01
```

### **Check InfluxDB Cloud directly:**
1. Go to: https://cloud2.influxdata.com/
2. Login with:
   - Email: `xaptronicsindia@gmail.com`
   - Password: `xaptronicshyd@2025`
3. Navigate to: **Data Explorer**
4. Bucket: `iot_data_gcp`
5. Check if data is present

---

## 🐛 Troubleshooting

### **Problem 1: Containers not starting**

**Check:**
```powershell
docker-compose ps
docker-compose logs
```

**Solution:**
```powershell
# Stop and remove containers
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### **Problem 2: Port 8050 already in use**

**Check:**
```powershell
netstat -ano | findstr :8050
```

**Solution:**
- Stop the process using port 8050
- Or change PORT in .env file

### **Problem 3: Dashboard not accessible**

**Check:**
```powershell
# Verify app is running
docker ps --filter "name=iotnarad_app"

# Check app logs
docker-compose logs app
```

**Solution:**
- Wait 30-60 seconds for app to fully start
- Check firewall settings
- Try: http://127.0.0.1:8050

### **Problem 4: MQTT connection failed**

**Check:**
```powershell
docker-compose logs mqtt
```

**Solution:**
```powershell
# Restart MQTT service
docker-compose restart mqtt
```

### **Problem 5: InfluxDB Cloud connection error**

**Check .env file:**
```powershell
Get-Content .env | findstr "INFLUXDB"
```

**Verify credentials:**
- URL: `https://us-east-1-1.aws.cloud2.influxdata.com`
- Token: Should match InfluxDB Cloud
- Org: `iot-narad-gcp`
- Bucket: `iot_data_gcp`

---

## 🧹 Clean Up After Testing

### **Stop all services:**
```powershell
docker-compose down
```

### **Remove all containers and volumes:**
```powershell
docker-compose down -v
```

### **Remove Docker images:**
```powershell
docker rmi iotnarad_dashboard_app
```

---

## ✅ Success Checklist

- [ ] Docker containers running (3 containers)
- [ ] Dashboard accessible at http://localhost:8050
- [ ] Login page displays correctly
- [ ] Can login with admin credentials
- [ ] Home page shows stats and navigation
- [ ] Analytics page displays charts
- [ ] Devices page shows configuration tables
- [ ] MQTT broker accepting connections
- [ ] InfluxDB Cloud connection successful
- [ ] No errors in logs

---

## 📝 Expected Output Examples

### **Successful Docker Compose Up:**
```
✔ Network iotnarad_dashboard_default    Created
✔ Container iotnarad_influxdb           Started
✔ Container iotnarad_mqtt               Started
✔ Container iotnarad_app                Started
```

### **Successful App Logs:**
```
INFO - 🚀 Connecting to MQTT Broker: mqtt:1883
INFO - ✅ Connected to MQTT Broker: mqtt:1883
INFO - 📡 Subscribed to: iotnarad/devices/+/data
INFO - ✅ Connected to InfluxDB: https://us-east-1-1.aws.cloud2.influxdata.com
INFO - 📊 Using bucket: iot_data_gcp
INFO - Starting IOTNarad Dashboard on 0.0.0.0:8050
```

---

## 🎯 Next Steps After Successful Test

1. **Test with real ESP32 device**
   - Flash ESP32 with code from `ESP32_INTEGRATION.md`
   - Configure WiFi and MQTT broker IP
   - Verify data appears in dashboard

2. **Deploy to GCP**
   - Follow `DEPLOYMENT_GUIDE.md`
   - Set up firewall rules
   - Configure domain (optional)

3. **Customize Dashboard**
   - Add more devices
   - Customize charts
   - Set up alerts

---

## 📞 Help & Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify .env configuration
3. Check README.md and DEPLOYMENT_GUIDE.md
4. Review error messages carefully

---

**Happy Testing! 🎉**

Your IOTNarad Dashboard should now be running successfully on your laptop!

