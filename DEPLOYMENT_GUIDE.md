# 🚀 IOTNarad Dashboard - Deployment Guide

Complete step-by-step deployment guide for GCP VM.

---

## 📋 Prerequisites

- GCP VM Instance (Ubuntu 20.04 or later)
- Docker & Docker Compose installed
- InfluxDB Cloud account (or local InfluxDB)
- Domain name (optional, for production)

---

## 🔧 Step 1: Prepare GCP VM

### 1.1 Create VM Instance

```bash
# Using gcloud CLI
gcloud compute instances create iotnarad-vm \
    --zone=asia-south1-a \
    --machine-type=e2-medium \
    --boot-disk-size=20GB \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server,https-server,mqtt-server
```

### 1.2 Configure Firewall Rules

```bash
# Allow HTTP, HTTPS, MQTT
gcloud compute firewall-rules create iotnarad-web \
    --allow tcp:80,tcp:443,tcp:8050,tcp:1883,tcp:9001 \
    --target-tags=http-server,https-server,mqtt-server \
    --description="IOTNarad Dashboard and MQTT"
```

### 1.3 SSH into VM

```bash
gcloud compute ssh iotnarad-vm --zone=asia-south1-a
```

---

## 🐳 Step 2: Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version

# Logout and login again
exit
```

---

## 📦 Step 3: Deploy Application

### 3.1 Clone Repository

```bash
# SSH back into VM
gcloud compute ssh iotnarad-vm --zone=asia-south1-a

# Clone your repository
git clone https://github.com/your-username/IOTNarad_dashboard.git
cd IOTNarad_dashboard
```

### 3.2 Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit configuration
nano .env
```

**Update these settings in .env:**

```env
# Application
APP_SECRET_KEY=your-strong-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password

# MQTT
MQTT_BROKER=mqtt
MQTT_PORT=1883

# InfluxDB Cloud
INFLUXDB_URL=https://your-region.influxdata.com
INFLUXDB_TOKEN=your-influxdb-cloud-token
INFLUXDB_ORG=your-organization
INFLUXDB_BUCKET=iotnarad-bucket

# Server
HOST=0.0.0.0
PORT=8050
DEBUG=False
```

Save and exit (Ctrl+X, Y, Enter).

### 3.3 Start Services

```bash
# Create data directory
mkdir -p data/configs

# Start with Docker Compose
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

---

## 🌐 Step 4: Access Dashboard

### Get VM External IP

```bash
# On your local machine
gcloud compute instances list

# Or on VM
curl ifconfig.me
```

### Access Dashboard

Open browser:
```
http://YOUR_VM_EXTERNAL_IP:8050
```

**Login:**
- Username: `admin`
- Password: `your-password-from-env`

---

## 📡 Step 5: Configure IoT Devices

### ESP32 Configuration

Update your ESP32 code with:

```cpp
// MQTT Broker
const char* mqtt_server = "YOUR_VM_EXTERNAL_IP";
const int mqtt_port = 1883;

// MQTT Topics
const char* topic_data = "iotnarad/devices/esp32_gw_01/data";
const char* topic_config = "iotnarad/devices/esp32_gw_01/config";
const char* topic_status = "iotnarad/devices/esp32_gw_01/status";
```

### Sample ESP32 MQTT Publish

```cpp
void publishSensorData() {
    StaticJsonDocument<200> doc;
    doc["device_id"] = "esp32_gw_01";
    doc["timestamp"] = getISOTimestamp();
    doc["temperature"] = 25.5;
    doc["humidity"] = 60.2;
    doc["voltage_ain0"] = 5.2;
    doc["current_ain1"] = 12.5;
    
    char buffer[256];
    serializeJson(doc, buffer);
    
    client.publish("iotnarad/devices/esp32_gw_01/data", buffer);
}
```

---

## 🔒 Step 6: Security (Production)

### 6.1 Set Up HTTPS with Let's Encrypt

```bash
# Install nginx
sudo apt install nginx -y

# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Configure nginx as reverse proxy
sudo nano /etc/nginx/sites-available/iotnarad
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8050;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/iotnarad /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 6.2 Secure MQTT with TLS

Update `infra/mosquitto/mosquitto.conf`:

