# 🔧 Update Firewall Rule - Add Port 8086

## Current Status:
- ✅ Port 8050 (App) already allowed in `allow-iot-narad-dashboard`
- ❌ Port 8086 (InfluxDB) missing from firewall rules

## 🎯 Solution: Add Port 8086 to Existing Rule

### **Option 1: Edit Existing Rule (Recommended)**

1. **Click on**: `allow-iot-narad-dashboard` rule (first row in table)

2. **Click**: "EDIT" button (top right)

3. **Scroll down** to "Protocols and ports" section

4. **Update ports field**:
   - Current: `1883, 8050, 8883, 9001`
   - Change to: `1883, 8050, 8086, 8883, 9001`
   - **Add `8086`** to the list

5. **Click**: "SAVE" button

6. **Wait 1-2 minutes** (for rule to propagate)

7. **Test**:
   ```
   http://34.131.186.225:8086
   ```

---

### **Option 2: Create New Rule (Alternative)**

1. **Click**: "+ Create firewall rule" button

2. **Fill form**:
   - **Name**: `allow-influxdb-8086`
   - **Description**: `Allow InfluxDB access on port 8086`
   - **Priority**: `1000`
   - **Direction**: `Ingress`
   - **Action on match**: `Allow`
   - **Targets**: `All instances in the network`
   - **Source IP ranges**: `0.0.0.0/0`
   - **Protocols and ports**:
     - ✅ **tcp**
     - **Ports**: `8086`

3. **Click**: "CREATE"

4. **Wait 1-2 minutes**

5. **Test**:
   ```
   http://34.131.186.225:8086
   ```

---

## ✅ Recommended: Option 1

**Reason**: Apka app already `allow-iot-narad-dashboard` rule use kar raha hai, same rule mein 8086 add karo - cleaner aur simpler.

---

## 📋 After Firewall Rule Updated:

1. **Wait 1-2 minutes** (propagation time)

2. **Browser mein try**:
   ```
   http://34.131.186.225:8086
   ```

3. **If First Time**: Setup form fill karo:
   - Username: `admin`
   - Password: your production password
   - Org: `iot-narad-production`
   - Bucket: `iot_data_production`

4. **Generate Token**:
   - Data → API Tokens → + Generate API Token → All Access Token
   - Name: `iotnarad-production-admin-token`
   - **Copy token**

5. **Add Token to .env**:
   ```bash
   nano ~/IOTNarad_dashboard/.env
   # Add: INFLUXDB_TOKEN=your_copied_token_here
   ```

---

**Quick Action**: `allow-iot-narad-dashboard` rule edit karo aur `8086` add karo! ✅

