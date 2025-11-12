import os
import smtplib
import logging
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp-mail.outlook.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME', 'noreply@xaptronics.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@xaptronics.com')
        self.from_name = os.getenv('FROM_NAME', 'IOTNarad Admin')
        
        # OAuth2 Configuration (if using Modern Authentication)
        self.use_oauth2 = os.getenv('USE_OAUTH2', 'false').lower() == 'true'
        self.tenant_id = os.getenv('AZURE_TENANT_ID', '')
        self.client_id = os.getenv('AZURE_CLIENT_ID', '')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET', '')
        self.oauth2_token = None
        
        # Check configuration
        if self.use_oauth2:
            # OAuth2 mode
            if not all([self.tenant_id, self.client_id, self.client_secret]):
                logger.warning("OAuth2 enabled but missing credentials. Set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET.")
                self.configured = False
            else:
                self.configured = True
                logger.info("Email service initialized with OAuth2/Modern Authentication.")
        else:
            # Basic Auth mode (App Password or regular password)
            if not self.smtp_username or not self.smtp_password:
                logger.warning("Email service not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
                self.configured = False
            else:
                self.configured = True
                logger.info("Email service initialized with Basic Authentication (App Password).")

    def send_user_credentials(self, user_data: Dict[str, Any]) -> bool:
        """Send user credentials via email"""
        if not self.configured:
            logger.error("Email service is not configured. Cannot send email.")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = user_data['Email_Id']
            msg['Subject'] = "Your IOTNarad Dashboard Credentials"
            
            # Create HTML content
            html_content = self._get_html_template(user_data)
            plain_content = self._get_plain_text_template(user_data)
            
            # Attach both plain text and HTML versions
            msg.attach(MIMEText(plain_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            if self.use_oauth2:
                # Use OAuth2 authentication
                self._send_email_oauth2(msg, user_data['Email_Id'])
            else:
                # Use Basic Authentication (App Password)
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, user_data['Email_Id'], msg.as_string())
            
            logger.info(f"Credentials email sent to {user_data['Email_Id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {user_data['Email_Id']}: {e}")
            logger.exception("Full error traceback:")
            return False
    
    def _get_oauth2_token(self) -> Optional[str]:
        """Get OAuth2 access token from Azure AD"""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'scope': 'https://outlook.office365.com/.default',
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                self.oauth2_token = access_token
                logger.info("✅ OAuth2 token obtained successfully")
                return access_token
            else:
                logger.error("Failed to get access token from OAuth2 response")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get OAuth2 token: {e}")
            logger.exception("Full error traceback:")
            return None
    
    def _send_email_oauth2(self, msg: MIMEMultipart, to_email: str) -> bool:
        """Send email using OAuth2 authentication"""
        try:
            # Get OAuth2 token
            token = self._get_oauth2_token()
            if not token:
                raise Exception("Failed to obtain OAuth2 token")
            
            # For OAuth2 with SMTP, we need to use XOAUTH2
            # However, Python's smtplib doesn't natively support OAuth2
            # We'll use Microsoft Graph API instead for OAuth2
            
            # Alternative: Use Microsoft Graph API to send email
            graph_url = "https://graph.microsoft.com/v1.0/users/{}/sendMail".format(self.from_email)
            
            # Convert MIME message to Graph API format
            email_payload = {
                "message": {
                    "subject": msg['Subject'],
                    "body": {
                        "contentType": "HTML",
                        "content": msg.get_payload()[1].get_payload() if len(msg.get_payload()) > 1 else msg.get_payload()[0].get_payload()
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": to_email
                            }
                        }
                    ]
                }
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(graph_url, json=email_payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Email sent via Microsoft Graph API to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email via OAuth2: {e}")
            logger.exception("Full error traceback:")
            # Fallback: Try SMTP with XOAUTH2 if available
            logger.warning("Attempting SMTP fallback with XOAUTH2...")
            return self._send_email_smtp_oauth2(msg, to_email)
    
    def _send_email_smtp_oauth2(self, msg: MIMEMultipart, to_email: str) -> bool:
        """Fallback: Send email via SMTP using XOAUTH2 (if smtplib supports it)"""
        try:
            # Note: This requires additional library like 'smtplib2' or manual XOAUTH2 implementation
            # For now, we'll log and return False
            logger.warning("SMTP XOAUTH2 not fully implemented. Using Microsoft Graph API is recommended.")
            return False
        except Exception as e:
            logger.error(f"SMTP OAuth2 fallback failed: {e}")
            return False

    def _get_html_template(self, user_data: Dict[str, Any]) -> str:
        """Generate HTML email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>IOTNarad Dashboard Credentials</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #007bff;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #007bff;
                    margin-bottom: 10px;
                }}
                .credentials-box {{
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .credential-item {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    padding: 8px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .credential-item:last-child {{
                    border-bottom: none;
                }}
                .label {{
                    font-weight: bold;
                    color: #495057;
                }}
                .value {{
                    font-family: 'Courier New', monospace;
                    background-color: #e9ecef;
                    padding: 4px 8px;
                    border-radius: 4px;
                    color: #007bff;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #007bff;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 10px 5px;
                    font-weight: bold;
                }}
                .button:hover {{
                    background-color: #0056b3;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">IOTNarad Dashboard</div>
                    <p>Welcome to the IoT Management Platform</p>
                </div>
                
                <h2>Your Account Has Been Created!</h2>
                <p>Hello {user_data.get('Company_Name', 'User')},</p>
                <p>Your account has been successfully created in the IOTNarad Dashboard. Below are your login credentials:</p>
                
                <div class="credentials-box">
                    <div class="credential-item">
                        <span class="label">User ID:</span>
                        <span class="value">{user_data['User_Id']}</span>
                    </div>
                    <div class="credential-item">
                        <span class="label">Password:</span>
                        <span class="value">{user_data['Password']}</span>
                    </div>
                    <div class="credential-item">
                        <span class="label">User Type:</span>
                        <span class="value">{user_data['User_Type'].title()}</span>
                    </div>
                    <div class="credential-item">
                        <span class="label">Status:</span>
                        <span class="value">{user_data.get('Status', 'active').title()}</span>
                    </div>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Important Security Notice:</strong><br>
                    Please change your password after your first login for security purposes.
                    Keep your credentials safe and do not share them with anyone.
                </div>
                
                <p>You can now access the dashboard using these credentials. If you have any questions or need assistance, please contact our support team.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:8050/login" class="button">Login to Dashboard</a>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from IOTNarad Dashboard.<br>
                    Please do not reply to this email.</p>
                    <p>&copy; 2024 Xaptronics. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _get_plain_text_template(self, user_data: Dict[str, Any]) -> str:
        """Generate plain text email template"""
        return f"""
IOTNarad Dashboard - Account Created

Hello {user_data.get('Company_Name', 'User')},

Your account has been successfully created in the IOTNarad Dashboard.

LOGIN CREDENTIALS:
==================
User ID: {user_data['User_Id']}
Password: {user_data['Password']}
User Type: {user_data['User_Type'].title()}
Status: {user_data.get('Status', 'active').title()}

IMPORTANT SECURITY NOTICE:
=========================
- Please change your password after your first login
- Keep your credentials safe and do not share them
- Contact support if you have any questions

You can now access the dashboard at: http://localhost:8050/login

Best regards,
IOTNarad Admin Team

---
This is an automated message from IOTNarad Dashboard.
Please do not reply to this email.
© 2024 Xaptronics. All rights reserved.
        """

    def send_notification(self, to_email: str, subject: str, message: str) -> bool:
        """Send a general notification email"""
        if not self.configured:
            logger.error("Email service is not configured. Cannot send email.")
            return False
        
        try:
            msg = MIMEText(message, 'plain')
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if self.use_oauth2:
                # Use OAuth2 authentication
                self._send_email_oauth2(msg, to_email)
            else:
                # Use Basic Authentication (App Password)
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())
            
            logger.info(f"Notification email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification email to {to_email}: {e}")
            return False