# Analytics Graph Update Flow - Detailed Explanation

## 📊 Graph Update Mechanism

### 1. **Auto-Refresh Component (dcc.Interval)**

```python
# Line 67 in analytics.py
dcc.Interval(id='analytics-refresh-interval', interval=5000, n_intervals=0)
```

**Kya hai:**
- Ye ek Dash component hai jo har **5 seconds** (5000 milliseconds) mein automatically trigger hota hai
- `n_intervals` har trigger par increment hota hai (0, 1, 2, 3, ...)
- Ye component browser mein client-side par run hota hai

**Kaise kaam karta hai:**
- Browser page load hote hi ye component start ho jata hai
- Har 5 seconds mein ye ek event trigger karta hai
- Ye event Dash callbacks ko trigger karta hai jo is component ko listen kar rahe hain

---

### 2. **Main Graph Update Callback**

```python
# Lines 455-467 in analytics.py
@callback(
    [
        Output({'type': 'analytics-chart', 'parameter': ALL}, 'figure'),
        Output({'type': 'live-value-container', 'parameter': ALL}, 'children'),
    ],
    [
        Input('analytics-refresh-interval', 'n_intervals'),      # ⏰ Har 5 seconds trigger
        Input('analytics-time-range-selector', 'value'),          # ⏱️ Time range change
        Input('analytics-device-store', 'data'),                 # 📱 Device change
        Input('analytics-params-store', 'data'),                 # 📊 Parameters change
    ],
    prevent_initial_call=False  # ✅ Page load par bhi run karega
)
def update_analytics_charts(n_intervals, time_range, device_id, enabled_params):
    """Update all charts with real-time data"""
```

**Callback Trigger Events:**

#### **Event 1: Auto-Refresh (Har 5 seconds)**
- **Trigger:** `analytics-refresh-interval` component ka `n_intervals` increment hota hai
- **Frequency:** Har 5 seconds
- **Action:** 
  - Current time recalculate hota hai
  - Database se latest data fetch hota hai
  - Graphs update hote hain
  - Live values update hote hain

#### **Event 2: Time Range Change**
- **Trigger:** User dropdown se time range change karta hai (1h, 6h, 24h, etc.)
- **Action:**
  - X-axis range recalculate hota hai
  - Historical data fetch hota hai
  - Graphs refresh hote hain

#### **Event 3: Device Change**
- **Trigger:** User device selector se device change karta hai
- **Action:**
  - New device ke parameters load hote hain
  - Graphs recreate hote hain
  - Data fetch hota hai

#### **Event 4: Parameters Change**
- **Trigger:** `load_enabled_parameters` callback se parameters update hote hain
- **Action:**
  - New parameters ke liye graphs create hote hain
  - Old parameters ke graphs remove hote hain

---

### 3. **Complete Flow Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                    PAGE LOAD / INITIAL                        │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Callback 1: load_enabled_parameters()                      │
│  - Device selector change                                   │
│  - Time range selector change                               │
│  Output:                                                    │
│    - analytics-device-store (device_id)                     │
│    - analytics-params-store (parameters + metadata)         │
│    - analytics-charts-container (chart components)         │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  dcc.Interval Component                                     │
│  - interval=5000 (5 seconds)                                │
│  - n_intervals increments: 0 → 1 → 2 → 3 ...              │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼ (Har 5 seconds)
┌─────────────────────────────────────────────────────────────┐
│  Callback 2: update_analytics_charts()                     │
│  Inputs:                                                     │
│    ✓ analytics-refresh-interval (n_intervals)              │
│    ✓ analytics-time-range-selector (time_range)            │
│    ✓ analytics-device-store (device_id)                     │
│    ✓ analytics-params-store (enabled_params)               │
│                                                              │
│  Process:                                                    │
│    1. Calculate current time (UTC)                          │
│    2. Calculate start_time = end_time - time_range          │
│    3. Convert UTC to IST for display                        │
│    4. Query database for data                              │
│    5. Filter data based on active periods                   │
│    6. Create/update Plotly figures                        │
│    7. Update live values                                    │
│                                                              │
│  Output:                                                     │
│    - All chart figures (updated)                            │
│    - All live value displays (updated)                     │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  Browser Updates UI                                         │
│  - Graphs refresh with new data                             │
│  - X-axis shifts to show current time range                │
│  - Live values update                                       │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼ (Repeat after 5 seconds)
                    [LOOP BACK]
```

---

### 4. **Detailed Step-by-Step Process**

#### **Step 1: Interval Component Triggers**
```python
# Browser mein ye component har 5 seconds mein trigger hota hai
dcc.Interval(id='analytics-refresh-interval', interval=5000, n_intervals=0)
# n_intervals: 0 → 1 → 2 → 3 → 4 → ...
```

#### **Step 2: Callback Receives Inputs**
```python
def update_analytics_charts(n_intervals, time_range, device_id, enabled_params):
    # n_intervals: Current count (0, 1, 2, ...)
    # time_range: Selected time range ('1h', '6h', etc.)
    # device_id: Selected device ID
    # enabled_params: Dictionary of parameters with metadata
