# Email Subscribe Form - Implementation Guide

## Overview
This email subscription form is designed to integrate seamlessly with your Quantum Investor blog. It collects user email addresses and submits them to an Azure Function endpoint, which then stores the data in Azure Table Storage.

## Features
- ✅ **Consistent Styling**: Matches your blog's existing CSS theme (purple/gray color scheme)
- ✅ **Email Validation**: Client-side validation with regex pattern matching
- ✅ **Async Submission**: Form submits via fetch API without page reload
- ✅ **User Feedback**: Clear success/error messages with visual indicators
- ✅ **Accessibility**: ARIA labels, focus states, and keyboard navigation support
- ✅ **Mobile Responsive**: Optimized for all screen sizes
- ✅ **Loading States**: Visual feedback during submission
- ✅ **Security**: CSP-compliant with nonce attribute
- ✅ **Analytics Ready**: Includes Google Analytics event tracking

## File Structure
```
My-blog/
├── templates/
│   └── subscribe.html           # Subscribe form template
├── js/
│   └── template-loader.js       # Existing template loader (handles injection)
├── subscribe-form.html          # Standalone version (optional)
└── README/
    └── subscribe-form-README.md # This documentation
```

## Quick Start

### 1. Include the Form in Your Pages (Using Template Loader)

**This is the recommended approach** - it uses your existing `template-loader.js` system for consistency.

Simply add this placeholder element anywhere you want the subscribe form to appear:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Your existing head content -->
    <link rel="stylesheet" href="styles.css">
    <script src="js/template-loader.js" defer nonce="qi123"></script>
</head>
<body>
    <!-- Your existing header -->
    <div data-template="header" data-root-path=""></div>
    
    <main>
        <!-- Your content -->
        
        <!-- Email Subscribe Form -->
        <div data-template="subscribe" data-root-path=""></div>
        
        <!-- More content -->
    </main>
    
    <!-- Your existing footer -->
    <div data-template="footer" data-root-path=""></div>
</body>
</html>
```

**For pages in subdirectories (like Posts/):**
```html
<div data-template="subscribe" data-root-path="../"></div>
```

That's it! The template loader will automatically inject the form.

### 2. Configure Azure Function Endpoint

In `templates/subscribe.html`, replace the placeholder URL with your actual Azure Function endpoint:

```javascript
// Line ~200 in templates/subscribe.html
const AZURE_FUNCTION_URL = 'https://your-function-app.azurewebsites.net/api/SubscribeEmail';
```

### 3. Test It

Open any page with the subscribe form and test the submission. The form will:
- ✅ Validate email format before submission
- ✅ Show loading state during submission
- ✅ Display success/error messages
- ✅ Track subscription in Google Analytics (if configured)

## Azure Function Setup

### Option 1: Node.js Azure Function (Recommended)

Create a new Azure Function with HTTP trigger:

```javascript
// index.js
const { TableClient, AzureNamedKeyCredential } = require("@azure/data-tables");

