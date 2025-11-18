# 🔄 InfluxDB Reset - Quick Commands

## ❌ Error: Volume in use

**Problem**: Container abhi bhi running hai, isliye volume delete nahi ho raha.

---

## ✅ Correct Sequence:

```bash
# Step 1: Stop and REMOVE the InfluxDB container
docker compose stop influxdb
docker compose rm -f influxdb

# Step 2: NOW remove the volume (container removed, so volume free hai)
docker volume rm iotnarad_dashboard_influxdb-data

# Step 3: Start InfluxDB fresh
docker compose up -d influxdb

# Step 4: Wait 15 seconds
sleep 15

# Step 5: Check logs
docker compose logs influxdb --tail 20
```

---

## 🎯 One-Line Solution:

```bash
docker compose stop influxdb && docker compose rm -f influxdb && docker volume rm iotnarad_dashboard_influxdb-data && docker compose up -d influxdb && sleep 15 && docker compose logs influxdb --tail 20
```

---

## 📝 What Each Command Does:

1. **`docker compose stop influxdb`** → Container ko stop karta hai
2. **`docker compose rm -f influxdb`** → Container ko DELETE karta hai (volume ab free)
3. **`docker volume rm iotnarad_dashboard_influxdb-data`** → Ab volume delete ho jayega
4. **`docker compose up -d influxdb`** → Fresh container start karta hai
5. **`sleep 15`** → InfluxDB ko start hone ke liye time deta hai
6. **`docker compose logs influxdb --tail 20`** → Logs check karta hai

---

## ✅ After Reset:

1. **Open browser**: `http://34.131.186.225:8086`
2. **Setup form fill karo**:
   - Username: `admin`
   - Password: `[Your strong password]`
   - Organization: `iot-narad-production`
   - Bucket: `iot_data_production`
3. **Generate Token**
4. **Update `.env`**
5. **Restart app**: `docker compose restart app`

---

**Run the commands above!** ✅

