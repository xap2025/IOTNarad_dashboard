# 🚀 GCP VM Production Setup Guide

## 📋 Overview

Apko GCP VM par production environment setup karna hai, jahan:
- **Laptop (Local)**: Development (already done ✅)
- **GCP VM (Production)**: Live production environment (setup karna hai)

**Important**: Dono environments alag-alag honge with separate InfluxDB instances and tokens.

---

## 🎯 Prerequisites

1. ✅ GCP VM already created hai
2. ✅ SSH access available hai
3. ✅ Docker aur Docker Compose installed hai (nahi hai toh step 1 mein install karenge)
4. ✅ Git access hai (repository clone karne ke liye)

---

## 📝 Step-by-Step Guide

### **STEP 1: GCP VM pe SSH karo**

```bash
ssh user@your-gcp-vm-ip
# Ya
ssh -i ~/.ssh/your-key.pem user@your-gcp-vm-ip
```

Replace:
- `user` → apna GCP VM username
- `your-gcp-vm-ip` → apka GCP VM IP address

---

### **STEP 2: Docker & Docker Compose install karo (agar nahi hai)**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Docker install
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Current user ko docker group mein add karo
sudo usermod -aG docker $USER

# Logout aur login karo (ya new terminal session)
exit
# Phir wapas SSH karo

# Docker Compose install
sudo apt-get install -y docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

---

### **STEP 3: Project clone/transfer karo**

**Option A: Git se clone (Recommended)**
```bash
cd ~
git clone git@github.com:xap2025/IOTNarad_dashboard.git
# Ya
git clone https://github.com/xap2025/IOTNarad_dashboard.git

cd IOTNarad_dashboard
```

**Option B: Local se copy karo**
```bash
# Local laptop se:
scp -r /path/to/IOTNarad_dashboard user@gcp-vm-ip:~/IOTNarad_dashboard

# GCP VM pe:
cd ~/IOTNarad_dashboard
```

---

### **STEP 4: .env file create karo (Production)**

```bash
cd ~/IOTNarad_dashboard

# .env.example copy karo (agar available hai)
cp .env.example .env

# Ya manually create karo
nano .env
```

**Production .env file contents**:

```env
# ============================================
# GCP VM: PRODUCTION Configuration
# ============================================

# Self-Hosted InfluxDB 2.x - Production
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_ORG=iot-narad-production
INFLUXDB_BUCKET=iot_data_production
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_production_password
INFLUXDB_TOKEN=will_be_generated_after_influxdb_setup

# MQTT - Production
MQTT_BROKER=mqtt
MQTT_PORT=1883

# App Configuration
FLASK_ENV=production
DEBUG=False
PORT=8050

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Admin User (for initial login)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
```

**Important Points**:
- `INFLUXDB_ORG`: Production organization name (kuch bhi rakh sakte ho, example: `iot-narad-production`)
- `INFLUXDB_BUCKET`: Production bucket name (kuch bhi rakh sakte ho, example: `iot_data_production`)
- `INFLUXDB_TOKEN`: Abhi empty rakho, InfluxDB setup ke baad generate karenge
- `INFLUXDB_PASSWORD`: Strong production password set karo
- `SECRET_KEY`: Strong random key generate karo (Python se: `python -c "import secrets; print(secrets.token_hex(32))"`)

---

### **STEP 5: InfluxDB start karo (Production)**

```bash
cd ~/IOTNarad_dashboard

# InfluxDB container start karo
docker compose up -d influxdb

# Wait 10-15 seconds
sleep 15

# Verify InfluxDB is running
docker compose ps
docker compose logs influxdb --tail 20
```

**Expected output**:
```
iotnarad_influxdb  | ts=... msg=Listening service=tcp-listener transport=http addr=:8086 port=8086
```

---

### **STEP 6: InfluxDB UI setup karo (Production)**

#### **6.1: GCP VM Firewall Rule add karo (port 8086 ke liye)**

**Option A: GCP Console se**
1. GCP Console → VPC Network → Firewall Rules
2. "Create Firewall Rule" click karo
3. Name: `allow-influxdb-8086`
4. Target tags: `influxdb` (ya apna VM tag)
5. Source IP ranges: `0.0.0.0/0` (ya specific IP)
6. Protocols and ports: `tcp:8086`
7. Create karo

