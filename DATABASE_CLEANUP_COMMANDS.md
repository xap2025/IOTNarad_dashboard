# Database Cleanup Commands - Type Conflict Fix

## 🚨 Problem
InfluxDB mein purane boolean records hain jo naye integer values ke saath conflict kar rahe hain.

## ✅ Solution: Delete Old Records

### **Option 1: Single Line Command (Recommended)**

```bash
docker exec -it iotnarad_influxdb influx delete --org iot-narad-gcp --bucket iot_data_gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== --start 1970-01-01T00:00:00Z --stop 2100-01-01T00:00:00Z --predicate '_measurement="Realtime_Data"'
```

**Note:** Last line pe backslash `\` mat lagana - single line mein complete command likhna.

---

### **Option 2: Multi-Line Command (If Needed)**

Agar multi-line chahiye, toh last line pe backslash mat lagana:

```bash
docker exec -it iotnarad_influxdb influx delete \
  --org iot-narad-gcp \
  --bucket iot_data_gcp \
  --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== \
  --start 1970-01-01T00:00:00Z \
  --stop 2100-01-01T00:00:00Z \
  --predicate '_measurement="Realtime_Data"'
```

**Important:** Last line pe backslash `\` nahi hona chahiye!

---

## 🔧 If Command Stuck (Showing `>` prompt)

Agar command stuck ho gaya hai aur `>` prompt dikha raha hai:

1. **Press `Ctrl+C`** to cancel the command
2. **Rewrite the command** (single line recommended)

---

## 🎯 Specific Device/Parameter Cleanup

### Delete All Realtime_Data for Specific Device:

```bash
docker exec -it iotnarad_influxdb influx delete --org iot-narad-gcp --bucket iot_data_gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== --start 1970-01-01T00:00:00Z --stop 2100-01-01T00:00:00Z --predicate '_measurement="Realtime_Data" AND device_id="8C4B144D3274"'
```

### Delete Specific Parameters Only:

```bash
docker exec -it iotnarad_influxdb influx delete --org iot-narad-gcp --bucket iot_data_gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== --start 1970-01-01T00:00:00Z --stop 2100-01-01T00:00:00Z --predicate '_measurement="Realtime_Data" AND device_id="8C4B144D3274" AND (parameter_name="Conductivity" OR parameter_name="Ph" OR parameter_name="Humidity" OR parameter_name="Air_Temp" OR parameter_name="moisture" OR parameter_name="Soil_Temp")'
```

---

## ✅ Verification

After cleanup, verify records are deleted:

```bash
docker exec -it iotnarad_influxdb influx query --org iot-narad-gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== 'from(bucket: "iot_data_gcp") |> range(start: -1h) |> filter(fn: (r) => r._measurement == "Realtime_Data") |> filter(fn: (r) => r.device_id == "8C4B144D3274") |> count()'
```

---

## ⚠️ Important Notes

1. **Backup First:** Important data ka backup le lein before deletion
2. **Token Security:** Token ko secure rakhein, share mat karein
3. **Time Range:** `--start` aur `--stop` properly set karein
4. **Predicate:** Predicate syntax sahi hona chahiye

---

## 🆘 Troubleshooting

### Command Stuck at `>` Prompt:
- Press `Ctrl+C` to cancel
- Rewrite command in single line

### Permission Denied:
- Check token permissions
- Verify org and bucket names

### No Records Deleted:
- Check predicate syntax
- Verify time range covers old records
- Check device_id/parameter_name values

---

**Last Updated:** January 23, 2026

