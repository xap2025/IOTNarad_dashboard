# 🔧 Troubleshoot InfluxDB UI Access on GCP VM

## 🎯 Problem: `http://34.131.186.225:8086/` page nahi khul raha

---

## ✅ Step-by-Step Troubleshooting

### **STEP 1: Check InfluxDB Container Status**

GCP VM pe SSH karo aur check karo:

```bash
# SSH into GCP VM
ssh user@34.131.186.225

# Check if InfluxDB is running
docker compose ps

# Ya individually check
docker ps | grep influxdb
```

**Expected Output**:
```
NAME                  STATUS
iotnarad_influxdb     Up X minutes
```

**Agar container nahi chal raha**:
```bash
cd ~/IOTNarad_dashboard
docker compose up -d influxdb

# Wait 15 seconds
sleep 15

# Check logs
docker compose logs influxdb --tail 20
```

---

### **STEP 2: Check InfluxDB Logs**

```bash
docker compose logs influxdb --tail 30
```

**Look for**:
```
ts=... msg=Listening service=tcp-listener transport=http addr=:8086 port=8086
```

**Agar yeh dikh raha hai** → InfluxDB running hai ✅

**Agar error dikh raha hai** → Next steps follow karo

---

### **STEP 3: Check if InfluxDB is Listening on Port 8086**

GCP VM pe check karo:

```bash
# Check if port 8086 is listening
sudo netstat -tlnp | grep 8086

# Ya
sudo ss -tlnp | grep 8086

# Ya
sudo lsof -i :8086
```

**Expected Output**:
```
tcp  0  0  0.0.0.0:8086  0.0.0.0:*  LISTEN  <PID>/influxd
```

**Agar `0.0.0.0:8086` dikh raha hai** → Port open hai ✅

**Agar `127.0.0.1:8086` dikh raha hai** → Sirf localhost se accessible hai ❌

---

### **STEP 4: Check GCP VM Firewall Rules**

#### **Option A: GCP Console se Check**

1. GCP Console → **VPC Network** → **Firewall Rules**
2. Search for rules containing `8086` or `influxdb`
3. Check if rule exists and allows traffic from `0.0.0.0/0`

#### **Option B: gcloud CLI se Check**

```bash
gcloud compute firewall-rules list | grep 8086
```

**Agar koi rule nahi hai** → Create karo (Step 5)

---

### **STEP 5: Create Firewall Rule for Port 8086**

#### **Option A: GCP Console se**

1. GCP Console → **VPC Network** → **Firewall Rules**
2. Click **"Create Firewall Rule"**
3. Fill form:
   - **Name**: `allow-influxdb-8086`
   - **Description**: `Allow InfluxDB access on port 8086`
   - **Priority**: `1000` (default)
   - **Direction**: `Ingress`
   - **Action on match**: `Allow`
   - **Targets**: `All instances in the network`
   - **Source IP ranges**: `0.0.0.0/0` (ya specific IPs)
   - **Protocols and ports**: 
     - ✅ **TCP** 
     - **Port**: `8086`
4. Click **"Create"**

#### **Option B: gcloud CLI se**

```bash
gcloud compute firewall-rules create allow-influxdb-8086 \
  --allow tcp:8086 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow InfluxDB access on port 8086" \
  --direction INGRESS
```

**Wait 1-2 minutes** for rule to propagate.

---

### **STEP 6: Check VM Network Tags (if using tags)**

Agar firewall rule specific tags use kar raha hai:

```bash
# Check VM tags
gcloud compute instances describe INSTANCE_NAME --zone=ZONE --format="get(tags.items)"

# Add tag if needed
gcloud compute instances add-tags INSTANCE_NAME \
  --tags=influxdb \
  --zone=ZONE
```

**Note**: `INSTANCE_NAME` aur `ZONE` ko replace karo apne values se.

---

### **STEP 7: Test from GCP VM Locally**

GCP VM pe hi test karo (internal access):

```bash
# Test from VM itself
curl http://localhost:8086

# Ya
curl http://127.0.0.1:8086

# Ya
wget http://localhost:8086
```

**Expected**: HTML response (InfluxDB setup page)

**Agar yeh kaam kar raha hai** → External firewall issue hai

