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

## Two-Stage Newsletter Generation Pipeline

**IMPORTANT**: Newsletter generation happens **OUTSIDE** Azure Functions, in a TWO-STAGE process.

### Why Two Stages?
- ✅ **Stage 1 (Narrative)**: Extract and condense blog post content (reusable, reviewable)
- ✅ **Stage 2 (HTML)**: Convert narrative to email-optimized HTML (platform-specific)
- ✅ **Human review checkpoint**: Between stages to verify narrative accuracy
- ✅ **Flexibility**: Can regenerate HTML without re-analyzing blog post

### Complete Workflow

```
[Stage 1: Narrative Generation]
Blog Post HTML + master.json → AI Analysis → narrative.json (Blob Storage)
                                                    ↓
                                          [Human Review/Edit]
                                                    ↓
[Stage 2: HTML Generation]
narrative.json → AI Email Formatting → week{N}.html (Blob Storage)
                                                    ↓
[Azure Function: Distribution]
week{N}.html → Brevo API → Subscribers
```

---

## STAGE 1: Generate Newsletter Narrative

### Purpose
Extract key insights from blog post and data, create concise newsletter narrative as JSON.

### Prompt 1: Narrative Extraction

**File**: `scripts/1_generate_narrative.py`

### AI Prompt for Stage 1

```
You are analyzing a weekly blog post about an AI-managed stock portfolio to extract newsletter content.

INPUT DATA:
1. Blog Post HTML: Posts/GenAi-Managed-Stocks-Portfolio-Week-{N}.html
2. Portfolio Data: Data/W{N}/master.json

TASK:
Extract and condense the blog post into newsletter-ready narrative elements. Focus on clarity, conciseness, and alignment with the blog's tone.

OUTPUT FORMAT (JSON):
{
  "week_number": 6,
  "date_range": "November 14-20, 2025",
  "subject_line": "📊 Week 6: -5.82% | Market-Wide Selloff",
  "preheader": "Portfolio update: Tech-led decline amid risk-off sentiment",
  "opening_paragraph": "This week tested the portfolio's resilience as broad market weakness pulled returns down -5.82%. The decline reduces our total return since inception to -3.01%, underperforming the S&P 500's -0.69% total return.",
  "key_insights": [
    {
      "title": "Tech Stocks Led Decline",
      "description": "Western Digital (WDC) and Palantir (PLTR) led losses, dropping -10.77% and -9.52% respectively as risk-off sentiment hit growth stocks."
    },
    {
      "title": "Gold Failed as Safe Haven",
      "description": "Newmont Corp (NEM) fell -8.59% despite its defensive positioning, highlighting synchronized market pressure."
    },
    {
      "title": "Bitcoin Crash Amplified Losses",
      "description": "Cryptocurrency exposure added pain with Bitcoin plunging -12.1%, reflecting extreme risk aversion."
    }
  ],
  "performance_data": {
    "portfolio_value": "$9,699",
    "weekly_change": "-5.82%",
    "total_return": "-3.01%",
    "sp500_weekly": "-1.41%",
    "sp500_total": "-0.69%",
    "bitcoin_weekly": "-12.10%",
    "bitcoin_total": "-28.96%",
    "top_performer": {"ticker": "HWM", "change": "-1.68%"},
    "worst_performer": {"ticker": "PLTR", "change": "-9.52%"}
  },
  "market_context": "Risk-off sentiment dominated markets this week, with synchronized drawdowns across equities, commodities, and crypto. The portfolio's sensitivity to broad market reversals was evident.",
  "call_to_action_url": "https://quantuminvestor.net/Posts/GenAi-Managed-Stocks-Portfolio-Week-6.html",
  "tone": "honest, data-driven, acknowledges losses without panic"
}

EXTRACTION RULES:
1. **Opening paragraph**: 2-3 sentences summarizing weekly performance and context
2. **Key insights**: Extract 2-3 main points from "Top Movers" or "Portfolio Progress" sections
3. **Keep numbers exact**: Use precise percentages from master.json
4. **Mirror tone**: Match blog post's sentiment (bullish/bearish/neutral)
5. **No new analysis**: Only condense existing blog content
6. **Subject line**: Format as "[Emoji] Week X: [%] | [Key Theme]" (under 50 chars)
7. **Preheader**: First 50-60 characters for inbox preview

OUTPUT: Valid JSON only, no markdown formatting.
```