module.exports = async function (context, req) {
    context.log('Email subscription request received');

    // CORS headers
    context.res = {
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': 'https://quantuminvestor.net',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    };

    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        context.res.status = 204;
        return;
    }

    // Validate request method
    if (req.method !== 'POST') {
        context.res.status = 405;
        context.res.body = { error: 'Method not allowed' };
        return;
    }

    try {
        // Get email from request body
        const email = req.body?.email;

        // Validate email
        if (!email || typeof email !== 'string') {
            context.res.status = 400;
            context.res.body = { error: 'Email is required' };
            return;
        }

        // Email validation regex
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            context.res.status = 400;
            context.res.body = { error: 'Invalid email format' };
            return;
        }

        // Azure Table Storage configuration
        const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME;
        const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY;
        const tableName = 'EmailSubscribers';

        const credential = new AzureNamedKeyCredential(accountName, accountKey);
        const tableClient = new TableClient(
            `https://${accountName}.table.core.windows.net`,
            tableName,
            credential
        );

        // Ensure table exists
        await tableClient.createTable().catch(() => {
            // Table might already exist, which is fine
        });

        // Create entity
        const emailDomain = email.split('@')[1];
        const timestamp = new Date().toISOString();
        const entity = {
            partitionKey: emailDomain,
            rowKey: email,
            email: email,
            subscribedAt: timestamp,
            status: 'active',
            source: 'website'
        };

        // Insert entity (will fail if duplicate)
        await tableClient.createEntity(entity);

        context.res.status = 201;
        context.res.body = {
            message: 'Successfully subscribed! Thank you for joining.',
            email: email
        };

    } catch (error) {
        context.log.error('Error processing subscription:', error);

        // Check for duplicate email
        if (error.statusCode === 409) {
            context.res.status = 409;
            context.res.body = { 
                error: 'This email is already subscribed',
                message: 'You are already on our mailing list!'
            };
            return;
        }

        // Generic error
        context.res.status = 500;
        context.res.body = { 
            error: 'Internal server error',
            message: 'Something went wrong. Please try again later.'
        };
    }
};
```

**package.json**:
```json
{
  "name": "subscribe-function",
  "version": "1.0.0",
  "description": "Email subscription Azure Function",
  "dependencies": {
    "@azure/data-tables": "^13.2.2"
  }
}
```

**function.json**:
```json
{
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post", "options"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

### Option 2: Python Azure Function

```python
# __init__.py
import logging
import json
import re
from datetime import datetime
from azure.data.tables import TableClient
from azure.core.exceptions import ResourceExistsError
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Email subscription request received')

    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://quantuminvestor.net',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    # Handle preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse('', status_code=204, headers=headers)

    # Validate method
    if req.method != 'POST':
        return func.HttpResponse(
            json.dumps({'error': 'Method not allowed'}),
            status_code=405,
            headers=headers
        )

    try:
        # Parse request body
        req_body = req.get_json()
        email = req_body.get('email')

        # Validate email
        if not email:
            return func.HttpResponse(
                json.dumps({'error': 'Email is required'}),
                status_code=400,
                headers=headers
            )

        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return func.HttpResponse(
                json.dumps({'error': 'Invalid email format'}),
                status_code=400,
                headers=headers
            )

        # Azure Table Storage
        connection_string = os.environ['AZURE_STORAGE_CONNECTION_STRING']
        table_name = 'EmailSubscribers'
        
        table_client = TableClient.from_connection_string(
            connection_string,
            table_name
        )

        # Create table if it doesn't exist
        try:
            table_client.create_table()
        except:
            pass

        # Prepare entity
        email_domain = email.split('@')[1]
        entity = {
            'PartitionKey': email_domain,
            'RowKey': email,
            'email': email,
            'subscribedAt': datetime.utcnow().isoformat(),
            'status': 'active',
            'source': 'website'
        }

        # Insert entity
        table_client.create_entity(entity)

        return func.HttpResponse(
            json.dumps({
                'message': 'Successfully subscribed! Thank you for joining.',
                'email': email
            }),
            status_code=201,
            headers=headers
        )

    except ResourceExistsError:
        return func.HttpResponse(
            json.dumps({
                'error': 'This email is already subscribed',
                'message': 'You are already on our mailing list!'
            }),
            status_code=409,
            headers=headers
        )
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                'error': 'Internal server error',
                'message': 'Something went wrong. Please try again later.'
            }),
            status_code=500,
            headers=headers
        )
```

**requirements.txt**:
```
azure-functions
azure-data-tables>=12.4.0
```

## Azure Configuration Steps

### 1. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-blog-subscriptions --location eastus

# Create storage account
az storage account create \
  --name stblogsubscriptions \
  --resource-group rg-blog-subscriptions \
  --location eastus \
  --sku Standard_LRS

# Create function app (Node.js)
az functionapp create \
  --resource-group rg-blog-subscriptions \
  --consumption-plan-location eastus \
  --runtime node \
  --runtime-version 18 \
  --functions-version 4 \
  --name func-blog-subscriptions \
  --storage-account stblogsubscriptions

# Or Python
az functionapp create \
  --resource-group rg-blog-subscriptions \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4 \
  --name func-blog-subscriptions \
  --storage-account stblogsubscriptions
```

### 2. Configure Environment Variables

In Azure Portal or via CLI:

```bash
# Get storage account connection string
az storage account show-connection-string \
  --name stblogsubscriptions \
  --resource-group rg-blog-subscriptions

# Set environment variables (Node.js)
az functionapp config appsettings set \
  --name func-blog-subscriptions \
  --resource-group rg-blog-subscriptions \
  --settings \
    "AZURE_STORAGE_ACCOUNT_NAME=stblogsubscriptions" \
    "AZURE_STORAGE_ACCOUNT_KEY=<your-key>"

# Or for Python
az functionapp config appsettings set \
  --name func-blog-subscriptions \
  --resource-group rg-blog-subscriptions \
  --settings \
    "AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>"
```

### 3. Deploy Function

Using VS Code Azure Functions extension or CLI:

```bash
# Using CLI
cd your-function-directory
func azure functionapp publish func-blog-subscriptions
```

### 4. Configure CORS

In Azure Portal:
1. Go to your Function App
2. Navigate to **CORS** under **API** section
3. Add your domain: `https://quantuminvestor.net`
4. Save changes

Or via CLI:

```bash
az functionapp cors add \
  --name func-blog-subscriptions \
  --resource-group rg-blog-subscriptions \
  --allowed-origins https://quantuminvestor.net
```

## Azure Table Storage Schema

**Table Name**: `EmailSubscribers`

| Field | Type | Description |
|-------|------|-------------|
| PartitionKey | String | Email domain (e.g., "gmail.com") |
| RowKey | String | Full email address (unique identifier) |
| email | String | Email address |
| subscribedAt | DateTime | Timestamp of subscription |
| status | String | Subscription status (active/unsubscribed) |
| source | String | Where they subscribed from (website) |

## Customization Options

### Change Colors

Modify the CSS variables in `subscribe-form.html`:

```css
.subscribe-container {
  /* Change gradient color */
  background: radial-gradient(circle at 0% 0%, rgba(6, 182, 212, 0.15), transparent 60%),
              var(--bg-gray-900);
}

.subscribe-button {
  /* Change button color to cyan theme */
  background-color: #06b6d4;
  border-color: #06b6d4;
}
```

### Change Text Content

Update the header section in HTML:

```html
<div class="subscribe-header">
  <h2 class="subscribe-title">Join Our Community</h2>
  <p class="subscribe-description">
    Get weekly updates on AI-powered investment strategies and market insights.
  </p>
</div>
```

### Add Additional Fields

To collect more information (name, interests, etc.), add fields to the form:

```html
<div class="subscribe-input-group">
  <label for="nameInput" class="subscribe-label">Name (Optional)</label>
  <input 
    type="text" 
    id="nameInput" 
    name="name" 
    class="subscribe-input" 
    placeholder="John Doe"
  >
</div>
```

And update the Azure Function to store the additional data.

## Testing

### Local Testing (before deploying to Azure)

1. Use a local Azure Function runtime:
```bash
npm install -g azure-functions-core-tools@4
func start
```

2. Update `AZURE_FUNCTION_URL` to `http://localhost:7071/api/SubscribeEmail`

3. Test the form in your browser

### Production Testing

1. Deploy to Azure
2. Update `AZURE_FUNCTION_URL` with your production endpoint
3. Test with real email addresses
4. Check Azure Table Storage to verify data is being stored

## Security Considerations

✅ **HTTPS Only**: Ensure your Azure Function only accepts HTTPS requests
✅ **CORS Configuration**: Restrict to your domain only
✅ **Rate Limiting**: Consider adding rate limiting in Azure Function to prevent abuse
✅ **Email Validation**: Both client-side and server-side validation
✅ **Authentication**: Function key authentication (authLevel: "function")
✅ **Input Sanitization**: Prevent injection attacks
✅ **CSP Compliance**: Script uses nonce attribute

### Optional: Add reCAPTCHA

To prevent bot submissions, integrate Google reCAPTCHA v3:

1. Get reCAPTCHA keys from Google
2. Add reCAPTCHA script to your page
3. Verify token in Azure Function before storing email

## Analytics Tracking

The form includes Google Analytics event tracking. When a user subscribes, it fires:

```javascript
gtag('event', 'subscribe', {
  'event_category': 'engagement',
  'event_label': 'email_subscription'
});
```

Ensure Google Analytics is configured in your blog's `<head>` section.

## Troubleshooting

### Issue: CORS Error
**Solution**: Verify CORS settings in Azure Function allow your domain

### Issue: 401 Unauthorized
**Solution**: Check function key is not required, or include it in URL: `?code=YOUR_FUNCTION_KEY`

### Issue: Email not saved
**Solution**: Check Azure Function logs in Azure Portal under **Monitor** > **Logs**

### Issue: Duplicate email error not showing
**Solution**: Ensure Azure Function returns 409 status code for duplicates

## Email Management

To manage subscribers, you can:

1. **View in Azure Portal**: Storage Browser > Tables > EmailSubscribers
2. **Export Data**: Use Azure Storage Explorer
3. **Send Emails**: Integrate with SendGrid, Mailchimp, or Azure Communication Services

### Example: Export Subscribers

```python
# Python script to export subscribers
from azure.data.tables import TableClient

connection_string = "your-connection-string"
table_client = TableClient.from_connection_string(connection_string, "EmailSubscribers")

subscribers = table_client.list_entities()
for subscriber in subscribers:
    if subscriber['status'] == 'active':
        print(subscriber['email'])
```

## Cost Estimation

**Azure Storage**: ~$0.05/month for 1,000 subscribers
**Azure Function**: Free tier includes 1 million executions/month
**Total**: Essentially free for small to medium blogs

## Support

For issues or questions:
- Check Azure Function logs in Azure Portal
- Review browser console for JavaScript errors
- Verify network requests in browser DevTools

## License

This component is part of your Quantum Investor blog and follows your blog's license.