```

#### **Step 3: Time Calculation**
```python
# Current time calculate karo (UTC)
end_time_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

# Start time calculate karo based on time_range
if time_range == '1h':
    start_time_utc = end_time_utc - timedelta(hours=1)
# ... other ranges

# Convert to IST for display
ist = pytz.timezone('Asia/Kolkata')
start_time = start_time_utc.astimezone(ist)
end_time = end_time_utc.astimezone(ist)
```

#### **Step 4: Database Query**
```python
# Database se data fetch karo (UTC times use karo)
all_data = db_service.get_realtime_data_multiple_params(
    device_id=device_id,
    parameter_names=param_names,
    start_time=start_time_utc,  # UTC
    end_time=end_time_utc       # UTC
)
```

#### **Step 5: Data Processing**
```python
# Har parameter ke liye:
for param_name, param_type in zip(param_names, param_types):
    # Data points get karo
    data_points = all_data.get(clean_param_name, [])
    
    # Active periods ke basis par filter karo
    # Timestamps ko UTC se IST mein convert karo
    
    # Latest value calculate karo
    latest_value = data_points[-1].get('value') if data_points else None
```

#### **Step 6: Graph Creation**
```python
# Plotly figure create karo
fig = go.Figure()

# Data trace add karo
fig.add_trace(go.Scatter(
    x=timestamps,  # IST timestamps
    y=values,
    ...
))

# X-axis range set karo (IST times)
fig.update_xaxes(
    range=[start_time, end_time],  # IST times
    autorange=False,
    dtick=dtick_string,
    tickformat=tick_format
)
```

#### **Step 7: Return Updated Figures**
```python
# Updated figures return karo
return figures, live_values
# Dash automatically UI update karta hai
```

---

### 5. **Other Related Callbacks**

#### **Callback 3: Device Status Update**
```python
@callback(
    Output('device-status-container', 'children'),
    [
        Input('analytics-refresh-interval', 'n_intervals'),  # Har 5 seconds
        Input('analytics-device-store', 'data'),
    ]
)
def update_device_status(n_intervals, device_id):
    # Device running hai ya nahi check karta hai
    # Status badge update karta hai
```

**Trigger:** Har 5 seconds (same interval component)

---

### 6. **Key Points**

✅ **Auto-Refresh:** Har 5 seconds mein automatic update
✅ **Manual Triggers:** Time range ya device change par bhi update
✅ **Real-time:** Current time se exactly 1 hour pehle se data dikhata hai
✅ **Dynamic X-axis:** Har update par X-axis range shift hota hai
✅ **Efficient:** Batch query se sabhi parameters ka data ek saath fetch hota hai

---

### 7. **Timeline Example**

```
Time: 16:27:00 IST
├─ Interval triggers (n_intervals = 100)
├─ Callback executes
├─ Current time: 16:27:00 IST (10:57:00 UTC)
├─ X-axis range: 15:27:00 IST to 16:27:00 IST
├─ Database query: 10:57:00 UTC - 1 hour
├─ Data fetched and converted to IST
├─ Graphs updated
└─ UI refreshed

[Wait 5 seconds]

Time: 16:27:05 IST
├─ Interval triggers (n_intervals = 101)
├─ Callback executes
├─ Current time: 16:27:05 IST (10:57:05 UTC)
├─ X-axis range: 15:27:05 IST to 16:27:05 IST
├─ Database query: 10:57:05 UTC - 1 hour
├─ Data fetched and converted to IST
├─ Graphs updated (X-axis shifted by 5 seconds)
└─ UI refreshed
```

---

### 8. **Why This Design?**

1. **Real-time Updates:** Har 5 seconds mein fresh data
2. **User Control:** Time range change karne par instant update
3. **Efficient:** Batch queries se performance better
4. **Responsive:** Multiple triggers se flexible updates
5. **Accurate:** Current time se exact calculation

---

## Summary

**Graph update kaise hota hai:**
1. `dcc.Interval` component har 5 seconds mein trigger hota hai
2. `update_analytics_charts` callback execute hota hai
3. Current time calculate hota hai
4. Database se latest data fetch hota hai
5. Data process hota hai (filter, convert timezone)
6. Plotly figures create/update hote hain
7. UI automatically refresh hota hai

**Graph kab update hota hai:**
- ✅ Har 5 seconds (automatic)
- ✅ Time range change par (manual)
- ✅ Device change par (manual)
- ✅ Page load par (initial)

**Graph kya listen karta hai:**
- `analytics-refresh-interval` (n_intervals)
- `analytics-time-range-selector` (time_range)
- `analytics-device-store` (device_id)
- `analytics-params-store` (enabled_params)

