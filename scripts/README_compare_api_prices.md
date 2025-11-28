# API Price Comparison Tool

A manual script to fetch and compare stock and cryptocurrency prices from all three API providers used in the Quantum Investor Digest portfolio automation.

## Features

- **Multi-Provider Support**: Fetches prices from Finnhub and Marketstack
- **Rate Limiting**: Respects API rate limits (50 req/min for Finnhub, 100 req/month for Marketstack)
- **Discrepancy Detection**: Calculates price differences and highlights significant variances
- **Formatted Output**: Clean table display with success/error status for each API
- **Flexible Querying**: Compare stocks, crypto, or both

## API Providers

| Provider | Stocks | Crypto | Rate Limit | Notes |
|----------|--------|--------|------------|-------|
| **Finnhub** | ✓ | ✓ | 50 req/min | Primary source (stocks, Bitcoin) |
| **Marketstack** | ✓ | ✗ | 100 req/month | Secondary fallback (stocks), primary (S&P 500) |

## Prerequisites

### Required Python Packages
```bash
pip install requests
```

### API Keys (Environment Variables)
Finnhub API key is recommended (primary source). Marketstack is optional (fallback/S&P 500).

```bash
# Windows PowerShell
$env:FINNHUB_API_KEY="your_key_here"
$env:MARKETSTACK_API_KEY="your_key_here"  # Optional

# Linux/Mac
export FINNHUB_API_KEY="your_key_here"
export MARKETSTACK_API_KEY="your_key_here"  # Optional
```

## Usage

### Basic Usage (Default Stocks + BTC)
```bash
python compare_api_prices.py
```

Default behavior:
- Stocks: AAPL, MSFT, GOOGL, AMZN, TSLA
- Crypto: BTC

### Custom Symbols
```bash
# Compare specific stocks
python compare_api_prices.py --symbols NVDA AMD INTC

# Compare multiple cryptocurrencies
python compare_api_prices.py --crypto BTC ETH

# Compare custom stocks and crypto
python compare_api_prices.py --symbols AAPL GOOGL --crypto BTC
```

### Filtering
```bash
# Only compare stocks (skip crypto)
python compare_api_prices.py --stocks-only

# Only compare crypto (skip stocks)
python compare_api_prices.py --crypto-only
```

## Sample Output

```
API KEY STATUS
====================================================================================================
Finnhub:       ✓ Available (Primary)
Marketstack:   ✓ Available (Secondary)
====================================================================================================

================================================================================
Fetching stock: AAPL
================================================================================
  → Querying Finnhub...
  [Rate limit] Waiting 1.3s for Finnhub...
  → Querying Marketstack...


====================================================================================================
PRICE COMPARISON SUMMARY
====================================================================================================

AAPL (STOCK)
----------------------------------------------------------------------------------------------------
API                       Price           Date            Status                                       
----------------------------------------------------------------------------------------------------
Finnhub                   $178.42         2025-11-26      ✓ Success (Primary)                            
Marketstack               $178.45         2025-11-25      ✓ Success (Fallback)                                    

Discrepancy Analysis:
  Min Price: $178.42
  Max Price: $178.45
  Difference: $0.03 (0.02%)
  ✓ Prices are consistent

BTC (CRYPTO)
----------------------------------------------------------------------------------------------------
API                       Price           Date            Status                                       
----------------------------------------------------------------------------------------------------
Finnhub (Crypto)          $94,230.12      2025-11-26      ✓ Success (BINANCE:BTCUSDT)                                    

Discrepancy Analysis:
  Min Price: $94,230.12
  Max Price: $94,234.56
  Difference: $4.44 (0.00%)
  ✓ Prices are consistent

====================================================================================================

OVERALL SUMMARY
====================================================================================================
Symbols Queried: 2
Total API Queries: 5
Successful: 5
Failed: 0
Success Rate: 100.0%
====================================================================================================
```

## Understanding the Output

