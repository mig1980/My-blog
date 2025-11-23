# GenAI Prompt for Weekly Newsletter Generation

## Context for AI Model

You are tasked with generating a professional, engaging weekly newsletter email for **Quantum Investor Digest**, a blog that tracks an AI-managed stock portfolio and explores the intersection of generative AI and investing.

---

## Data Input Required

You will receive TWO sources of data:

### 1. JSON Data File (e.g., `Data/W6/master.json`)

Contains structured performance metrics:
- Portfolio current value, weekly percentage change, total percentage change
- Individual stock holdings with prices, shares, and performance metrics
- S&P 500 weekly and total performance
- Bitcoin weekly and total performance
- Week-by-week value progression since inception
- Normalized performance chart data

### 2. Blog Post HTML File (e.g., `Posts/GenAi-Managed-Stocks-Portfolio-Week-6.html`)

Contains narrative content and context:
- **Opening paragraph**: Sets the weekly tone (e.g., "This week, the GenAi Chosen portfolio fell -5.82%...")
- **Portfolio Progress section**: Explains strategy and weekly developments
- **Top Movers section**: Highlights best/worst performers with market context
- **Performance narrative**: Interprets the data with market insights

**Critical**: The newsletter must **echo the blog post's narrative style** and key insights, condensed to 300-500 words. Extract:
- Opening tone/sentiment (bearish, bullish, neutral)
- 2-3 key insights from "Top Movers" section
- Strategic context from "Portfolio Progress" section
- Market commentary (risk-on vs. risk-off, sector rotation, etc.)

---

## Newsletter Requirements

### Design Constraints
- **Maximum width**: 600px (standard email best practice)
- **Mobile-first**: Must render perfectly on iOS Mail, Gmail (Android), Outlook, Apple Mail
- **Safe fonts**: Arial, Helvetica, sans-serif (web fonts unreliable in email)
- **Inline CSS only**: No external stylesheets or `<style>` blocks in `<head>`
- **Image strategy**: Host images on quantuminvestor.net, use absolute URLs
- **Dark mode aware**: Use colors that work in both light and dark email clients

