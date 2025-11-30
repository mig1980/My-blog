"""
Configuration constants for portfolio automation.

This module centralizes magic numbers and configurable parameters
to improve maintainability and allow easy adjustments.
"""

from typing import Any, Dict, List

# =============================================================================
# CHART RENDERING CONSTANTS
# =============================================================================
# Used by portfolio_automation.py for generating performance SVG charts

CHART_CONFIG: Dict[str, Any] = {
    "width": 900,
    "height": 400,
    "padding": {
        "left": 80,
        "right": 50,
        "top": 50,
        "bottom": 50,
    },
    "y_axis": {
        "min": 80,
        "max": 120,
        "labels": [120, 110, 100, 90, 80],
        "positions": [50, 125, 200, 275, 350],  # SVG y-coordinates for labels
    },
}

# Legacy constants for backward compatibility (individual variables)
CHART_WIDTH: int = CHART_CONFIG["width"]
CHART_HEIGHT: int = CHART_CONFIG["height"]
CHART_PAD_LEFT: int = CHART_CONFIG["padding"]["left"]
CHART_PAD_RIGHT: int = CHART_CONFIG["padding"]["right"]
CHART_PAD_TOP: int = CHART_CONFIG["padding"]["top"]
CHART_PAD_BOTTOM: int = CHART_CONFIG["padding"]["bottom"]
CHART_Y_MIN: int = CHART_CONFIG["y_axis"]["min"]
CHART_Y_MAX: int = CHART_CONFIG["y_axis"]["max"]
CHART_Y_LABELS: List[int] = CHART_CONFIG["y_axis"]["labels"]
CHART_Y_POSITIONS: List[int] = CHART_CONFIG["y_axis"]["positions"]


# =============================================================================
# API RATE LIMITS
# =============================================================================
# Seconds between API calls to respect rate limits

RATE_LIMITS: Dict[str, float] = {
    "finnhub": 1.3,  # 50 req/min = 1.2s minimum, using 1.3s for safety
    "marketstack": 2.0,  # 100 req/month, conservative delay
    "yfinance": 0.5,  # Courtesy delay, no hard limit
}

# Legacy constants for backward compatibility
FINNHUB_MIN_INTERVAL: float = RATE_LIMITS["finnhub"]
MARKETSTACK_MIN_INTERVAL: float = RATE_LIMITS["marketstack"]
DELAY_BETWEEN_TICKERS: float = RATE_LIMITS["yfinance"]


# =============================================================================
# PORTFOLIO CONSTRAINTS
# =============================================================================
# Used by automated_rebalance.py for validation

PORTFOLIO_CONSTRAINTS: Dict[str, Any] = {
    "min_positions": 6,
    "max_positions": 10,
    "max_position_pct": 0.20,  # 20% cap per position
    "min_position_value": 500,  # $500 minimum per position
}

# Legacy constants for backward compatibility
MIN_POSITIONS: int = PORTFOLIO_CONSTRAINTS["min_positions"]
MAX_POSITIONS: int = PORTFOLIO_CONSTRAINTS["max_positions"]
MAX_POSITION_PCT: float = PORTFOLIO_CONSTRAINTS["max_position_pct"]
MIN_POSITION_VALUE: int = PORTFOLIO_CONSTRAINTS["min_position_value"]


# =============================================================================
# RETRY CONFIGURATION
# =============================================================================
# Used by resilient_fetcher.py for ticker-level retry logic

RETRY_CONFIG: Dict[str, Any] = {
    "max_retries": 3,  # Maximum retry attempts per ticker
    "backoff_base": 2.0,  # Exponential backoff base (2^attempt seconds)
    "timeout": 10.0,  # Request timeout in seconds
}

# Legacy constants for backward compatibility
MAX_RETRIES: int = RETRY_CONFIG["max_retries"]
BACKOFF_BASE: float = RETRY_CONFIG["backoff_base"]
REQUEST_TIMEOUT: float = RETRY_CONFIG["timeout"]
