# Email Configuration Setup Script
# Run this script to configure email settings

Write-Host "📧 Email Configuration Setup" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "Creating .env file..."
    New-Item -Path .env -ItemType File
}

# Get email provider
Write-Host "Select your email provider:" -ForegroundColor Yellow
Write-Host "1. Google Workspace (Gmail Business)"
Write-Host "2. Microsoft 365 (Outlook Business)"
Write-Host "3. Custom Email Server"
$provider = Read-Host "Enter choice (1/2/3)"

# Get SMTP settings based on provider
switch ($provider) {
    "1" {
        $SMTP_SERVER = "smtp.gmail.com"
        $SMTP_PORT = "587"
        Write-Host "`n✅ Google Workspace selected" -ForegroundColor Green
        Write-Host "⚠️  Note: You need to generate App Password from Google Admin Console" -ForegroundColor Yellow
    }
    "2" {
        $SMTP_SERVER = "smtp.office365.com"
        $SMTP_PORT = "587"
        Write-Host "`n✅ Microsoft 365 selected" -ForegroundColor Green
    }
    "3" {
        $SMTP_SERVER = Read-Host "Enter SMTP server (e.g., mail.xaptronics.com)"
        $SMTP_PORT = Read-Host "Enter SMTP port (usually 587)"
        Write-Host "`n✅ Custom server selected" -ForegroundColor Green
    }
    default {
        Write-Host "❌ Invalid choice!" -ForegroundColor Red
        exit
    }
}

# Get email credentials
$SMTP_USERNAME = Read-Host "Enter email address (e.g., info@xaptronics.com)"
$SMTP_PASSWORD = Read-Host "Enter password/App Password" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SMTP_PASSWORD)
$SMTP_PASSWORD_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Remove old email settings if exists
$envContent = Get-Content .env | Where-Object { $_ -notmatch "SMTP_|FROM_EMAIL|FROM_NAME" }
$envContent | Set-Content .env

# Add new email settings
Add-Content .env "`n# Email Configuration"
Add-Content .env "SMTP_SERVER=$SMTP_SERVER"
Add-Content .env "SMTP_PORT=$SMTP_PORT"
Add-Content .env "SMTP_USERNAME=$SMTP_USERNAME"
Add-Content .env "SMTP_PASSWORD=$SMTP_PASSWORD_PLAIN"
Add-Content .env "FROM_EMAIL=$SMTP_USERNAME"
Add-Content .env "FROM_NAME=Xaptronics IOTNarad"

Write-Host "`n✅ Email configuration added to .env file!" -ForegroundColor Green
Write-Host "`n📋 Configuration Summary:" -ForegroundColor Cyan
Write-Host "   SMTP Server: $SMTP_SERVER"
Write-Host "   SMTP Port: $SMTP_PORT"
Write-Host "   Email: $SMTP_USERNAME"
Write-Host "`n⚠️  Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Restart Docker: docker compose down && docker compose up -d"
Write-Host "   2. Test email by creating a new user"
Write-Host ""

