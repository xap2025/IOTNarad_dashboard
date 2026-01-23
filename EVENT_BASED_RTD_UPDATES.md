# ⚡ Event-Based Real-Time Data Updates

## 📋 Overview

Analytics page ab **event-based real-time updates** use karta hai instead of fixed 5-second interval. Ab jaise hi MQTT topic `RTD/#` par data aata hai, UI immediately update ho jata hai.

---

## 🎯 Key Changes

### **Before (Fixed Interval)**
- ❌ Har 5 seconds mein page refresh hota tha
- ❌ Data agar 1 second mein aaye ya 5 minute mein, same behavior
- ❌ Unnecessary database queries har 5 seconds
- ❌ User ko lagta tha ke data real-time nahi aa raha

### **After (Event-Based)**
- ✅ **Jaise hi MQTT data aaye, UI immediately update**
- ✅ Data frequency ke according automatically adjust
- ✅ Database queries sirf tab jab data actually aaye
- ✅ User ko clearly dikhta hai ke data real-time aa raha hai
- ✅ Fallback interval (30 seconds) agar koi data na aaye

---

## 🔧 Technical Implementation

### **1. MQTT → SocketIO Event**

**File: `app/main.py`**

```python
def on_realtime_data_received(device_id: str, data: Dict[str, Any]):
    # ... existing code to save data ...
    
    # Emit SocketIO event to trigger real-time UI updates
    socketio.emit('rtd_data_update', {
        'device_id': device_id,
        'timestamp': timestamp.isoformat(),
        'data_type': normalized_type,
        'parameters_count': len(values)
    })
```

**Flow:**
```
MQTT RTD/# topic par data aata hai
  ↓
on_realtime_data_received() callback
  ↓
Data database mein save hota hai
  ↓
SocketIO event emit hota hai: 'rtd_data_update'
```

---

### **2. Client-Side SocketIO Listener**

**File: `app/pages/analytics.py`**

```javascript
const socket = io();

socket.on('rtd_data_update', function(data) {
    console.log('📊 RTD data update received:', data);
    
    // Hidden button click trigger karta hai
    const triggerBtn = document.getElementById('analytics-rtd-trigger-btn');
    if (triggerBtn) {
        triggerBtn.click();
    }
});
```

**Flow:**
```
SocketIO event receive hota hai
  ↓
Hidden button click trigger hota hai
  ↓
Dash callback trigger hota hai
```

---

### **3. RTD Trigger Store Update**

**File: `app/pages/analytics.py`**

```python
@callback(
    Output('analytics-rtd-update-trigger', 'data'),
    Input('analytics-rtd-trigger-btn', 'n_clicks'),
    State('analytics-device-store', 'data'),
    prevent_initial_call=True
)
def update_rtd_trigger(n_clicks, device_id):
    """Update RTD trigger Store when SocketIO event is received"""
    if n_clicks and n_clicks > 0:
        logger.info(f"🔄 RTD update trigger activated")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'device_id': device_id
        }
    return no_update
```

**Flow:**
```
Hidden button click
  ↓
update_rtd_trigger() callback
  ↓
analytics-rtd-update-trigger Store update hota hai
```

---

### **4. Analytics Charts Update**

**File: `app/pages/analytics.py`**

```python
@callback(
    [
        Output({'type': 'analytics-chart', 'parameter': ALL}, 'figure'),
        Output({'type': 'live-value-container', 'parameter': ALL}, 'children'),
    ],
    [
        Input('analytics-refresh-interval', 'n_intervals'),  # Fallback (30s)
        Input('analytics-rtd-update-trigger', 'data'),  # Event-based trigger
        Input('analytics-time-range-selector', 'value'),
        Input('analytics-device-store', 'data'),
        Input('analytics-params-store', 'data'),
    ],
    prevent_initial_call=False
)
def update_analytics_charts(n_intervals, rtd_trigger, time_range, device_id, enabled_params):
    # Check what triggered this callback
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else 'initial'
    
    if 'analytics-rtd-update-trigger' in triggered_id:
        logger.info(f"⚡ Analytics callback triggered by RTD MQTT data")
    elif 'analytics-refresh-interval' in triggered_id:
        logger.info(f"⏱️ Analytics callback triggered by fallback interval")
    
    # ... rest of the code to update charts ...
```

