# Email Infrastructure & Azure Functions Guide

This document describes how your blog’s email subscription pipeline works and how to extend it with SendGrid for weekly emails, using a simple, module-based structure.

## 1. Project Structure

In `azure-functions/MyBlogSubscribers` the recommended layout is:

- `function_app.py` – HTTP/timer function definitions (bindings + HTTP concerns only)
- `email_subscriber.py` – logic for storing subscribers in Azure Table Storage
- `mailer.py` – (future) SendGrid email sending helpers
- `weekly_job.py` – (future) timer-triggered weekly email sender
- `requirements.txt` – Python dependencies
- `host.json`, `local.settings.json` – Azure Functions configuration

This keeps responsibilities clear and minimizes future maintenance.

## 2. Local Configuration

`local.settings.json` should contain at least:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "STORAGE_CONNECTION_STRING": "<your_storage_connection_string>",
    "SENDGRID_API_KEY": "<your_sendgrid_key_later>"
  }
}
```

- `STORAGE_CONNECTION_STRING` is the connection string for the `myblogsubscribers` storage account.
- `SENDGRID_API_KEY` will be used later when you wire up email sending.

Get the storage connection string via:

```powershell
az storage account show-connection-string `
  --name myblogsubscribers `
  --resource-group myblog-subscribers_group `
  --query connectionString -o tsv
```

Use the same value both in `local.settings.json` (local dev) and as an App Setting in the Function App in Azure.

## 3. Subscription Logic Module (`email_subscriber.py`)

Create `email_subscriber.py` to encapsulate all Azure Table Storage interactions for subscribers:

- Reads `STORAGE_CONNECTION_STRING` from environment.
- Uses table name `subscribers`.
- Uses `PartitionKey = subscriber` and `RowKey = email.lower()`.
- Provides a simple API:
  - `subscribe_email(email: str) -> dict`
  - Raises `SubscriptionError` if configuration is missing.

Example outline:

```python
import os
from datetime import datetime
from azure.data.tables import TableClient, TableEntity
from azure.core.exceptions import ResourceExistsError

TABLE_NAME = "subscribers"
PARTITION_KEY = "subscriber"

class SubscriptionError(Exception):
    pass

def get_table_client():
    conn_str = os.environ.get("STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise SubscriptionError("Storage connection not configured")
    return TableClient.from_connection_string(conn_str, TABLE_NAME)

def subscribe_email(email: str) -> dict:
    table = get_table_client()
    entity = TableEntity()
    entity["PartitionKey"] = PARTITION_KEY
    entity["RowKey"] = email.lower()
    entity["email"] = email.lower()
    entity["subscribedAt"] = datetime.utcnow().isoformat()
    entity["isActive"] = True

    try:
        table.create_entity(entity=entity)
        return {
            "status": "created",
            "message": "Thank you for subscribing! You'll receive weekly updates."
        }
    except ResourceExistsError:
        return {
            "status": "exists",
            "message": "You're already subscribed!"
        }
```

## 4. HTTP Function (`function_app.py`)

`function_app.py` is responsible for:

- HTTP binding and routes (`SubscribeEmail`).
- CORS headers.
- Parsing JSON and validating email format.
- Calling `email_subscriber.subscribe_email` and mapping its result to HTTP responses.

High-level flow for `SubscribeEmail`:

1. Handle `OPTIONS` preflight with CORS headers.
2. Read JSON body, extract `email`.
3. Validate presence and format (regex).
4. Call `subscribe_email(email)` from `email_subscriber`.
5. If status is `created` or `exists`, return `200` + corresponding message.
6. On `SubscriptionError`, return `500` with a generic service configuration error.
7. On unexpected exceptions, log and return `500`.

This keeps the function small and testable.

## 5. Front-End Integration (`templates/subscribe-form.html`)

In `templates/subscribe-form.html` you already have a subscription form and JS that posts to an Azure Function URL:

```js
const AZURE_FUNCTION_URL = 'PASTE_YOUR_FUNCTION_URL_HERE';
```

