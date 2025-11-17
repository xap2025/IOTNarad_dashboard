# 🚀 Migration Guide: Cloud Serverless v3 → Self-Hosted InfluxDB 2.x

यह guide आपको step-by-step बताएगा कि InfluxDB Cloud Serverless v3 से Self-Hosted InfluxDB 2.x में कैसे migrate करें।

---

## 📋 Pre-Migration Checklist

### Current Setup:
- ✅ Cloud Serverless v3: `https://us-east-1-1.aws.cloud2.influxdata.com`
- ✅ Docker-compose.yml में `influxdb:2.7` already configured
- ✅ Data exists in Cloud

### Target Setup:
- 🎯 Self-Hosted InfluxDB 2.7 (localhost:8086)
- 🎯 DELETE API ✅ Enabled
- 🎯 Flux Queries ✅ Supported
- 🎯 No Limitations ✅

---

## 🔄 Migration Steps

### **STEP 1: Backup Current Data (Optional but Recommended)**

अगर आप अपना existing data preserve करना चाहते हैं:

#### Option A: Export Specific Measurements (Recommended)

```powershell
# PowerShell: Export Device_Config_Analog data
$BUCKET = "iot_data_gcp"
$ORG = "iot-narad-gcp"
$TOKEN = "T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA=="
$URL = "https://us-east-1-1.aws.cloud2.influxdata.com"

# Export using InfluxDB CLI (if installed) or Python script
# This exports to CSV/JSON format for later import
```

#### Option B: Start Fresh (Simpler)

अगर आप existing data की जरूरत नहीं है:
- Fresh start करें
- Existing configs फिर से save करेंगे

**Recommendation:** अगर data important नहीं है, तो **Option B (Fresh Start)** choose करें - यह simpler है।

---

### **STEP 2: Stop Current Application**

```powershell
# Stop all containers
docker compose down

# Verify containers are stopped
docker ps | Select-String "influxdb|app"
```

---

### **STEP 3: Update .env File**

आपका `.env` file update करें:

#### Current .env (Cloud Serverless v3):
```env
INFLUXDB_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUXDB_TOKEN=T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA==
INFLUXDB_ORG=iot-narad-gcp
INFLUXDB_BUCKET=iot_data_gcp
```

#### New .env (Self-Hosted 2.x):
```env
# Self-Hosted InfluxDB 2.x Configuration
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_ORG=iot-narad-gcp
INFLUXDB_BUCKET=iot_data_gcp

# These will be set by docker-compose (first-time setup creates token)
# But you can set defaults here
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_password_here
INFLUXDB_TOKEN=will_be_generated_on_first_start
```

**Important Notes:**
1. `INFLUXDB_URL`: Cloud URL से `http://influxdb:8086` change करें
   - `influxdb` = docker-compose service name
   - `8086` = default InfluxDB port
2. `INFLUXDB_TOKEN`: पहली बार start करने पर automatically generate होगा
3. `INFLUXDB_ORG` और `INFLUXDB_BUCKET`: Same रखें (अगर data migrate कर रहे हैं)

---

### **STEP 4: Configure Docker Compose (Already Done ✅)**

आपका `docker-compose.yml` already correct है! Verify करें:

```yaml
influxdb:
  image: influxdb:2.7                    # ✅ Correct version
  container_name: iotnarad_influxdb      # ✅ Container name
  ports:
    - "8086:8086"                        # ✅ Port mapping
  environment:
    - DOCKER_INFLUXDB_INIT_MODE=setup    # ✅ First-time setup
    - DOCKER_INFLUXDB_INIT_USERNAME=${INFLUXDB_USERNAME}
    - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUXDB_PASSWORD}
    - DOCKER_INFLUXDB_INIT_ORG=${INFLUXDB_ORG}
    - DOCKER_INFLUXDB_INIT_BUCKET=${INFLUXDB_BUCKET}
    - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}
  volumes:
    - influxdb-data:/var/lib/influxdb2   # ✅ Data persistence
```

**No changes needed** - यह already correct है!

---

### **STEP 5: Start Self-Hosted InfluxDB**

#### 5.1: Start InfluxDB Container Only (First Time)

```powershell
# Start only InfluxDB container
docker compose up -d influxdb

# Check logs to see initialization
docker compose logs influxdb -f
```

**Expected Output:**
```
influxdb  | ts=2025-11-17T... level=info msg="InfluxDB starting"
influxdb  | ts=2025-11-17T... level=info msg="InfluxDB started"
influxdb  | ts=2025-11-17T... level=info msg="Setup complete" org=iot-narad-gcp bucket=iot_data_gcp
```

#### 5.2: Wait for Initialization