```conf
listener 1883 0.0.0.0
allow_anonymous false
password_file /mosquitto/config/passwd

listener 8883 0.0.0.0
cafile /mosquitto/certs/ca.crt
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key
```

Generate certificates and create password file:

```bash
# Create password file
docker exec -it iotnarad_mqtt mosquitto_passwd -c /mosquitto/config/passwd iotdevice

# Restart MQTT
docker-compose restart mqtt
```

---

## 📊 Step 7: InfluxDB Cloud Setup

### 7.1 Create InfluxDB Cloud Account

1. Go to https://www.influxdata.com/products/influxdb-cloud/
2. Sign up for free account
3. Select your region (closest to GCP VM)

### 7.2 Create Bucket

1. Go to **Data** → **Buckets**
2. Click **Create Bucket**
3. Name: `iotnarad-bucket`
4. Retention: 30 days (or as needed)

### 7.3 Generate Token

1. Go to **Data** → **API Tokens**
2. Click **Generate API Token**
3. Select **Read/Write Token**
4. Select your bucket
5. Copy the token

### 7.4 Update .env

```bash
cd ~/IOTNarad_dashboard
nano .env
```

Update:
```env
INFLUXDB_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUXDB_TOKEN=your-copied-token
INFLUXDB_ORG=your-email@example.com
INFLUXDB_BUCKET=iotnarad-bucket
```

Restart app:
```bash
docker-compose restart app
```

---

## 🔄 Step 8: Auto-Start on Boot

### Create systemd service

```bash
sudo nano /etc/systemd/system/iotnarad.service
```

Add:

```ini
[Unit]
Description=IOTNarad Dashboard
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/your-username/IOTNarad_dashboard
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=your-username

[Install]
WantedBy=multi-user.target
```

Enable service:

```bash
sudo systemctl enable iotnarad.service
sudo systemctl start iotnarad.service
```

---

## 📈 Step 9: Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# App only
docker-compose logs -f app

# MQTT only
docker-compose logs -f mqtt
```

### Update Application

```bash
cd ~/IOTNarad_dashboard
git pull
docker-compose down
docker-compose up -d --build
```

### Backup Configurations

```bash
# Backup device configs
tar -czf backup-$(date +%Y%m%d).tar.gz data/configs/

# Copy to local machine
gcloud compute scp iotnarad-vm:~/backup-*.tar.gz . --zone=asia-south1-a
```

### Monitor Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check docker resources
docker stats
```

---

## 🐛 Troubleshooting

### Dashboard not accessible

```bash
# Check if containers are running
docker-compose ps

# Check app logs
docker-compose logs app

# Restart services
docker-compose restart
```

### MQTT connection issues

```bash
# Test MQTT from VM
docker run --rm -it efrecon/mqtt-client sub -h mqtt -t "iotnarad/#" -v

# Check MQTT logs
docker-compose logs mqtt
```

### InfluxDB not storing data

```bash
# Test InfluxDB connection
curl -X GET "https://your-influxdb-url/api/v2/buckets" \
  -H "Authorization: Token your-token"

# Check app logs for errors
docker-compose logs app | grep -i influx
```

### High CPU/Memory usage

```bash
# Check resource usage
docker stats

# Increase VM size if needed
gcloud compute instances set-machine-type iotnarad-vm \
    --machine-type=e2-standard-2 \
    --zone=asia-south1-a
```

---

## 📝 Maintenance Checklist

### Daily
- [ ] Check dashboard accessibility
- [ ] Verify devices are sending data
- [ ] Check MQTT connection status

### Weekly
- [ ] Review logs for errors
- [ ] Check disk space
- [ ] Verify InfluxDB data storage

### Monthly
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`
- [ ] Update Docker images: `docker-compose pull && docker-compose up -d`
- [ ] Backup device configurations
- [ ] Review and clean old data in InfluxDB

---

## 🎯 Production Checklist

- [ ] Change default admin password
- [ ] Set up HTTPS with SSL certificate
- [ ] Enable MQTT authentication
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerts
- [ ] Configure automatic backups
- [ ] Document device IDs and locations
- [ ] Set up logging aggregation
- [ ] Configure auto-start on boot
- [ ] Test disaster recovery

---

## 📞 Support

For issues during deployment:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check README.md for additional info
4. Contact support team

---

**Deployment Complete! 🎉**

Your IOTNarad Dashboard is now running in production on GCP VM.