**Agar yeh bhi nahi chal raha** → InfluxDB issue hai

---

### **STEP 8: Check docker-compose.yml Port Mapping**

GCP VM pe check karo:

```bash
cd ~/IOTNarad_dashboard
cat docker-compose.yml | grep -A 5 influxdb
```

**Should show**:
```yaml
influxdb:
  ports:
    - "8086:8086"  # ✅ Correct
```

**Agar `127.0.0.1:8086:8086` dikh raha hai** → External access band hai

**Fix**:
```yaml
influxdb:
  ports:
    - "0.0.0.0:8086:8086"  # Ya
    - "8086:8086"  # Default allows external access
```

---

### **STEP 9: Restart InfluxDB Container**

Agar kuch changes kiye hain:

```bash
docker compose restart influxdb

# Ya
docker compose up -d --force-recreate influxdb

# Wait 15 seconds
sleep 15

# Check logs
docker compose logs influxdb --tail 20
```

---

### **STEP 10: Test from Local Machine**

Laptop se test karo:

```bash
# Test connection
curl http://34.131.186.225:8086

# Ya browser mein try karo
# http://34.131.186.225:8086
```

**Agar timeout ho raha hai** → Firewall rule issue

**Agar "Connection refused"** → InfluxDB not running ya port not open

---

## 🔐 Alternative: SSH Tunnel (Temporary Solution)

Agar firewall setup mein time lagega, toh temporarily SSH tunnel use karo:

### **From Local Machine (Laptop)**:

```bash
# SSH tunnel create karo
ssh -L 8086:localhost:8086 user@34.131.186.225

# Keep this terminal open!
```

**Phir browser mein**:
```
http://localhost:8086
```

Yeh direct VM ke InfluxDB ko access karega via SSH tunnel.

---

## 📋 Complete Checklist

- [ ] InfluxDB container running (`docker compose ps`)
- [ ] InfluxDB logs show "Listening on :8086"
- [ ] Port 8086 listening on `0.0.0.0:8086` (not `127.0.0.1`)
- [ ] GCP Firewall rule exists for port 8086
- [ ] Firewall rule allows `0.0.0.0/0` (or your IP)
- [ ] VM network tags match firewall rule (if using tags)
- [ ] docker-compose.yml has correct port mapping
- [ ] Can access from VM locally (`curl localhost:8086`)
- [ ] Can access from external browser

---

## ✅ Quick Fix Commands (All-in-One)

GCP VM pe run karo:

```bash
# 1. Check InfluxDB status
docker compose ps influxdb

# 2. If not running, start it
docker compose up -d influxdb

# 3. Wait for startup
sleep 15

# 4. Check logs
docker compose logs influxdb --tail 20

# 5. Check port listening
sudo netstat -tlnp | grep 8086

# 6. Create firewall rule (if needed)
gcloud compute firewall-rules create allow-influxdb-8086 \
  --allow tcp:8086 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow InfluxDB access" \
  --direction INGRESS

# 7. Test locally
curl http://localhost:8086
```

---

## 🎯 Once Access is Working

Jab `http://34.131.186.225:8086` open ho jaye:

### **1. First-Time Setup (if needed)**
- Username: `admin`
- Password: apni production password
- Org: `iot-narad-production`
- Bucket: `iot_data_production`

### **2. Generate Token**
1. **Data** → **API Tokens**
2. **+ Generate API Token** → **All Access Token**
3. Name: `iotnarad-production-admin-token`
4. **Copy token** (sirf ek baar dikhta hai!)

### **3. Add Token to .env**
```bash
nano ~/IOTNarad_dashboard/.env
```

Add:
```env
INFLUXDB_TOKEN=your_copied_token_here
```

---

## 🔍 Still Not Working?

Agar abhi bhi page nahi khul raha:

1. **Check VM external IP**: `gcloud compute instances describe INSTANCE_NAME --format="get(networkInterfaces[0].accessConfigs[0].natIP)"`
2. **Check if VM has external IP**: GCP Console → Compute Engine → VM → Check "External IP"
3. **Try SSH tunnel** (temporary solution above)
4. **Check InfluxDB logs**: `docker compose logs influxdb`

---

**Need more help?** Check logs: `docker compose logs influxdb`

