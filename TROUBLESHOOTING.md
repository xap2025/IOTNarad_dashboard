# 🔧 IOTNarad Dashboard - Troubleshooting Guide

## Common Issues and Solutions

---

## 🐳 Docker Issues

### Issue 1: "Docker is not running"

**Error:**
```
error during connect: This error may indicate that the docker daemon is not running
```

**Solution:**
1. Open **Docker Desktop** application
2. Wait for Docker to start (whale icon in system tray)
3. Try the command again

---

### Issue 2: Port already in use

**Error:**
```
Error: Bind for 0.0.0.0:8050 failed: port is already allocated
```

**Check what's using the port:**
```powershell
netstat -ano | findstr :8050
```

**Solution A - Stop the process:**
```powershell
# Find PID from netstat output, then:
taskkill /PID <PID_NUMBER> /F
```

**Solution B - Change port in .env:**
```env
PORT=8051
```

Then restart:
```powershell
docker-compose down
docker-compose up -d
```

---

### Issue 3: Containers keep restarting

**Check logs:**
```powershell
docker-compose logs app
```

**Common causes:**
- Missing .env file → Create from credentials
- Wrong InfluxDB credentials → Check .env
- Python errors → Check logs for stack trace

**Solution:**
```powershell
# Clean rebuild
docker-compose down -v
docker-compose up -d --build
```

---

## 🌐 Dashboard Access Issues

### Issue 1: "This site can't be reached"

**Checklist:**
- [ ] Containers are running: `docker ps`
- [ ] App container is healthy: `docker-compose ps`
- [ ] Waited 30-60 seconds after start
- [ ] Using correct URL: http://localhost:8050

**Try alternative URLs:**
```
http://127.0.0.1:8050
http://[YOUR_IP_ADDRESS]:8050
```

**Check firewall:**
```powershell
# Add firewall rule
netsh advfirewall firewall add rule name="IOTNarad" dir=in action=allow protocol=TCP localport=8050
```

---

### Issue 2: Page loads but no content

**F12 Developer Console check:**
- Look for JavaScript errors
- Check Network tab for failed requests

**Solution:**
```powershell
# Clear browser cache
Ctrl + Shift + Delete

# Or try incognito mode
Ctrl + Shift + N
```

---

### Issue 3: Login fails with correct credentials

**Check app logs:**
```powershell
docker-compose logs app | findstr "login"
```

**Verify .env credentials:**
```powershell
Get-Content .env | findstr "ADMIN"
```

**Solution:**
```powershell
# Restart app container
docker-compose restart app
```

---

## 📡 MQTT Issues

### Issue 1: MQTT broker not connecting

**Check MQTT logs:**
```powershell
docker-compose logs mqtt
```

**Test MQTT directly:**
```powershell
# Subscribe to test topic
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t "test" -v
```

**In another terminal, publish:**
```powershell
docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -t "test" -m "hello"
```

If you see "hello" in subscriber, MQTT works!

---

### Issue 2: Device data not appearing

**Check topic format:**
- Must be: `iotnarad/devices/{device_id}/data`
- Example: `iotnarad/devices/esp32_gw_01/data`

**Test with correct format:**
```powershell
docker exec -it iotnarad_mqtt mosquitto_pub -h localhost -t "iotnarad/devices/esp32_gw_01/data" -m "{\"device_id\":\"esp32_gw_01\",\"temperature\":25.5}"
```

**Check app receives it:**
```powershell
docker-compose logs -f app
```

Look for: `📨 Message received on...`

---

## 💾 InfluxDB Issues

### Issue 1: InfluxDB connection failed

**Error in logs:**
```
❌ Failed to connect to InfluxDB: ...
```

**Check .env configuration:**
```powershell
Get-Content .env | findstr "INFLUXDB"
```

**Verify credentials match:**
```
INFLUXDB_URL=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUXDB_TOKEN=T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA==
INFLUXDB_ORG=iot-narad-gcp
INFLUXDB_BUCKET=iot_data_gcp
```

