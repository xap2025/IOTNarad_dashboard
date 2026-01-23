# 🔧 Database Cleanup - Corrected Queries

## ✅ Corrected Flux Queries

### **Step 1: Check Existing Records (Count)**

```bash
docker exec -it iotnarad_influxdb influx query --org iot-narad-gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== 'from(bucket: "iot_data_gcp") |> range(start: -30d) |> filter(fn: (r) => r._measurement == "Realtime_Data") |> filter(fn: (r) => r.device_id == "8C4B144D3274") |> filter(fn: (r) => r.parameter_name == "pump" or r.parameter_name == "hydrolic") |> count()'
```

**Note:** Flux mein `OR` nahi, `or` (lowercase) use karein.

---

### **Step 2: Delete Digital Records (pump & hydrolic)**

```bash
docker exec -it iotnarad_influxdb influx delete --org iot-narad-gcp --bucket iot_data_gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== --start 1970-01-01T00:00:00Z --stop 2100-01-01T00:00:00Z --predicate '_measurement="Realtime_Data" AND device_id="8C4B144D3274" AND (parameter_name="pump" OR parameter_name="hydrolic")'
```

**Note:** `influx delete` command mein predicate syntax different hai - yahan `OR` (uppercase) use karein.

---

### **Step 3: Verify Deletion (Should return 0)**

```bash
docker exec -it iotnarad_influxdb influx query --org iot-narad-gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== 'from(bucket: "iot_data_gcp") |> range(start: -30d) |> filter(fn: (r) => r._measurement == "Realtime_Data") |> filter(fn: (r) => r.device_id == "8C4B144D3274") |> filter(fn: (r) => r.parameter_name == "pump" or r.parameter_name == "hydrolic") |> count()'
```

---

## 📋 How Data is Saved (From Code)

**File:** `app/services/realtime_data_db.py` - Lines 117-122

```python
point = Point("Realtime_Data") \
    .tag("device_id", device_id) \           # Tag: "8C4B144D3274"
    .tag("data_type", data_type) \           # Tag: "Digital"
    .tag("parameter_name", parameter_name) \ # Tag: "pump" or "hydrolic"
    .field("value", field_value) \           # Field: 1 or 0 (integer)
    .time(timestamp, WritePrecision.NS)
```

**Structure:**
- **Measurement:** `Realtime_Data`
- **Tags:** `device_id`, `data_type`, `parameter_name`
- **Field:** `value` (integer: 1 or 0 for Digital)

---

## 🎯 Alternative: Delete All Digital Records for Device

Agar sirf Digital type ke records delete karne hain:

```bash
docker exec -it iotnarad_influxdb influx delete --org iot-narad-gcp --bucket iot_data_gcp --token YJrPDGIfrM9ql_fZWyeNFOp-MEr0vC5XmQPW1eR7dCoNCAi72ZjjrpFt63CHPF1DrhEaW9O67ZYsUMPTDc57rg== --start 1970-01-01T00:00:00Z --stop 2100-01-01T00:00:00Z --predicate '_measurement="Realtime_Data" AND device_id="8C4B144D3274" AND data_type="Digital"'
```

---

## ⚠️ Important Notes

1. **Flux Query (`influx query`):** Use lowercase `or`
2. **Delete Predicate (`influx delete`):** Use uppercase `OR`
3. **Tag Names:** `device_id`, `data_type`, `parameter_name` (as saved in code)
4. **Field Name:** `value` (the actual data)

---

**Last Updated:** January 23, 2026

