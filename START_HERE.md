# 🚀 START HERE - Testing Your IOTNarad Dashboard

## 📋 You Have Everything You Need!

✅ **Docker** installed (v28.4.0)  
✅ **Docker Compose** installed (v2.39.2)  
✅ **Python** installed (v3.12.0)  
✅ **.env** file configured with InfluxDB Cloud credentials  
✅ **Code** is ready to run  

---

## 🎯 Choose Your Testing Method

### **Option 1: Interactive Menu (EASIEST)** ⭐ RECOMMENDED

**Just run this:**
```cmd
quick_test.bat
```

**What it does:**
- Shows you a menu with numbered options
- You can test step-by-step
- Opens browser automatically
- No need to remember commands

**Perfect for:** First-time testing, beginners

---

### **Option 2: Manual Commands (ADVANCED)**

**Run these commands one by one:**

```powershell
# Step 1: Create data directory
mkdir data\configs

# Step 2: Start all services
docker-compose up -d --build

# Step 3: Wait 30 seconds, then check status
docker ps

# Step 4: View logs
docker-compose logs -f app

# Step 5: Open browser
start http://localhost:8050
```

**Perfect for:** Developers, troubleshooting

---

### **Option 3: Read Full Guide**

**Open this file:**
```
TESTING_GUIDE.md
```

**What's inside:**
- Complete step-by-step instructions
- Expected outputs for each step
- Success checklist
- Troubleshooting tips

**Perfect for:** Understanding how everything works

---

## ⚡ Quick Start (30 seconds)

**The absolute fastest way to test:**

```cmd
1. Open Command Prompt or PowerShell
2. Type: cd C:\Users\ridhi\IOTNarad_dashboard
3. Type: docker-compose up -d --build
4. Wait 30 seconds
5. Open browser: http://localhost:8050
6. Login: admin / iotnarad@2025
```

**That's it!** 🎉

---

## 🎨 What You'll See

### **Login Page**
- Beautiful purple gradient background
- Modern login form
- IOTNarad branding

### **Home Dashboard**
- 24 Active Devices
- 1,542 Messages/Hour
- 2.4 GB Data Stored
- 99.8% Uptime
- System status indicators

### **Analytics Page**
- Real-time temperature chart
- Real-time humidity chart
- Voltage monitoring (0-10V)
- Current monitoring (4-20mA)
- Digital I/O status
- Activity log

### **Devices Page**
- Device selector dropdown
- Three tabs:
  - ⚡ **Analog**: Configure 4-20mA, 1-10V inputs/outputs
  - 🔢 **Digital**: Configure NPN, PNP, Relays
  - 📡 **Communication**: WiFi, MQTT, Modbus, CAN settings

---

## ✅ Success Indicators

**You'll know it's working when:**

1. ✅ 3 Docker containers running
2. ✅ Browser opens to login page
3. ✅ Can login successfully
4. ✅ Dashboard shows charts and data
5. ✅ No errors in logs

**Check logs for these messages:**
```
✅ Connected to MQTT Broker: mqtt:1883
✅ Connected to InfluxDB: https://us-east-1-1.aws.cloud2.influxdata.com
📊 Using bucket: iot_data_gcp
🚀 Starting IOTNarad Dashboard on 0.0.0.0:8050
```

---

## ❌ If Something Goes Wrong

### **Quick Fixes:**

**Problem: Port already in use**
```powershell
docker-compose down
docker-compose up -d
```

**Problem: Containers not starting**
```powershell
docker-compose down
docker-compose up -d --build
```

**Problem: Dashboard not loading**
- Wait 60 seconds (first start takes time)
- Check: http://127.0.0.1:8050
- View logs: `docker-compose logs app`

**Problem: Need detailed help**
- Open: `TROUBLESHOOTING.md`
- Run: `quick_test.bat` → Option 4 (Check Status)

---

## 📚 All Available Files

| File | Purpose |
|------|---------|
| `quick_test.bat` | Interactive testing menu ⭐ |
| `TESTING_GUIDE.md` | Complete testing instructions |
| `TROUBLESHOOTING.md` | Fix common problems |
| `README.md` | Full project documentation |
| `DEPLOYMENT_GUIDE.md` | Deploy to GCP |
| `ESP32_INTEGRATION.md` | Connect ESP32 devices |
| `CREDENTIALS.md` | All passwords & tokens |

---

## 🎯 Your Testing Path

```
START → Run quick_test.bat → Choose Option 3 (Start Services)
   ↓
Wait 30 seconds
   ↓
Choose Option 6 (Open Browser) → Login
   ↓
SUCCESS! ✅ Dashboard is working!
   ↓
Test each page (Home, Analytics, Devices)
   ↓
When done → Choose Option 8 (Stop Services)
```

---

## 🧪 Test with Sample Data

**After dashboard is running:**

1. Open new terminal
2. Run this:
```powershell
docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -t "iotnarad/devices/esp32_gw_01/data" -m "{\"device_id\":\"esp32_gw_01\",\"temperature\":25.5,\"humidity\":60.2}"
```

3. Check Analytics page → Charts should update!

---

## 💡 Pro Tips

✨ **Tip 1:** Keep logs open in separate terminal
```powershell
docker-compose logs -f app
```

✨ **Tip 2:** Check container status anytime
```powershell
docker ps
```

✨ **Tip 3:** Restart just the app (keeps data)
```powershell
docker-compose restart app
```

✨ **Tip 4:** Clean restart (fresh start)
```powershell
docker-compose down
docker-compose up -d --build
```

---

## 🎓 Next Steps After Successful Test

1. ✅ **Familiarize yourself** with the dashboard UI
2. ✅ **Try all features** (Home, Analytics, Devices)
3. ✅ **Test MQTT** publishing (see above)
4. ✅ **Check InfluxDB Cloud** for stored data
5. ✅ **Read ESP32_INTEGRATION.md** to connect real devices
6. ✅ **Deploy to GCP** using DEPLOYMENT_GUIDE.md

---

## 📞 Need Help?

**Follow this order:**

1. **Quick issue?** → `TROUBLESHOOTING.md`
2. **Want to understand?** → `TESTING_GUIDE.md`
3. **Deployment help?** → `DEPLOYMENT_GUIDE.md`
4. **ESP32 help?** → `ESP32_INTEGRATION.md`

---

## 🎉 You're Ready!

**Your IOTNarad Dashboard is configured and ready to test.**

**Just run:**
```cmd
quick_test.bat
```

**And follow the menu!**

---

**Good luck! 🚀**

*If you see the login page, you've already succeeded!*