InfluxDB पहली बार start होने पर:
1. Setup mode run होता है
2. Admin user create होता है
3. Organization और Bucket create होते हैं
4. Admin token generate होता है

**Wait for:** `Setup complete` message in logs

---

### **STEP 6: Get Admin Token (After First Start)**

#### Option A: From Docker Logs

```powershell
# Get admin token from logs
docker compose logs influxdb | Select-String -Pattern "token|Token" -Context 2
```

Look for line like:
```
token: T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA==
```

#### Option B: From InfluxDB UI

1. Open browser: `http://localhost:8086`
2. Login with:
   - Username: `admin` (from INFLUXDB_USERNAME)
   - Password: जो `.env` में set किया
3. Go to: **Load Data** → **API Tokens**
4. Copy admin token

#### Option C: Generate New Token

```powershell
# Generate new token via InfluxDB CLI
docker exec -i iotnarad_influxdb influx auth create \
    --org iot-narad-gcp \
    --all-access \
    --description "Dashboard Admin Token"
```

---

### **STEP 7: Update .env with Generated Token**

`.env` file में token update करें:

```env
# Self-Hosted InfluxDB 2.x Configuration
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_ORG=iot-narad-gcp
INFLUXDB_BUCKET=iot_data_gcp
INFLUXDB_TOKEN=your_generated_token_here
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_password_here
```

**Important:**
- `INFLUXDB_URL`: `http://influxdb:8086` (docker service name)
- `INFLUXDB_TOKEN`: Step 6 में जो token generate हुआ, वही use करें

---

### **STEP 8: Test Connection**

```powershell
# Test InfluxDB connection
docker exec -i iotnarad_influxdb influx ping

# List organizations
docker exec -i iotnarad_influxdb influx org list

# List buckets
docker exec -i iotnarad_influxdb influx bucket list

# Verify token works
docker exec -i iotnarad_influxdb influx query 'buckets()'
```

**Expected Output:**
```
ID                  Name            Retention       Shard group duration    Organization ID
--                  ----            --------        --------------------    ---------------
1234567890abcdef    iot_data_gcp    0s              168h0m0s                9876543210fedcba
```

---

### **STEP 9: Start Full Application**

```powershell
# Start all containers (app + influxdb + mqtt)
docker compose up -d

# Check all containers are running
docker ps

# Check app logs for connection success
docker compose logs app --tail 20 | Select-String -Pattern "InfluxDB|connected|ERROR"
```

**Expected Output:**
```
iotnarad_app  | ✅ Device Config DB Service connected to InfluxDB: http://influxdb:8086
iotnarad_app  |    Bucket: iot_data_gcp, Org: iot-narad-gcp
```

---

### **STEP 10: Verify DELETE API Works**

```powershell
# Test DELETE API (This should work now!)
$BUCKET = "iot_data_gcp"
$ORG = "iot-narad-gcp"
$TOKEN = "your_token_from_step_6"

docker exec -i iotnarad_influxdb influx delete `
    --org "$ORG" `
    --bucket "$BUCKET" `
    --token "$TOKEN" `
    --start 1970-01-01T00:00:00Z `
    --stop 2025-01-01T00:00:00Z `
    --predicate '_measurement="test_measurement"'
```

**Expected Output:**
```
(No error - DELETE successful!)
```

---

### **STEP 11: Verify Flux Queries Work**

```powershell
# Test Flux query
docker exec -i iotnarad_influxdb influx query `
    --org "$ORG" `
    --token "$TOKEN" `
    'from(bucket: "iot_data_gcp") |> range(start: -1h) |> limit(n: 5)'
```

**Expected Output:**
```
(Query results - Flux is working!)
```

---

### **STEP 12: Test Your Application**

1. **Open Dashboard**: `http://localhost:8050/dashboard`
2. **Navigate to**: Devices → Analog
3. **Select Device**: Dropdown से device select करें
4. **Fill Configuration**: Analog settings fill करें
5. **Click Save**: "Save Configuration" button click करें
6. **Verify**: 
   - Success message दिखना चाहिए
   - Data InfluxDB में save होना चाहिए
   - No errors in logs

---

### **STEP 13: Migrate Data (Optional - If Needed)**

अगर आप existing Cloud data migrate करना चाहते हैं:

#### Step 13.1: Export from Cloud

```powershell
# Export data from Cloud (if you need it)
# Use InfluxDB CLI or Python script to export
```

#### Step 13.2: Import to Self-Hosted

```powershell
# Import data to self-hosted
docker exec -i iotnarad_influxdb influx write `
    --org "$ORG" `
    --bucket "$BUCKET" `
    --token "$TOKEN" `
    --file /path/to/exported_data.csv
```

