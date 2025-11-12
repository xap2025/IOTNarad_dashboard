# ⚡ Hardware Initialization - Quick Reference

## 🎯 What Happens

1. **Hardware sends:** `{"SerialNumber": "DF5647"}` → `Dev/Init/DF5647`
2. **Server receives:** Extracts serial number, checks database
3. **Server stores:** New device (ignores existing)
4. **Server acknowledges:** `{"status":"success",...}` → `Dev/Ack/DF5647`

---

## 🚀 Quick Test Commands

### Test from GCP VM

```bash
# Run automated test
./tools/test_hardware_init_gcp.sh DF5647

# Manual test
SERIAL="DF5647"
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost -p 1883 \
    -t "Dev/Init/$SERIAL" \
    -m '{"SerialNumber": "'$SERIAL'"}'
```

### Test from Local Machine (Windows)

```powershell
# PowerShell script
.\tools\test_hardware_init_gcp.ps1 -VM_IP "34.131.186.225" -SerialNumber "DF5647"

# Python script
python tools/test_hardware_init_python.py --vm-ip 34.131.186.225 --serial DF5647
```

---

## 📡 Topic & Message Format

### Topics

```
Initialization:  Dev/Init/<SerialNumber>
Acknowledgment:  Dev/Ack/<SerialNumber>
```

### Messages

**Initialization:**
```json
{"SerialNumber": "DF5647"}
```

**Acknowledgment:**
```json
{
  "status": "success",
  "message": "Device registered successfully",
  "timestamp": "2025-01-15T10:30:45Z"
}
```

---

## 🔧 Hardware Configuration

### ESP32/Arduino

```cpp
const char* mqtt_broker = "34.131.186.225";  // Your GCP VM IP
const int mqtt_port = 1883;
const char* serial_number = "DF5647";
```

**Full code:** See `hardware_examples/esp32_device_init.ino`

---

## ✅ Verification

### Check Server Logs

```bash
docker logs iotnarad_app -f | grep -E "Device initialization|SerialNumber|Acknowledgment"
```

### Monitor MQTT Messages

```bash
# All initialization messages
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t "Dev/Init/+" -v

# All acknowledgments
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t "Dev/Ack/+" -v
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect | Check GCP firewall (port 1883) |
| No acknowledgment | Verify hardware subscribed to `Dev/Ack/<Serial>` |
| Message not received | Check topic format: `Dev/Init/DF5647` (case sensitive) |
| JSON error | Verify format: `{"SerialNumber": "DF5647"}` |

---

## 📚 Full Documentation

- `HARDWARE_INIT_TESTING_GCP.md` - Complete testing guide
- `MQTT_TESTING_GCP_VM.md` - General MQTT testing
- `hardware_examples/esp32_device_init.ino` - ESP32 code example

---

**GCP VM IP:** 34.131.186.225 (update with your IP)  
**MQTT Port:** 1883