### Brand Guidelines
- **Primary color**: #a855f7 (purple) - use for CTAs, links, highlights
- **Background**: Light (#f9f9f9 or #ffffff for body), dark accent (#1a1a1a) for header/footer
- **Typography**: Clean, modern, professional tone
- **Voice**: Data-driven, transparent, educational, slightly technical but accessible

### Content Structure (Best Practices)

**Length**: 300-500 words of body content (excludes data tables)
- Short enough to read in 2-3 minutes
- Long enough to provide value and drive clicks

**Sections**:

1. **Header** (40-60px height)
   - Logo or site name
   - Simple, clean design
   - Dark background (#1a1a1a) with white text

2. **Hero/Opening** (2-3 sentences)
   - Week number and date range
   - Emotional hook: "Tough week" / "Strong rebound" / "Mixed signals"
   - Set expectations for what's inside

3. **Portfolio Performance Snapshot** (Visual priority)
   - Current value: $X,XXX
   - Weekly change: ±X.XX% (color-coded: green for positive, red for negative)
   - Total return since inception: ±X.XX%
   - Use emoji sparingly: 📊 📈 📉 (max 2-3 per email)

4. **Key Insights** (3 bullet points max)
   - Top performer this week (stock ticker + %)
   - Biggest loser this week (stock ticker + %)
   - One strategic observation from AI analysis

5. **Benchmark Comparison** (Simple table or list)
   - GenAI Portfolio: X.XX%
   - S&P 500: X.XX%
   - Bitcoin: X.XX%

6. **Call-to-Action** (Primary button)
   - Text: "Read Full Week X Analysis →" or "See Complete Portfolio Breakdown"
   - Link to: https://quantuminvestor.net/Posts/GenAi-Managed-Stocks-Portfolio-Week-X.html
   - Button style: Purple (#a855f7), 12-16px padding, rounded corners, white text
   - Make it look clickable but avoid image-based buttons

7. **Footer** (Unsubscribe, legal, branding)
   - "You're subscribed to Quantum Investor Digest"
   - Links: Website | Unsubscribe (use # placeholder for now)
   - Small text (11-12px), gray color (#666666)

---

## Tone and Writing Style

- **Objective, not promotional**: Report facts, let data speak
- **Acknowledge losses**: If portfolio is down, say so directly (builds trust)
- **Avoid hype**: No "🚀 TO THE MOON" language
- **Educational angle**: Brief mention of why something happened (if data suggests reason)
- **Conversational but professional**: "This week was challenging" not "OMG BRUTAL WEEK!!!"

---

## Technical Email Requirements

### HTML Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Investor - Week X Update</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
</head>
<body style="margin:0; padding:0; font-family:Arial,sans-serif; background-color:#f4f4f4;">
    <!-- Email content here -->
</body>
</html>
```

### CSS Best Practices for Email
- **All styles inline**: `<div style="color:#333;">`
- **Use tables for layout**: Flexbox/Grid unreliable in Outlook
- **Padding over margin**: Margins buggy in some clients
- **Hex colors only**: Named colors can render differently
- **Test links**: Use full `https://` URLs, never relative paths

### Mobile Optimization
- **Font size**: Minimum 14px for body text, 16px+ for important info
- **Touch targets**: Buttons at least 44px height for easy tapping
- **Single column layout**: Don't rely on multi-column layouts on mobile
- **Preheader text**: First 40-60 characters show in inbox preview

---

## Example Prompt for AI Model

```
Generate a professional weekly newsletter email for Quantum Investor Digest using BOTH sources:

1. JSON Data: Data/W6/master.json
2. Blog Post HTML: Posts/GenAi-Managed-Stocks-Portfolio-Week-6.html

Week: 6
Date Range: November 14-20, 2025

Key Data Points (from JSON):
- Portfolio Value: $9,699 (-5.82% weekly, -3.01% total)
- S&P 500: -1.41% weekly (-0.69% total)
- Bitcoin: -12.10% weekly (-28.96% total)
- Top Performer: HWM (-1.68% weekly)
- Biggest Loser: PLTR (-9.52% weekly)

Narrative Guidance (from Blog Post HTML):
- Opening tone: "This week, the GenAi Chosen portfolio fell -5.82%, reducing its total return since inception to -3.01%"
- Key insight 1: "Tech stocks led the decline, with Western Digital (WDC) dropping -10.77%"
- Key insight 2: "Gold exposure failed to provide a safe haven, as Newmont Corp (NEM) declined -8.59%"
- Key insight 3: "Bitcoin's plunge accentuates risk aversion, with the cryptocurrency crashing -12.1%"
- Market context: "Risk-off sentiment dominating broader markets" + "Synchronized drawdown highlights portfolio's sensitivity to broad market reversals"

Newsletter Requirements:
1. Email must be 600px max width
2. Use inline CSS only (no external stylesheets)
3. Color scheme: Purple #a855f7 (primary), dark gray #1a1a1a (header), light gray #f9f9f9 (body)
4. Include one strong CTA button linking to: https://quantuminvestor.net/Posts/GenAi-Managed-Stocks-Portfolio-Week-6.html
5. Mobile-responsive (test on iOS Mail, Gmail, Outlook)
6. Professional tone matching blog post (honest, data-driven, acknowledge losses)
7. Keep body content under 400 words (condensed version of blog narrative)
8. Preheader text (first sentence): "Week 6 portfolio update: -5.82% amid market volatility"
9. **CRITICAL**: Newsletter content must align with and summarize the blog post HTML narrative, NOT create new analysis

Content Structure:
- Hero: Mirror the blog's opening paragraph tone
- Performance section: Use exact numbers from JSON
- Insights section: Condense "Top Movers" section (2-3 key points)
- CTA: "Read Full Week 6 Analysis" button

Output: Complete HTML email code ready to send via Brevo API.
```

---

## Quality Checklist

Before sending, generated email must have:

- [ ] Subject line under 50 characters
- [ ] Preheader text optimized (40-60 chars)
- [ ] All images use absolute URLs (https://quantuminvestor.net/...)
- [ ] CTA button clearly visible and clickable
- [ ] Unsubscribe link present in footer
- [ ] Mobile-responsive (tested on iPhone, Android)
- [ ] No broken links
- [ ] Honest, transparent performance reporting
- [ ] Brand colors consistent (#a855f7 purple)
- [ ] Total read time under 3 minutes
- [ ] No spelling or grammar errors
- [ ] Alt text for images (accessibility)

---

## Subject Line Formula

**Pattern**: `[Emoji] Week X: [Performance] | [Key Insight]`

**Examples**:
- `📊 Week 6: -5.82% | Market-Wide Selloff`
- `📈 Week 5: Holding Strong at +2.98%`
- `📉 Week 4: Portfolio Dips -2% | Rebalancing Ahead?`

**Best Practices**:
- 40-50 characters (mobile inbox display)
- Include weekly percentage (transparency)
- One emoji max (improves open rates)
- Avoid spam trigger words: "Free", "Act Now", "Limited Time"

---

## A/B Testing Suggestions (Future Enhancement)

Test variations of:
1. **Subject lines**: Emoji vs. no emoji, performance first vs. insight first
2. **CTA button text**: "Read Full Analysis" vs. "See This Week's Trades"
3. **Opening tone**: Data-first vs. storytelling-first
4. **Send time**: Friday 12 PM UTC vs. Saturday 8 AM UTC

---

## Data Parsing Instructions for AI

When processing `master.json`:

1. Extract `portfolio_totals.weekly_pct` → Main headline number
2. Sort `stocks` array by `weekly_pct` → Find top/bottom performers
3. Compare `portfolio_totals.weekly_pct` vs. `benchmarks.sp500.history[-1].weekly_pct`
4. Include inception date and current date from `meta` section
5. Format all percentages to 2 decimal places with explicit +/- sign

---

## Output Format

The AI should generate a **single HTML file** containing:
- Complete `<!DOCTYPE html>` through `</html>`
- All CSS inline on elements
- No external dependencies
- Ready to pass as `html_body` to Brevo API

Example output start:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Investor - Week 6 Update</title>
</head>
<body style="margin:0; padding:0; font-family:Arial,Helvetica,sans-serif; background-color:#f4f4f4; line-height:1.6;">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f4f4f4;">
        <tr>
            <td align="center" style="padding:20px 10px;">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" style="max-width:600px; background-color:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color:#1a1a1a; padding:30px 20px; text-align:center;">
                            <h1 style="margin:0; font-size:24px; color:#ffffff; font-weight:700;">Quantum Investor Digest</h1>
                            <p style="margin:5px 0 0 0; font-size:14px; color:#a855f7;">Week 6 Portfolio Update</p>
                        </td>
                    </tr>
                    <!-- Body content continues... -->
```

---

## Integration with Newsletter Generation Script

**IMPORTANT**: Newsletter generation happens **OUTSIDE** Azure Functions, in a separate script.

### Why Separate?
- ✅ Azure Functions have timeout limits (5-10 minutes)
- ✅ AI API calls can be slow and expensive
- ✅ Allows human review before sending
- ✅ Generation and distribution on different schedules

### Recommended Workflow

1. **Create `scripts/generate_newsletter.py`** (runs locally or via GitHub Actions):
   - Reads `Data/W{current_week}/master.json`
   - Reads `Posts/GenAi-Managed-Stocks-Portfolio-Week-{current_week}.html`
   - Calls OpenAI/Claude API with this prompt
   - Generates newsletter HTML
   - **Uploads to Azure Blob Storage** `newsletters/week{N}.html`

2. **Azure Function `weekly_job.py`** (runs on timer):
   - Auto-detects latest week from GitHub Posts/ folder
   - **Downloads newsletter from Blob Storage**
   - Sends to subscribers via Brevo

### Generation Script Pseudocode

### Newsletter Generation Script Example

**File**: `scripts/generate_newsletter.py`

```python
import json
import openai
import os
from bs4 import BeautifulSoup
from azure.storage.blob import BlobServiceClient

def generate_and_upload_newsletter(week_num):
    # Read latest week's data
    week_num = 6  # TODO: Auto-detect latest week
    
    # Load JSON data
    with open(f'../../Data/W{week_num}/master.json') as f:
        data = json.load(f)
    
    # Load blog post HTML
    with open(f'../../Posts/GenAi-Managed-Stocks-Portfolio-Week-{week_num}.html') as f:
        html_content = f.read()
    
    # Parse HTML to extract narrative sections
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract key narrative elements
    opening_para = soup.find('p', class_='text-xl').get_text() if soup.find('p', class_='text-xl') else ""
    
    # Find "Top Movers" section
    top_movers_section = ""
    for h2 in soup.find_all('h2'):
        if 'Top Movers' in h2.get_text():
            # Get next few paragraphs after this heading
            current = h2.find_next_sibling('p')
            paragraphs = []
            while current and current.name == 'p' and len(paragraphs) < 3:
                paragraphs.append(current.get_text())
                current = current.find_next_sibling()
            top_movers_section = ' '.join(paragraphs)
            break
    
    # Generate prompt with both data sources
    prompt = f"""
    Generate a professional weekly newsletter for Quantum Investor Digest.
    
    WEEK: {week_num}
    DATE RANGE: [Extract from data]
    
    JSON DATA:
    {json.dumps(data, indent=2)}
    
    BLOG POST NARRATIVE TO ALIGN WITH:
    
    Opening: {opening_para}
    
    Top Movers Context: {top_movers_section}
    
    REQUIREMENTS:
    - 600px max width, inline CSS only
    - Color scheme: Purple #a855f7 (primary), #1a1a1a (header), #f9f9f9 (body)
    - CTA button to: https://quantuminvestor.net/Posts/GenAi-Managed-Stocks-Portfolio-Week-{week_num}.html
    - Newsletter must summarize and align with blog post narrative (same tone, key insights)
    - Body content under 400 words
    - Mobile-responsive for iOS Mail, Gmail, Outlook
    
    OUTPUT: Complete HTML email ready for Brevo API.
    """
    
    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    html_body = response.choices[0].message.content
    
    # Save locally first (for review)
    output_path = f'newsletters/week{week_num}.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_body)
    
    print(f"✅ Newsletter generated: {output_path}")
    
    # Upload to Azure Blob Storage
    connection_string = os.environ['STORAGE_CONNECTION_STRING']
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(
        container='newsletters',
        blob=f'week{week_num}.html'
    )
    
    with open(output_path, 'rb') as data:
        blob_client.upload_blob(data, overwrite=True)
    
    print(f"✅ Uploaded to Azure Blob Storage: newsletters/week{week_num}.html")
    
    # Generate subject line from data
    weekly_pct = data['portfolio_totals']['weekly_pct']
    subject = f"📊 Week {week_num}: {weekly_pct:+.2f}% | {get_sentiment(weekly_pct)}"
    
    return {"subject": subject, "file_path": output_path}

def get_sentiment(pct):
    """Generate subject line sentiment based on performance"""
    if pct > 2:
        return "Strong Gains"
    elif pct > 0:
        return "Positive Week"
    elif pct > -2:
        return "Minor Pullback"
    else:
        return "Market Volatility"
```

### Required Python Packages

**For generation script** (`scripts/requirements.txt`):
```
beautifulsoup4
openai
azure-storage-blob
```

**For Azure Function** (`azure-functions/MyBlogSubscribers/requirements.txt`):
```
azure-functions
azure-data-tables
azure-storage-blob
sib-api-v3-sdk
requests  # For fetching from GitHub raw URLs
```

---

## Final Notes

- **Test every email**: Use Litmus or Email on Acid to preview across 40+ clients
- **Monitor metrics**: Track open rates, click rates, unsubscribe rates
- **Iterate weekly**: Improve based on engagement data
- **Respect subscribers**: Make unsubscribe easy and honor it immediately
- **Legal compliance**: Include physical address (can be PO Box) per CAN-SPAM Act

---

## Resources

- [Email on Acid](https://www.emailonacid.com/) - Email testing
- [Really Good Emails](https://reallygoodemails.com/) - Design inspiration
- [Litmus](https://www.litmus.com/) - Email analytics
- [Can I Email](https://www.caniemail.com/) - CSS support in email clients
