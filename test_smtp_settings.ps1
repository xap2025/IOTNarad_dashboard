# Test SMTP Settings Script
# Usage: .\test_smtp_settings.ps1 -Server "mail.xaptronics.com" -Port 587 -Username "info@xaptronics.com" -Password "your-password"

param(
    [Parameter(Mandatory=$false)]
    [string]$Server = "mail.xaptronics.com",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 587,
    
    [Parameter(Mandatory=$false)]
    [string]$Username = "info@xaptronics.com",
    
    [Parameter(Mandatory=$false)]
    [string]$Password = ""
)

Write-Host "`n🔍 Testing SMTP Connection..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Server:   $Server" -ForegroundColor Yellow
Write-Host "Port:     $Port" -ForegroundColor Yellow
Write-Host "Username: $Username" -ForegroundColor Yellow
Write-Host ""

if (-not $Password) {
    $Password = Read-Host "Enter password" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

# Test different ports
$portsToTest = @(587, 465, 25)

foreach ($testPort in $portsToTest) {
    Write-Host "Testing port $testPort..." -ForegroundColor Cyan
    try {
        $smtp = New-Object System.Net.Mail.SmtpClient($Server, $testPort)
        
        # Try SSL/TLS
        if ($testPort -eq 465) {
            $smtp.EnableSsl = $true
        } elseif ($testPort -eq 587) {
            $smtp.EnableSsl = $true
        }
        
        $smtp.Credentials = New-Object System.Net.NetworkCredential($Username, $Password)
        $smtp.Timeout = 5000
        
        # Test connection
        $smtp.Send($null, $null, "test@test.com", "test@test.com")
        
        Write-Host "✅ Port $testPort works!" -ForegroundColor Green
        Write-Host "`n📋 Use these settings in .env:" -ForegroundColor Green
        Write-Host "SMTP_SERVER=$Server" -ForegroundColor White
        Write-Host "SMTP_PORT=$testPort" -ForegroundColor White
        Write-Host "SMTP_USERNAME=$Username" -ForegroundColor White
        Write-Host "SMTP_PASSWORD=$Password" -ForegroundColor White
        Write-Host "FROM_EMAIL=$Username" -ForegroundColor White
        Write-Host "FROM_NAME=Xaptronics IOTNarad" -ForegroundColor White
        
        $smtp.Dispose()
        break
    } catch {
        Write-Host "❌ Port $testPort failed: $_" -ForegroundColor Red
        if ($testPort -ne $portsToTest[-1]) {
            Write-Host ""
        }
    }
}

Write-Host "`n💡 If all ports failed:" -ForegroundColor Yellow
Write-Host "   1. Check server address is correct" -ForegroundColor Yellow
Write-Host "   2. Verify username/password" -ForegroundColor Yellow
Write-Host "   3. Check firewall/network settings" -ForegroundColor Yellow
Write-Host "   4. Contact IT team for SMTP settings" -ForegroundColor Yellow