### Stage 1 Script Example

```python
import json
import os
from bs4 import BeautifulSoup
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI
import os

def generate_narrative(week_num: int):
    """
    STAGE 1: Generate newsletter narrative from blog post and data.
    Uploads narrative JSON to Azure Blob Storage for review/editing.
    """
    # Load JSON data
    data_path = f'Data/W{week_num}/master.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        portfolio_data = json.load(f)
    
    # Load blog post HTML
    blog_path = f'Posts/GenAi-Managed-Stocks-Portfolio-Week-{week_num}.html'
    with open(blog_path, 'r', encoding='utf-8') as f:
        blog_html = f.read()
    
    # Prepare AI prompt
    prompt = f"""
You are analyzing a weekly blog post about an AI-managed stock portfolio to extract newsletter content.

BLOG POST HTML:
{blog_html[:5000]}... [truncated for brevity]

PORTFOLIO DATA (master.json):
{json.dumps(portfolio_data, indent=2)}

TASK:
Extract and condense the blog post into newsletter-ready narrative elements.

OUTPUT FORMAT (JSON):
{{
  "week_number": {week_num},
  "date_range": "Extract from blog or data",
  "subject_line": "Generate based on performance",
  "preheader": "50-60 char inbox preview",
  "opening_paragraph": "2-3 sentences summarizing week",
  "key_insights": [
    {{"title": "...", "description": "..."}},
    {{"title": "...", "description": "..."}},
    {{"title": "...", "description": "..."}}
  ],
  "performance_data": {{
    "portfolio_value": "...",
    "weekly_change": "...",
    "total_return": "...",
    "sp500_weekly": "...",
    "sp500_total": "...",
    "bitcoin_weekly": "...",
    "bitcoin_total": "...",
    "top_performer": {{"ticker": "...", "change": "..."}},
    "worst_performer": {{"ticker": "...", "change": "..."}}
  }},
  "market_context": "1-2 sentence market summary",
  "call_to_action_url": "https://quantuminvestor.net/Posts/GenAi-Managed-Stocks-Portfolio-Week-{week_num}.html",
  "tone": "honest/bullish/bearish"
}}

RULES:
- Extract from blog, don't create new analysis
- Keep numbers exact from master.json
- Subject line under 50 characters
- Tone must match blog post sentiment

OUTPUT: Valid JSON only.
"""
    
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
        api_version="2024-05-01-preview",
        azure_endpoint="https://myportfolious2-resource.cognitiveservices.azure.com/openai/"
    )
    
    # Call Azure OpenAI API
    response = client.chat.completions.create(
        model="gpt-5.1-chat",
        messages=[
            {"role": "system", "content": "You extract newsletter narratives from blog posts. Output valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        # Note: GPT-5.1 only supports default temperature (1)
        max_completion_tokens=2000
    )
    
    narrative_json = response.choices[0].message.content.strip()
    
    # Parse to validate JSON
    narrative_data = json.loads(narrative_json)
    
    # Save locally for review
    local_path = f'newsletters/week{week_num}_narrative.json'
    os.makedirs('newsletters', exist_ok=True)
    with open(local_path, 'w', encoding='utf-8') as f:
        json.dump(narrative_data, f, indent=2)
    
    print(f"✅ Narrative generated: {local_path}")
    print(f"   Subject: {narrative_data['subject_line']}")
    print(f"   Tone: {narrative_data['tone']}")
    
    # Upload to Azure Blob Storage
    connection_string = os.environ.get('STORAGE_CONNECTION_STRING')
    if connection_string:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(
            container='newsletters',
            blob=f'week{week_num}_narrative.json'
        )
        
        blob_client.upload_blob(narrative_json, overwrite=True)
        print(f"✅ Uploaded to Blob Storage: newsletters/week{week_num}_narrative.json")
    
    return narrative_data

if __name__ == "__main__":
    week = 6  # Auto-detect from Posts folder
    narrative = generate_narrative(week)
    print("\n📋 REVIEW NARRATIVE BEFORE STAGE 2")
    print("Edit newsletters/week6_narrative.json if needed, then run Stage 2")
```

---

## STAGE 2: Generate Email HTML

### Purpose
Convert narrative JSON into mobile-optimized HTML email with inline CSS.

