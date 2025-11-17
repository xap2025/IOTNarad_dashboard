# Setup A: Local Development + Production Separation

## 🖥️ LAPTOP (Local Development) - InfluxDB Setup

### **STEP 1: Create Username & Password in InfluxDB UI**

#### **Option A: First-Time Setup via UI (If setup page appears)**

1. **Open Browser**: Go to `http://localhost:8086`

2. **Fill First-Time Setup Form**:
   ```
   Username: admin (or your preferred username)
   Password: [Create a strong password]
   Confirm Password: [Same password]
   Organization Name: iot-narad-local (or your org name)
   Bucket Name: iot_data_local (or your bucket name)
   ```

3. **Click "Continue"** → Setup complete!

4. **After Setup**:
   - You'll see the InfluxDB dashboard
   - Click on **"Data"** → **"API Tokens"** (left sidebar)
   - Click **"Generate API Token"** → **"All Access Token"**
   - Give it a name: `iotnarad-local-admin-token`
   - **Copy the token** (shown only once!)

---

#### **Option B: Reset and Start Fresh (If login fails)**

**⚠️ WARNING**: This will delete all existing InfluxDB data!

1. **Stop InfluxDB Container**:
   ```powershell
   docker compose stop influxdb
   ```

2. **Remove InfluxDB Volume** (delete all data):
   ```powershell
   docker volume rm iotnarad_dashboard_influxdb-data
   ```

3. **Remove .env Variables** (temporary):
   - Open `.env` file
   - Comment out or remove:
     ```env
     # INFLUXDB_USERNAME=admin
     # INFLUXDB_PASSWORD=your_password
     # INFLUXDB_TOKEN=old_token
     ```

4. **Start InfluxDB Fresh**:
   ```powershell
   docker compose up -d influxdb
   ```

5. **Wait 10 seconds**, then open: `http://localhost:8086`

6. **Complete Setup Form** (Option A, Step 2-4)

---

#### **Option C: Use Existing Credentials (If you know them)**

If you already have username/password:

1. **Check your `.env` file**:
   ```powershell
   cat .env | Select-String "INFLUXDB"
   ```

2. **Or check docker logs**:
   ```powershell
   docker compose logs influxdb | Select-String "Username\|Password\|Token"
   ```

3. **Login with those credentials**

---

### **STEP 2: Generate Admin Token**

After successful login:

1. **Go to**: `http://localhost:8086`
2. **Click**: "Data" (left sidebar) → "API Tokens"
3. **Click**: "+ Generate API Token" → "All Access Token"
4. **Enter Name**: `iotnarad-local-admin-token`
5. **Click**: "Generate Token"
6. **COPY THE TOKEN** (shown only once! Example: `abc123xyz...`)

---

### **STEP 3: Update .env for Local Development**

Create or update `.env` file:

```env
# ============================================
# LAPTOP: Local Development Configuration
# ============================================

# InfluxDB - Local Development Instance
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_ORG=iot-narad-local
INFLUXDB_BUCKET=iot_data_local
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_local_password
INFLUXDB_TOKEN=abc123xyz...your_generated_token_here

# MQTT - Local (if using)
MQTT_BROKER=mqtt
MQTT_PORT=1883

# App Configuration
FLASK_ENV=development
DEBUG=True
```

**Important**:
- Replace `your_secure_local_password` with your actual password
- Replace `abc123xyz...` with your generated token
- `INFLUXDB_ORG` and `INFLUXDB_BUCKET` should match what you created in UI

---

### **STEP 4: Verify Local Setup**

1. **Restart app**:
   ```powershell
   docker compose restart app
   ```

2. **Check logs**:
   ```powershell
   docker compose logs -f app
   ```

3. **Look for**: `Connected to InfluxDB successfully` ✅

4. **Test**: Open app → Devices tab → Try saving configuration

---

## ☁️ GCP VM (Production) - InfluxDB Setup

### **STEP 1: SSH into GCP VM**

```bash
ssh user@your-gcp-vm-ip
```

---

### **STEP 2: Setup InfluxDB on GCP VM**

1. **Clone/Copy your project** (if not already done):
   ```bash
   cd ~/IOTNarad_dashboard
   ```

2. **Create `.env` file for Production**:
   ```bash
   nano .env
   ```

3. **Add Production Configuration**:
   ```env
   # ============================================
   # GCP VM: Production Configuration
   # ============================================

   # InfluxDB - Production Instance (Separate from Laptop)
   INFLUXDB_URL=http://influxdb:8086
   INFLUXDB_ORG=iot-narad-production
   INFLUXDB_BUCKET=iot_data_production
   INFLUXDB_USERNAME=admin
   INFLUXDB_PASSWORD=your_secure_production_password
   INFLUXDB_TOKEN=will_be_generated_on_first_start

   # MQTT - Production
   MQTT_BROKER=mqtt
   MQTT_PORT=1883

   # App Configuration
   FLASK_ENV=production
   DEBUG=False
   ```

4. **Start InfluxDB**:
   ```bash
   docker compose up -d influxdb
   ```

5. **Wait 10 seconds**, then open: `http://your-gcp-vm-ip:8086`

---

### **STEP 3: Complete Production Setup**

1. **Open**: `http://your-gcp-vm-ip:8086` in browser

2. **Fill Setup Form**:
   ```
   Username: admin (or production username)
   Password: [Strong production password]
   Confirm Password: [Same password]
   Organization Name: iot-narad-production
   Bucket Name: iot_data_production
   ```

3. **Generate Production Token**:
   - Data → API Tokens → Generate All Access Token
   - Name: `iotnarad-production-admin-token`
   - **Copy the token**

4. **Update `.env` with production token**:
   ```bash
   nano .env
   ```
   ```env
   INFLUXDB_TOKEN=xyz789abc...your_production_token_here
   ```

---

### **STEP 4: Start Production App**

```bash
docker compose up -d
```

**Verify**:
```bash
docker compose logs -f app
```

---

## 📊 Summary: Setup A Configuration

### **Laptop (.env)**:
```env
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_ORG=iot-narad-local
INFLUXDB_BUCKET=iot_data_local
INFLUXDB_TOKEN=token_local_abc123...  # Local token
```

### **GCP VM (.env)**:
```env
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_ORG=iot-narad-production
INFLUXDB_BUCKET=iot_data_production
INFLUXDB_TOKEN=token_prod_xyz789...  # Production token (different!)
```

---

## ✅ Key Points:

1. **Different Instances**: Laptop and GCP VM run separate InfluxDB containers
2. **Different Tokens**: Each instance generates its own token
3. **Different Data**: Local development data ≠ Production data
4. **Isolation**: Test freely on laptop without affecting production

---

## 🔧 Troubleshooting

### **Problem**: "Could not sign in" error

**Solution**:
1. Check if InfluxDB container is running: `docker compose ps`
2. Check logs: `docker compose logs influxdb`
3. Try reset (Option B above)

### **Problem**: Token not working

**Solution**:
1. Generate new token via UI
2. Update `.env` with new token
3. Restart app: `docker compose restart app`

### **Problem**: Cannot access GCP VM InfluxDB from browser

**Solution**:
1. Check firewall rules (allow port 8086)
2. Check GCP VM security group
3. Use SSH tunnel: `ssh -L 8086:localhost:8086 user@vm-ip`

---

## 🚀 Next Steps:

1. ✅ Complete local InfluxDB setup (UI)
2. ✅ Generate local admin token
3. ✅ Update local `.env` file
4. ✅ Test local app
5. ⏭️ Setup GCP VM (when ready)

---

**Need help?** Check logs: `docker compose logs -f influxdb app`