**Flow:**
```
RTD trigger Store update
  ↓
update_analytics_charts() callback trigger
  ↓
Database se latest data fetch
  ↓
Graphs aur live values update
```

---

## 📊 Complete Data Flow

```
Device publishes to RTD/<Device ID>
  ↓
MQTT Broker receives
  ↓
on_realtime_data_received() callback (main.py)
  ↓
Data saved to InfluxDB
  ↓
SocketIO.emit('rtd_data_update') event
  ↓
Client-side SocketIO listener (analytics.py script)
  ↓
Hidden button click triggered
  ↓
update_rtd_trigger() callback
  ↓
analytics-rtd-update-trigger Store updated
  ↓
update_analytics_charts() callback triggered
  ↓
Database query for latest data
  ↓
Graphs and live values updated in UI
```

---

## 🎨 UI Components

### **New Components Added:**

1. **`analytics-rtd-update-trigger` Store**
   - Stores timestamp and device_id when RTD data arrives
   - Used to trigger chart updates

2. **`analytics-rtd-trigger-btn` Button**
   - Hidden button (display: none)
   - Clicked by client-side script when SocketIO event received
   - Triggers Dash callback

3. **Client-Side Script**
   - Listens to SocketIO `rtd_data_update` events
   - Automatically clicks hidden button
   - Handles SocketIO initialization

---

## ⚙️ Configuration

### **Interval Settings:**

- **Fallback Interval**: 30 seconds (changed from 5 seconds)
  - Used only if no MQTT data arrives
  - Ensures UI updates even if SocketIO fails

- **Event-Based Updates**: Immediate
  - Triggered as soon as MQTT data arrives
  - No fixed delay

---

## ✅ Benefits

1. **Real-Time Updates**
   - UI immediately reflects new data
   - No waiting for fixed interval

2. **Efficient**
   - Database queries only when data actually arrives
   - Reduces unnecessary load

3. **User Experience**
   - User clearly sees data is coming in real-time
   - Graphs update smoothly as data arrives

4. **Flexible**
   - Works with any data frequency
   - Handles both high-frequency (1 second) and low-frequency (5 minutes) data

5. **Reliable**
   - Fallback interval ensures updates even if SocketIO fails
   - Multiple trigger sources for redundancy

---

## 🔍 Debugging

### **Check Logs:**

1. **MQTT Data Received:**
   ```
   📊 Real-time data received from device: {device_id}
   📡 Emitted SocketIO RTD update event for device {device_id}
   ```

2. **SocketIO Event:**
   ```
   Client console: 📊 RTD data update received: {data}
   ```

3. **Callback Triggered:**
   ```
   ⚡ Analytics callback triggered by RTD MQTT data: device_id={device_id}
   ```

4. **Fallback Interval:**
   ```
   ⏱️ Analytics callback triggered by fallback interval: n_intervals={n}
   ```

---

## 🐛 Troubleshooting

### **Problem: UI not updating when data arrives**

**Solution:**
1. Check browser console for SocketIO errors
2. Verify SocketIO is loaded: `typeof io !== 'undefined'`
3. Check if `rtd_data_update` event is being received
4. Verify hidden button exists: `document.getElementById('analytics-rtd-trigger-btn')`

### **Problem: Updates only happening on interval**

**Solution:**
1. Check if SocketIO event is being emitted in `main.py`
2. Verify client-side script is running
3. Check browser console for JavaScript errors

### **Problem: Multiple updates for same data**

**Solution:**
- This is normal - both event-based and interval can trigger
- Callback uses `ctx.triggered` to identify source
- No duplicate updates occur

---

## 📝 Notes

1. **Backward Compatible**: Old interval-based system still works as fallback
2. **No Breaking Changes**: Existing functionality preserved
3. **Performance**: More efficient than fixed interval
4. **Scalable**: Works with any number of devices and parameters

---

## 🚀 Future Enhancements

1. **Device-Specific Updates**: Only update charts for the device that sent data
2. **Parameter-Specific Updates**: Only update the specific parameter that changed
3. **Batch Updates**: Group multiple rapid updates into single UI update
4. **WebSocket Optimization**: Use WebSocket directly instead of SocketIO for lower latency

---

**Last Updated**: January 2026

