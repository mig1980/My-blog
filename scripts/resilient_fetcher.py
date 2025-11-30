"""
Resilient Fetcher - Ticker-level retry logic with fallback support.

This module provides robust API fetching with:
- Configurable retry attempts per ticker
- Exponential backoff between retries
- Optional fallback to secondary data source
- Detailed failure tracking for reporting

Usage:
    fetcher = ResilientFetcher(max_retries=3, backoff_base=2.0)

    for ticker in tickers:
        quote = fetcher.fetch_with_retry(
            ticker,
            primary_fetcher=fetch_finnhub,
            fallback_fetcher=fetch_marketstack
        )
        if quote:
            price_data[ticker] = quote

    if fetcher.has_failures():
        logging.warning(f"Failed tickers: {fetcher.get_failures()}")
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

from config import RETRY_CONFIG

# Type alias for fetcher functions
FetcherFunc = Callable[[str], Optional[Dict[str, Any]]]


class ResilientFetcher:
    """
    Handles ticker-level retry logic with optional fallback to secondary sources.

    Features:
    - Configurable retry attempts with exponential backoff
    - Fallback to secondary data source when primary fails
    - Tracks all failures for reporting
    - Thread-safe failure tracking
    """

    def __init__(
        self,
        max_retries: Optional[int] = None,
        backoff_base: Optional[float] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize the resilient fetcher.

        Args:
            max_retries: Maximum retry attempts per ticker (default from config)
            backoff_base: Base for exponential backoff calculation (default from config)
            timeout: Request timeout in seconds (default from config)
        """
        self.max_retries = max_retries or RETRY_CONFIG["max_retries"]
        self.backoff_base = backoff_base or RETRY_CONFIG["backoff_base"]
        self.timeout = timeout or RETRY_CONFIG["timeout"]

        # Track failures: ticker -> error message
        self.failed_tickers: Dict[str, str] = {}

        # Track statistics
        self.stats = {
            "total_attempts": 0,
            "primary_successes": 0,
            "fallback_successes": 0,
            "total_failures": 0,
            "retries_used": 0,
        }

    def fetch_with_retry(
        self,
        ticker: str,
        primary_fetcher: FetcherFunc,
        fallback_fetcher: Optional[FetcherFunc] = None,
        rate_limit_delay: float = 0.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data for a ticker with retry logic and optional fallback.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "MSFT")
            primary_fetcher: Primary data source function
            fallback_fetcher: Optional fallback function if primary fails
            rate_limit_delay: Delay between retry attempts (respects API rate limits)

        Returns:
            Quote data dict if successful, None if all attempts fail
        """
        self.stats["total_attempts"] += 1

        # Try primary source with retries
        for attempt in range(self.max_retries):
            try:
                result = primary_fetcher(ticker)
                if result:
                    self.stats["primary_successes"] += 1
                    if attempt > 0:
                        self.stats["retries_used"] += attempt
                        logging.info(f"✓ {ticker}: Succeeded on attempt {attempt + 1}")
                    return result

                # Result was None/empty - treat as soft failure
                logging.debug(f"⚠️ {ticker}: Primary returned empty (attempt {attempt + 1})")

            except Exception as e:
                wait_time = self._calculate_backoff(attempt, rate_limit_delay)
                logging.warning(f"⚠️ {ticker} attempt {attempt + 1}/{self.max_retries} failed: {e}")

                if attempt < self.max_retries - 1:
                    logging.info(f"   Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)

        # Primary exhausted - try fallback if available
        if fallback_fetcher:
            logging.info(f"⟳ {ticker}: Trying fallback source...")
            try:
                result = fallback_fetcher(ticker)
                if result:
                    self.stats["fallback_successes"] += 1
                    logging.info(f"✓ {ticker}: Fallback succeeded")
                    return result
            except Exception as e:
                logging.warning(f"⚠️ {ticker} fallback failed: {e}")

        # All sources exhausted
        self._record_failure(ticker, "All sources exhausted after retries")
        return None

    def fetch_batch(
        self,
        tickers: List[str],
        primary_fetcher: FetcherFunc,
        fallback_fetcher: Optional[FetcherFunc] = None,
        rate_limit_delay: float = 0.0,
        continue_on_failure: bool = True,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch data for multiple tickers with retry logic.

        Args:
            tickers: List of ticker symbols
            primary_fetcher: Primary data source function
            fallback_fetcher: Optional fallback function
            rate_limit_delay: Delay between tickers (respects API rate limits)
            continue_on_failure: If True, continue processing after failures

        Returns:
            Dict mapping ticker -> quote data (only successful fetches)
        """
        results: Dict[str, Dict[str, Any]] = {}

        for i, ticker in enumerate(tickers):
            # Rate limiting between tickers (not between retries)
            if i > 0 and rate_limit_delay > 0:
                time.sleep(rate_limit_delay)

            quote = self.fetch_with_retry(
                ticker,
                primary_fetcher,
                fallback_fetcher,
                rate_limit_delay=rate_limit_delay,
            )

            if quote:
                results[ticker] = quote
            elif not continue_on_failure:
                logging.error(f"❌ Aborting batch due to failure on {ticker}")
                break

        return results

    def _calculate_backoff(self, attempt: int, base_delay: float) -> float:
        """
        Calculate exponential backoff delay.

        Formula: base_delay + (backoff_base ^ attempt)
        Example with backoff_base=2.0:
          - Attempt 0: base_delay + 1.0s
          - Attempt 1: base_delay + 2.0s
          - Attempt 2: base_delay + 4.0s

        Args:
            attempt: Current attempt number (0-indexed)
            base_delay: Minimum delay (e.g., API rate limit)

        Returns:
            Total delay in seconds
        """
        exponential_delay = self.backoff_base**attempt
        return base_delay + exponential_delay

    def _record_failure(self, ticker: str, error_message: str) -> None:
        """Record a ticker failure for reporting."""
        self.failed_tickers[ticker] = error_message
        self.stats["total_failures"] += 1
        logging.error(f"❌ {ticker}: {error_message}")

    def get_failures(self) -> Dict[str, str]:
        """Get all failed tickers and their error messages."""
        return self.failed_tickers.copy()

    def has_failures(self) -> bool:
        """Check if any tickers failed."""
        return len(self.failed_tickers) > 0

    def get_failure_count(self) -> int:
        """Get count of failed tickers."""
        return len(self.failed_tickers)

    def get_stats(self) -> Dict[str, int]:
        """Get fetch statistics."""
        return self.stats.copy()

    def get_success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.stats["total_attempts"] == 0:
            return 100.0
        successes = self.stats["primary_successes"] + self.stats["fallback_successes"]
        return (successes / self.stats["total_attempts"]) * 100

    def reset(self) -> None:
        """Reset all tracking state for reuse."""
        self.failed_tickers.clear()
        self.stats = {
            "total_attempts": 0,
            "primary_successes": 0,
            "fallback_successes": 0,
            "total_failures": 0,
            "retries_used": 0,
        }

    def log_summary(self) -> None:
        """Log a summary of fetch results."""
        stats = self.stats
        success_rate = self.get_success_rate()

        logging.info("=" * 50)
        logging.info("📊 Fetch Summary:")
        logging.info(f"   Total attempts: {stats['total_attempts']}")
        logging.info(f"   Primary successes: {stats['primary_successes']}")
        logging.info(f"   Fallback successes: {stats['fallback_successes']}")
        logging.info(f"   Failures: {stats['total_failures']}")
        logging.info(f"   Retries used: {stats['retries_used']}")
        logging.info(f"   Success rate: {success_rate:.1f}%")

        if self.has_failures():
            logging.warning(f"   Failed tickers: {list(self.failed_tickers.keys())}")
        logging.info("=" * 50)
