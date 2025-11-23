# Environment Variables Documentation

This document lists all environment variables required by the MyBlogSubscribers Azure Function.

## Required Variables

### Azure Storage
**`STORAGE_CONNECTION_STRING`** (Required)
- **Purpose**: Connection string for Azure Table Storage (subscribers) and Blob Storage (newsletters)
- **Format**: `DefaultEndpointsProtocol=https;AccountName=<name>;AccountKey=<key>;EndpointSuffix=core.windows.net`
- **Used By**: `email_subscriber.py`, `weekly_job.py`
- **How to Get**: Azure Portal → Storage Account → Access Keys
- **Example**: `DefaultEndpointsProtocol=https;AccountName=myblogsubscribers;AccountKey=xxxxx...`

### Email Service (Brevo)
**`BREVO_API_KEY`** (Required)
- **Purpose**: API key for Brevo (formerly Sendinblue) transactional email service
- **Used By**: `mailer.py`
- **How to Get**: Brevo Dashboard → Settings → API Keys → Create API Key
- **Example**: `xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxx`

**`BREVO_FROM_EMAIL`** (Required)
- **Purpose**: Sender email address for newsletters
- **Used By**: `mailer.py`
- **Format**: Valid email address verified in Brevo
- **Example**: `noreply@quantuminvestor.net`

**`BREVO_FROM_NAME`** (Optional)
- **Purpose**: Sender display name for newsletters
- **Used By**: `mailer.py`
- **Default**: `Quantum Investor Digest`
- **Example**: `Quantum Investor`

### GitHub Configuration
**`GITHUB_OWNER`** (Optional)
- **Purpose**: GitHub repository owner/organization name
- **Used By**: `weekly_job.py`
- **Default**: `mig1980`
- **Example**: `mig1980`

**`GITHUB_REPO`** (Optional)
- **Purpose**: GitHub repository name containing blog posts
- **Used By**: `weekly_job.py`
- **Default**: `quantuminvestor`
- **Example**: `quantuminvestor`

**`GITHUB_POSTS_PATH`** (Optional)
- **Purpose**: Path to blog posts directory in GitHub repository
- **Used By**: `weekly_job.py`
- **Default**: `Posts`
- **Example**: `Posts`

### CORS Configuration
**`CORS_ALLOWED_ORIGIN`** (Optional)
- **Purpose**: Allowed origin for CORS requests to SubscribeEmail endpoint
- **Used By**: `function_app.py`
- **Default**: `*` (allow all origins)
- **Production**: Set to your domain (e.g., `https://quantuminvestor.net`)
- **Example**: `https://quantuminvestor.net`

---

## Local Development Setup

### Create `local.settings.json`
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "STORAGE_CONNECTION_STRING": "your-azure-storage-connection-string",
    "BREVO_API_KEY": "your-brevo-api-key",
    "BREVO_FROM_EMAIL": "noreply@yourdomain.com",
    "BREVO_FROM_NAME": "Your Newsletter Name",
    "CORS_ALLOWED_ORIGIN": "*"
  }
}
```

**⚠️ Important**: `local.settings.json` is excluded from git via `.gitignore`. Never commit this file.

---

## Azure Portal Configuration

### Navigate to Function App Settings
1. Open Azure Portal
2. Go to your Function App
3. Select **Configuration** → **Application Settings**

### Add Each Variable
For each required variable above:
1. Click **+ New application setting**
2. Enter the **Name** (e.g., `BREVO_API_KEY`)
3. Enter the **Value** (your actual key/connection string)
4. Click **OK**
5. Click **Save** at the top

### GitHub Secrets (for CI/CD)
If using GitHub Actions:
1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Add secret: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
3. Add secret: `STORAGE_CONNECTION_STRING` (if deploying newsletter generation scripts)

---

## Validation

### Test Local Setup
```powershell
# Check if environment variables are set
$env:STORAGE_CONNECTION_STRING
$env:BREVO_API_KEY
$env:BREVO_FROM_EMAIL
```

### Test Azure Function
```powershell
# Test subscription endpoint
Invoke-RestMethod -Uri "https://your-function-app.azurewebsites.net/api/subscribeemail" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"test@example.com"}'
```

---

## Security Best Practices

✅ **DO:**
- Use Azure Key Vault for sensitive values in production
- Rotate API keys regularly
- Use managed identities when possible
- Set CORS_ALLOWED_ORIGIN to specific domain in production

❌ **DON'T:**
- Commit `local.settings.json` to git
- Share API keys in chat/email
- Use production keys in development
- Leave CORS set to `*` in production

---

## Troubleshooting

### "STORAGE_CONNECTION_STRING not configured"
- Check variable exists in Configuration
- Verify connection string format is correct
- Test connection string with Azure Storage Explorer

### "BREVO_API_KEY not configured"
- Check variable exists in Configuration
- Verify API key is valid in Brevo dashboard
- Ensure API key has permissions for transactional emails

### "Email not found: ..."
- Verify STORAGE_CONNECTION_STRING points to correct storage account
- Check Table Storage contains "subscribers" table
- Verify email exists in table with isActive=true

### CORS errors in browser
- Check CORS_ALLOWED_ORIGIN matches your domain
- Verify domain includes https:// prefix
- Check browser console for specific CORS error

---

## Monitoring

Enable Application Insights to track:
- Function execution times
- Error rates and types
- Dependency failures (Storage, Brevo API)
- Custom metrics from structured logging

To enable:
1. Uncomment `azure-monitor-opentelemetry` in `requirements.txt`
2. Add `APPLICATIONINSIGHTS_CONNECTION_STRING` to Configuration
3. Redeploy function

---

Last Updated: November 23, 2025
