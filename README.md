# GenAI-Managed Stock Portfolio

Automated portfolio management using Azure OpenAI for market analysis and weekly performance reports.

## Quick Start

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Set required environment variables
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_DEPLOYMENT="your-deployment"
export FINNHUB_API_KEY="your-finnhub-key"           # Required - primary stock/crypto data
export MARKETSTACK_API_KEY="your-marketstack-key"   # Required - S&P 500 & fallback

# Run weekly automation
python scripts/portfolio_automation.py --week 8 --data-source ai
```

## Features

- **Automated Analysis**: Weekly price fetching, performance calculations, benchmark comparisons
- **AI Research**: GPT-4 screens candidates using web search and fundamental analysis
- **Data Enrichment**: Yahoo Finance fundamentals (free, unlimited)
- **HTML Reports**: Auto-generated blog posts and newsletters
- **Smart Caching**: Skips regeneration if data already exists (use `--force-research` to override)

## API Requirements

| API | Purpose | Cost | Notes |
|-----|---------|------|-------|
| **Azure OpenAI** | AI analysis | Pay-per-token | Required |
| **Finnhub** | Stock & crypto prices | Free (60/min) | Primary source |
| **Marketstack** | S&P 500 benchmark | Free (100/month) | Required fallback |
| **Yahoo Finance** | Fundamentals | Free (unlimited) | Auto-integrated |

## Repository Structure

```
scripts/              # Python automation (10 active scripts)
  portfolio_automation.py   # Main orchestrator (4,300 lines)
  config.py                 # Centralized configuration
  resilient_fetcher.py      # Retry logic with fallback
  yfinance_enrichment.py    # Yahoo Finance integration
  automated_rebalance.py    # Execute AI trade decisions
Data/W{n}/            # Weekly data snapshots
master data/          # Single source of truth (master.json)
Posts/                # Generated HTML blog posts
```

## Data Flow

```
1. Fetch Prices     → Finnhub (primary) / Marketstack (fallback)
2. Market Research  → AI + web search → research_candidates.json
3. Enrichment       → Yahoo Finance fundamentals (automatic)
4. AI Analysis      → Prompt A (validate) → Prompt B (decide) → Prompt D (assemble)
5. Output           → Blog post HTML + master.json update
```

## Portfolio Constraints

- **Positions**: 6-10 holdings
- **Max Position**: 20% of portfolio
- **Min Value**: $500 per position
- **Rebalancing**: Only when AI signals REBALANCE

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: yfinance` | `pip install yfinance` |
| `AZURE_OPENAI_DEPLOYMENT not set` | Set environment variable |
| `Marketstack limit exceeded` | Wait for monthly reset (100 calls/month) |

## Documentation

- [scripts/README.md](scripts/README.md) - Script details
- [README/yfinance-guide.md](README/yfinance-guide.md) - Yahoo Finance setup

## License

MIT License - See [LICENSE](LICENSE)

---
**Blog**: https://quantuminvestor.me | **GitHub**: https://github.com/mig1980/quantuminvestor