**Option B: gcloud CLI se**
```bash
gcloud compute firewall-rules create allow-influxdb-8086 \
  --allow tcp:8086 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow InfluxDB access"
```

#### **6.2: Browser se InfluxDB UI access karo**

1. Browser mein open karo:
   ```
   http://your-gcp-vm-ip:8086
   ```

2. **First-Time Setup Form** fill karo:
   ```
   Username: admin
   Password: [Your production password - same as .env mein]
   Confirm Password: [Same password]
   
   Organization Name: iot-narad-production
   Bucket Name: iot_data_production
   ```

3. **Click "Continue"** → Setup complete! ✅

#### **6.3: Production Admin Token generate karo**

1. InfluxDB Dashboard mein:
   - **"Data"** (left sidebar) → **"API Tokens"**
   - **"+ Generate API Token"** → **"All Access Token"**
   - **Name**: `iotnarad-production-admin-token`
   - **Click "Generate Token"**
   - **COPY THE TOKEN** (sirf ek baar dikhta hai!)

#### **6.4: .env file mein token add karo**

```bash
nano ~/IOTNarad_dashboard/.env
```

Update this line:
```env
INFLUXDB_TOKEN=your_production_token_here_paste_kiya_hua_token
```

Save karo (Ctrl+X, Y, Enter)

---

### **STEP 7: App start karo (Production)**

```bash
cd ~/IOTNarad_dashboard

# App build aur start karo
docker compose up -d --build

# Wait for app to start
sleep 10

# Check logs
docker compose logs -f app
```

**Expected logs**:
```
✅ Connected to InfluxDB: http://influxdb:8086
✅ User Service connected to InfluxDB: http://influxdb:8086
   Database: Self-Hosted InfluxDB 2.x
   Bucket: iot_data_production, Org: iot-narad-production
```

---

### **STEP 8: GCP VM Firewall Rule add karo (port 8050 - App)**

**Option A: GCP Console se**
1. GCP Console → VPC Network → Firewall Rules
2. "Create Firewall Rule"
3. Name: `allow-app-8050`
4. Target tags: apka VM tag
5. Source IP ranges: `0.0.0.0/0` (ya specific IP)
6. Protocols and ports: `tcp:8050`
7. Create

**Option B: gcloud CLI se**
```bash
gcloud compute firewall-rules create allow-app-8050 \
  --allow tcp:8050 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow IOTNarad Dashboard access"
```

---

### **STEP 9: App access karo**

Browser mein open karo:
```
http://your-gcp-vm-ip:8050
```

✅ App should load successfully!

---

### **STEP 10: Verify Production Setup**

#### **10.1: All containers running**
```bash
docker compose ps
```

**Expected output**:
```
NAME                  STATUS
iotnarad_app          Up
iotnarad_mqtt         Up
iotnarad_influxdb     Up
```

#### **10.2: Check logs**
```bash
docker compose logs app --tail 50
```

Look for:
- ✅ Connected to InfluxDB: `http://influxdb:8086`
- ✅ Bucket: `iot_data_production`
- ✅ Org: `iot-narad-production`
- ✅ Database: Self-Hosted InfluxDB 2.x

#### **10.3: Test login**
1. Browser: `http://your-gcp-vm-ip:8050`
2. Login karo with existing credentials (ya create new user)
3. Dashboard should load

#### **10.4: Test InfluxDB**
1. Browser: `http://your-gcp-vm-ip:8086`
2. Login karo with production credentials
3. Data Explorer mein check karo - data save ho raha hai

---

## 🔒 Security Best Practices

### **1. Firewall Rules (Recommended)**
- Port 8086 (InfluxDB) ko sirf specific IPs se allow karo (production team)
- Port 8050 (App) ko sirf trusted IPs se allow karo

**Example** (specific IPs only):
```bash
gcloud compute firewall-rules create allow-app-8050 \
  --allow tcp:8050 \
  --source-ranges 203.0.113.0/24 \
  --description "Allow IOTNarad Dashboard from office IPs"
```

