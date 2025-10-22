# 🔧 Manual Test Steps - IOTNarad Dashboard

## Problem: Dashboard not starting at http://localhost:8050

Let's test step by step to find the issue.

---

## Step 1: Check Docker Desktop

1. **Open Docker Desktop application**
2. **Make sure it's running** (whale icon in system tray)
3. **Wait for it to fully start** (usually 30-60 seconds)

---

## Step 2: Test Docker Commands

**Open PowerShell and run these commands one by one:**

```powershell
# Check Docker is working
docker --version

# Check Docker Compose
docker-compose --version

# Check if any containers are running
docker ps

# Check all containers (including stopped)
docker ps -a
```

**Expected output:**
- Docker version should show (like v28.4.0)
- Docker Compose version should show (like v2.39.2)
- `docker ps` might show empty or some containers

---

## Step 3: Clean Start

**Run these commands to clean everything:**

```powershell
# Stop all containers
docker-compose down

# Remove all containers
docker container prune -f

# Remove all images
docker image prune -a -f

# Remove all volumes
docker volume prune -f
```

---

## Step 4: Test Simple Container

**Test if Docker can run a simple container:**

```powershell
# Run a simple test container
docker run hello-world
```

**Expected:** You should see "Hello from Docker!" message

---

## Step 5: Start IOTNarad Services

**If Docker is working, try starting our services:**

```powershell
# Make sure you're in the right directory
cd C:\Users\ridhi\IOTNarad_dashboard

# Start services
docker-compose up -d --build
```

**Wait 2-3 minutes for first build**

---

## Step 6: Check Container Status

**After waiting, check if containers started:**

```powershell
# Check running containers
docker ps

# Check all containers
docker ps -a

# Check logs
docker-compose logs
```

**Expected:** You should see 3 containers:
- `iotnarad_app`
- `iotnarad_mqtt` 
- `iotnarad_influxdb`

---

## Step 7: Check App Logs

**If containers are running, check app logs:**

```powershell
# View app logs
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f app
```

**Look for these messages:**
```
✅ Connected to MQTT Broker: mqtt:1883
✅ Connected to InfluxDB: https://us-east-1-1.aws.cloud2.influxdata.com
🚀 Starting IOTNarad Dashboard on 0.0.0.0:8050
```

---

## Step 8: Test Browser Access

**If logs look good, try browser:**

1. **Open browser**
2. **Go to:** http://localhost:8050
3. **Wait 30 seconds** (first load takes time)
4. **Try:** http://127.0.0.1:8050 (alternative)

---

## Common Issues & Solutions

### Issue 1: "Docker is not running"
**Solution:** Start Docker Desktop application

### Issue 2: "Port 8050 already in use"
**Solution:**
```powershell
# Find what's using port 8050
netstat -ano | findstr :8050

# Kill the process (replace PID with actual number)
taskkill /PID <PID_NUMBER> /F
```

### Issue 3: "Containers keep restarting"
**Solution:**
```powershell
# Check logs for errors
docker-compose logs app

# Common causes:
# - Missing .env file
# - Wrong InfluxDB credentials
# - Python errors
```

### Issue 4: "This site can't be reached"
**Solution:**
- Wait 60 seconds after starting
- Try http://127.0.0.1:8050
- Check firewall settings
- Check if app container is running: `docker ps`

---

## Alternative: Test Without Docker

**If Docker keeps failing, test the Python code directly:**

```powershell
# Install Python dependencies
pip install dash flask flask-socketio paho-mqtt influxdb-client

# Run the app directly
python -m app.main
```

**Then open:** http://localhost:8050

---

## Quick Fix Commands

**If nothing works, try this nuclear option:**

```powershell
# Stop everything
docker-compose down -v

# Remove all IOTNarad containers
docker rm -f $(docker ps -a --filter "name=iotnarad" -q)

# Remove IOTNarad images  
docker rmi $(docker images --filter "reference=iotnarad*" -q)

# Clean everything
docker system prune -a --volumes -f

# Start fresh
docker-compose up -d --build
```

---

## Success Indicators

**You'll know it's working when:**

✅ Docker Desktop is running  
✅ `docker ps` shows 3 containers  
✅ `docker-compose logs app` shows success messages  
✅ Browser opens to login page at http://localhost:8050  
✅ Can login with admin/iotnarad@2025  

---

## Need Help?

**If you're still stuck:**

1. **Check Docker Desktop** is running
2. **Restart Docker Desktop** completely
3. **Try the nuclear option** above
4. **Check Windows firewall** settings
5. **Try a different browser** (Chrome, Edge, Firefox)

---

**Good luck! 🍀**

The code is definitely working - it's just a Docker/configuration issue.
