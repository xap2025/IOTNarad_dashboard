# ⚡ Quick GCP VM Production Setup (TL;DR)

## 🎯 Fast Setup Commands

### **1. SSH into GCP VM**
```bash
ssh user@your-gcp-vm-ip
```

### **2. Install Docker (if needed)**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt-get install -y docker-compose-plugin
exit  # Logout
# SSH again
```

### **3. Clone Project**
```bash
cd ~
git clone git@github.com:xap2025/IOTNarad_dashboard.git
cd IOTNarad_dashboard
```

### **4. Create Production .env**
```bash
nano .env
```

Paste this:
```env
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_ORG=iot-narad-production
INFLUXDB_BUCKET=iot_data_production
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_production_password
INFLUXDB_TOKEN=will_add_after_setup

MQTT_BROKER=mqtt
MQTT_PORT=1883

FLASK_ENV=production
DEBUG=False
```

### **5. Start InfluxDB**
```bash
docker compose up -d influxdb
sleep 15
```

### **6. Setup InfluxDB UI**
1. Open: `http://your-gcp-vm-ip:8086`
2. Fill setup form:
   - Username: `admin`
   - Password: `your_production_password`
   - Org: `iot-narad-production`
   - Bucket: `iot_data_production`
3. Generate token → Copy it

### **7. Add Token to .env**
```bash
nano .env
# Add token to INFLUXDB_TOKEN=
```

### **8. Add Firewall Rules**
```bash
# Port 8050 (App)
gcloud compute firewall-rules create allow-app-8050 \
  --allow tcp:8050 --source-ranges 0.0.0.0/0

# Port 8086 (InfluxDB)
gcloud compute firewall-rules create allow-influxdb-8086 \
  --allow tcp:8086 --source-ranges 0.0.0.0/0
```

### **9. Start App**
```bash
docker compose up -d --build
docker compose logs -f app
```

### **10. Access App**
```
http://your-gcp-vm-ip:8050
```

---

## ✅ Verify

```bash
# Check containers
docker compose ps

# Check logs
docker compose logs app | grep "Connected to InfluxDB"

# Should show: http://influxdb:8086
```

---

## 🔄 Common Commands

```bash
# Restart app
docker compose restart app

# View logs
docker compose logs -f app

# Update code
git pull
docker compose up -d --build
```

---

**Detailed guide**: See `GCP_VM_PRODUCTION_SETUP.md`

