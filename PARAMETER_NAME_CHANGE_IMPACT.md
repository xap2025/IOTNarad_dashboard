# ⚠️ Parameter Name Change - Impact on Analytics Page

## 🎯 Scenario

**Initial Setup (T=0):**
- 2 enabled 4-20mA Input channels
- Channel 1: Name = **"current"** (enabled)
- Channel 2: Name = **"voltage"** (enabled)

**After 15 minutes (T=15min):**
- Names change kar diye
- Channel 1: Name = **"temperature"** (enabled)
- Channel 2: Name = **"pressure"** (enabled)

**Question:** 
1. 1 hour time range select karne par UI par kya dikhega?
2. 45 minutes baad check karne par kya dikhega?

---

## 📊 How Data is Stored

### **Database Structure (InfluxDB)**

Data `parameter_name` ke saath **TAG** ke roop mein save hota hai:

```python
Point("Realtime_Data")
  .tag("device_id", "DEV001")
  .tag("data_type", "Analog")
  .tag("parameter_name", "current")    # ← TAG (exact match required)
  .field("value", 4.5)
  .time(timestamp)
```

**Important:** `parameter_name` ek **TAG** hai, isliye:
- Query mein exact match chahiye
- Different names = Different data series
- Name change = New data series (purana data disconnect ho jata hai)

---

## 🔍 What Happens When Parameter Name Changes

### **Timeline:**

```
T=0 min:     Configuration saved
             Channel 1: name="current"
             Channel 2: name="voltage"
             
T=0-15 min:  Data arrives → Saved as:
             - parameter_name="current"  (Channel 1 data)
             - parameter_name="voltage"   (Channel 2 data)

T=15 min:    Configuration changed
             Channel 1: name="temperature"
             Channel 2: name="pressure"
             
T=15-60 min: Data arrives → Saved as:
             - parameter_name="temperature"  (Channel 1 data)
             - parameter_name="pressure"    (Channel 2 data)
```

### **Database State:**

**InfluxDB mein data:**

```
Measurement: Realtime_Data

Records with parameter_name="current":
  - T=0min: value=4.2
  - T=5min: value=4.3
  - T=10min: value=4.4
  - T=15min: value=4.5  ← Last record with "current"

Records with parameter_name="temperature":
  - T=15min: value=25.0  ← First record with "temperature"
  - T=20min: value=25.5
  - T=25min: value=26.0
  ... (continues)

Records with parameter_name="voltage":
  - T=0min: value=12.0
  - T=5min: value=12.1
  - T=10min: value=12.2
  - T=15min: value=12.3  ← Last record with "voltage"

Records with parameter_name="pressure":
  - T=15min: value=1013.0  ← First record with "pressure"
  - T=20min: value=1013.5
  ... (continues)
```

---

## 📱 UI Behavior

### **Step 1: Analytics Page Load**

**When:** User Analytics page par device select karta hai

**Process:**
1. `load_enabled_parameters()` callback trigger hota hai
2. **CURRENT** configuration fetch hoti hai (latest from database)
3. Enabled parameters list banata hai:
   ```python
   enabled_params = {
       "temperature": "Analog",  # ← Current name
       "pressure": "Analog"      # ← Current name
   }
   ```
4. Charts create hote hain:
   - Chart 1: "temperature"
   - Chart 2: "pressure"

**Important:** Analytics page sirf **CURRENT** configuration use karta hai, purani configuration nahi.

---

### **Scenario 1: 1 Hour Time Range Select (T=60min)**

**Time Range:** Last 1 hour (T=0 to T=60min)

**What Happens:**

#### **A. Chart 1: "temperature"**

**Query:**
```flux
from(bucket: "iotnarad-bucket")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "Realtime_Data")
  |> filter(fn: (r) => r.device_id == "DEV001")
  |> filter(fn: (r) => r.parameter_name == "temperature")  ← Current name
```

**Result:**
- ✅ **Data Found:** T=15min to T=60min (last 45 minutes)
- ❌ **No Data:** T=0 to T=15min (purana data "current" name se hai)

**Chart Display:**
- **Graph:** Shows data from T=15min onwards only
- **Live Value:** Latest value from "temperature" (if available)
- **Gap:** T=0 to T=15min mein koi data nahi dikhega (empty graph ya gap)

