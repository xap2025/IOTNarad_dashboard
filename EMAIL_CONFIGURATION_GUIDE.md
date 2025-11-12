# 📧 Email Configuration Guide - Xaptronics Email Setup

## 🎯 Goal
Configure email service to send emails from `info@xaptronics.com`

---

## 📋 Required Information

Aapko yeh information chahiye:

### 1. Email Provider Details
- **Email Provider**: Xaptronics ka email provider kya hai?
  - Google Workspace (Gmail for Business)?
  - Microsoft 365 (Outlook)?
  - Custom email server?
  - Other (Zoho, etc.)?

### 2. SMTP Settings
Agar aapko email provider pata hai, toh yeh settings chahiye:

**For Google Workspace (Gmail Business):**
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=info@xaptronics.com
SMTP_PASSWORD=<App Password>  (See Step 3 below)
```

**For Microsoft 365 (Outlook Business):**
```
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=info@xaptronics.com
SMTP_PASSWORD=<Your Email Password>
```

**For Custom Email Server:**
```
SMTP_SERVER=<your-server.com> (e.g., mail.xaptronics.com)
SMTP_PORT=587 (or 465 for SSL)
SMTP_USERNAME=info@xaptronics.com
SMTP_PASSWORD=<email password>
```

---

## 🔧 Step-by-Step Configuration

### Step 1: Email Provider Identify Karein

**Option A: Google Workspace (Gmail Business)**
- Agar aap `@xaptronics.com` ke liye Google Workspace use karte hain
- SMTP: `smtp.gmail.com:587`

**Option B: Microsoft 365 (Outlook Business)**
- Agar aap `@xaptronics.com` ke liye Microsoft 365 use karte hain
- SMTP: `smtp.office365.com:587`

**Option C: Custom Email Server**
- Agar aap custom email server use karte hain
- Contact your IT team for SMTP settings

---

### Step 2: Email Password / App Password Generate Karein

**For Google Workspace:**
1. Login karein: https://admin.google.com/
2. Go to: Security → App Passwords
3. Generate new App Password
4. Copy password (16 characters)

**For Microsoft 365:**
1. Login karein: https://admin.microsoft.com/
2. Go to: Settings → Mail → App passwords
3. Generate new App Password

**For Custom Server:**
- Use your regular email password

---

### Step 3: .env File Me Configuration Add Karein

Create or update `.env` file in project root:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=info@xaptronics.com
SMTP_PASSWORD=your-app-password-here
FROM_EMAIL=info@xaptronics.com
FROM_NAME=Xaptronics IOTNarad
```

**Important**: `.env` file ko `.gitignore` me add karein (security ke liye)

---

### Step 4: Docker Compose Me Environment Variables Add Karein

If using Docker, update `docker-compose.yml`:

```yaml
services:
  app:
    environment:
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - FROM_EMAIL=${FROM_EMAIL}
      - FROM_NAME=${FROM_NAME}
```

---

### Step 5: Test Email Configuration

```powershell
# Test email service
docker exec iotnarad_app python -c "from app.services.email_service import EmailService; e=EmailService(); print('Configured:', e.configured); print('Server:', e.smtp_server); print('Port:', e.smtp_port); print('Username:', e.smtp_username)"
```

---

## 🔍 Troubleshooting

### Issue 1: "Authentication failed"
**Solution**: 
- Check if App Password sahi hai (Google Workspace ke liye)
- Check if email password sahi hai
- For Google: Make sure "Less secure app access" enabled hai (if not using App Password)

### Issue 2: "Connection timeout"
**Solution**:
- Check SMTP server address
- Check port (587 for TLS, 465 for SSL)
- Check firewall settings

### Issue 3: "Email sending failed"
**Solution**:
- Check server logs: `docker compose logs app | grep -i email`
- Verify SMTP credentials
- Test SMTP connection manually

---

## 📝 Quick Setup Commands

### 1. Create/Update .env file:
```powershell
# Add these lines to .env file
echo SMTP_SERVER=smtp.gmail.com >> .env
echo SMTP_PORT=587 >> .env
echo SMTP_USERNAME=info@xaptronics.com >> .env
echo SMTP_PASSWORD=your-password >> .env
echo FROM_EMAIL=info@xaptronics.com >> .env
echo FROM_NAME=Xaptronics IOTNarad >> .env
```

### 2. Restart Docker:
```powershell
docker compose down
docker compose up -d
```

### 3. Test Email:
```powershell
docker compose logs app | Select-String -Pattern "Email|SMTP"
```

---

## 🎯 Next Steps

1. **Identify your email provider** (Google/Microsoft/Custom)
2. **Get SMTP settings** from IT team or email provider
3. **Generate App Password** (if using Google Workspace)
4. **Update .env file** with correct settings
5. **Restart Docker** containers
6. **Test email** by creating a new user

---

## 📞 Need Help?

Agar aapko email provider details nahi pata, toh:
1. IT team se contact karein
2. Email provider se SMTP settings request karein
3. Company email admin se help lein

---

**After configuration, test karein:**
1. Create a new user
2. Check if email is sent successfully
3. Check inbox/spam folder