### Prompt 2: HTML Email Generation

**File**: `scripts/2_generate_html.py`

### AI Prompt for Stage 2

```
You are generating a mobile-optimized HTML email for a financial newsletter.

INPUT DATA (JSON):
{narrative_json}

TASK:
Convert this narrative into a professional HTML email that renders perfectly on:
- iOS Mail, Gmail (Android), Outlook, Apple Mail
- Mobile and desktop screens

DESIGN REQUIREMENTS:
1. Maximum width: 600px
2. Inline CSS only (no <style> blocks or external stylesheets)
3. Table-based layout (Flexbox/Grid unreliable in Outlook)
4. Color scheme:
   - Primary: #a855f7 (purple for CTAs and accents)
   - Header: #1a1a1a (dark background)
   - Body: #ffffff (white background)
   - Text: #333333 (dark gray)
   - Footer: #666666 (medium gray)
5. Font: Arial, Helvetica, sans-serif
6. CTA button: Purple (#a855f7), white text, 14px padding, rounded corners
7. Emoji: Use sparingly (1-2 max in header/subject)

HTML STRUCTURE:
- Header: Site name + week number
- Opening: Hero paragraph from narrative
- Performance Box: Visual snapshot (current value, weekly %, total %)
- Key Insights: 3 bullet points from narrative.key_insights
- Benchmark Table: Portfolio vs S&P 500 vs Bitcoin
- CTA Button: "Read Full Week {N} Analysis →"
- Footer: Unsubscribe link, website link, disclaimer

CRITICAL CSS RULES:
- All styles inline: <td style="padding:20px;">
- Use `cellpadding="0" cellspacing="0" border="0"` on all tables
- Touch-friendly buttons: min-height 44px
- Font size: 14px minimum for body, 16px for important text
- Test in Outlook: Use `<!--[if mso]>` conditionals if needed

TONE:
Match the tone specified in narrative.tone (honest, data-driven, professional)

OUTPUT:
Complete HTML email from <!DOCTYPE html> to </html>
Ready to upload to Blob Storage and send via Brevo API
```

### Stage 2 Script Example

