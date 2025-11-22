# Brevo Setup Quick Start

## What Was Created

✅ **`mailer.py`** - Brevo email module with send_email() and send_bulk_email()  
✅ **`weekly_job.py`** - Newsletter logic with customizable content  
✅ **`email_subscriber.py`** - Subscriber management with table operations  
✅ **`function_app.py`** - Timer trigger for weekly newsletter  
✅ **`requirements.txt`** - Added sib-api-v3-sdk (Brevo SDK)

## Next Steps to Go Live

### 1. Get Brevo Credentials

1. **Sign up**: https://www.brevo.com (free: 300 emails/day)
2. **Create API Key**: 
   - Login → **Settings** → **SMTP & API** → **API Keys**
   - Click **Generate a new API key**
   - Name it (e.g., "Azure Functions Newsletter")
   - Copy the key immediately (shown once)
3. **Verify sender**: 
   - **Settings** → **Senders & IP**
   - Add and verify your email address
   - For production: Complete domain authentication

### 2. Configure Azure

```powershell
# Set Brevo API key
az functionapp config appsettings set `
  --name myblog-subscribers `
  --resource-group myblog-subscribers_group `
  --settings "BREVO_API_KEY=xkeysib-your_actual_key_here"

# Set sender email (must be verified in Brevo)
az functionapp config appsettings set `
  --name myblog-subscribers `
  --resource-group myblog-subscribers_group `
  --settings "BREVO_FROM_EMAIL=newsletter@quantuminvestor.net"

# Set sender display name (optional)
az functionapp config appsettings set `
  --name myblog-subscribers `
  --resource-group myblog-subscribers_group `
  --settings "BREVO_FROM_NAME=Quantum Investor"
```

### 3. Deploy Updated Code

```powershell
cd C:\Users\mgavril\Documents\GitHub\My-blog\azure-functions\MyBlogSubscribers
func azure functionapp publish myblog-subscribers --build remote
```

**Wait for deployment to complete** (~1-2 minutes). You should see:
```
Deployment successful.
Functions in myblog-subscribers:
    subscribe_email - [httpTrigger]
        Invoke url: https://myblog-subscribers-dbatcqezhcddd6gy.canadacentral-01.azurewebsites.net/api/subscribeemail
    weekly_newsletter - [timerTrigger]
