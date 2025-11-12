# Email to IT Department - SMTP Authentication Request

**Subject:** Request for SMTP Authentication Credentials for noreply@xaptronics.com

---

Hi IT Team,

Thank you for providing the SMTP configuration details for noreply@xaptronics.com.

Since the account uses **OAuth2 / Modern Authentication**, I need clarification on the authentication method we should use for our backend service:

## **Option 1: App Password (Preferred - if allowed)**

If App Passwords are enabled for this account, please:
1. Generate an **App Password** for noreply@xaptronics.com
2. Confirm that SMTP AUTH is enabled for this account
3. Share the App Password with us

**Note:** App Password will work if:
- MFA is enabled on the account, OR
- The tenant allows App Passwords for SMTP authentication

---

## **Option 2: OAuth2 / Modern Authentication (If App Password not available)**

If App Passwords are not available or not allowed, we need OAuth2 credentials:

Please provide the following details:

1. **Tenant ID** (Azure AD Tenant ID)
   - Format: Usually a GUID like `12345678-1234-1234-1234-123456789012`

2. **Client ID** (Azure AD Application ID)
   - We need an Azure AD App Registration created for SMTP sending
   - Format: Usually a GUID

3. **Client Secret**
   - A secret key generated for the Azure AD App Registration
   - This will be used for backend token generation

4. **Required Permissions/Scopes:**
   - `https://outlook.office365.com/.default` (Microsoft Graph API)
   - OR `https://graph.microsoft.com/.default`
   - Mail.Send permission for the app

5. **Confirmation:**
   - The app has permission to send emails on behalf of noreply@xaptronics.com
   - The app is registered as a "Confidential client" (not public)

---

## **Our Requirements:**

- **SMTP Server:** smtp-mail.outlook.com
- **SMTP Port:** 587
- **Encryption:** STARTTLS
- **From Email:** noreply@xaptronics.com
- **Purpose:** Automated email sending for user credentials and notifications

---

## **Questions:**

1. Can we use an **App Password** for SMTP authentication with this account?
   - If YES → Please generate and share the App Password
   - If NO → Please proceed with Option 2 (OAuth2)

2. If OAuth2 is required:
   - Do you already have an Azure AD App Registration for SMTP?
   - Or should we create one? (We can provide the redirect URI if needed)

3. What is the **preferred authentication method** for this use case?

---

Please let us know which option is available and provide the necessary credentials.

Thank you!

---

**Technical Contact:** [Your Name/Team]
**Purpose:** Backend service for IOTNarad Dashboard - Automated email notifications

