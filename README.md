# Quantum Investor Digest - System Architecture

## Overview

The Quantum Investor Digest is a blog platform featuring an AI-managed stock portfolio with automated weekly content generation, real-time data visualization, and email newsletters.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          QUANTUM INVESTOR DIGEST                             │
│                        AI-Powered Portfolio Blog                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  index.html  │  │  about.html  │  │   docs.html  │  │  tools.html  │   │
│  │  (Homepage)  │  │ (About Page) │  │ (Tech Docs)  │  │ (Utilities)  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                  │                  │                  │           │
│         └──────────────────┴──────────────────┴──────────────────┘           │
│                                    │                                         │
│                    ┌───────────────▼────────────────┐                       │
│                    │       templates/               │                       │
│                    │  ┌──────────┐  ┌──────────┐  │                       │
│                    │  │ header   │  │ footer   │  │                       │
│                    │  │.html     │  │.html     │  │                       │
│                    │  └──────────┘  └──────────┘  │                       │
│                    │  ┌──────────────────────┐    │                       │
│                    │  │ subscribe-form.html  │    │                       │
│                    │  └──────────────────────┘    │                       │
│                    └────────────────────────────────┘                       │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                         Posts/ Directory                            │    │
│  │  ┌──────────────────────────────────────────────────────────┐     │    │
│  │  │ GenAi-Managed-Stocks-Portfolio-Week-{N}.html             │     │    │
│  │  │ - Weekly performance narrative                            │     │    │
│  │  │ - Embedded performance table                              │     │    │
│  │  │ - Embedded performance chart                              │     │    │
│  │  │ - TLDR metrics strip (dynamic)                            │     │    │
│  │  └──────────────────────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                       Static Assets                                 │    │
│  │  Media/           styles.css          js/                          │    │
│  │  - Hero images    - 2061 lines       - template-loader.js          │    │
│  │  - Logos          - Responsive        - mobile-menu.js             │    │
│  │  - OG images      - Dark theme        - tldr.js                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           AUTOMATION LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              portfolio_automation.py (2984 lines)                    │   │
│  │                  Main Orchestration Script                           │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                       │   │
│  │  Step 0: API Status Check                                            │   │
│  │  ┌──────────────────────────────────────────────────────────┐      │   │
│  │  │ • Verify Finnhub, Marketstack, Azure OpenAI connectivity │      │   │
│  │  │ • Test authentication and rate limits                     │      │   │
│  │  │ • Block execution if no working APIs                      │      │   │
│  │  └──────────────────────────────────────────────────────────┘      │   │
│  │                           ↓                                          │   │
│  │  Phase 1: Data Collection                                           │   │
│  │  ┌──────────────────────────────────────────────────────────┐      │   │
│  │  │ • Fetch stock prices (Finnhub primary, 50 calls/min)     │      │   │
│  │  │ • Fallback: Marketstack (100 calls/month)                 │      │   │
│  │  │ • Rate limiting: Finnhub 1.3s, Marketstack 2s            │      │   │
│  │  │ • Retry logic with exponential backoff                    │      │   │
│  │  └──────────────────────────────────────────────────────────┘      │   │
│  │                           ↓                                          │   │
│  │  Phase 2: Calculations                                              │   │
│  │  ┌──────────────────────────────────────────────────────────┐      │   │
│  │  │ • Portfolio value & returns                               │      │   │
│  │  │ • Individual stock performance                            │      │   │
│  │  │ • Benchmark comparisons (S&P 500, Bitcoin)                │      │   │
│  │  │ • Normalized chart data                                   │      │   │
│  │  │ • Save to master.json                                     │      │   │
│  │  └──────────────────────────────────────────────────────────┘      │   │
│  │                           ↓                                          │   │
│  │  Phase 3: Visual Generation (Python)                                │   │
│  │  ┌──────────────────────────────────────────────────────────┐      │   │
│  │  │ • Generate performance table HTML                         │      │   │
│  │  │ • Generate performance chart SVG                          │      │   │
│  │  │ • Deterministic output (no AI)                            │      │   │
│  │  └──────────────────────────────────────────────────────────┘      │   │
│  │                           ↓                                          │   │
│  │  Phase 4: AI Narrative (Prompt A → B → D)                          │   │
│  │  ┌──────────────────────────────────────────────────────────┐      │   │
│  │  │ Prompt A: Validator                                       │      │   │
│  │  │ • Validates calculations                                  │      │   │
│  │  │ • Non-fatal (warnings only)                               │      │   │
│  │  │ • Saves validation_report.txt                             │      │   │
│  │  ├───────────────────────────────────────────────────────────┤      │   │
│  │  │ Prompt B: Narrative Writer                                │      │   │
│  │  │ • Generates prose content (narrative.html)                │      │   │
│  │  │ • Generates SEO metadata (seo.json)                       │      │   │
│  │  │ • Uses GPT-5.1 (Azure OpenAI)                             │      │   │
│  │  ├───────────────────────────────────────────────────────────┤      │   │
│  │  │ Prompt D: Final Assembler                                 │      │   │
│  │  │ • Combines narrative + visuals + metadata                 │      │   │
│  │  │ • Generates complete HTML page                            │      │   │
│  │  │ • Applies CSP policy with nonce                           │      │   │
│  │  │ • Adds JSON-LD structured data                            │      │   │
│  │  └──────────────────────────────────────────────────────────┘      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              Newsletter Generation (2-Stage)                         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  generate_newsletter_narrative.py                                   │   │
│  │  • Stage 1: Generate narrative JSON with AI                         │   │
│  │  • Extracts key insights, performance highlights                    │   │
│  │  • Optimized for email format                                       │   │
│  │                           ↓                                          │   │
│  │  generate_newsletter_html.py                                        │   │
│  │  • Stage 2: Transform JSON → HTML email                             │   │
│  │  • Table-based layout (email-safe)                                  │   │
│  │  • 95%+ email client compatibility                                  │   │
│  │  • ~50KB target size                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                             DATA LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                    master data/ (Primary)                         │      │
│  │  ┌────────────────────────────────────────────────────────┐     │      │
│  │  │ master.json (Single Source of Truth)                   │     │      │
│  │  │ {                                                       │     │      │
│  │  │   "meta": { inception_date, current_date, ... },      │     │      │
│  │  │   "stocks": [ {ticker, prices, shares, ...} ],        │     │      │
│  │  │   "portfolio_history": [ {date, value, pct, ...} ],   │     │      │
│  │  │   "benchmarks": {                                      │     │      │
│  │  │     "sp500": { history: [...] },                      │     │      │
│  │  │     "bitcoin": { history: [...] }                     │     │      │
│  │  │   },                                                    │     │      │
│  │  │   "normalized_chart": [ ... ]                          │     │      │
│  │  │ }                                                       │     │      │
│  │  └────────────────────────────────────────────────────────┘     │      │
│  │                                                                   │      │
│  │  archive/                                                         │      │
│  │  └── master-YYYYMMDD.json (Timestamped backups)                  │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                    Data/W{N}/ (Legacy Snapshots)                  │      │
│  │  - master.json (week copy)                                        │      │
│  │  - performance_table.html                                         │      │
│  │  - performance_chart.svg                                          │      │
│  │  - validation_report.txt                                          │      │
│  │  - visuals.json                                                   │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                    newsletters/ Directory                         │      │
│  │  - week{N}_narrative.json (AI-generated content)                  │      │
│  │  - week{N}_newsletter.html (Final email)                          │      │
│  └──────────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Finnhub    │  │ Marketstack  │  │ Azure OpenAI │   │
│  │  (Primary)   │  │ (Secondary)  │  │  GPT-5.1     │   │
│  │              │  │              │  │              │   │
│  │ Stock prices │  │ S&P 500 data │  │ Narrative    │   │
│  │ Crypto data  │  │ Stock prices │  │ generation   │   │
│  │              │  │ (fallback)   │  │              │   │
│  │ 50 req/min   │  │ 100 req/mo   │  │ API calls    │   │
│  │ 1.3s delay   │  │ 2s delay     │  │ w/ retry     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐                                         │
│  │  Azure Blob  │  │   GitHub     │                                         │
│  │   Storage    │  │   Actions    │                                         │
│  │              │  │              │                                         │
│  │ Newsletter   │  │ Weekly       │                                         │
│  │ upload       │  │ automation   │                                         │
│  │              │  │ workflow     │                                         │
│  └──────────────┘  └──────────────┘                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLIENT-SIDE FEATURES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │ template-loader.js                                             │         │
│  │ • Loads header/footer templates dynamically                    │         │
│  │ • Path-aware (adjusts for /Posts/ subdirectory)                │         │
│  │ • Applies theme from localStorage                              │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │ mobile-menu.js                                                 │         │
│  │ • Hamburger menu for mobile devices                            │         │
│  │ • Slide-in panel with backdrop                                 │         │
│  │ • Escape key / click-outside to close                          │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │ tldr.js                                                        │         │
│  │ • Fetches week data from master.json                           │         │
│  │ • Populates TLDR strip (Week %, Total %, Alpha)               │         │
│  │ • Auto-detects week number from URL                            │         │
│  │ • Fallback handling for missing data                           │         │
│  └────────────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Weekly Automation Pipeline