**Visual:**
```
Chart: "temperature"
Time:  [0min]----[15min]========[60min]
Data:  [NO DATA] [DATA STARTS] [DATA CONTINUES]
       └─ Gap ─┘ └─── 45 min data ───┘
```

#### **B. Chart 2: "pressure"**

**Query:**
```flux
|> filter(fn: (r) => r.parameter_name == "pressure")  ← Current name
```

**Result:**
- ✅ **Data Found:** T=15min to T=60min (last 45 minutes)
- ❌ **No Data:** T=0 to T=15min (purana data "voltage" name se hai)

**Chart Display:**
- **Graph:** Shows data from T=15min onwards only
- **Live Value:** Latest value from "pressure" (if available)
- **Gap:** T=0 to T=15min mein koi data nahi dikhega

**Visual:**
```
Chart: "pressure"
Time:  [0min]----[15min]========[60min]
Data:  [NO DATA] [DATA STARTS] [DATA CONTINUES]
       └─ Gap ─┘ └─── 45 min data ───┘
```

#### **Summary:**

**UI Display:**
- ✅ 2 charts show honge: "temperature" aur "pressure"
- ✅ Har chart mein last 45 minutes ka data dikhega
- ❌ First 15 minutes ka data **MISSING** dikhega (gap in graph)
- ❌ "current" aur "voltage" charts show nahi honge (purane names)

**Why?**
- Analytics page sirf CURRENT configuration se enabled parameters load karta hai
- Query sirf CURRENT parameter names se karta hai
- Purane names ("current", "voltage") ab enabled parameters list mein nahi hain

---

### **Scenario 2: 45 Minutes Later Check (T=60min)**

**Time:** 45 minutes after name change (T=60min total)

**What Happens:**

Same as Scenario 1, kyunki:
- Analytics page har baar CURRENT configuration load karta hai
- Enabled parameters list: `{"temperature": "Analog", "pressure": "Analog"}`
- Query sirf "temperature" aur "pressure" se karta hai

**UI Display:**
- ✅ 2 charts: "temperature" aur "pressure"
- ✅ Har chart mein T=15min to T=60min ka data (45 minutes)
- ❌ T=0 to T=15min ka data missing (gap)

**Important:** Time pass hone se kuch nahi hoga - purana data ab bhi show nahi hoga kyunki:
- Purane names ("current", "voltage") ab configuration mein nahi hain
- Query sirf current names se karta hai

---

## 🔍 Code Flow

### **Step 1: Load Enabled Parameters**

**File:** `app/pages/analytics.py` (line 185)

```python
def load_enabled_parameters(device_id):
    # Get CURRENT configuration
    analog_config = db_service.get_analog_config(device_id)
    
    # Filter enabled parameters
    for channel in analog_config.get('input_4_20ma', []):
        if channel.get('enabled', False):
            name = channel.get('name')  # ← CURRENT name
            enabled_params[name] = 'Analog'
    
    # Result: enabled_params = {"temperature": "Analog", "pressure": "Analog"}
    # Note: "current" aur "voltage" ab list mein nahi hain
```

### **Step 2: Query Data**

**File:** `app/pages/analytics.py` (line 471)

```python
for param_name in enabled_params:  # ["temperature", "pressure"]
    data_points = db_service.get_realtime_data(
        device_id=device_id,
        parameter_name=param_name,  # ← "temperature" or "pressure"
        start_time=start_time,      # ← 1 hour ago
        end_time=end_time
    )
```

**File:** `app/services/realtime_data_db.py` (line 241)

```flux
|> filter(fn: (r) => r.parameter_name == "temperature")  ← Exact match
```

**Result:**
- Sirf "temperature" name se data milta hai
- "current" name se data nahi milta (different tag)

---

## ⚠️ Important Limitations

### **1. Historical Data Disconnect**

**Problem:**
- Parameter name change karne se historical data disconnect ho jata hai
- Purana data purane name se save hai
- Naya data naye name se save hota hai
- Analytics page sirf current names se query karta hai

**Impact:**
- Historical charts mein gaps dikhenge
- Purane data show nahi hoga
- Data continuity break ho jati hai

### **2. No Automatic Mapping**

**Current Behavior:**
- System automatically purane name ko naye name se map nahi karta
- Har name ek alag data series hai
- Manual mapping required agar purana data chahiye

### **3. Configuration-Based Display**

