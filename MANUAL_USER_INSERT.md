# 👤 Manual User Insert via InfluxDB CLI

## 🎯 Goal:
Insert first admin user manually in `User_info` measurement using InfluxDB CLI.

---

## 📋 User Data:
```
Company_Name = Xaptronics
Email_Id = xaptronicsindia.com
Phone_No = 7042703926
User_Id = admin
User_Type = admin
status = active
Password = admin
```

---

## 🔧 Step 1: Check .env File for Bucket and Org

GCP VM pe SSH karo aur check karo:

```bash
cd ~/IOTNarad_dashboard
cat .env | grep -E "INFLUXDB_BUCKET|INFLUXDB_ORG|INFLUXDB_TOKEN|INFLUXDB_URL"
```

**Expected output** (example):
```
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=your_token_here
INFLUXDB_ORG=iot-narad-production
INFLUXDB_BUCKET=iot_data_production
```

**Note these values** - we'll need them for CLI command.

---

## 🔧 Step 2: Install InfluxDB CLI (if not installed)

### **Option A: Use Docker Exec (Recommended - No installation needed)**

```bash
docker exec -it iotnarad_influxdb influx write \
  --org YOUR_ORG \
  --bucket YOUR_BUCKET \
  --token YOUR_TOKEN \
  --precision ns \
  'User_info,Company_Name=Xaptronics,Email_Id=xaptronicsindia.com,Phone_No=7042703926,User_Id=admin,User_Type=admin,status=active Password="admin"'
```

### **Option B: Install InfluxDB CLI on VM**

```bash
# Download and install InfluxDB CLI
wget https://dl.influxdata.com/influxdb/releases/influxdb2-client-2.7.3-linux-amd64.tar.gz
tar xvzf influxdb2-client-2.7.3-linux-amd64.tar.gz
sudo cp influxdb2-client-2.7.3-linux-amd64/influx /usr/local/bin/
rm -rf influxdb2-client-2.7.3-linux-amd64*

# Verify installation
influx version
```

---

## ✅ Step 3: Insert User via CLI

### **Method 1: Using Docker Exec (Easiest)**

Replace `YOUR_ORG`, `YOUR_BUCKET`, and `YOUR_TOKEN` with values from `.env`:

```bash
cd ~/IOTNarad_dashboard

# Get values from .env
export INFLUXDB_ORG=$(grep INFLUXDB_ORG .env | cut -d '=' -f2)
export INFLUXDB_BUCKET=$(grep INFLUXDB_BUCKET .env | cut -d '=' -f2)
export INFLUXDB_TOKEN=$(grep INFLUXDB_TOKEN .env | cut -d '=' -f2)

# Insert user via Docker exec
docker exec -i iotnarad_influxdb influx write \
  --org "$INFLUXDB_ORG" \
  --bucket "$INFLUXDB_BUCKET" \
  --token "$INFLUXDB_TOKEN" \
  --precision ns \
  'User_info,Company_Name=Xaptronics,Email_Id=xaptronicsindia.com,Phone_No=7042703926,User_Id=admin,User_Type=admin,status=active Password="admin"'
```

### **Method 2: One-Line Command (Replace values manually)**

```bash
docker exec -i iotnarad_influxdb influx write \
  --org iot-narad-production \
  --bucket iot_data_production \
  --token YOUR_TOKEN_HERE \
  --precision ns \
  'User_info,Company_Name=Xaptronics,Email_Id=xaptronicsindia.com,Phone_No=7042703926,User_Id=admin,User_Type=admin,status=active Password="admin"'
```

**Replace**:
- `iot-narad-production` → Your actual org name from `.env`
- `iot_data_production` → Your actual bucket name from `.env`
- `YOUR_TOKEN_HERE` → Your actual token from `.env`

---

## 🔍 Step 4: Verify Insert

### **Check via InfluxDB UI**:
1. Open: `http://34.131.186.225:8086`
2. Login
3. Go to **Data Explorer**
4. Select bucket
5. Select measurement: `User_info`
6. Run query

### **Check via CLI**:

```bash
# Set environment variables
export INFLUXDB_ORG=$(grep INFLUXDB_ORG .env | cut -d '=' -f2)
export INFLUXDB_BUCKET=$(grep INFLUXDB_BUCKET .env | cut -d '=' -f2)
export INFLUXDB_TOKEN=$(grep INFLUXDB_TOKEN .env | cut -d '=' -f2)

# Query user
docker exec -i iotnarad_influxdb influx query \
  --org "$INFLUXDB_ORG" \
  --token "$INFLUXDB_TOKEN" \
  "from(bucket: \"$INFLUXDB_BUCKET\") |> range(start: -1d) |> filter(fn: (r) => r._measurement == \"User_info\" AND r.User_Id == \"admin\")"
```

---

## 📝 Line Protocol Format Explained:

```
User_info,Company_Name=Xaptronics,Email_Id=xaptronicsindia.com,Phone_No=7042703926,User_Id=admin,User_Type=admin,status=active Password="admin"
```

**Breakdown**:
- `User_info` → Measurement name
- `Company_Name=Xaptronics` → Tag (key=value)
- `Email_Id=xaptronicsindia.com` → Tag
- `Phone_No=7042703926` → Tag
- `User_Id=admin` → Tag
- `User_Type=admin` → Tag
- `status=active` → Tag
- `Password="admin"` → Field (string value, so quotes required)
- Timestamp → Auto-added (nanoseconds precision)

**Important Notes**:
- **Tags** are separated by commas
- **Field** comes after tags, separated by space
- **String fields** must be in double quotes
- **Timestamp** is optional - if not provided, current time is used

---

## ⚠️ Common Issues:

### **Issue 1: Token Invalid**
```
Error: unauthorized access
```
**Fix**: Check token in `.env` file, make sure it's correct.

### **Issue 2: Bucket/Org Not Found**
```
Error: bucket not found
```
**Fix**: Verify bucket and org names match exactly with `.env` file.

### **Issue 3: Permission Denied**
```
Error: insufficient permissions
```
**Fix**: Make sure token has "All Access" permissions.

---

## 🎯 Quick One-Liner (Copy-Paste Ready):

Replace values first, then run:

```bash
cd ~/IOTNarad_dashboard && \
export INFLUXDB_ORG=$(grep INFLUXDB_ORG .env | cut -d '=' -f2) && \
export INFLUXDB_BUCKET=$(grep INFLUXDB_BUCKET .env | cut -d '=' -f2) && \
export INFLUXDB_TOKEN=$(grep INFLUXDB_TOKEN .env | cut -d '=' -f2) && \
docker exec -i iotnarad_influxdb influx write \
  --org "$INFLUXDB_ORG" \
  --bucket "$INFLUXDB_BUCKET" \
  --token "$INFLUXDB_TOKEN" \
  --precision ns \
  'User_info,Company_Name=Xaptronics,Email_Id=xaptronicsindia.com,Phone_No=7042703926,User_Id=admin,User_Type=admin,status=active Password="admin"' && \
echo "✅ User inserted successfully!"
```

---

## ✅ After Insert:

1. **Test Login** in your dashboard: `http://34.131.186.225:8050`
2. **Username**: `admin`
3. **Password**: `admin`

**Should work!** 🎉

---

**Run the commands above to insert the user manually!** ✅