```
1. TRIGGER (GitHub Actions - Every Thursday 6:00 PM EST)
   │
   ├─→ 2. FETCH DATA
   │   ├─ Finnhub API → Stock prices (primary)
   │   ├─ Marketstack API → S&P 500 (primary), stocks (fallback)
   │   └─ Finnhub Crypto → Bitcoin (BINANCE:BTCUSDT)
   │
   ├─→ 3. CALCULATE METRICS
   │   ├─ Portfolio value
   │   ├─ Individual stock performance
   │   ├─ Benchmark comparisons
   │   └─ Normalized chart data
   │
   ├─→ 4. SAVE DATA
   │   ├─ master data/master.json (primary)
   │   ├─ master data/archive/master-DATE.json (backup)
   │   └─ Data/W{N}/master.json (legacy snapshot)
   │
   ├─→ 5. GENERATE VISUALS (Python)
   │   ├─ performance_table.html
   │   └─ performance_chart.svg
   │
   ├─→ 6. AI NARRATIVE GENERATION
   │   ├─ Prompt A: Validate calculations
   │   ├─ Prompt B: Generate narrative + SEO
   │   └─ Prompt D: Assemble final HTML
   │
   ├─→ 7. PUBLISH
   │   ├─ Save to Posts/GenAi-Managed-Stocks-Portfolio-Week-{N}.html
   │   └─ Update index.html with new post
   │
   └─→ 8. NEWSLETTER (Optional)
       ├─ Stage 1: Generate narrative JSON
       ├─ Stage 2: Generate HTML email
       └─ Upload to Azure Blob Storage
```