**Note:** अगर data critical नहीं है, तो skip करें - fresh start simpler है।

---

## 🔍 Verification Checklist

Migration successful है या नहीं, यह verify करें:

### ✅ Connection Check
- [ ] App logs में: `✅ Connected to InfluxDB: http://influxdb:8086`
- [ ] No connection errors
- [ ] InfluxDB UI accessible: `http://localhost:8086`

### ✅ Features Check
- [ ] DELETE API works (Step 10)
- [ ] Flux queries work (Step 11)
- [ ] Write data works (Save Configuration)
- [ ] Read data works (Load from Device)

### ✅ Application Check
- [ ] Dashboard loads without errors
- [ ] Device selector works
- [ ] Save Configuration works
- [ ] Data appears in InfluxDB UI

---

## 🎯 What Changed

### Before (Cloud Serverless v3):
```env
INFLUXDB_URL=https://us-east-1-1.aws.cloud2.influxdata.com
```
- ❌ DELETE API disabled
- ❌ Flux not supported
- ❌ SQL read-only

### After (Self-Hosted 2.x):
```env
INFLUXDB_URL=http://influxdb:8086
```
- ✅ DELETE API enabled
- ✅ Flux supported
- ✅ Full feature set
- ✅ No limitations

---

## 🆘 Troubleshooting

### Issue 1: Connection Failed

**Error:** `Failed to connect to InfluxDB`

**Solution:**
```powershell
# Check InfluxDB container is running
docker ps | Select-String "influxdb"

# Check InfluxDB logs
docker compose logs influxdb --tail 50

# Restart InfluxDB
docker compose restart influxdb
```

### Issue 2: Token Not Working

**Error:** `Unauthorized` or `Invalid token`

**Solution:**
```powershell
# Generate new token
docker exec -i iotnarad_influxdb influx auth create `
    --org iot-narad-gcp `
    --all-access

# Update .env with new token
# Restart app
docker compose restart app
```

### Issue 3: Bucket Not Found

**Error:** `Bucket not found`

**Solution:**
```powershell
# Create bucket manually
docker exec -i iotnarad_influxdb influx bucket create `
    --org iot-narad-gcp `
    --name iot_data_gcp `
    --retention 0
```

### Issue 4: Port Already in Use

**Error:** `Port 8086 already in use`

**Solution:**
```powershell
# Find process using port 8086
netstat -ano | findstr :8086

# Stop conflicting service or change port in docker-compose.yml
```

---

## 📊 Comparison: Before vs After

| Feature | Cloud Serverless v3 | Self-Hosted 2.x |
|---------|---------------------|-----------------|
| DELETE API | ❌ No | ✅ Yes |
| Flux Queries | ❌ No | ✅ Yes |
| SQL Queries | ✅ Read-only | ✅ Full |
| Cost | Free tier | Free (self-hosted) |
| Hosting | Managed | Self-managed |
| Storage | Limited | Unlimited |
| Performance | Shared | Dedicated |
| Control | Limited | Full |
| Backup | Automatic | Manual |

---

## 🎉 Benefits After Migration

1. ✅ **DELETE API Enabled**: Configs delete कर सकते हैं
2. ✅ **Flux Queries**: Full Flux support
3. ✅ **No Limitations**: Storage, queries, features
4. ✅ **Full Control**: अपनी needs के according configure कर सकते हैं
5. ✅ **Free**: Self-hosted = no cloud costs
6. ✅ **Better for Development**: Local testing easy

---

## 📝 Next Steps After Migration

1. **Test DELETE API**: Confirm it works
2. **Test Flux Queries**: Verify queries run
3. **Update Code Comments**: Remove "Serverless v3" notes
4. **Setup Backup**: Self-hosted = manual backup needed
5. **Monitor Storage**: Track disk usage

---

## 🔐 Security Notes

1. **Password**: Strong password use करें `.env` में
2. **Token**: Secure token storage
3. **Network**: InfluxDB port 8086 को public expose न करें (internal Docker network OK)
4. **Backup**: Regular backups schedule करें

---

## ✅ Summary

### Quick Migration Steps:
1. ✅ Stop containers: `docker compose down`
2. ✅ Update `.env`: Change `INFLUXDB_URL` to `http://influxdb:8086`
3. ✅ Start InfluxDB: `docker compose up -d influxdb`
4. ✅ Get token: Check logs or UI
5. ✅ Update `.env`: Add generated token
6. ✅ Start app: `docker compose up -d`
7. ✅ Test: Verify DELETE API and Flux work

---

**Ready to migrate? Follow steps 1-13 above!** 🚀

---

**Document Version**: 1.0  
**Created**: 2025-11-17  
**Status**: ✅ Ready for Migration

