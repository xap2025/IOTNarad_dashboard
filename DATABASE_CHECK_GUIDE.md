# Database Check Guide - InfluxDB Cloud

## ❌ Problem in Screenshot:
Query language "SQL" select hai, lekin aap Flux query run kar rahe hain.

## ✅ Solution:

### Step 1: Query Language Change Karein
1. Query editor ke **right side** me "SQL" label dikh raha hai
2. Usko click karein ya dropdown me se **"Flux"** select karein

### Step 2: Correct Flux Query Run Karein
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "User_info")
```

### Step 3: Results Dekhein
- Agar users hain, table me dikhenge
- Agar koi user nahi hai, "No Results" dikhega

---

## Alternative: Simple Query (Agar above nahi work kare)

### Option 1: Schema Browser se
1. Left sidebar me **Schema Browser** me jayein
2. **Bucket**: `iot_data_gcp` select karein
3. **Measurement**: `User_info` click karein
4. Automatic query generate hoga

### Option 2: Basic Query
```flux
from(bucket: "iot_data_gcp")
  |> range(start: -1d)
  |> filter(fn: (r) => r._measurement == "User_info")
```

---

## Quick Check via Dashboard (Easier Method)

1. Dashboard me login karein: `http://localhost:8050`
2. **Settings** tab click karein
3. **Users List** table me sabhi users dikhenge automatically
4. Agar koi user nahi hai, "No users found" message dikhega

---

## Check via Docker Command

```powershell
docker exec iotnarad_app python -c "from app.services.user_service import UserService; s=UserService(); u=s.get_all_users(); print(f'Total: {len(u)} users'); [print(f\"{i+1}. {x.get('User_Id')} - {x.get('Email_Id')} - {x.get('Company_Name')}\") for i,x in enumerate(u)]"
```

---

**Main Fix**: Query language ko "SQL" se "Flux" me change karein!

