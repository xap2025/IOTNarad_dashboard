# 🔧 Callback Architecture Guide

## 📋 Current Structure

### **main.py** - Central Router & Auth
- ✅ **Routing callbacks** - Handle page navigation
- ✅ **Authentication callbacks** - Login/logout logic
- ✅ **Session management** - User session handling
- ✅ **Initial app setup** - Dash app initialization

### **pages/dashboard.py** - Dashboard Page
- ✅ **Layout function** - `create_dashboard_layout()`
- ✅ **Page-specific callbacks** - All dashboard callbacks using `@callback`
- ✅ Examples:
  - Clock update callback
  - Username display callback
  - Page navigation callbacks
  - Content update callbacks

### **pages/analytics.py** - Analytics Page
- ✅ **Layout function** - `create_analytics_layout()`
- ✅ **Page-specific callbacks** - Analytics-related callbacks

### **Other pages follow same pattern**

---

## 🎯 How Callbacks Work in Dash

### **Two Ways to Register Callbacks:**

#### **1. Using `@app.callback` (in main.py)**
```python
@app.callback(
    Output('output-id', 'property'),
    Input('input-id', 'property')
)
def my_callback(input_value):
    return output_value
```
- Used in `main.py` for routing/auth
- Directly references `app` instance

#### **2. Using `@callback` (in page files)**
```python
from dash import callback

@callback(
    Output('output-id', 'property'),
    Input('input-id', 'property')
)
def my_callback(input_value):
    return output_value
```
- Used in `app/pages/*.py` files
- Automatically registered when page is imported
- **Requires `suppress_callback_exceptions=True`** in Dash app

---

## ✅ Best Practices

### **✅ DO:**
1. **Keep routing/auth callbacks in main.py**
   - Centralized control
   - Easy to debug

2. **Keep page callbacks in their own files**
   - `dashboard.py` → dashboard callbacks
   - `analytics.py` → analytics callbacks
   - Separation of concerns

3. **Use `@callback` decorator in page files**
   - Automatic registration
   - No need to pass app instance

4. **Import pages in main.py**
   - Callbacks get registered when files are imported
   - `from app.pages.dashboard import create_dashboard_layout`

### **❌ DON'T:**
1. Don't mix page callbacks in main.py
2. Don't use `@app.callback` in page files (unless you pass app instance)
3. Don't create circular imports

---

## 🔄 How It Works

1. **App starts** → `main.py` runs
2. **Dash app created** → `suppress_callback_exceptions=True`
3. **Pages imported** → `from app.pages.dashboard import ...`
4. **Callbacks registered** → `@callback` decorators execute
5. **User navigates** → `main.py` routing callback loads page layout
6. **Page callbacks active** → All callbacks work automatically

---

## 🐛 Current Issue Fixes Applied

### **1. html.Style Error**
- ❌ **Problem:** `html.Style()` doesn't exist in Dash
- ✅ **Solution:** 
  - Moved CSS to `assets/sidebar.css`
  - Added `assets_folder='../assets'` in Dash app
  - CSS automatically loaded

### **2. Routing Issue**
- ❌ **Problem:** Dashboard showing at root `/` instead of login
- ✅ **Solution:**
  - Fixed `display_page()` callback to show login at root
  - Improved redirect callback logic
  - Better pathname handling

### **3. Callback Registration**
- ✅ **Already working correctly:**
  - Using `@callback` in page files
  - `suppress_callback_exceptions=True` set
  - Callbacks auto-register on import

---

## 📝 Example Structure

```python
# app/main.py
app = dash.Dash(suppress_callback_exceptions=True)

@app.callback(...)  # Routing callback
def display_page(...):
    return create_dashboard_layout()

# app/pages/dashboard.py  
from dash import callback

@callback(...)  # Page callback - auto-registers!
def update_time(...):
    return current_time
```

---

## 🚀 Testing

After changes:
1. Restart Docker container: `docker-compose restart app`
2. Check logs: `docker-compose logs -f app`
3. Visit: `http://localhost:8050/` → Should show login
4. After login → Redirects to `/dashboard`

---

**Last Updated:** 2025-10-29

