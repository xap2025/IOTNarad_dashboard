# 🚨 URGENT: Database Cleanup - Complete Command

## ⚠️ CRITICAL: Database mein purane boolean records delete karni hain

Abhi sabhi parameters ke liye type conflict errors aa rahe hain. Purane boolean records delete karni hain.

---

## ✅ COMPLETE CLEANUP COMMAND (Copy-Paste Ready)

```bash
docker exec -it iotnarad_influxdb influx delete --org iot-narad-gcp --bucket iot_data_gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== --start 1970-01-01T00:00:00Z --stop 2100-01-01T00:00:00Z --predicate '_measurement="Realtime_Data" AND device_id="8C4B144D3274"'
```

**Yeh command:**
- Device `8C4B144D3274` ke **sabhi Realtime_Data** records delete karega
- Purane boolean records hata dega
- Naye integer values save ho sakenge

---

## 📋 Step-by-Step Instructions

1. **Terminal open karein**
2. **Yeh command copy-paste karein** (ek hi line mein)
3. **Enter press karein**
4. **Wait karein** - deletion complete hone tak
5. **Server restart karein** (optional, but recommended)

---

## ✅ Verification

Cleanup ke baad verify karein:

```bash
docker exec -it iotnarad_influxdb influx query --org iot-narad-gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== 'from(bucket: "iot_data_gcp") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "Realtime_Data") |> filter(fn: (r) => r.device_id == "8C4B144D3274") |> count()'
```

Agar count `0` dikhaye, toh cleanup successful hai.

---

## 🎯 After Cleanup

1. **MQTT data automatically save hoga** (ab type conflict nahi hoga)
2. **SocketIO events properly emit honge**
3. **UI mein real-time values dikhenge**

---

**IMPORTANT:** Yeh command sirf device `8C4B144D3274` ke records delete karega. Agar aur devices hain, unke liye alag command chahiye.

