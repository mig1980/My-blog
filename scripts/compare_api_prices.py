#!/usr/bin/env python3
"""
API Price Comparison Tool

Fetches stock and cryptocurrency prices from all three API providers:
- Alpha Vantage (primary)
- Finnhub (fallback)
- Marketstack (fallback for stocks only)

Displays results in a formatted comparison table showing prices and discrepancies.

Usage:
    python compare_api_prices.py
    python compare_api_prices.py --symbols AAPL MSFT GOOGL
    python compare_api_prices.py --crypto-only
"""

import argparse
import os
import sys
import time
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIPriceComparator:
    """Compares stock and crypto prices across multiple API providers."""

    def __init__(self):
        """Initialize with API keys from environment variables."""
        self.alphavantage_key = os.getenv("ALPHAVANTAGE_API_KEY")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")
        self.marketstack_key = os.getenv("MARKETSTACK_API_KEY")

        # Validate at least one API key is present
        if not any([self.alphavantage_key, self.finnhub_key, self.marketstack_key]):
            raise ValueError(
                "At least one API key required. Set ALPHAVANTAGE_API_KEY, "
                "FINNHUB_API_KEY, or MARKETSTACK_API_KEY environment variable."
            )

        # Configure session with retries
        self.session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Rate limiting trackers
        self.last_alphavantage_call = 0
        self.last_finnhub_call = 0
        self.alphavantage_min_interval = 12  # 5 req/min = 12 seconds
        self.finnhub_min_interval = 12  # 5 req/min = 12 seconds
        self.marketstack_min_interval = 2  # Higher rate limit

    def _wait_for_rate_limit(self, last_call_time, min_interval, api_name):
        """Wait if necessary to respect rate limits."""
        elapsed = time.time() - last_call_time
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            print(f"  [Rate limit] Waiting {wait_time:.1f}s for {api_name}...")
            time.sleep(wait_time)

    # ==================== ALPHA VANTAGE ====================

    def fetch_alphavantage_stock(self, symbol):
        """Fetch stock price from Alpha Vantage."""
        if not self.alphavantage_key:
            return None

        self._wait_for_rate_limit(self.last_alphavantage_call, self.alphavantage_min_interval, "Alpha Vantage")

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.alphavantage_key,
        }

        try:
            self.last_alphavantage_call = time.time()
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "Global Quote" in data and data["Global Quote"]:
                quote = data["Global Quote"]
                date_str = quote.get("07. latest trading day", "")
                price = float(quote.get("05. price", 0))

                return {
                    "price": price,
                    "date": date_str[:10] if date_str else "N/A",
                    "api": "Alpha Vantage",
                    "error": None,
                }
            elif "Note" in data:
                return {
                    "price": None,
                    "date": None,
                    "api": "Alpha Vantage",
                    "error": "Rate limit exceeded",
                }
            else:
                return {
                    "price": None,
                    "date": None,
                    "api": "Alpha Vantage",
                    "error": "No data returned",
                }
        except Exception as e:
            return {
                "price": None,
                "date": None,
                "api": "Alpha Vantage",
                "error": str(e),
            }

    def fetch_alphavantage_crypto(self, symbol, to_currency="USD"):
        """Fetch crypto price from Alpha Vantage."""
        if not self.alphavantage_key:
            return None

        self._wait_for_rate_limit(self.last_alphavantage_call, self.alphavantage_min_interval, "Alpha Vantage")

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": symbol,
            "to_currency": to_currency,
            "apikey": self.alphavantage_key,
        }

        try:
            self.last_alphavantage_call = time.time()
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "Realtime Currency Exchange Rate" in data:
                rate = data["Realtime Currency Exchange Rate"]
                date_str = rate.get("6. Last Refreshed", "")
                price = float(rate.get("5. Exchange Rate", 0))

                return {
                    "price": price,
                    "date": date_str[:10] if date_str else "N/A",
                    "api": "Alpha Vantage (Crypto)",
                    "error": None,
                }
            else:
                return {
                    "price": None,
                    "date": None,
                    "api": "Alpha Vantage (Crypto)",
                    "error": "No data returned",
                }
        except Exception as e:
            return {
                "price": None,
                "date": None,
                "api": "Alpha Vantage (Crypto)",
                "error": str(e),
            }

    # ==================== FINNHUB ====================

    def fetch_finnhub_stock(self, symbol):
        """Fetch stock price from Finnhub."""
        if not self.finnhub_key:
            return None

        self._wait_for_rate_limit(self.last_finnhub_call, self.finnhub_min_interval, "Finnhub")

        url = "https://finnhub.io/api/v1/quote"
        params = {"symbol": symbol, "token": self.finnhub_key}

        try:
            self.last_finnhub_call = time.time()
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "c" in data and data.get("c") not in (None, 0):
                price = float(data.get("c", 0))
                timestamp = data.get("t")
                try:
                    date_str = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d") if timestamp else "N/A"
                except Exception:
                    date_str = "N/A"

                return {
                    "price": price,
                    "date": date_str,
                    "api": "Finnhub",
                    "error": None,
                }
            else:
                return {
                    "price": None,
                    "date": None,
                    "api": "Finnhub",
                    "error": "No usable quote returned",
                }
        except Exception as e:
            return {
                "price": None,
                "date": None,
                "api": "Finnhub",
                "error": str(e),
            }

    def fetch_finnhub_crypto(self, symbol):
        """Fetch crypto price from Finnhub (uses BINANCE:BTCUSDT for BTC)."""
        if not self.finnhub_key:
            return None

        self._wait_for_rate_limit(self.last_finnhub_call, self.finnhub_min_interval, "Finnhub")

        # Map generic symbols to Finnhub crypto symbols
        finnhub_symbol = "BINANCE:BTCUSDT" if symbol.upper() == "BTC" else symbol
        url = "https://finnhub.io/api/v1/quote"
        params = {"symbol": finnhub_symbol, "token": self.finnhub_key}

        try:
            self.last_finnhub_call = time.time()
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "c" in data and data.get("c") not in (None, 0):
                price = float(data.get("c", 0))
                timestamp = data.get("t")
                try:
                    date_str = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d") if timestamp else "N/A"
                except Exception:
                    date_str = "N/A"

                return {
                    "price": price,
                    "date": date_str,
                    "api": "Finnhub (Crypto)",
                    "error": None,
                }
            else:
                return {
                    "price": None,
                    "date": None,
                    "api": "Finnhub (Crypto)",
                    "error": "No usable quote returned",
                }
        except Exception as e:
            return {
                "price": None,
                "date": None,
                "api": "Finnhub (Crypto)",
                "error": str(e),
            }

    # ==================== MARKETSTACK ====================

    def fetch_marketstack_stock(self, symbol):
        """Fetch stock price from Marketstack."""
        if not self.marketstack_key:
            return None

        time.sleep(self.marketstack_min_interval)  # Simple rate limiting

        url = "http://api.marketstack.com/v1/eod/latest"
        params = {"access_key": self.marketstack_key, "symbols": symbol}

        try:
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "data" in data and data["data"] and len(data["data"]) > 0:
                quote = data["data"][0]
                price = float(quote.get("close", 0))
                date_str = quote.get("date", "")

                return {
                    "price": price,
                    "date": date_str[:10] if date_str else "N/A",
                    "api": "Marketstack",
                    "error": None,
                }
            else:
                return {
                    "price": None,
                    "date": None,
                    "api": "Marketstack",
                    "error": "No data returned",
                }
        except Exception as e:
            return {
                "price": None,
                "date": None,
                "api": "Marketstack",
                "error": str(e),
            }

    # ==================== COMPARISON LOGIC ====================

    def compare_stock_prices(self, symbol):
        """Fetch stock prices from all available APIs and return comparison."""
        print(f"\n{'='*80}")
        print(f"Fetching stock: {symbol}")
        print(f"{'='*80}")

        results = []

        # Alpha Vantage
        if self.alphavantage_key:
            print(f"  → Querying Alpha Vantage...")
            result = self.fetch_alphavantage_stock(symbol)
            if result:
                results.append(result)

        # Finnhub
        if self.finnhub_key:
            print(f"  → Querying Finnhub...")
            result = self.fetch_finnhub_stock(symbol)
            if result:
                results.append(result)

        # Marketstack
        if self.marketstack_key:
            print(f"  → Querying Marketstack...")
            result = self.fetch_marketstack_stock(symbol)
            if result:
                results.append(result)

        return {"symbol": symbol, "type": "stock", "results": results}

    def compare_crypto_prices(self, symbol):
        """Fetch crypto prices from all available APIs and return comparison."""
        print(f"\n{'='*80}")
        print(f"Fetching crypto: {symbol}")
        print(f"{'='*80}")

        results = []

        # Alpha Vantage
        if self.alphavantage_key:
            print(f"  → Querying Alpha Vantage (Crypto)...")
            result = self.fetch_alphavantage_crypto(symbol)
            if result:
                results.append(result)

        # Finnhub
        if self.finnhub_key:
            print(f"  → Querying Finnhub (Crypto)...")
            result = self.fetch_finnhub_crypto(symbol)
            if result:
                results.append(result)

        # Note: Marketstack doesn't support crypto

        return {"symbol": symbol, "type": "crypto", "results": results}

    # ==================== OUTPUT FORMATTING ====================

    def print_comparison_table(self, comparisons):
        """Print formatted comparison table for all symbols."""
        print(f"\n\n{'='*100}")
        print("PRICE COMPARISON SUMMARY")
        print(f"{'='*100}\n")

        for comp in comparisons:
            symbol = comp["symbol"]
            comp_type = comp["type"]
            results = comp["results"]

            print(f"\n{symbol} ({comp_type.upper()})")
            print("-" * 100)
            print(f"{'API':<25} {'Price':<15} {'Date':<15} {'Status':<45}")
            print("-" * 100)

            valid_prices = []
            for result in results:
                api_name = result["api"]
                price = result["price"]
                date = result["date"]
                error = result["error"]

                if price is not None:
                    price_str = f"${price:,.2f}"
                    valid_prices.append(price)
                    status = "✓ Success"
                else:
                    price_str = "N/A"
                    status = f"✗ {error}" if error else "✗ Failed"

                date_str = date if date else "N/A"
                print(f"{api_name:<25} {price_str:<15} {date_str:<15} {status:<45}")

            # Calculate discrepancies
            if len(valid_prices) > 1:
                min_price = min(valid_prices)
                max_price = max(valid_prices)
                diff = max_price - min_price
                diff_pct = (diff / min_price * 100) if min_price > 0 else 0

                print(f"\n{'Discrepancy Analysis:':<25}")
                print(f"  Min Price: ${min_price:,.2f}")
                print(f"  Max Price: ${max_price:,.2f}")
                print(f"  Difference: ${diff:,.2f} ({diff_pct:.2f}%)")

                if diff_pct > 1:
                    print(f"  ⚠ WARNING: Price discrepancy exceeds 1%")
                else:
                    print(f"  ✓ Prices are consistent")
            elif len(valid_prices) == 1:
                print(f"\n  ℹ Only one source returned valid data")
            else:
                print(f"\n  ✗ No valid prices retrieved from any source")

        print(f"\n{'='*100}\n")

    def print_summary(self, comparisons):
        """Print overall summary statistics."""
        total_symbols = len(comparisons)
        total_queries = sum(len(c["results"]) for c in comparisons)
        successful_queries = sum(1 for c in comparisons for r in c["results"] if r["price"] is not None)
        failed_queries = total_queries - successful_queries

        print("OVERALL SUMMARY")
        print("=" * 100)
        print(f"Symbols Queried: {total_symbols}")
        print(f"Total API Queries: {total_queries}")
        print(f"Successful: {successful_queries}")
        print(f"Failed: {failed_queries}")
        print(f"Success Rate: {(successful_queries/total_queries*100):.1f}%")
        print("=" * 100)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Compare stock and crypto prices across multiple API providers")
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
        help="Stock symbols to compare (default: AAPL MSFT GOOGL AMZN TSLA)",
    )
    parser.add_argument(
        "--crypto",
        nargs="+",
        default=["BTC"],
        help="Crypto symbols to compare (default: BTC)",
    )
    parser.add_argument(
        "--stocks-only",
        action="store_true",
        help="Only compare stock prices",
    )
    parser.add_argument(
        "--crypto-only",
        action="store_true",
        help="Only compare crypto prices",
    )

    args = parser.parse_args()

    # Initialize comparator
    try:
        comparator = APIPriceComparator()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Print API availability
    print("\nAPI KEY STATUS")
    print("=" * 100)
    print(f"Alpha Vantage: {'✓ Available' if comparator.alphavantage_key else '✗ Not configured'}")
    print(f"Finnhub:       {'✓ Available' if comparator.finnhub_key else '✗ Not configured'}")
    print(f"Marketstack:   {'✓ Available' if comparator.marketstack_key else '✗ Not configured'}")
    print("=" * 100)

    comparisons = []

    # Compare stocks
    if not args.crypto_only:
        for symbol in args.symbols:
            comparison = comparator.compare_stock_prices(symbol)
            comparisons.append(comparison)

    # Compare crypto
    if not args.stocks_only:
        for symbol in args.crypto:
            comparison = comparator.compare_crypto_prices(symbol)
            comparisons.append(comparison)

    # Print results
    comparator.print_comparison_table(comparisons)
    comparator.print_summary(comparisons)


if __name__ == "__main__":
    main()
