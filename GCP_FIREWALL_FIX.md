# GCP Firewall Fix for Port 8050

## Problem: Can't access http://34.131.43.114:8050 from browser

## Solution: Check & Add Firewall Rule

### Method 1: Using Google Cloud Console (Easiest)

1. **Go to Google Cloud Console:**
   - Open: https://console.cloud.google.com
   - Project: `iot-narad-dashboard-v2`

2. **Navigate to Firewall Rules:**
   - Left menu → **VPC network** → **Firewall**
   - OR direct link: https://console.cloud.google.com/networking/firewalls

3. **Check if rule exists:**
   - Look for rule allowing port `8050` (tcp)
   - Rule name might be: `allow-dashboard-8050` or `default-allow-8050`

4. **If rule doesn't exist, CREATE ONE:**
   - Click **"CREATE FIREWALL RULE"**
   - **Name:** `allow-dashboard-8050`
   - **Direction:** `Ingress` (incoming)
   - **Targets:** `All instances in the network`
   - **Source IP ranges:** `0.0.0.0/0` (allow from anywhere)
   - **Protocols and ports:**
     - Select: `Specified protocols and ports`
     - Check: `tcp`
     - Ports: `8050`
   - Click **"CREATE"**

### Method 2: Using gcloud command (Terminal)

```bash
# From your laptop terminal (with gcloud installed):
gcloud compute firewall-rules create allow-dashboard-8050 \
  --allow tcp:8050 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow dashboard on port 8050" \
  --project iot-narad-dashboard-v2
```

### Method 3: Verify existing rules

```bash
# List all firewall rules
gcloud compute firewall-rules list --project iot-narad-dashboard-v2

# Check specific rule
gcloud compute firewall-rules describe allow-dashboard-8050 --project iot-narad-dashboard-v2
```

---

## Additional Checks

### Check if app is listening on correct interface:

**On GCP VM:**
```bash
sudo ss -ltnp | grep 8050
```

**Should show:**
```
LISTEN 0      128     0.0.0.0:8050    0.0.0.0:*    users:(("python",pid=XXX,fd=X))
```

**If it shows `127.0.0.1:8050` instead of `0.0.0.0:8050`, that's the problem!**

---

## Test Connection

### From your laptop:
```powershell
# PowerShell:
Test-NetConnection -ComputerName 34.131.43.114 -Port 8050

# OR using curl:
curl -I http://34.131.43.114:8050
```

**Expected:** Should connect successfully if firewall is correct.

---

## Common Issues

1. **Firewall rule exists but doesn't apply to your VM:**
   - Check VM network tags
   - Ensure rule targets "All instances"

2. **App listening on wrong interface:**
   - Check app logs: `docker logs iotnarad_app`
   - Should listen on `0.0.0.0:8050`, not `127.0.0.1:8050`

3. **VM has internal firewall (iptables):**
   - Run: `sudo iptables -L -n | grep 8050`
   - If blocked, allow it: `sudo iptables -A INPUT -p tcp --dport 8050 -j ACCEPT`