### Price Table Columns
- **API**: Provider name and type (Stock/Crypto)
- **Price**: Latest closing price (N/A if unavailable)
- **Date**: Price date timestamp
- **Status**: 
  - `✓ Success`: Price retrieved successfully
  - `✗ Failed`: Failed to retrieve (shows error reason)

### Discrepancy Analysis
- **Min/Max Price**: Range across all successful queries
- **Difference**: Absolute and percentage difference
- **Warning**: Shows `⚠ WARNING` if difference exceeds 1%

### Status Indicators
- `✓` - Success
- `✗` - Error/failure
- `⚠` - Warning (high discrepancy)
- `ℹ` - Information

## Common Issues

### Rate Limit Errors
If you see "Rate limit exceeded" errors:
- Script automatically waits 12 seconds between calls
- For many symbols, total runtime increases (12s per symbol per API)
- Consider running with `--stocks-only` or `--crypto-only`

### API Key Issues
```
ERROR: At least one API key required...
```
Solution: Set at least one environment variable (see Prerequisites)

### Date Mismatches
Different APIs may return different dates due to:
- Time zone differences
- Data refresh schedules
- Market closures

This is normal and expected.

## Use Cases

### 1. Validate Portfolio Data
Before weekly automation runs, verify all APIs are returning consistent prices:
```bash
python compare_api_prices.py --symbols AAPL MSFT NVDA GOOGL AMZN TSLA META --crypto BTC
```

### 2. Diagnose API Issues
If automation shows unexpected values, compare APIs manually:
```bash
python compare_api_prices.py --symbols PROBLEMATIC_TICKER
```

### 3. Test New Stocks
Before adding a new stock to the portfolio, verify data availability:
```bash
python compare_api_prices.py --symbols NEW_TICKER
```

### 4. Monitor API Health
Run daily to track which APIs are reliable:
```bash
python compare_api_prices.py > api_health_$(date +%Y%m%d).log
```

## Rate Limiting Details

### Finnhub (Primary)
- Free tier: 50 requests/minute, 60 requests/day
- Script enforces: 1.3 seconds between calls
- Used for: All stocks, Bitcoin (BINANCE:BTCUSDT)

### Marketstack (Secondary)
- Free tier: 100 requests/month
- Script enforces: 2 seconds between calls
- Used for: S&P 500 (primary), stock prices (fallback)

**Tip**: Finnhub's 50 calls/min limit allows faster data fetching than previous Alpha Vantage implementation (5 calls/min).

## Integration with Portfolio Automation

This script uses the same API fetching logic as `portfolio_automation.py`:
- Same rate limiting strategy
- Same fallback hierarchy:
  - **Stocks**: Finnhub (primary) → Marketstack (secondary)
  - **S&P 500**: Marketstack (primary) → Finnhub (secondary)
  - **Bitcoin**: Finnhub only (BINANCE:BTCUSDT)
- Same error handling patterns

Results from this script can help diagnose issues in the main automation pipeline.

## Troubleshooting

### No Data Returned
Check:
1. API key is valid and active
2. Symbol is correct (case-sensitive for some APIs)
3. Market is open (historical data may be delayed)
4. API service status (check provider websites)

### High Discrepancies
If price differences exceed 1%:
- Check if symbols refer to different exchanges
- Verify API data freshness (time zones, delays)
- Consider which API is most reliable for your use case

### Script Hangs
- Rate limiting may cause delays (up to 12s per call)
- Use Ctrl+C to interrupt
- Check network connectivity

## Future Enhancements

Potential improvements:
- [ ] Add CSV export option
- [ ] Historical price comparison
- [ ] JSON output format
- [ ] Batch processing from file
- [ ] Async API calls (respecting rate limits)
- [ ] Caching to reduce redundant calls

## Related Files

- `portfolio_automation.py` - Main automation script
- `requirements.txt` - Python dependencies

## License

Part of the Quantum Investor Digest project.

---

**Last Updated**: November 26, 2025  
**Maintained By**: Michael Gavrilov