### Client-Side Data Access

```
Browser Request
   │
   ├─→ Page Load (GenAi-Managed-Stocks-Portfolio-Week-{N}.html)
   │   ├─ Static HTML with embedded visuals
   │   └─ Initial content visible immediately
   │
   └─→ Dynamic TLDR Strip (tldr.js)
       ├─ Detects week number from URL
       ├─ Fetches master data/master.json
       ├─ Extracts metrics for specific week
       └─ Populates TLDR strip elements
```

## Technology Stack

### Frontend
- **HTML5**: Semantic markup, accessibility features
- **CSS3**: Custom properties, responsive design, dark theme
- **Vanilla JavaScript**: No frameworks, minimal dependencies
- **SVG**: Performance charts, logos

### Backend/Automation
- **Python 3.x**: Main automation language
  - `requests`: HTTP client
  - `openai`: Azure OpenAI SDK
  - `json`, `pathlib`: Data handling
- **Azure OpenAI**: GPT-5.1 for narrative generation
- **GitHub Actions**: CI/CD automation

### Data APIs
- **Finnhub**: Primary stock data source (50 calls/min, free tier)
- **Marketstack**: Secondary fallback for stocks, primary for S&P 500 (100 calls/month, free tier)
- **Azure Blob Storage**: Newsletter distribution

### Security
- **CSP (Content Security Policy)**: Strict with nonce-based scripts
- **HTTPS**: Enforced across all pages
- **CORS**: Restricted to same-origin
- **Input Validation**: API data sanitization

## File Structure

