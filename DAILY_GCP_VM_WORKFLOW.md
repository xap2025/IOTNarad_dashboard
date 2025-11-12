# 🌅 Daily GCP VM Workflow Guide

## 🎯 Quick Start Checklist (5 Minutes)

### **Morning Routine:**

1. ✅ **Check VM Status** (30 seconds)
2. ✅ **Connect to VM** (30 seconds)
3. ✅ **Verify Services Running** (1 minute)
4. ✅ **Check Dashboard Access** (30 seconds)
5. ✅ **Review Logs** (2 minutes)

---

## 📋 Step-by-Step Daily Workflow

### **Step 1: Check VM is Running**

**From your laptop (PowerShell/CMD):**

```powershell
# Option A: Using gcloud
gcloud compute instances list --project iot-narad-dashboard-v2

# Option B: Check via Google Cloud Console
# Open: https://console.cloud.google.com/compute/instances?project=iot-narad-dashboard-v2
```

**Expected:** VM status should be `RUNNING` ✅

**If VM is stopped:**
```powershell
gcloud compute instances start iot-narad-4-0 --project iot-narad-dashboard-v2 --zone asia-south2-a
```

---

### **Step 2: Get Current External IP**

**Why:** IP might change if VM was restarted

```powershell
# Get VM external IP
gcloud compute instances describe iot-narad-4-0 \
  --project iot-narad-dashboard-v2 \
  --zone asia-south2-a \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

**OR** Connect to VM and check:
```bash
curl -s ifconfig.me
```

**Save this IP** - you'll need it to access dashboard!

---

### **Step 3: Connect to VM**

**Option A: Browser SSH (Easiest)**
- Open: https://console.cloud.google.com
- Go to: Compute Engine → VM instances
- Click: **SSH** button next to `iot-narad-4-0`

**Option B: gcloud command**
```powershell
gcloud compute ssh iot-narad-4-0 \
  --project iot-narad-dashboard-v2 \
  --zone asia-south2-a
```

**Option C: Browser SSH-in-browser**
- URL: `https://console.cloud.google.com/compute/instances?project=iot-narad-dashboard-v2`
- Click VM → **SSH** button

---

### **Step 4: Check Docker Containers**

**On VM terminal:**

```bash
# Quick check
docker ps

# Expected output: 3 containers running
# - iotnarad_app
# - iotnarad_mqtt
# - iotnarad_influxdb
```

**If containers not running:**
```bash
cd ~/IOTNarad_dashboard
docker compose up -d
docker ps  # Verify
```

---

### **Step 5: Verify Services Health**

```bash
# Check app is responding
curl -I http://localhost:8050

# Check app logs (last 20 lines)
docker logs iotnarad_app --tail 20

# Check for errors
docker logs iotnarad_app --tail 50 | grep -i error
```

**Expected:**
- ✅ `HTTP/1.1 200 OK` from curl
- ✅ No errors in logs
- ✅ "Running on 0.0.0.0:8050" message

---

### **Step 6: Access Dashboard from Browser**

**Open in browser:**
```
http://YOUR_CURRENT_IP:8050
```

**If IP changed:**
- Get new IP (Step 2)
- Update bookmark/favorite

**If can't connect:**
- Check firewall: Port 8050 allowed?
- Check containers: `docker ps`
- Check logs: `docker logs iotnarad_app`

---

## 🚀 Quick Start Script (One Command)

**Create this file on VM:** `~/daily_start.sh`

```bash
#!/bin/bash
echo "🌅 Starting Daily GCP VM Check..."
echo ""

# Get external IP
echo "📍 External IP:"
EXTERNAL_IP=$(curl -s ifconfig.me)
echo "   http://$EXTERNAL_IP:8050"
echo ""

# Check containers
echo "🐳 Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep iotnarad
echo ""

# Check app health
echo "🏥 App Health Check:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8050 | grep -q "200"; then
    echo "   ✅ App is running and healthy"
else
    echo "   ❌ App not responding - check logs"
    echo "   Run: docker logs iotnarad_app --tail 50"
fi
echo ""

# Check disk space
echo "💾 Disk Space:"
df -h / | tail -1 | awk '{print "   Used: " $3 " / " $2 " (" $5 ")"}'
echo ""

# Recent errors (last hour)
echo "⚠️  Recent Errors (last hour):"
docker logs iotnarad_app --since 1h 2>&1 | grep -i error | tail -5 || echo "   No errors found"
echo ""

echo "✅ Daily check complete!"
echo ""
echo "📊 Quick Commands:"
echo "   - View logs: docker logs iotnarad_app -f"
echo "   - Restart: docker compose restart"
echo "   - Update code: git pull && docker compose up -d --build"
```

