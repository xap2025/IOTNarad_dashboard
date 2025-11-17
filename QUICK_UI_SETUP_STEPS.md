# Quick Steps: Create Username/Password via InfluxDB UI

## 🎯 Current Situation:
- InfluxDB is running but login fails
- You want to create username/password via UI (not docker-compose env vars)

## ✅ Solution: Reset & Start Fresh with UI Setup

---

## 📋 STEP-BY-STEP INSTRUCTIONS:

### **STEP 1: Stop & Reset InfluxDB**

```powershell
# Stop InfluxDB
docker compose stop influxdb

# Delete all existing data (fresh start)
docker volume rm iotnarad_dashboard_influxdb-data
```

**OR run the reset script:**
```powershell
.\reset_influxdb.ps1
```

---

### **STEP 2: Start InfluxDB (Fresh)**

```powershell
docker compose up -d influxdb
```

**Wait 10-15 seconds** for InfluxDB to start.

---

### **STEP 3: Open Browser & Complete Setup**

1. **Open**: `http://localhost:8086`

2. **You should see**: "Get Started" or "Welcome to InfluxDB" setup page

3. **Fill the form**:
   ```
   Username: admin
   Password: [Create your secure password]
   Confirm Password: [Same password]
   
   Organization Name: iot-narad-local
   Bucket Name: iot_data_local
   ```

4. **Click**: "Continue" or "Get Started"

5. **After setup**: You'll see the InfluxDB dashboard ✅

---

### **STEP 4: Generate Admin Token**

1. **In InfluxDB Dashboard**:
   - Click **"Data"** (left sidebar)
   - Click **"API Tokens"**
   - Click **"+ Generate API Token"**
   - Select **"All Access Token"**

2. **Enter Name**:
   ```
   iotnarad-local-admin-token
   ```

3. **Click**: "Generate Token"

4. **IMPORTANT**: Copy the token immediately (shown only once!)
   ```
   Example: abc123xyz789...
   ```

---

### **STEP 5: Update .env File**

Create or update `.env` file in your project root:

```env
# ============================================
# LAPTOP: Local Development Configuration
# ============================================

# InfluxDB - Local Development
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_ORG=iot-narad-local
INFLUXDB_BUCKET=iot_data_local
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_password_here
INFLUXDB_TOKEN=abc123xyz789...your_token_here

# MQTT (if using)
MQTT_BROKER=mqtt
MQTT_PORT=1883
```

**Replace**:
- `your_password_here` → Your actual password
- `abc123xyz789...` → Your generated token

---

### **STEP 6: Restart App**

```powershell
docker compose restart app
```

---

### **STEP 7: Verify**

1. **Check logs**:
   ```powershell
   docker compose logs -f app
   ```

2. **Look for**: `Connected to InfluxDB successfully` ✅

3. **Test**: Open app → Devices tab → Try saving configuration

---

## ✅ Success Checklist:

- [ ] InfluxDB resetted (old data deleted)
- [ ] InfluxDB started fresh
- [ ] UI setup completed (username/password created)
- [ ] Admin token generated
- [ ] Token copied and saved
- [ ] `.env` file updated with token
- [ ] App restarted
- [ ] App connected to InfluxDB successfully

---

## 🔧 Troubleshooting:

### **Problem**: Still see login page (not setup page)

**Solution**:
- Check if volume was deleted: `docker volume ls | Select-String influxdb`
- If volume still exists, delete it: `docker volume rm iotnarad_dashboard_influxdb-data`
- Restart InfluxDB: `docker compose restart influxdb`

### **Problem**: "Get Started" page not appearing

**Solution**:
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito mode
- Check InfluxDB logs: `docker compose logs influxdb`

### **Problem**: Token not working after adding to .env

**Solution**:
- Verify token is correct (no extra spaces)
- Restart app: `docker compose restart app`
- Check logs: `docker compose logs app | Select-String InfluxDB`

---

## 📝 Next Steps (After Local Setup):

Once local setup is complete, you'll repeat similar steps on **GCP VM**:

1. Setup InfluxDB on GCP VM
2. Create production username/password via UI
3. Generate production token
4. Update GCP VM `.env` with production token
5. Both will have **different tokens** (Setup A: Local + Production separation)

---

**Ready?** Start with STEP 1! 🚀