**How It Works:**
- Analytics page har baar **CURRENT** configuration load karta hai
- Purani configuration use nahi hoti
- Sirf enabled parameters show hote hain (current names)

---

## 💡 Solutions & Workarounds

### **Option 1: Don't Change Parameter Names**

**Best Practice:**
- Parameter names ko change na karein
- Agar change karna hi hai, toh pehle plan karein
- Historical data continuity maintain karein

### **Option 2: Use Alias/Mapping**

**If Needed:**
- Database query modify karein to support name aliases
- Mapping table maintain karein:
  ```python
  name_mapping = {
      "temperature": ["temperature", "current"],  # New name → Old names
      "pressure": ["pressure", "voltage"]
  }
  ```
- Query mein multiple names check karein

**Implementation Required:**
- Code modification needed
- Database query logic change

### **Option 3: Manual Data Migration**

**If Historical Data Needed:**
- InfluxDB query manually run karein
- Purane name se data fetch karein
- Naye name se data merge karein
- Data reprocess karein

**Complexity:** High
**Time:** Manual effort required

---

## 📊 Visual Example

### **Timeline View:**

```
Time:     0min    15min    30min    45min    60min
         ────────┼────────┼────────┼────────┼────────
         
Config:   current,voltage  →  temperature,pressure
         ────────┼────────┼────────┼────────┼────────
         
Data:
  "current":     ████████░░░░░░░░░░░░░░░░░░░░░░░░░░
  "voltage":     ████████░░░░░░░░░░░░░░░░░░░░░░░░░░
  "temperature": ░░░░░░░░███████████████████████████
  "pressure":    ░░░░░░░░███████████████████████████
                └─ Old ─┘└─────── New ────────────┘

Analytics UI (1h range):
  temperature:   [GAP]███████████████████████████
  pressure:      [GAP]███████████████████████████
                └─ Missing ─┘└─── Visible ────────┘
```

### **Chart Display:**

**Chart 1: "temperature"**
```
Value
  │
  │     ╱╲
  │    ╱  ╲
  │   ╱    ╲
  │  ╱      ╲
  │ ╱        ╲
  │╱          ╲
  └─────────────── Time
  0min  15min  60min
  └─Gap─┘└──Data──┘
```

**Chart 2: "pressure"**
```
Value
  │
  │     ╱╲
  │    ╱  ╲
  │   ╱    ╲
  │  ╱      ╲
  │ ╱        ╲
  │╱          ╲
  └─────────────── Time
  0min  15min  60min
  └─Gap─┘└──Data──┘
```

---

## ✅ Summary

### **Question 1: 1 Hour Time Range Select**

**Answer:**
- ✅ 2 charts dikhenge: "temperature" aur "pressure"
- ✅ Har chart mein **last 45 minutes** ka data dikhega (T=15min to T=60min)
- ❌ **First 15 minutes** ka data **MISSING** dikhega (gap in graph)
- ❌ "current" aur "voltage" charts show nahi honge

**Reason:**
- Analytics page sirf CURRENT configuration use karta hai
- Query sirf current parameter names ("temperature", "pressure") se karta hai
- Purane names ("current", "voltage") ab enabled parameters list mein nahi hain

---

### **Question 2: 45 Minutes Later Check**

**Answer:**
- ✅ Same result: 2 charts ("temperature", "pressure")
- ✅ Har chart mein **45 minutes** ka data dikhega (T=15min to T=60min)
- ❌ **First 15 minutes** ka data ab bhi **MISSING** rahega

**Reason:**
- Time pass hone se kuch nahi hoga
- Analytics page har baar CURRENT configuration load karta hai
- Purane data ab bhi show nahi hoga kyunki purane names configuration mein nahi hain

---

## 🔑 Key Takeaways

1. **Parameter names are critical:** Name change = Data disconnect
2. **Current configuration only:** Analytics page sirf current config use karta hai
3. **Historical gaps:** Name change se historical charts mein gaps aayenge
4. **No automatic mapping:** System automatically purane name ko naye name se map nahi karta
5. **Best practice:** Parameter names ko change na karein, ya pehle plan karein

---

## 📝 Code References

- **Load Parameters:** `app/pages/analytics.py` (line 185)
- **Query Data:** `app/services/realtime_data_db.py` (line 198)
- **Data Storage:** `app/services/realtime_data_db.py` (line 50)

