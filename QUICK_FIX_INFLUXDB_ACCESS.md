# ⚡ Quick Fix: InfluxDB UI Access (34.131.186.225:8086)

## 🎯 Fast Solution

### **Step 1: SSH into GCP VM**
```bash
ssh user@34.131.186.225
```

### **Step 2: Check if InfluxDB is Running**
```bash
cd ~/IOTNarad_dashboard
docker compose ps influxdb
```

### **Step 3: If Not Running, Start It**
```bash
docker compose up -d influxdb
sleep 15
docker compose logs influxdb --tail 10
```

### **Step 4: Create Firewall Rule (Most Common Issue)**
```bash
gcloud compute firewall-rules create allow-influxdb-8086 \
  --allow tcp:8086 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow InfluxDB access"
```

**Wait 1-2 minutes** for rule to apply.

### **Step 5: Test**
Browser mein try karo:
```
http://34.131.186.225:8086
```

---

## 🔐 Alternative: SSH Tunnel (If Firewall Setup Takes Time)

### **From Your Laptop**:
```bash
ssh -L 8086:localhost:8086 user@34.131.186.225
```

**Keep terminal open**, phir browser mein:
```
http://localhost:8086
```

---

## ✅ Once Page Opens

1. **Setup** (if first time):
   - Org: `iot-narad-production`
   - Bucket: `iot_data_production`

2. **Generate Token**:
   - Data → API Tokens → Generate All Access Token
   - Copy token

3. **Add to .env**:
   ```bash
   nano ~/IOTNarad_dashboard/.env
   # Add: INFLUXDB_TOKEN=your_token_here
   ```

---

**Detailed troubleshooting**: See `TROUBLESHOOT_INFLUXDB_ACCESS.md`

