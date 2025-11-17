# ⚡ Quick Migration Steps (Summary)

## 🎯 Goal: Switch from Cloud Serverless v3 to Self-Hosted 2.x

---

## 📝 Step-by-Step Commands

### Step 1: Stop Everything
```powershell
docker compose down
```

### Step 2: Backup Current .env (Optional)
```powershell
Copy-Item .env .env.backup
```

### Step 3: Update .env File

Open `.env` and change:

```env
# OLD (Cloud Serverless v3)
INFLUXDB_URL=https://us-east-1-1.aws.cloud2.influxdata.com

# NEW (Self-Hosted 2.x)
INFLUXDB_URL=http://influxdb:8086
```

Also add/verify these (if not present):
```env
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=YourSecurePassword123!
```

### Step 4: Start InfluxDB Only (First Time)
```powershell
docker compose up -d influxdb
```

### Step 5: Wait & Check Logs
```powershell
docker compose logs influxdb -f
```

**Wait for:** `Setup complete` message (usually 10-30 seconds)

### Step 6: Get Admin Token

```powershell
# Method 1: From logs
docker compose logs influxdb | Select-String -Pattern "token|Token" -Context 1

# Method 2: From UI (http://localhost:8086)
# Login → Load Data → API Tokens → Copy token
```

### Step 7: Update .env with Token

Add/update token in `.env`:
```env
INFLUXDB_TOKEN=<paste_token_from_step_6>
```

### Step 8: Start All Services
```powershell
docker compose up -d
```

### Step 9: Verify Connection
```powershell
# Check app logs
docker compose logs app --tail 30 | Select-String -Pattern "InfluxDB|connected"

# Should see: "✅ Connected to InfluxDB: http://influxdb:8086"
```

### Step 10: Test DELETE API (Verify It Works!)
```powershell
docker exec -i iotnarad_influxdb influx delete `
    --org "iot-narad-gcp" `
    --bucket "iot_data_gcp" `
    --token "<your_token>" `
    --start 1970-01-01T00:00:00Z `
    --stop 2025-01-01T00:00:00Z `
    --predicate '_measurement="test_measurement"'
```

**Expected:** No error = DELETE API works! ✅

---

## ✅ Verification

1. ✅ Open: `http://localhost:8086` - InfluxDB UI should load
2. ✅ Open: `http://localhost:8050/dashboard` - App should load
3. ✅ Test: Save Configuration - Should work
4. ✅ Test: DELETE API - Should work (no errors)

---

## 🆘 Quick Fixes

### If Connection Fails:
```powershell
# Restart InfluxDB
docker compose restart influxdb

# Check logs
docker compose logs influxdb --tail 50
```

### If Token Not Working:
```powershell
# Generate new token
docker exec -i iotnarad_influxdb influx auth create `
    --org iot-narad-gcp `
    --all-access `
    --description "Dashboard Token"
```

---

## 🎉 That's It!

After these steps:
- ✅ Self-Hosted InfluxDB 2.x running
- ✅ DELETE API enabled
- ✅ Flux queries working
- ✅ No limitations