```

### 4. Customize Email Content

Edit `weekly_job.py` → `get_weekly_email_content()` function:
- Change subject line
- Update HTML template with your content
- Add your logo, links, branding
- Include latest blog post link
- Add market insights, portfolio summary, etc.

Example customization:
```python
def get_weekly_email_content():
    # TODO: Pull latest blog post dynamically
    latest_post_url = "https://quantuminvestor.net/Posts/GenAi-Managed-Stocks-Portfolio-Week-6.html"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body>
        <h1>📊 Weekly Market Insights</h1>
        <p>This week's portfolio update is live!</p>
        <a href="{latest_post_url}">Read the full analysis →</a>
    </body>
    </html>
    """
    
    return {
        "subject": "📊 Your Weekly Quantum Investor Digest",
        "html_body": html_body
    }
```

### 5. Test Manually

**Option A: Azure Portal (Recommended)**
1. Go to: https://portal.azure.com
2. Navigate to **myblog-subscribers** Function App
3. Click **Functions** → **weekly_newsletter**
4. Click **Code + Test** → **Test/Run**
5. Click **Run** button
6. Check **Logs** tab for output

**Option B: Azure CLI**
```powershell
az functionapp function invoke `
  --name myblog-subscribers `
  --resource-group myblog-subscribers_group `
  --function-name weekly_newsletter
```

**Verify emails sent:**
- Check your test subscriber inbox
- Brevo Dashboard → **Statistics** → **Email**
- View real-time delivery logs

### 6. Adjust Schedule (Optional)

In `function_app.py`, change the schedule parameter:

```python
# Current: Every Friday at 12:00 PM UTC
@app.timer_trigger(schedule="0 0 12 * * FRI", ...)

# Change to Monday 9 AM UTC:
@app.timer_trigger(schedule="0 0 9 * * MON", ...)

# Or Saturday 8 AM UTC:
@app.timer_trigger(schedule="0 0 8 * * SAT", ...)
```

**Schedule format:** `"second minute hour day month dayOfWeek"`
- Use [crontab.guru](https://crontab.guru/) to generate expressions
- Azure uses UTC timezone (adjust for your local time)

## Email Content Ideas

Your newsletter can include:
- 📈 **Portfolio performance summary** (weekly returns)
- 💡 **Top 3-5 trades** from the AI analysis
- 🤖 **AI insights and reasoning** behind decisions
- 📰 **Link to latest blog post** (Week 7, 8, etc.)
- 📊 **Market commentary** and outlook
- 🎯 **Key takeaways** for subscribers

**Start simple, iterate based on engagement!**

## Monitoring

### Brevo Dashboard
- Real-time email statistics
- Delivery, open, click rates
- Bounce and spam reports
- Individual email logs

### Azure Function Logs
```powershell
# Stream live logs
func azure functionapp logstream myblog-subscribers

# Or in Azure Portal:
# Function App → Monitor → Logs
```

### Subscriber Table
```powershell
# Count active subscribers
az storage entity query `
  --account-name myblogsubscribers `
  --table-name subscribers `
  --filter "PartitionKey eq 'subscriber' and isActive eq true" `
  --select email
```

## Cost Comparison

### Brevo Free Tier
- **300 emails/day** (9,000/month)
- Unlimited contacts
- Email API included
- Enough for ~1,200+ weekly subscribers

### Azure Costs
- **Timer triggers:** Free (included)
- **HTTP triggers:** Free (first 1M requests)
- **Table Storage:** ~$0.001 per 1,000 subscribers/month

**Total cost for first 1,000 subscribers: $0** (within free tiers)

## Troubleshooting

### Issue: "BREVO_API_KEY not configured"
**Solution:** Verify API key is set in Azure:
```powershell
az functionapp config appsettings list `
  --name myblog-subscribers `
  --resource-group myblog-subscribers_group `
  --query "[?name=='BREVO_API_KEY']"
```

### Issue: "Sender email not verified"
**Solution:** 
1. Check Brevo Dashboard → Senders & IP
2. Resend verification email if needed
3. Use the exact verified email in BREVO_FROM_EMAIL

### Issue: No emails being sent
**Check:**
1. Function executed successfully (check logs)
2. Subscribers exist with `isActive=true`
3. Brevo API key has correct permissions
4. No rate limit errors in Brevo dashboard

### Issue: Emails going to spam
**Solutions:**
- Complete domain authentication in Brevo
- Add SPF and DKIM records to your DNS
- Use a professional sender email (not gmail.com)
- Avoid spam trigger words in subject/content

## Next Features (Optional)

1. **Unsubscribe page**
   - Create HTML form on site
   - Call Azure Function with email
   - Use `email_subscriber.unsubscribe_email()`

2. **Dynamic content**
   - Pull latest blog post from master.json
   - Include portfolio performance from Data/W6/
   - Add personalized greeting

3. **Email analytics**
   - Track open rates (Brevo provides this)
   - Add UTM parameters to links
   - Measure subscriber engagement

4. **A/B testing**
   - Test different subject lines
   - Optimize send times
   - Improve content based on clicks

## Support Resources

- **Brevo Documentation:** https://developers.brevo.com/
- **Brevo Python SDK:** https://github.com/sendinblue/APIv3-python-library
- **Azure Functions Docs:** https://learn.microsoft.com/azure/azure-functions/
- **Cron Scheduler:** https://crontab.guru/

---

**You're all set! 🎉**

Just configure Brevo, deploy, and test. Your weekly newsletter system will run automatically every Friday at noon UTC.