**Test connection manually:**
```powershell
curl -X GET "https://us-east-1-1.aws.cloud2.influxdata.com/api/v2/buckets" -H "Authorization: Token T0ZoSucqSCbNtgfcZSYE81-vYA7DdXpPFRb17vc2iUZsUZ0CsebGlOTpr9XTGFjlaiyqI5bwUhtqLQe2zU7wnA=="
```

---

### Issue 2: Data not being stored

**Check write permissions:**
- Token must have **write** access to bucket
- Verify in InfluxDB Cloud dashboard

**Check app logs:**
```powershell
docker-compose logs app | findstr "InfluxDB"
```

Look for: `💾 Data written to InfluxDB...`

---

## 🖥️ Windows-Specific Issues

### Issue 1: PowerShell script execution blocked

**Error:**
```
cannot be loaded because running scripts is disabled
```

**Solution (run as Administrator):**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Or bypass for single command:
```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

---

### Issue 2: Docker Desktop WSL 2 issues

**If WSL 2 backend errors:**

1. Update WSL:
```powershell
wsl --update
```

2. Set WSL 2 as default:
```powershell
wsl --set-default-version 2
```

3. Restart Docker Desktop

---

## 🔍 Debugging Commands

### View all logs at once:
```powershell
docker-compose logs
```

### View specific service logs:
```powershell
docker-compose logs app
docker-compose logs mqtt
docker-compose logs influxdb
```

### Follow logs in real-time:
```powershell
docker-compose logs -f app
```

### Check container health:
```powershell
docker ps
docker stats
```

### Inspect container:
```powershell
docker inspect iotnarad_app
```

### Enter container shell:
```powershell
docker exec -it iotnarad_app /bin/bash
```

### Check network:
```powershell
docker network ls
docker network inspect iotnarad_dashboard_default
```

---

## 🧹 Nuclear Option (Complete Reset)

If nothing works, try a complete reset:

```powershell
# Stop everything
docker-compose down -v

# Remove all IOTNarad containers
docker rm -f $(docker ps -a --filter "name=iotnarad" -q)

# Remove IOTNarad images
docker rmi $(docker images --filter "reference=iotnarad*" -q)

# Clean Docker system
docker system prune -a --volumes -f

# Rebuild from scratch
docker-compose up -d --build
```

**⚠️ Warning:** This removes all data!

---

## 📊 Performance Issues

### Dashboard is slow:

1. **Check Docker resources:**
   - Docker Desktop → Settings → Resources
   - Increase CPU/Memory if needed

2. **Check container stats:**
```powershell
docker stats
```

3. **Reduce chart update frequency:**
   - Edit `app/pages/analytics.py`
   - Increase `interval` value in `dcc.Interval`

---

## 🆘 Still Not Working?

### Collect diagnostic information:

```powershell
# Create diagnostic report
echo "=== System Info ===" > diagnostic.txt
systeminfo >> diagnostic.txt

echo "=== Docker Info ===" >> diagnostic.txt
docker version >> diagnostic.txt
docker-compose version >> diagnostic.txt

echo "=== Container Status ===" >> diagnostic.txt
docker ps -a >> diagnostic.txt

echo "=== App Logs ===" >> diagnostic.txt
docker-compose logs app >> diagnostic.txt

echo "=== MQTT Logs ===" >> diagnostic.txt
docker-compose logs mqtt >> diagnostic.txt

notepad diagnostic.txt
```

---

## 📞 Getting Help

1. **Check documentation:**
   - README.md
   - TESTING_GUIDE.md
   - DEPLOYMENT_GUIDE.md
   - ESP32_INTEGRATION.md

2. **Review credentials:**
   - CREDENTIALS.md (verify InfluxDB token)

3. **Search error messages:**
   - Copy exact error from logs
   - Search online or in documentation

---

**Most issues are solved by:**
1. ✅ Checking .env file exists and is correct
2. ✅ Waiting 30-60 seconds after start
3. ✅ Viewing logs: `docker-compose logs app`
4. ✅ Restarting: `docker-compose restart`
5. ✅ Clean rebuild: `docker-compose down && docker-compose up -d --build`

Good luck! 🍀

