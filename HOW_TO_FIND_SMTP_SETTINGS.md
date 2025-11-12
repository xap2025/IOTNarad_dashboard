# 🔍 How to Find Custom Email Server SMTP Settings

## 📋 Information You Need to Find:

1. **SMTP_SERVER** - Email server address
2. **SMTP_PORT** - Port number (usually 587, 465, or 25)
3. **SMTP_USERNAME** - Your email address
4. **SMTP_PASSWORD** - Your email password
5. **FROM_EMAIL** - Same as username (usually)
6. **FROM_NAME** - Display name (optional)

---

## 🎯 Method 1: Check Email Client Settings (Easiest)

### Outlook Desktop:
1. Open **Outlook**
2. Go to **File** → **Account Settings** → **Account Settings**
3. Select your email account
4. Click **Change**
5. Click **More Settings** → **Advanced** tab
6. Look for:
   - **Outgoing server (SMTP)**: `SMTP_SERVER`
   - **Port**: `SMTP_PORT`
   - **Account**: `SMTP_USERNAME`

### Thunderbird:
1. Open **Thunderbird**
2. Go to **Tools** → **Account Settings**
3. Select **Outgoing Server (SMTP)**
4. Click **Edit** on your SMTP server
5. Note:
   - **Server Name**: `SMTP_SERVER`
   - **Port**: `SMTP_PORT`
   - **Username**: `SMTP_USERNAME`

### Webmail (Check Settings):
1. Login to your webmail (e.g., cPanel, Roundcube, etc.)
2. Go to **Settings** → **Email Accounts**
3. Look for **SMTP Settings** or **Outgoing Mail Server**

---

## 🔧 Method 2: Check Email Provider Documentation

### Common Email Providers:

**cPanel/WHM:**
```
SMTP_SERVER = mail.yourdomain.com (or mail.xaptronics.com)
SMTP_PORT = 587 (TLS) or 465 (SSL)
SMTP_USERNAME = info@xaptronics.com
SMTP_PASSWORD = your-email-password
```

**Zoho Mail:**
```
SMTP_SERVER = smtp.zoho.com
SMTP_PORT = 587
SMTP_USERNAME = info@xaptronics.com
SMTP_PASSWORD = your-password
```

**SendGrid:**
```
SMTP_SERVER = smtp.sendgrid.net
SMTP_PORT = 587
SMTP_USERNAME = apikey
SMTP_PASSWORD = your-api-key
```

**Mailgun:**
```
SMTP_SERVER = smtp.mailgun.org
SMTP_PORT = 587
SMTP_USERNAME = your-mailgun-username
SMTP_PASSWORD = your-mailgun-password
```

---

## 📞 Method 3: Contact IT Team / Email Admin

**Ask them:**
1. What is the SMTP server address?
2. What port should be used? (587 for TLS, 465 for SSL, 25 for unencrypted)
3. Do I need authentication?
4. Is TLS/SSL required?
5. Are there any IP restrictions?

**Example Questions:**
```
Hi IT Team,

I need SMTP settings for info@xaptronics.com:
- SMTP server address
- SMTP port (587/465/25)
- Authentication requirements
- TLS/SSL settings

Thank you!
```

---

## 🔍 Method 4: DNS Lookup (Technical)

### Find Mail Server:
```powershell
# PowerShell command to find mail server
nslookup -type=MX xaptronics.com
```

**Output example:**
```
xaptronics.com   MX preference = 10, mail exchanger = mail.xaptronics.com
```

Then SMTP server would be: `mail.xaptronics.com`

### Test SMTP Connection:
```powershell
# Test SMTP port
Test-NetConnection mail.xaptronics.com -Port 587
Test-NetConnection mail.xaptronics.com -Port 465
Test-NetConnection mail.xaptronics.com -Port 25
```

---

## 🧪 Method 5: Test SMTP Settings Manually

### Using PowerShell:
```powershell
# Test SMTP connection
$smtpServer = "mail.xaptronics.com"
$smtpPort = 587
$username = "info@xaptronics.com"
$password = "your-password"

try {
    $smtp = New-Object System.Net.Mail.SmtpClient($smtpServer, $smtpPort)
    $smtp.EnableSsl = $true
    $smtp.Credentials = New-Object System.Net.NetworkCredential($username, $password)
    Write-Host "✅ SMTP connection successful!" -ForegroundColor Green
    $smtp.Dispose()
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}
```

