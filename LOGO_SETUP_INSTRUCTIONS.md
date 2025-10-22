# 🏭 Logo Setup Instructions for IOTNarad Dashboard

## 📁 Where to Save Your Logo

Save your Xaptronics logo image file in this exact location:

```
📂 IOTNarad_dashboard/
  └── 📂 assets/
      └── 📂 images/
          └── 📄 xaptronics-logo.png  ← Save your logo here
```

**Full Path:** `C:\Users\ridhi\IOTNarad_dashboard\assets\images\xaptronics-logo.png`

## 📋 Logo Requirements

### ✅ Supported Formats:
- **PNG** (recommended - best quality)
- **JPG** (good for photos)
- **SVG** (scalable vector graphics)

### ✅ Recommended Specifications:
- **Size:** 200x200 pixels or larger
- **Background:** Transparent or white
- **File Size:** Under 500KB for best performance
- **Quality:** High resolution for crisp display

## 🚀 How to Set Up Your Logo

### Step 1: Save Your Logo
1. Copy your Xaptronics logo image file
2. Navigate to: `IOTNarad_dashboard\assets\images\`
3. Rename your logo file to: `xaptronics-logo.png`
4. Save it in the `assets\images\` folder

### Step 2: Restart the Application
```bash
# Restart Docker containers
docker-compose restart app

# Or restart all services
docker-compose down
docker-compose up -d
```

### Step 3: View Your Logo
1. Open browser: `http://localhost:8050`
2. Login with admin credentials
3. Your logo will appear in the left sidebar!

## 🎨 Logo Display Features

Your logo will be displayed with:
- **Size:** 120x120 pixels
- **Color:** White (automatically converted)
- **Position:** Centered in the sidebar
- **Fallback:** CSS logo if image fails to load

## 📱 Logo Layout in Sidebar

```
┌─────────────────────────┐
│     admin (User ID)     │
├─────────────────────────┤
│                         │
│    [Your Logo Image]    │  ← Your Xaptronics logo here
│                         │
│      Xaptronics         │
│   Possibilities Infinite│
│                         │
│      IOTNarad           │
│     IoT Dashboard       │
│                         │
└─────────────────────────┘
```

## 🔧 Troubleshooting

### Logo Not Showing?
1. **Check file name:** Must be exactly `xaptronics-logo.png`
2. **Check location:** Must be in `assets\images\` folder
3. **Check format:** Use PNG, JPG, or SVG
4. **Restart app:** Run `docker-compose restart app`

### Logo Looks Wrong?
1. **Size issues:** Use image editing software to resize to 200x200px
2. **Background issues:** Use PNG with transparent background
3. **Color issues:** Logo will be automatically converted to white

### Need Help?
1. Run the setup script: `python save_logo.py`
2. Check the logs: `docker-compose logs app`
3. Verify file exists: Check `assets\images\` folder

## 🎯 Quick Setup Commands

```bash
# 1. Navigate to project directory
cd C:\Users\ridhi\IOTNarad_dashboard

# 2. Check if logo folder exists
dir assets\images

# 3. Save your logo as: assets\images\xaptronics-logo.png

# 4. Restart the application
docker-compose restart app

# 5. Open dashboard
start http://localhost:8050
```

## ✅ Success Checklist

- [ ] Logo file saved as `xaptronics-logo.png`
- [ ] File is in `assets\images\` folder
- [ ] File size is under 500KB
- [ ] Docker containers restarted
- [ ] Dashboard shows your logo in sidebar
- [ ] Logo appears white and centered

---

**Your logo is now ready to display in the IOTNarad Dashboard! 🎉**