### **2. Strong Passwords**
- Production InfluxDB password: 16+ characters, mixed case, numbers, symbols
- Admin password: Strong password set karo

### **3. SSL/TLS (Optional but Recommended)**
- Nginx reverse proxy setup karo with SSL certificate
- Let's Encrypt use karo free SSL ke liye

### **4. Backup Strategy**
- InfluxDB data backup regularly
- Docker volumes backup karo

---

## 📊 Comparison: Local vs Production

| Feature | Local (Laptop) | Production (GCP VM) |
|---------|----------------|---------------------|
| **InfluxDB URL** | `http://influxdb:8086` | `http://influxdb:8086` |
| **Org** | `iot-narad-local` | `iot-narad-production` |
| **Bucket** | `iot_data_local` | `iot_data_production` |
| **Token** | `local_token_abc123...` | `production_token_xyz789...` |
| **Data** | Development data | Production data |
| **Access** | `localhost:8050` | `gcp-vm-ip:8050` |

---

## 🛠️ Troubleshooting

### **Problem 1: Cannot access InfluxDB UI (`http://gcp-vm-ip:8086`)**

**Solutions**:
1. Check firewall rule: `gcloud compute firewall-rules list | grep 8086`
2. Check VM network tags: VM should have correct network tags
3. Check InfluxDB logs: `docker compose logs influxdb`
4. Verify InfluxDB is running: `docker compose ps`

---

### **Problem 2: App cannot connect to InfluxDB**

**Solutions**:
1. Check `.env` file: `cat .env | grep INFLUXDB`
2. Verify token is correct
3. Check InfluxDB is running: `docker compose ps influxdb`
4. Check app logs: `docker compose logs app | grep InfluxDB`
5. Recreate container: `docker compose up -d --force-recreate app`

---

### **Problem 3: Port already in use**

**Solutions**:
```bash
# Check which process is using the port
sudo lsof -i :8050
sudo lsof -i :8086

# Kill the process (if needed)
sudo kill -9 <PID>
```

---

### **Problem 4: Docker permission denied**

**Solutions**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
exit
# SSH again

# Or use sudo (not recommended)
sudo docker compose up -d
```

---

## 🔄 Production Deployment Commands

### **Daily Operations**

```bash
# App restart
docker compose restart app

# View logs
docker compose logs -f app

# Stop all services
docker compose down

# Start all services
docker compose up -d

# Rebuild and restart (after code changes)
docker compose up -d --build
```

---

## 📝 Quick Reference

### **Important Files Location**
- Project: `~/IOTNarad_dashboard/`
- Config: `~/IOTNarad_dashboard/.env`
- Logs: `docker compose logs -f`

### **Important URLs**
- App: `http://your-gcp-vm-ip:8050`
- InfluxDB UI: `http://your-gcp-vm-ip:8086`

### **Important Commands**
```bash
# Check status
docker compose ps

# View logs
docker compose logs -f app

# Restart app
docker compose restart app

# Update code (after git pull)
docker compose up -d --build
```

---

## ✅ Success Checklist

- [ ] SSH into GCP VM successful
- [ ] Docker and Docker Compose installed
- [ ] Project cloned/copied to GCP VM
- [ ] `.env` file created with production values
- [ ] InfluxDB container started
- [ ] InfluxDB UI setup completed (production org/bucket created)
- [ ] Production admin token generated
- [ ] Token added to `.env` file
- [ ] Firewall rules added (ports 8050 and 8086)
- [ ] App container started successfully
- [ ] App accessible via `http://gcp-vm-ip:8050`
- [ ] Login successful
- [ ] InfluxDB data saving correctly
- [ ] All services running (`docker compose ps`)

---

## 🎉 Setup Complete!

Apka production environment ready hai! Ab:
- ✅ Local (Laptop): Development
- ✅ GCP VM: Production

Dono environments completely separate hain with their own InfluxDB instances and data.

---

## 📞 Next Steps

1. **Create first production user** via UI
2. **Register first production device**
3. **Test complete workflow** (device config save, MQTT, etc.)
4. **Setup automated backups** (InfluxDB data)
5. **Monitor logs** regularly

---

**Questions?** Check logs: `docker compose logs -f`