### Using Python (if available):
```python
import smtplib

try:
    server = smtplib.SMTP('mail.xaptronics.com', 587)
    server.starttls()
    server.login('info@xaptronics.com', 'your-password')
    print("✅ SMTP connection successful!")
    server.quit()
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 📝 Common SMTP Ports & Settings

### Port 587 (TLS/STARTTLS) - Recommended:
```
SMTP_PORT = 587
Encryption: STARTTLS
Most secure and commonly used
```

### Port 465 (SSL):
```
SMTP_PORT = 465
Encryption: SSL/TLS
Legacy but still supported
```

### Port 25 (Unencrypted):
```
SMTP_PORT = 25
Encryption: None
Not recommended (often blocked by ISPs)
```

---

## 🎯 Step-by-Step Guide for Xaptronics

### Step 1: Check Current Email Setup
- Do you currently use Outlook/Thunderbird for `info@xaptronics.com`?
- If yes, check settings from Method 1 above

### Step 2: Check cPanel (if you have access)
1. Login to cPanel: `https://xaptronics.com/cpanel` (or your hosting URL)
2. Go to **Email Accounts**
3. Click on **Connect Devices** or **Configure Mail Client**
4. Look for **Outgoing Server (SMTP)** settings

### Step 3: Try Common Settings
If you have a custom domain email, try these:

**Option A:**
```
SMTP_SERVER = mail.xaptronics.com
SMTP_PORT = 587
SMTP_USERNAME = info@xaptronics.com
SMTP_PASSWORD = your-email-password
```

**Option B:**
```
SMTP_SERVER = smtp.xaptronics.com
SMTP_PORT = 587
SMTP_USERNAME = info@xaptronics.com
SMTP_PASSWORD = your-email-password
```

**Option C:**
```
SMTP_SERVER = mail.yourhostingcompany.com
SMTP_PORT = 587
SMTP_USERNAME = info@xaptronics.com
SMTP_PASSWORD = your-email-password
```

---

## ✅ Quick Test Script

Save this as `test_smtp.ps1`:

```powershell
# Test SMTP Settings
param(
    [string]$Server = "mail.xaptronics.com",
    [int]$Port = 587,
    [string]$Username = "info@xaptronics.com",
    [string]$Password = ""
)

Write-Host "Testing SMTP Connection..." -ForegroundColor Cyan
Write-Host "Server: $Server" -ForegroundColor Yellow
Write-Host "Port: $Port" -ForegroundColor Yellow
Write-Host "Username: $Username" -ForegroundColor Yellow

try {
    $smtp = New-Object System.Net.Mail.SmtpClient($Server, $Port)
    $smtp.EnableSsl = $true
    $smtp.Credentials = New-Object System.Net.NetworkCredential($Username, $Password)
    $smtp.Timeout = 5000
    
    Write-Host "`n✅ Connection successful!" -ForegroundColor Green
    Write-Host "These settings should work:" -ForegroundColor Green
    Write-Host "SMTP_SERVER=$Server"
    Write-Host "SMTP_PORT=$Port"
    Write-Host "SMTP_USERNAME=$Username"
    
    $smtp.Dispose()
} catch {
    Write-Host "`n❌ Connection failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "`nTry different port: 465 or 25" -ForegroundColor Yellow
}
```

**Usage:**
```powershell
.\test_smtp.ps1 -Server "mail.xaptronics.com" -Port 587 -Username "info@xaptronics.com" -Password "your-password"
```

---

## 📋 Summary Checklist

- [ ] Checked email client settings (Outlook/Thunderbird)
- [ ] Checked webmail/cPanel settings
- [ ] Contacted IT team for SMTP details
- [ ] Tested SMTP connection
- [ ] Found correct SMTP server address
- [ ] Found correct port (587/465/25)
- [ ] Confirmed username format
- [ ] Confirmed password works
- [ ] Tested email sending

---

## 🆘 Still Can't Find?

**Contact these sources:**
1. **IT Support Team** - They have all SMTP settings
2. **Email Provider** - Check provider documentation
3. **Hosting Company** - If using shared hosting
4. **Domain Registrar** - May have email hosting info

**Ask them:**
"Hi, I need SMTP settings for info@xaptronics.com to send emails programmatically. Can you provide:
- SMTP server address
- SMTP port (587/465/25)
- Authentication requirements
- Any special settings needed"

