# Email Subscription System - Implementation Guide

## Overview

This Azure Functions application provides:
1. **HTTP Endpoint**: Public API for email subscriptions
2. **Table Storage**: Subscriber data persistence
3. **Timer Trigger**: Weekly newsletter automation with Brevo
4. **Modular Design**: Separation of concerns for maintainability

---

## Architecture

```
azure-functions/MyBlogSubscribers/
├── function_app.py          # HTTP + Timer triggers
├── email_subscriber.py      # Table Storage operations
├── mailer.py                # Brevo email sending
├── weekly_job.py            # Newsletter generation & sending
├── requirements.txt         # Python dependencies
└── local.settings.json      # Local environment config
```

---

## Module Responsibilities

### 1. `function_app.py` - Azure Functions Entry Point
**Purpose**: Defines HTTP and timer-triggered functions

**Key Functions**:
- `subscribe_email()`: HTTP POST endpoint for subscriptions
  - Auth: ANONYMOUS (public access)
  - Methods: POST, OPTIONS (CORS support)
  - Returns: JSON response with status

- `weekly_newsletter()`: Timer trigger for weekly emails
  - Schedule: `"0 0 12 * * FRI"` (Every Friday at 12 PM UTC)
  - Calls: `weekly_job.send_weekly_newsletter()`

### 2. `email_subscriber.py` - Data Layer
**Purpose**: Azure Table Storage CRUD operations

**Key Functions**:
- `subscribe_email(email)`: Add new subscriber
  - Validates email format
  - Handles duplicates gracefully
  - Sets `isActive=true` by default

- `get_active_subscribers()`: Retrieve all active subscribers
  - Filters: `isActive eq true`
  - Returns: List of email addresses

- `unsubscribe_email(email)`: Soft delete
  - Sets `isActive=false` (preserves data)

**Table Schema**:
```python
{
    "PartitionKey": "subscriber",      # Fixed value
    "RowKey": "user@example.com",      # Email as unique key
    "email": "user@example.com",       # Searchable email field
    "subscribedAt": "2025-01-23T...",  # ISO timestamp
    "isActive": true                    # Boolean flag
}
```

### 3. `mailer.py` - Email Delivery Layer
**Purpose**: Brevo API abstraction

**Key Functions**:
- `send_email(to_email, subject, html_body)`: Single email
  - Uses Brevo transactional API
  - Returns status dict with success/failure

- `send_bulk_email(recipients, subject, html_body)`: Batch sending
  - Loops through recipients
  - Logs individual failures
  - Returns summary statistics

**Environment Variables Required**:
- `BREVO_API_KEY`: API key from Brevo
- `BREVO_FROM_EMAIL`: Verified sender address
- `BREVO_FROM_NAME`: Sender display name (optional, defaults to "Quantum Investor Digest")

### 4. `weekly_job.py` - Newsletter Business Logic
**Purpose**: Newsletter content generation and distribution

**Key Functions**:
- `get_weekly_email_content()`: Generate newsletter HTML
  - Returns: `{"subject": "...", "html_body": "..."}`
  - Customizable template

- `send_weekly_newsletter()`: Main job function
  1. Fetch active subscribers
  2. Generate email content
  3. Send via `mailer.send_bulk_email()`
  4. Log results

---

## Configuration

### Azure Function App Settings
Set these in Azure Portal → Function App → Configuration:

```bash
# Storage connection (already configured)
STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;..."

# Brevo configuration (ADD THESE)
BREVO_API_KEY = "xkeysib-xxxxxxxxxxxxx"
BREVO_FROM_EMAIL = "noreply@quantuminvestor.net"
BREVO_FROM_NAME = "Quantum Investor"
```

### Brevo Setup
1. **Create Account**: https://www.brevo.com/
2. **Verify Sender**: Settings → Senders & IP
   - Add and verify sender email address
   - Complete domain authentication for production
3. **Get API Key**: Settings → SMTP & API → API Keys
   - Create new API key with name (e.g., "Azure Functions")
   - Copy key immediately (shown once)

### Update Azure Configuration
```powershell
# Set Brevo API key
az functionapp config appsettings set `
  --name myblog-subscribers `
  --resource-group myblog-subscribers_group `
  --settings "BREVO_API_KEY=xkeysib-your_key_here"

# Set sender email
az functionapp config appsettings set `
  --name myblog-subscribers `
  --resource-group myblog-subscribers_group `
  --settings "BREVO_FROM_EMAIL=noreply@quantuminvestor.net"

# Set sender name (optional)
az functionapp config appsettings set `
  --name myblog-subscribers `
  --resource-group myblog-subscribers_group `
  --settings "BREVO_FROM_NAME=Quantum Investor"
```

---

## Deployment

### Method 1: Azure Functions Core Tools (Recommended)
```powershell
cd c:\Users\mgavril\Documents\GitHub\My-blog\azure-functions\MyBlogSubscribers
func azure functionapp publish myblog-subscribers --build remote
```

### Method 2: GitHub Actions
Push to main branch triggers `.github/workflows/main_myblog-subscribers.yml`

---

## Testing

### Test Subscription Endpoint
```powershell
# Subscribe a new email
curl -X POST https://myblog-subscribers-dbatcqezhcddd6gy.canadacentral-01.azurewebsites.net/api/subscribeemail `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"test@example.com\"}'

