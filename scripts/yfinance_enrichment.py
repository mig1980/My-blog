"""Yahoo Finance Enrichment Script
Enriches research_candidates.json with fundamental data from Yahoo Finance

FREE and UNLIMITED - No API key required!
Uses yfinance library (unofficial Yahoo Finance API wrapper)

Data Available:
- Company info: sector, industry, description, employees, website
- Valuation: P/E ratio, P/B ratio, PEG ratio, market cap, enterprise value
- Profitability: profit margins, gross margins, ROE, ROA, operating margins
- Growth: revenue growth, earnings growth, quarterly earnings growth
- Financial health: debt/equity, current ratio, quick ratio, cash, debt, free cash flow
- Analyst sentiment: recommendation, price target, number of analysts
- Ownership: institutional ownership %, short interest %

Usage:
    pip install yfinance
    python yfinance_enrichment.py --week 7

Features:
    - Completely free, no rate limits
    - Complements Marketstack (price/volume/momentum)
    - Non-blocking: Always returns success
    - Detailed logging to Data/W{week}/yfinance_enrichment.log
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

try:
    import yfinance as yf
except ImportError:
    print("❌ ERROR: yfinance not installed")
    print("Run: pip install yfinance")
    sys.exit(1)

# Import centralized configuration constants
from config import DELAY_BETWEEN_TICKERS

# Configure paths
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent
DATA_DIR = WORKSPACE_ROOT / "Data"

# DELAY_BETWEEN_TICKERS imported from config.py (0.5s - courtesy delay for Yahoo servers)


class YahooFinanceEnricher:
    """Enriches candidates using Yahoo Finance (yfinance library)"""

    def __init__(self, week_number: int, force_refresh: bool = False):
        self.week_number = week_number
        self.force_refresh = force_refresh
        self.data_dir = DATA_DIR / f"W{week_number}"
        self.candidates_file = self.data_dir / "research_candidates.json"
        self.log_file = self.data_dir / "yfinance_enrichment.log"
        self.candidates: List[Dict] = []
        self.stats = {
            "total": 0,
            "enriched": 0,
            "failed": 0,
            "fields_added": 0,
            "skipped": 0,
        }

        self._setup_logging()

    def _setup_logging(self):
        """Configure logging to file and console"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(f"YFinance_W{self.week_number}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        # File handler
        fh = logging.FileHandler(self.log_file, mode="w", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        self.logger.info("✅ Yahoo Finance enrichment initialized")

    def load_candidates(self) -> bool:
        """Load research_candidates.json and check if already enriched"""
        try:
            if not self.candidates_file.exists():
                self.logger.error(f"❌ File not found: {self.candidates_file}")
                return False

            with open(self.candidates_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check if already enriched (unless --force)
            if not self.force_refresh:
                enrichment_info = data.get("enrichment", {}).get("yahoo_finance", {})
                if enrichment_info:
                    timestamp = enrichment_info.get("timestamp", "unknown")
                    enriched_count = enrichment_info.get("enriched", 0)
                    self.logger.info(f"✅ Already enriched on {timestamp}")
                    self.logger.info(f"   Enriched: {enriched_count} candidates")
                    self.logger.info("   Use --force to re-enrich")
                    return False  # Skip - already done

            # Handle both formats: {"candidates": [...]} or [...]
            if isinstance(data, dict):
                self.candidates = data.get("candidates", [])
            else:
                self.candidates = data

            if not self.candidates:
                self.logger.warning("⚠️  No candidates found")
                return False

            self.stats["total"] = len(self.candidates)
            self.logger.info(f"✅ Loaded {len(self.candidates)} candidates")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error loading candidates: {e}")
            return False

    def enrich_candidate(self, candidate: Dict) -> Dict:
        """Enrich single candidate with Yahoo Finance data

        Fetches comprehensive data in one API call per ticker:
        - Company info: sector, industry, description, employees, website
        - Valuation: P/E ratio, P/B ratio, PEG ratio, market cap, enterprise value
        - Profitability: profit margins, gross margins, ROE, ROA, operating margins
        - Growth: revenue growth, earnings growth, quarterly earnings growth
        - Financial health: debt/equity, current ratio, quick ratio, cash, free cash flow
        - Analyst sentiment: recommendation (1-5), price target, analyst count
        - Ownership: institutional ownership %, short interest %
        """
        ticker = candidate.get("ticker", "UNKNOWN")
        self.logger.info(f"\n🔍 Enriching {ticker}...")

        enrichments = {}

        try:
            # Fetch all data in one call
            stock = yf.Ticker(ticker)
            info = stock.info

            if not info or len(info) < 5:  # Minimal data check
                self.logger.warning(f"⚠️  No data available for {ticker}")
                self.stats["failed"] += 1
                return candidate

            # Company basics
            if "sector" in info and info["sector"]:
                enrichments["sector"] = info["sector"]
                self.logger.info(f"   • Sector: {info['sector']}")

            if "industry" in info and info["industry"]:
                enrichments["industry"] = info["industry"]
                self.logger.info(f"   • Industry: {info['industry']}")

            if "longBusinessSummary" in info and info["longBusinessSummary"]:
                desc = info["longBusinessSummary"]
                enrichments["description"] = desc[:250] + "..." if len(desc) > 250 else desc

            if "website" in info and info["website"]:
                enrichments["website"] = info["website"]

            if "fullTimeEmployees" in info and info["fullTimeEmployees"]:
                enrichments["employees"] = info["fullTimeEmployees"]

            if "country" in info and info["country"]:
                enrichments["country"] = info["country"]

            # Valuation metrics
            if "forwardPE" in info and info["forwardPE"]:
                enrichments["pe_ratio_forward"] = round(info["forwardPE"], 2)
                self.logger.info(f"   • P/E (Forward): {info['forwardPE']:.2f}")
            elif "trailingPE" in info and info["trailingPE"]:
                enrichments["pe_ratio"] = round(info["trailingPE"], 2)
                self.logger.info(f"   • P/E (Trailing): {info['trailingPE']:.2f}")

            if "priceToBook" in info and info["priceToBook"]:
                enrichments["pb_ratio"] = round(info["priceToBook"], 2)

            if "marketCap" in info and info["marketCap"]:
                enrichments["market_cap"] = info["marketCap"]
                market_cap_b = info["marketCap"] / 1_000_000_000
                self.logger.info(f"   • Market Cap: ${market_cap_b:.1f}B")

            # Profitability metrics
            if "profitMargins" in info and info["profitMargins"]:
                enrichments["profit_margin_pct"] = round(info["profitMargins"] * 100, 2)
                self.logger.info(f"   • Profit Margin: {info['profitMargins']*100:.2f}%")

            if "returnOnEquity" in info and info["returnOnEquity"]:
                enrichments["roe_pct"] = round(info["returnOnEquity"] * 100, 2)
                self.logger.info(f"   • ROE: {info['returnOnEquity']*100:.2f}%")

            if "returnOnAssets" in info and info["returnOnAssets"]:
                enrichments["roa_pct"] = round(info["returnOnAssets"] * 100, 2)

            if "operatingMargins" in info and info["operatingMargins"]:
                enrichments["operating_margin_pct"] = round(info["operatingMargins"] * 100, 2)

            # Growth metrics
            if "revenueGrowth" in info and info["revenueGrowth"]:
                enrichments["revenue_growth_yoy"] = round(info["revenueGrowth"] * 100, 1)
                self.logger.info(f"   • Revenue Growth: {info['revenueGrowth']*100:+.1f}%")

            if "earningsGrowth" in info and info["earningsGrowth"]:
                enrichments["earnings_growth_yoy"] = round(info["earningsGrowth"] * 100, 1)
                self.logger.info(f"   • Earnings Growth: {info['earningsGrowth']*100:+.1f}%")

            # Financial health
            if "debtToEquity" in info and info["debtToEquity"]:
                enrichments["debt_equity_ratio"] = round(info["debtToEquity"] / 100, 2)

            if "currentRatio" in info and info["currentRatio"]:
                enrichments["current_ratio"] = round(info["currentRatio"], 2)

            if "totalCash" in info and info["totalCash"]:
                cash_millions = info["totalCash"] / 1_000_000
                enrichments["cash_millions"] = round(cash_millions, 1)

            if "totalDebt" in info and info["totalDebt"]:
                debt_millions = info["totalDebt"] / 1_000_000
                enrichments["debt_millions"] = round(debt_millions, 1)

            # Additional useful metrics
            if "beta" in info and info["beta"]:
                enrichments["beta"] = round(info["beta"], 2)

            if "dividendYield" in info and info["dividendYield"]:
                enrichments["dividend_yield_pct"] = round(info["dividendYield"] * 100, 2)

            if "fiftyTwoWeekHigh" in info and info["fiftyTwoWeekHigh"]:
                enrichments["year_high"] = round(info["fiftyTwoWeekHigh"], 2)

            if "fiftyTwoWeekLow" in info and info["fiftyTwoWeekLow"]:
                enrichments["year_low"] = round(info["fiftyTwoWeekLow"], 2)

            # ============ NEW FIELDS (Prompt-B requirements) ============

            # Institutional ownership (explicitly required by Prompt-B)
            if "heldPercentInstitutions" in info and info["heldPercentInstitutions"]:
                enrichments["institutional_ownership_pct"] = round(info["heldPercentInstitutions"] * 100, 1)
                self.logger.info(f"   • Institutional Ownership: {info['heldPercentInstitutions']*100:.1f}%")

            # Analyst sentiment (1.0 = Strong Buy, 5.0 = Strong Sell)
            if "recommendationMean" in info and info["recommendationMean"]:
                enrichments["analyst_rating"] = round(info["recommendationMean"], 2)
                # Convert to human-readable
                rating_val = info["recommendationMean"]
                if rating_val <= 1.5:
                    rating_label = "Strong Buy"
                elif rating_val <= 2.5:
                    rating_label = "Buy"
                elif rating_val <= 3.5:
                    rating_label = "Hold"
                elif rating_val <= 4.5:
                    rating_label = "Sell"
                else:
                    rating_label = "Strong Sell"
                enrichments["analyst_rating_label"] = rating_label
                self.logger.info(f"   • Analyst Rating: {rating_val:.2f} ({rating_label})")

            if "numberOfAnalystOpinions" in info and info["numberOfAnalystOpinions"]:
                enrichments["analyst_count"] = info["numberOfAnalystOpinions"]

            if "targetMeanPrice" in info and info["targetMeanPrice"]:
                enrichments["analyst_target_price"] = round(info["targetMeanPrice"], 2)
                # Calculate upside if we have current price
                current = info.get("currentPrice") or info.get("regularMarketPrice")
                if current and current > 0:
                    upside = ((info["targetMeanPrice"] - current) / current) * 100
                    enrichments["analyst_upside_pct"] = round(upside, 1)
                    self.logger.info(f"   • Analyst Target: ${info['targetMeanPrice']:.2f} ({upside:+.1f}% upside)")

            # Short interest (risk/squeeze indicator)
            if "shortPercentOfFloat" in info and info["shortPercentOfFloat"]:
                enrichments["short_interest_pct"] = round(info["shortPercentOfFloat"] * 100, 2)
                self.logger.info(f"   • Short Interest: {info['shortPercentOfFloat']*100:.2f}%")

            # PEG ratio (growth-adjusted valuation)
            if "trailingPegRatio" in info and info["trailingPegRatio"]:
                enrichments["peg_ratio"] = round(info["trailingPegRatio"], 2)
                self.logger.info(f"   • PEG Ratio: {info['trailingPegRatio']:.2f}")

            # Free cash flow (cash generation quality)
            if "freeCashflow" in info and info["freeCashflow"]:
                fcf_millions = info["freeCashflow"] / 1_000_000
                enrichments["free_cashflow_millions"] = round(fcf_millions, 1)
                self.logger.info(f"   • Free Cash Flow: ${fcf_millions:.1f}M")

            # Quarterly earnings growth (recent performance)
            if "earningsQuarterlyGrowth" in info and info["earningsQuarterlyGrowth"]:
                enrichments["earnings_growth_quarterly"] = round(info["earningsQuarterlyGrowth"] * 100, 1)
                self.logger.info(f"   • Quarterly Earnings Growth: {info['earningsQuarterlyGrowth']*100:+.1f}%")

            # Gross margins (pricing power)
            if "grossMargins" in info and info["grossMargins"]:
                enrichments["gross_margin_pct"] = round(info["grossMargins"] * 100, 2)

            # Quick ratio (stricter liquidity)
            if "quickRatio" in info and info["quickRatio"]:
                enrichments["quick_ratio"] = round(info["quickRatio"], 2)

            # Enterprise value (better for comparisons)
            if "enterpriseValue" in info and info["enterpriseValue"]:
                ev_billions = info["enterpriseValue"] / 1_000_000_000
                enrichments["enterprise_value_billions"] = round(ev_billions, 2)

            if enrichments:
                self.stats["enriched"] += 1
                self.stats["fields_added"] += len(enrichments)
                self.logger.info(f"✅ Added {len(enrichments)} field(s)")
            else:
                self.stats["failed"] += 1
                self.logger.warning(f"⚠️  No data extracted")

            return {**candidate, **enrichments}

        except Exception as e:
            self.logger.error(f"❌ Error enriching {ticker}: {str(e)}")
            self.stats["failed"] += 1
            return candidate

    def save_candidates(self, enriched: List[Dict]) -> bool:
        """Save enriched candidates"""
        try:
            with open(self.candidates_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both formats
            if isinstance(data, dict):
                data["candidates"] = enriched
            else:
                data = {"candidates": enriched}

            if "enrichment" not in data:
                data["enrichment"] = {}

            data["enrichment"]["yahoo_finance"] = {
                "timestamp": datetime.now().isoformat(),
                "week": self.week_number,
                **self.stats,
            }

            tmp = self.candidates_file.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            tmp.replace(self.candidates_file)
            self.logger.info(f"\n✅ Saved to {self.candidates_file.name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Save error: {e}")
            return False

    def run(self) -> bool:
        """Execute enrichment workflow"""
        self.logger.info("=" * 60)
        self.logger.info(f"YAHOO FINANCE ENRICHMENT - WEEK {self.week_number}")
        self.logger.info("=" * 60)
        self.logger.info("📌 FREE & UNLIMITED - No API key required")
        self.logger.info("📌 Complements Marketstack (price/volume/momentum)")
        self.logger.info("📌 Adds: company info, ratios, growth, financials")
        self.logger.info("=" * 60)

        if not self.load_candidates():
            self.logger.warning("⚠️  Skipping enrichment")
            return True

        enriched = []
        for i, candidate in enumerate(self.candidates, 1):
            ticker = candidate.get("ticker", f"Unknown_{i}")
            self.logger.info(f"\n[{i}/{len(self.candidates)}] {ticker}")

            try:
                enriched.append(self.enrich_candidate(candidate))

                # Delay between tickers (except after last one)
                if i < len(self.candidates):
                    time.sleep(DELAY_BETWEEN_TICKERS)
            except Exception as e:
                self.logger.error(f"❌ Error: {e}")
                enriched.append(candidate)
                self.stats["failed"] += 1

        self.save_candidates(enriched)

        self.logger.info("\n" + "=" * 60)
        self.logger.info("SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total: {self.stats['total']}")
        self.logger.info(f"Enriched: {self.stats['enriched']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"Fields added: {self.stats['fields_added']}")
        self.logger.info(f"\nLog: {self.log_file}")
        self.logger.info("=" * 60)

        return True


def main():
    parser = argparse.ArgumentParser(description="Enrich candidates with Yahoo Finance fundamentals (free, unlimited)")
    parser.add_argument("--week", type=int, required=True, help="Week number (e.g., 7)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-enrichment even if already done",
    )
    args = parser.parse_args()

    enricher = YahooFinanceEnricher(args.week, force_refresh=args.force)
    enricher.run()
    sys.exit(0)  # Always success to not break automation


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(0)  # Non-fatal
