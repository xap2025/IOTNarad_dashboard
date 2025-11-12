# 🚀 MQTT GCP VM Testing - Quick Start

## ⚡ Quick Steps

### 1. Configure GCP Firewall (One-time setup)

**Option A: GCP Console**
1. Go to: **VPC Network → Firewall**
2. Create rule: `mqtt-broker-allow`
3. Allow: TCP ports `1883`, `9001`
4. Source: `0.0.0.0/0` (or specific IPs)

**Option B: gcloud CLI**
```bash
gcloud compute firewall-rules create mqtt-broker-allow \
    --allow tcp:1883,tcp:9001 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow MQTT broker connections"
```

### 2. Get Your VM External IP

```bash
# From GCP VM
curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip

# Or from GCP Console: Compute Engine → VM instances
```

### 3. Test from GCP VM (SSH into VM first)

```bash
# Make script executable
chmod +x tools/test_mqtt_gcp_vm.sh

# Run test script
./tools/test_mqtt_gcp_vm.sh
```

### 4. Test from Your Local Machine (Windows)

```powershell
# Run PowerShell script
.\tools\test_mqtt_gcp_vm.ps1 -VM_IP "YOUR_VM_EXTERNAL_IP"
```

### 5. Manual Testing Commands

#### On GCP VM:
```bash
# Subscribe to all topics
docker exec -it iotnarad_mqtt mosquitto_sub -h localhost -t '#' -v

# Publish test message
docker exec -i iotnarad_mqtt mosquitto_pub \
    -h localhost \
    -p 1883 \
    -t 'test/topic' \
    -m '{"test": "message"}'
```

#### From Local Machine (if Docker installed):
```powershell
# Subscribe
docker run --rm eclipse-mosquitto:2 mosquitto_sub \
    -h YOUR_VM_EXTERNAL_IP \
    -p 1883 \
    -t '#' \
    -v

# Publish
docker run --rm eclipse-mosquitto:2 mosquitto_pub \
    -h YOUR_VM_EXTERNAL_IP \
    -p 1883 \
    -t 'test/topic' \
    -m '{"test": "message"}'
```

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection timeout | Check GCP firewall rules |
| Port not accessible | Verify port 1883 is open in firewall |
| Container not running | Run `docker compose up -d mqtt` |
| No messages received | Check topic names match exactly |

## 📚 Full Documentation

See `MQTT_TESTING_GCP_VM.md` for complete guide.