# Expected: {"status": "success", "message": "Thank you for subscribing!"}
```

### Test Timer Trigger Manually
1. Azure Portal → Function App → Functions → weekly_newsletter
2. Click "Code + Test" → "Test/Run"
3. Click "Run" (no input needed)
4. Check "Logs" tab for output

### Verify Brevo Delivery
1. Brevo Dashboard → Statistics → Email
2. View real-time sending stats
3. Check individual email logs

---

## Monitoring

### Azure Function Logs
```powershell
# Stream live logs
func azure functionapp logstream myblog-subscribers
```

### Azure Portal Insights
1. Function App → Monitor → Logs
2. Query example:
```kusto
traces
| where timestamp > ago(1h)
| where message contains "newsletter"
| order by timestamp desc
```

---

## Troubleshooting

### Issue: Timer Not Triggering
**Check**:
- Function App is running (not stopped)
- Schedule syntax: `"0 0 12 * * FRI"` (cron format)
- Timezone: Azure uses UTC by default

**Solution**:
```powershell
# View function status
az functionapp show --name myblog-subscribers --resource-group myblog-subscribers_group --query "state"
```

### Issue: Brevo Emails Not Sending
**Check**:
1. API key configured correctly
2. Sender email verified in Brevo
3. Check mailer.py logs for errors
4. Brevo account has available email credits

**Debug**:
```python
# Add to weekly_job.py after send_bulk_email()
logging.info(f"Email results: {result}")
```

### Issue: No Subscribers Returned
**Check**:
- Table Storage connection string valid
- Subscribers exist with `isActive=true`

**Query Storage**:
```powershell
# List all subscribers (Azure CLI)
az storage entity query `
  --account-name myblogsubscribers `
  --table-name subscribers `
  --filter "PartitionKey eq 'subscriber'"
```

---

## Email Template Customization

### Edit Newsletter Content
Modify `weekly_job.py` → `get_weekly_email_content()`:

```python
def get_weekly_email_content():
    """Generate weekly email content."""
    
    html_body = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .header { background: #1a1a1a; color: white; padding: 20px; }
            .content { padding: 20px; }
            .footer { background: #f5f5f5; padding: 10px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Quantum Investor - Weekly Digest</h1>
        </div>
        <div class="content">
            <p>Hi there! 👋</p>
            <p>Here's what happened this week in the markets...</p>
            
            <!-- ADD YOUR CONTENT HERE -->
            <ul>
                <li>Market update</li>
                <li>Portfolio performance</li>
                <li>Key insights</li>
            </ul>
            
            <p>Read more on <a href="https://quantuminvestor.net">quantuminvestor.net</a></p>
        </div>
        <div class="footer">
            <p>You're receiving this because you subscribed at quantuminvestor.net</p>
            <p><a href="https://quantuminvestor.net/unsubscribe">Unsubscribe</a></p>
        </div>
    </body>
    </html>
    """
    
    return {
        "subject": "📊 Your Weekly Quantum Investor Digest",
        "html_body": html_body
    }
```

---

## Next Steps

1. **Set Up Brevo**
   - Create account + verify sender
   - Add API key to Azure settings

2. **Test Email Sending**
   - Manually trigger `weekly_newsletter` function
   - Verify delivery to test subscriber

3. **Customize Email Template**
   - Edit `get_weekly_email_content()` in `weekly_job.py`
   - Include blog post links, images, etc.

4. **Schedule Adjustment** (optional)
   - Current: Friday 12 PM UTC
   - Edit `function_app.py` schedule if needed

5. **Add Unsubscribe Page**
   - Create `unsubscribe.html` on site
   - Call Azure Function with email parameter
   - Use `email_subscriber.unsubscribe_email()`

---

## API Reference

### Subscribe Endpoint
**URL**: `https://myblog-subscribers-dbatcqezhcddd6gy.canadacentral-01.azurewebsites.net/api/subscribeemail`

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "email": "user@example.com"
}
```

**Responses**:
```json
// Success
{
  "status": "success",
  "message": "Thank you for subscribing! You'll receive weekly updates."
}

// Already subscribed
{
  "status": "exists",
  "message": "You're already subscribed!"
}

// Invalid email
{
  "status": "error",
  "message": "Invalid email address"
}

// Server error
{
  "status": "error",
  "message": "Failed to process subscription"
}
```

---

## Production Checklist

- [x] Azure Function deployed
- [x] Storage Table created
- [x] CORS configured for domain
- [x] CSP updated in index.html
- [x] Subscribe form tested
- [ ] Brevo account created
- [ ] Sender email verified
- [ ] API key configured in Azure
- [ ] Newsletter template customized
- [ ] Timer trigger tested manually
- [ ] Email delivery verified
- [ ] Unsubscribe flow implemented

---

## Resources

- [Azure Functions Python Docs](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Table Storage SDK](https://docs.microsoft.com/python/api/azure-data-tables)
- [Brevo API Documentation](https://developers.brevo.com/)
- [Brevo Python SDK](https://github.com/sendinblue/APIv3-python-library)
- [Cron Expression Generator](https://crontab.guru/)