```
quantuminvestor/
├── index.html                 # Homepage
├── about.html                 # About page
├── docs.html                  # Technical documentation
├── tools.html                 # Utility tools page
├── Disclosures.html           # Legal disclosures
├── styles.css                 # Main stylesheet (2061 lines)
├── ARCHITECTURE.md            # This file
│
├── Media/                     # Images and assets
│   ├── Hero.webp             # Homepage hero image
│   ├── W{N}.webp             # Weekly hero images
│   ├── Full-Logo.webp        # Site logo
│   └── favicon.ico           # Site icon
│
├── Posts/                     # Blog posts
│   ├── posts.html            # Blog index
│   ├── GenAi-Managed-Stocks-Portfolio-Week-{N}.html
│   └── portfolio-heatmap.html
│
├── templates/                 # Reusable components
│   ├── header.html           # Site header
│   ├── footer.html           # Site footer
│   └── subscribe-form.html   # Email subscription
│
├── js/                        # JavaScript modules
│   ├── template-loader.js    # Dynamic template loading
│   ├── mobile-menu.js        # Mobile navigation
│   └── tldr.js               # TLDR strip population
│
├── scripts/                   # Python automation
│   ├── portfolio_automation.py           # Main orchestrator (2984 lines)
│   ├── generate_newsletter_narrative.py  # Newsletter Stage 1
│   ├── generate_newsletter_html.py       # Newsletter Stage 2
│   ├── upload_newsletter_to_blob.py     # Azure upload
│   └── requirements.txt                  # Python dependencies
│
├── master data/              # Primary data store
│   ├── master.json          # Single source of truth
│   └── archive/             # Timestamped backups
│       └── master-YYYYMMDD.json
│
├── Data/                     # Legacy weekly snapshots
│   └── W{N}/
│       ├── master.json
│       ├── performance_table.html
│       ├── performance_chart.svg
│       ├── validation_report.txt
│       └── visuals.json
│
├── newsletters/              # Email content
│   ├── week{N}_narrative.json
│   └── week{N}_newsletter.html
│
├── Prompt/                   # AI prompt templates
│   ├── Prompt-A-v5.4A.md    # Validation prompt
│   ├── Prompt-B-v5.4B.md    # Narrative prompt
│   └── Prompt-D-v5.4D.md    # Assembly prompt
│
└── .github/
    └── workflows/
        └── weekly-portfolio.yml  # Automation workflow
```

## Key Design Decisions

### 1. **Single Source of Truth**
- `master data/master.json` consolidates all portfolio data
- Weekly snapshots in `Data/W{N}/` for backward compatibility
- Atomic writes with `.tmp` suffix for data integrity

### 2. **Separation of Concerns**
- **Calculations**: Pure Python (deterministic)
- **Visuals**: Python-generated HTML/SVG (no AI)
- **Narrative**: AI-generated prose only

### 3. **Error Handling Strategy**
- **FATAL**: Missing data, API failures → Abort pipeline
- **NON-FATAL**: Validation warnings → Continue with logs
- **TRANSIENT**: Network errors → Retry with exponential backoff

### 4. **Performance Optimizations**
- Lazy loading for images below the fold
- Template caching in browser
- Minified production assets
- WebP image format

### 5. **Accessibility First**
- ARIA labels on all interactive elements
- Semantic HTML structure
- Keyboard navigation support
- Skip-to-content links

## Security Model

### Content Security Policy (CSP)
```
default-src 'self';
script-src 'self' 'nonce-qi123' https://cdn.jsdelivr.net;
style-src 'self' 'unsafe-inline';
img-src 'self' data: https: http:;
connect-src 'self' https://www.google-analytics.com;
```

### Nonce-Based Scripts
- Unique nonce (`qi123`) for inline scripts
- Prevents XSS attacks
- CSP-compliant external scripts

### API Key Management
- Environment variables for secrets
- GitHub Actions secrets for CI/CD
- No keys in source code

## Future Enhancements

### Short Term
1. Split `portfolio_automation.py` into modules
2. Add unit tests (pytest)
3. CSS optimization (minification, critical CSS)

### Medium Term
4. TypeScript migration for JavaScript
5. Component library for reusable elements
6. Performance monitoring (Lighthouse CI)

### Long Term
7. Backend API for real-time data
8. User accounts and personalization
9. Interactive portfolio builder

## Monitoring & Observability

### Current
- Python logging throughout automation
- GitHub Actions workflow logs
- Error reporting in validation reports

### Planned
- Sentry for error tracking
- Google Analytics for user behavior
- Performance budgets with alerts

## Deployment

### Hosting
- **GitHub Pages**: Static site hosting
- **Azure Blob Storage**: Newsletter hosting
- **CDN**: CloudFlare (planned)

### CI/CD Pipeline
```
Git Push → GitHub Actions → Tests → Build → Deploy
                          ↓
                    Weekly Automation
                          ↓
                    Generate Content
                          ↓
                    Commit & Push
```

## Related Documentation

- [Code Audit Report](../code-audit-report.md) (if exists)
- [API Documentation](../API.md) (planned)
- [Contributing Guidelines](../CONTRIBUTING.md) (planned)
- [Deployment Guide](../DEPLOYMENT.md) (planned)

---

**Last Updated**: November 26, 2025  
**Version**: 1.0  
**Maintained By**: Michael Gavrilov