```python
import json
import os
from azure.storage.blob import BlobServiceClient
import openai

def generate_html(week_num: int):
    """
    STAGE 2: Generate HTML email from narrative JSON.
    Downloads narrative from Blob Storage, generates HTML, uploads final email.
    """
    # Load narrative from Blob Storage (or local if reviewing)
    connection_string = os.environ.get('STORAGE_CONNECTION_STRING')
    
    if connection_string:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(
            container='newsletters',
            blob=f'week{week_num}_narrative.json'
        )
        narrative_json = blob_client.download_blob().readall().decode('utf-8')
        print(f"✅ Downloaded narrative from Blob Storage")
    else:
        # Fallback to local file
        with open(f'newsletters/week{week_num}_narrative.json', 'r', encoding='utf-8') as f:
            narrative_json = f.read()
    
    narrative_data = json.loads(narrative_json)
    
    # Prepare AI prompt
    prompt = f"""
You are generating a mobile-optimized HTML email for a financial newsletter.

INPUT DATA (JSON):
{narrative_json}

TASK:
Convert this narrative into a professional HTML email (600px max width, inline CSS, table layout).

DESIGN:
- Colors: Purple #a855f7 (CTA), Dark #1a1a1a (header), White #ffffff (body)
- Font: Arial, Helvetica, sans-serif
- CTA button to: {narrative_data['call_to_action_url']}
- Responsive for iOS Mail, Gmail, Outlook

STRUCTURE:
1. Header: Site name + Week {narrative_data['week_number']}
2. Opening: {narrative_data['opening_paragraph']}
3. Performance Box: Portfolio value, weekly %, total %
4. Key Insights: 3 bullets from narrative
5. Benchmark Table: Portfolio vs S&P 500 vs Bitcoin
6. CTA Button: "Read Full Week {narrative_data['week_number']} Analysis"
7. Footer: Unsubscribe + website links

OUTPUT: Complete HTML from <!DOCTYPE> to </html>, inline CSS only.
"""
    
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
        api_version="2024-05-01-preview",
        azure_endpoint="https://myportfolious2-resource.cognitiveservices.azure.com/openai/"
    )
    
    # Call Azure OpenAI API
    response = client.chat.completions.create(
        model="gpt-5.1-chat",
        messages=[
            {"role": "system", "content": "You generate email-optimized HTML with inline CSS. Output HTML only."},
            {"role": "user", "content": prompt}
        ],
        # Note: GPT-5.1 only supports default temperature (1)
        max_completion_tokens=3000
    )
    
    html_content = response.choices[0].message.content.strip()
    
    # Remove markdown code fences if present
    if html_content.startswith('```html'):
        html_content = html_content.replace('```html', '').replace('```', '').strip()
    
    # Save locally
    local_path = f'newsletters/week{week_num}.html'
    with open(local_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML generated: {local_path} ({len(html_content)} bytes)")
    
    # Upload to Azure Blob Storage
    if connection_string:
        blob_client = blob_service_client.get_blob_client(
            container='newsletters',
            blob=f'week{week_num}.html'
        )
        blob_client.upload_blob(html_content, overwrite=True)
        print(f"✅ Uploaded to Blob Storage: newsletters/week{week_num}.html")
        print(f"🚀 Ready to send! Azure Function will distribute on Friday 12PM UTC")
    
    return html_content

if __name__ == "__main__":
    week = 6
    html = generate_html(week)
    print("\n✅ STAGE 2 COMPLETE")
    print("Newsletter HTML ready in Blob Storage")
    print("Test by manually triggering weekly_newsletter function in Azure Portal")
```

---

## Complete Pipeline Execution

### Manual Workflow

```bash
# Stage 1: Generate narrative
python scripts/1_generate_narrative.py
# Output: newsletters/week6_narrative.json (local + Blob Storage)

# Review and edit narrative if needed
# Edit newsletters/week6_narrative.json

# Upload edited narrative to Blob Storage
az storage blob upload --container-name newsletters --name week6_narrative.json --file newsletters/week6_narrative.json --connection-string "..."

# Stage 2: Generate HTML
python scripts/2_generate_html.py
# Output: newsletters/week6.html (local + Blob Storage)

# Test email (manual trigger in Azure Portal)
# Azure Function automatically detects week 6 from GitHub
# Downloads week6.html from Blob Storage
# Sends to all subscribers
```

### Automated Workflow (GitHub Actions)

```yaml
name: Generate Newsletter
on:
  workflow_dispatch:
    inputs:
      week_number:
        description: 'Week number to generate'
        required: true

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Stage 1 - Generate Narrative
        run: python scripts/1_generate_narrative.py
        env:
          AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
          STORAGE_CONNECTION_STRING: ${{ secrets.STORAGE_CONNECTION_STRING }}
      
      - name: Review Gate (Manual Approval)
        uses: trstringer/manual-approval@v1
        with:
          approvers: mig1980
          minimum-approvals: 1
      
      - name: Stage 2 - Generate HTML
        run: python scripts/2_generate_html.py
        env:
          AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
          STORAGE_CONNECTION_STRING: ${{ secrets.STORAGE_CONNECTION_STRING }}
```

---

## Benefits of Two-Stage Approach

### ✅ Advantages:
1. **Human Review Checkpoint**: Edit narrative JSON before HTML generation
2. **Faster Iteration**: Regenerate HTML without re-analyzing blog
3. **Version Control**: Track narrative changes separately from HTML
4. **Reusability**: Same narrative can generate multiple formats (email, social, SMS)
5. **Testing**: Validate narrative accuracy before committing to HTML
6. **Cost Efficiency**: Stage 2 is cheaper (shorter prompt, less context)

### 📊 Blob Storage Structure:
```
newsletters/
├── week6_narrative.json     # Stage 1 output (reviewable)
└── week6.html              # Stage 2 output (sendable)
```

### 🔄 Azure Function Behavior:
- Reads only `week6.html` from Blob Storage
- Ignores `week6_narrative.json` (used only during generation)
- No changes needed to `weekly_job.py`

---

## Required Python Packages

**For generation scripts** (`scripts/requirements.txt`):
```
beautifulsoup4
openai  # Azure OpenAI client
azure-storage-blob
requests
```

**For Azure Function** (`azure-functions/MyBlogSubscribers/requirements.txt`):
```
azure-functions
azure-data-tables
azure-storage-blob
sib-api-v3-sdk
requests
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