After deploying the function:

1. In the Azure Portal, go to Function App `myblogsubscribers`.
2. Open `SubscribeEmail` function.
3. Click **Get Function URL** and copy the URL (with `code` query parameter).
4. Replace the placeholder in the HTML:

```js
const AZURE_FUNCTION_URL = 'https://myblogsubscribers.azurewebsites.net/api/SubscribeEmail?code=...';
```

For local testing, use the local URL from `func start`, e.g.:

```js
const AZURE_FUNCTION_URL = 'http://localhost:7071/api/SubscribeEmail';
```

## 6. Running Locally in VS Code

From the repo root:

```powershell
cd azure-functions\MyBlogSubscribers

# (if using a virtualenv, activate it first)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

func start
```

- The Functions host will start and show the URL for `SubscribeEmail`.
- Point the front-end to that local URL and submit the form to test end-to-end.

## 7. Verifying Table Writes

Use Azure CLI or Azure Storage Explorer to confirm that subscribers are written into the `subscribers` table.

Example CLI query:

```powershell
az storage entity query `
  --account-name myblogsubscribers `
  --table-name subscribers `
  --connection-string "<your_connection_string>"
```

You should see entities with:

- `PartitionKey = subscriber`
- `RowKey = <email>`
- `isActive = true`

## 8. Deploying the Function App

1. Ensure you are logged into Azure and using the correct subscription:

```powershell
az login
az account set --subscription "cf6c1145-b49c-4d96-9384-9f092c407031"
```

2. From `azure-functions/MyBlogSubscribers`:

```powershell
func azure functionapp publish myblogsubscribers
```

3. In Azure Portal → Function App → **Configuration** → **Application settings**, set:

- `STORAGE_CONNECTION_STRING` = your storage connection string
- (later) `SENDGRID_API_KEY` = your SendGrid API key

4. Use the **Test/Run** blade on `SubscribeEmail` with JSON:

```json
{
  "email": "test@example.com"
}
```

5. Once confirmed working, update the front-end to use the production function URL (see section 5).

## 9. CORS Configuration

Allow your blog domain (e.g. `https://quantuminvestor.ai`) to call the function:

```powershell
az functionapp cors add `
  --name myblogsubscribers `
  --resource-group myblog-subscribers_group `
  --allowed-origins "https://quantuminvestor.ai"
```

For local testing, you can temporarily allow `http://localhost:<port>` if served via Live Server or similar.

## 10. Preparing for Weekly Emails with SendGrid

When ready to send weekly emails:

1. Add SendGrid to `requirements.txt`:

```txt
sendgrid==6.11.0
```

2. Create `mailer.py` with a small API (example):

- Reads `SENDGRID_API_KEY` from env.
- Exposes `send_email(to: str, subject: str, html_body: str)`.

3. Create `weekly_job.py` with a timer trigger, for example running every Friday:

- CRON schedule example: `0 0 12 * * 5` (12:00 UTC Fridays).
- Logic:
  - Use `email_subscriber.get_table_client()` to query active subscribers.
  - Build your email HTML (from templates or generated content).
  - Loop over subscribers and call `mailer.send_email(...)`.

Because subscription logic is centralized in `email_subscriber.py`, the weekly job stays small and easy to maintain.

## 11. Best Practices Recap

- **Single responsibility**:
  - `function_app.py`: triggers and bindings, HTTP/timer glue.
  - `email_subscriber.py`: table operations and subscription rules.
  - `mailer.py`: email delivery via SendGrid.
- **Configuration via environment**: no secrets hard-coded in source.
- **Simple data model**: 1 table (`subscribers`), fixed partition key, `RowKey = email`.
- **Reusable modules**: weekly job and any future tooling reuse the same subscription logic.
- **Minimal moving parts**: Azure Functions + Storage Tables + SendGrid.

This setup gives you a clean foundation: the subscribe form writes to Azure Table Storage via a Function, and you can layer on weekly SendGrid-based emails with minimal extra code and clear separation of concerns.