**Make executable:**
```bash
chmod +x ~/daily_start.sh
```

**Run daily:**
```bash
~/daily_start.sh
```

---

## 📝 Common Daily Tasks

### **1. Update Code (After git push from laptop)**

```bash
cd ~/IOTNarad_dashboard
git pull origin main
docker compose down
docker compose build
docker compose up -d
docker ps  # Verify
```

### **2. View Real-time Logs**

```bash
# App logs
docker logs iotnarad_app -f

# All services
docker compose logs -f

# Specific service
docker logs iotnarad_mqtt -f
```

### **3. Restart Services (if needed)**

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart app

# Complete restart (stop + start)
docker compose down
docker compose up -d
```

### **4. Check Disk Space**

```bash
# Overall usage
df -h

# Docker disk usage
docker system df

# Clean up old images (if needed)
docker system prune -a
```

### **5. Check Resource Usage**

```bash
# Container stats
docker stats

# System resources
htop  # OR: top
```

---

## 🔧 Troubleshooting Commands

### **App Not Starting:**

```bash
docker logs iotnarad_app --tail 100
docker compose down
docker compose up -d
```

### **Port Already in Use:**

```bash
docker compose down
docker container prune -f
docker compose up -d
```

### **Code Changes Not Reflecting:**

```bash
git pull origin main
docker compose build --no-cache
docker compose up -d
```

### **Can't Connect from Browser:**

```bash
# Get current IP
curl -s ifconfig.me

# Check firewall
sudo iptables -L -n | grep 8050

# Test locally
curl http://localhost:8050
```

---

## 📅 Weekly Maintenance Tasks

### **Once a Week:**

1. **Update system packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Clean Docker:**
   ```bash
   docker system prune -a
   ```

3. **Check disk space:**
   ```bash
   df -h
   docker system df
   ```

4. **Review logs for errors:**
   ```bash
   docker logs iotnarad_app --since 7d | grep -i error
   ```

5. **Backup important data:**
   ```bash
   # Backup .env file
   cp ~/IOTNarad_dashboard/.env ~/backup/.env.$(date +%Y%m%d)
   ```

---

## 🎯 Morning Checklist Template

**Print this and check daily:**

```
☐ VM is RUNNING
☐ Got current External IP
☐ Connected to VM via SSH
☐ All 3 containers running (app, mqtt, influxdb)
☐ Dashboard accessible at http://IP:8050
☐ No errors in logs
☐ Disk space OK
```

---

## ⚡ Pro Tips

1. **Bookmark Dashboard URL:**
   - But remember IP might change!
   - Better: Use domain name (if you have one)

2. **Set Static IP:**
   - So IP never changes
   - Cost: ~$0.005/hour (very cheap)

3. **Use SSH Keys:**
   - Faster connection
   - No password needed

4. **Monitor Daily:**
   - Set up alerts (optional)
   - Check logs weekly for issues

5. **Keep Notes:**
   - Document any changes
   - Save important commands

---

## 📱 Quick Reference Card

```bash
# ============================================
# DAILY START COMMANDS (Copy-Paste Ready)
# ============================================

# 1. Connect to VM
gcloud compute ssh iot-narad-4-0 --project iot-narad-dashboard-v2 --zone asia-south2-a

# 2. Get IP (once connected)
curl -s ifconfig.me

# 3. Check containers
docker ps

# 4. Check app health
curl -I http://localhost:8050

# 5. View logs
docker logs iotnarad_app --tail 30

# 6. Restart if needed
cd ~/IOTNarad_dashboard && docker compose restart

# 7. Update code (after git push)
cd ~/IOTNarad_dashboard && git pull && docker compose up -d --build
```

---

**Last Updated:** 2025-10-31  
**Your VM:** `iot-narad-4-0`  
**Project:** `iot-narad-dashboard-v2`  
**Zone:** `asia-south2-a`

