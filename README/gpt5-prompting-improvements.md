# GPT-5 Prompting Guide - Application to Quantum Investor Portfolio System

**Date:** November 29, 2025  
**Source:** [OpenAI GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5-1_prompting_guide)  
**System:** Quantum Investor AI-driven portfolio automation (Azure OpenAI GPT-5.1-chat)

---

## Executive Summary

The OpenAI GPT-5 prompting guide provides valuable best practices that **directly apply to our GPT-5.1-chat deployment** in the portfolio automation system. This document outlines 5 high-impact improvements based on the guide, with implementation recommendations for our multi-agent AI architecture.

---

## Current System Architecture

### AI Model Configuration
- **Model:** `gpt-5.1-chat` via Azure OpenAI
- **Deployment:** Custom Azure OpenAI endpoint
- **Temperature:** Fixed at 1.0 (GPT-5.1 limitation)
- **API:** Uses both `chat.completions.create()` and `responses.create()` with web search

### Multi-Agent Prompt System
1. **Prompt A** - Data Validator (optional QA step)
2. **Prompt B** - Portfolio Analyst & Narrative Writer (core decision engine)
3. **Prompt D** - Final HTML Assembler
4. **Prompt-MarketResearch** - Market Intelligence Agent (pre-screener)

### Key Files
- `portfolio_automation.py` - Main orchestration (3000+ lines)
- `automated_rebalance.py` - Trade execution script (600+ lines)
- `Prompt-B-v5.4B.md` - Investment decision framework
- `Prompt-MarketResearch.md` - Stock screening criteria

---

## 5 High-Impact Improvements from GPT-5 Guide

### 1. Structured Output Enforcement

**Current State:**
- JSON schemas exist (`decision_summary.json`, `research_candidates.json`)
- Basic validation in Python but no schema enforcement in prompts

**Recommended Implementation:**

#### Add to `Prompt-B-v5.4B.md`:
```markdown
## DECISION_SUMMARY.JSON SCHEMA (STRICT)

{
  "week": integer (required, range: 1-52),
  "decision": enum ["HOLD", "REBALANCE"] (required),
  "position_count": integer (required, range: 6-10),
  "triggers_activated": array<string> (required, may be empty),
  "trades_executed": array<TradeObject> (required, empty if HOLD),
  "portfolio_value": string (required, format: "$X,XXX"),
  "sp500_alpha_bps": integer (required, basis points),
  "confidence": float (NEW, range: 0.0-1.0)
}

TradeObject {
  "action": enum ["exit", "buy", "trim", "add_to_existing"] (required),
  "ticker": string (required, uppercase),
  "name": string (required, full company name),
  "value": integer (required, positive),
  "price": float (optional, 2 decimals),
  "rationale": string (NEW, max 200 chars)
}

VALIDATION RULES:
- If decision="HOLD", trades_executed MUST be empty array
- If decision="REBALANCE", trades_executed MUST have 1+ trades
- Sum of BUY values + existing holdings ≤ portfolio_value
- All tickers must be valid US stock symbols
```

#### Add to `automated_rebalance.py`:
```python
from jsonschema import validate, ValidationError

DECISION_SCHEMA = {
    "type": "object",
    "required": ["week", "decision", "position_count", "trades_executed"],
    "properties": {
        "decision": {"enum": ["HOLD", "REBALANCE"]},
        "position_count": {"type": "integer", "minimum": 6, "maximum": 10},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "trades_executed": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["action", "ticker", "value"],
                "properties": {
                    "action": {"enum": ["exit", "buy", "trim", "add_to_existing"]},
                    "ticker": {"type": "string", "pattern": "^[A-Z]{1,5}$"},
                    "value": {"type": "integer", "minimum": 500}
                }
            }
        }
    }
}

def validate_decision(self) -> bool:
    try:
        validate(instance=self.decision_data, schema=DECISION_SCHEMA)
        logging.info("✅ Schema validation passed")
        return True
    except ValidationError as e:
        logging.error(f"❌ Schema validation failed: {e.message}")
        return False
```

---

### 2. Multi-Turn Reasoning for Complex Decisions

**Current State:**
- Prompt B makes decisions in a single LLM call
- No explicit chain-of-thought structure

**Recommended Implementation:**

#### Modify `Prompt/Prompt-B-v5.4B.md`:
```markdown
## DECISION WORKFLOW (MANDATORY STEPS)

You MUST follow this multi-step reasoning process:

### Step 1: Trigger Assessment
List all active triggers and rate severity (1-5 scale):
- Position count outside 6-10 range: [score]
- Any position >20% of portfolio: [score]
- Lagging S&P 500 by >500 bps: [score]
- Individual stock underperformance: [score]

### Step 2: Trade Candidate Evaluation
For each potential trade, score on:
- Momentum strength (1-5)
- Portfolio fit (1-5)
- Risk/reward (1-5)
- Confidence in thesis (1-5)

### Step 3: Constraint Validation
Before finalizing trades, verify:
- ✓ Position count will be 6-10 after trades
- ✓ No position >20% after trades
- ✓ Sector diversification maintained (<45% any sector)
- ✓ All positions ≥$500

### Step 4: Final Decision
Based on Steps 1-3, state decision (HOLD or REBALANCE) with confidence score (0.0-1.0)

### Step 5: Generate Outputs
Only after completing Steps 1-4, produce:
- narrative.html
- seo.json
- decision_summary.json (include confidence score)
```

#### Update `scripts/portfolio_automation.py`:
```python
def run_prompt_b(self):
    system_prompt = """You are the GenAi Chosen Portfolio Analyst.

CRITICAL: You MUST use multi-step reasoning. Show your work for each step:
1. Trigger Assessment (list + score each)
2. Trade Evaluation (score candidates)
3. Constraint Validation (check all rules)
4. Final Decision (with confidence 0.0-1.0)
5. Generate JSON outputs

Do not skip steps. Document reasoning at each stage."""
```

---

### 3. Few-Shot Examples for Edge Cases

**Current State:**
- No concrete examples in prompts
- AI must infer behavior from abstract rules

**Recommended Implementation:**

#### Add to `Prompt/Prompt-B-v5.4B.md`:
```markdown
## EXAMPLE DECISION SCENARIOS

### Example 1: Strong Performance, No Triggers
**Input:**
- Position count: 9
- All positions: 8-15% weight
- Portfolio weekly: +3.2%
- S&P 500 weekly: +2.1%
- Alpha: +110 bps

**Reasoning:**
Step 1: No triggers activated (position count OK, no oversized positions, outperforming S&P)
Step 2: Review research_candidates for watchlist inclusion
Step 3: No constraint violations
Step 4: HOLD decision, confidence: 0.95

**Output:**
```json
{
  "decision": "HOLD",
  "position_count": 9,
  "triggers_activated": [],
  "trades_executed": [],
  "confidence": 0.95,
  "sp500_alpha_bps": 110
}
```

### Example 2: Underperformance with Clear Laggards
**Input:**
- Position count: 8
- NVDA: -8% weekly (lagging portfolio by -11%)
- TSLA: -6% weekly (lagging portfolio by -9%)
- Portfolio weekly: +3%
- S&P 500 weekly: +2%
- Research candidates: AVGO (+12% 4w), AMD (+9% 4w)

**Reasoning:**
Step 1: Triggers activated
  - Individual underperformance: severity 4/5 (NVDA, TSLA both >5% below portfolio)
Step 2: Trade evaluation
  - Exit NVDA: momentum broken, severity: 4/5
  - Exit TSLA: momentum broken, severity: 4/5
  - Buy AVGO: strong momentum (5/5), semi sector fit (4/5), confidence: 4/5
  - Buy AMD: strong momentum (4/5), semi sector fit (5/5), confidence: 4/5
Step 3: Constraint check
  - Pre-trade: 8 positions → Post-trade: 8 positions ✓
  - AVGO $1,300 (13%), AMD $1,300 (13%) both <20% ✓
  - Sector: Technology 45% (at cap but not exceeding) ✓
Step 4: REBALANCE, confidence: 0.82 (moderate due to sector concentration)

**Output:**
```json
{
  "decision": "REBALANCE",
  "position_count": 8,
  "triggers_activated": ["individual_underperformance"],
  "trades_executed": [
    {"action": "exit", "ticker": "NVDA", "value": 1250, "rationale": "Momentum breakdown, -11% vs portfolio"},
    {"action": "exit", "ticker": "TSLA", "value": 1280, "rationale": "Weak momentum, -9% vs portfolio"},
    {"action": "buy", "ticker": "AVGO", "name": "Broadcom Inc", "value": 1300, "rationale": "Strong semi momentum, +12% 4w"},
    {"action": "buy", "ticker": "AMD", "name": "Advanced Micro Devices", "value": 1300, "rationale": "AI chip exposure, +9% 4w"}
  ],
  "confidence": 0.82,
  "portfolio_value": "$10,400",
  "sp500_alpha_bps": 100
}
```

### Example 3: Position Count Violation (Edge Case)
**Input:**
- Position count: 11 (VIOLATION)
- All performing well
- No clear laggards

**Reasoning:**
Step 1: Triggers activated
  - Position count violation: severity 5/5 (11 > max 10)
Step 2: Trade evaluation
  - Must exit 1 position to comply
  - Identify weakest performer or smallest position
  - If smallest is PLTR ($850, 8%), exit to free capital
Step 3: Constraint check
  - Pre: 11 → Post: 10 ✓
Step 4: REBALANCE (forced by constraint), confidence: 0.65 (not ideal to exit performing asset)

**Output:**
```json
{
  "decision": "REBALANCE",
  "position_count": 10,
  "triggers_activated": ["position_count_violation"],
  "trades_executed": [
    {"action": "exit", "ticker": "PLTR", "value": 850, "rationale": "Smallest position, forced exit for compliance"}
  ],
  "confidence": 0.65,
  "portfolio_value": "$10,850",
  "sp500_alpha_bps": 145
}
```
```

---

### 4. Error Recovery Instructions

**Current State:**
- Prompt-MarketResearch has two-phase approach (research then JSON)
- No fallback guidance for missing data

**Recommended Implementation:**

#### Add to `Prompt/Prompt-MarketResearch.md`:
```markdown
## ERROR RECOVERY PROTOCOLS

### Data Source Failures

**If web search fails for a ticker:**
1. Use most recent cached data (max age: 48 hours)
2. Mark in JSON: `"data_quality": "STALE"`
3. Downgrade recommendation: `"BUY"` → `"WATCHLIST"`
4. Document in notes: "Using cached data from [date]"

**If <3 candidates found after screening:**
1. Relax 4-week momentum filter: +5% → +3%
2. Document deviation: `"screening_deviation": "Relaxed momentum threshold to +3% due to market conditions"`
3. Ensure quality bars remain (institutional ownership, market cap, liquidity)

**If sector data unavailable:**
1. Use GICS classification from ticker lookup
2. If unavailable, classify as "Technology" (portfolio default)
3. Flag: `"sector_source": "ESTIMATED"`

### Output Format Failures

**If JSON generation produces invalid syntax:**
1. Strip all markdown formatting (```, ```json)
2. Remove citations (e.g., [1], [source])
3. Replace special characters: en-dash (–) → hyphen (-)
4. Validate quotes: ensure all strings properly closed
5. Remove trailing commas

**Validation checklist before responding:**
- [ ] Valid JSON (no syntax errors)
- [ ] All required fields present
- [ ] 3-5 candidates included
- [ ] All tickers are valid uppercase symbols
- [ ] All percentages formatted as strings ("+12.5%")
```

#### Add to `automated_rebalance.py`:
```python
def fetch_current_price(self, ticker: str, max_age_hours: int = 48) -> Optional[float]:
    """Fetch current price from Finnhub API with fallback to cached data"""
    
    # Try live API first
    try:
        url = f"{FINNHUB_BASE_URL}/quote"
        params = {"symbol": ticker, "token": FINNHUB_API_KEY}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current_price = data.get("c")
        if current_price and current_price > 0:
            # Cache the result
            self._cache_price(ticker, current_price)
            logging.info(f"   Fetched live price for {ticker}: ${current_price:.2f}")
            return round(current_price, 2)
    
    except Exception as e:
        logging.warning(f"⚠️  Live price fetch failed for {ticker}: {str(e)}")
    
    # Fallback to cached data
    cached_price, cached_age = self._get_cached_price(ticker)
    if cached_price and cached_age < max_age_hours:
        logging.info(f"   Using cached price for {ticker}: ${cached_price:.2f} (age: {cached_age}h)")
        return cached_price
    
    logging.error(f"❌ No valid price available for {ticker} (cache too old or missing)")
    return None

def _cache_price(self, ticker: str, price: float):
    """Store price with timestamp in master.json or separate cache"""
    cache_entry = {
        "price": price,
        "timestamp": datetime.now().isoformat(),
        "source": "finnhub"
    }
    # Implementation: store in master.json metadata or separate cache file

def _get_cached_price(self, ticker: str) -> Tuple[Optional[float], int]:
    """Retrieve cached price and age in hours"""
    # Implementation: read from cache, calculate age
    return None, 999  # Placeholder
```

---

### 5. Explicit Token Budget Management

**Current State:**
- `_extract_narrative_summary()` already compresses data
- No explicit token limits in prompts

**Recommended Implementation:**

#### Add to all prompt files header:
```markdown
## TOKEN BUDGET CONSTRAINTS

**CRITICAL: Your response must fit within these limits:**

| Output File | Max Tokens | Priority |
|-------------|------------|----------|
| `narrative.html` | 4,000 | MANDATORY |
| `seo.json` | 300 | MANDATORY |
| `decision_summary.json` | 200 | MANDATORY |

**Response prioritization if approaching limits:**

1. **Must include (never omit):**
   - Decision rationale (why HOLD or REBALANCE)
   - Trade execution details (all trades with tickers, values, actions)
   - SEO title and description
   - JSON decision tracking

2. **Can trim if needed:**
   - Market color commentary (reduce from 2 paragraphs → 1)
   - Holdings descriptions (use bullet points instead of prose)
   - Risk disclosure (use standard template)

3. **Estimation formula:**
   - ~4 characters per token
   - narrative.html target: 16,000 chars max
   - seo.json target: 1,200 chars max
   - decision_summary.json target: 800 chars max

**If you detect you're approaching limits:**
- Use concise language
- Remove redundant phrases
- Prioritize data over prose
- Use abbreviations (e.g., "YoY" not "year-over-year")
```

#### Update `scripts/portfolio_automation.py`:
```python
def run_prompt_b(self):
    # ... existing code ...
    
    # Add token budget warning to user_message
    user_message += """

⚠️ TOKEN BUDGET: Your response must fit:
- narrative.html: <4000 tokens (~16K chars)
- seo.json: <300 tokens (~1.2K chars)  
- decision_summary.json: <200 tokens (~800 chars)

If approaching limits, prioritize decision rationale and trade details over commentary.
"""
    
    response = self.call_ai(system_prompt, user_message)
    
    # Validate response size
    narrative_len = len(self.narrative_html)
    seo_len = len(json.dumps(self.seo_json))
    
    if narrative_len > 18000:  # 4000 tokens * 4.5 chars/token
        logging.warning(f"⚠️  Narrative HTML exceeds recommended size: {narrative_len} chars")
    if seo_len > 1500:
        logging.warning(f"⚠️  SEO JSON exceeds recommended size: {seo_len} chars")
```

---

## Implementation Priority

### Phase 1 (Immediate - Week 8):
1. ✅ Add confidence scoring to `decision_summary.json` schema
2. ✅ Add 3 few-shot examples to `Prompt/Prompt-B-v5.4B.md`
3. ✅ Add token budget headers to all prompts

### Phase 2 (Next Week):
4. ⏳ Implement JSON schema validation in `automated_rebalance.py`
5. ⏳ Add error recovery protocols to `Prompt/Prompt-MarketResearch.md`
6. ⏳ Add price caching with fallback in `automated_rebalance.py`

### Phase 3 (Future Enhancement):
7. 📋 Implement multi-turn reasoning workflow in `Prompt-B`
8. 📋 Add self-critique step before finalizing decisions
9. 📋 Create automated prompt testing harness

---

## Testing Strategy

### Unit Tests
```python
# Test schema validation
def test_decision_schema_validation():
    valid_decision = {"decision": "HOLD", "position_count": 9, ...}
    assert validate_decision_schema(valid_decision) == True
    
    invalid_decision = {"decision": "INVALID", "position_count": 11, ...}
    assert validate_decision_schema(invalid_decision) == False

# Test error recovery
def test_price_fetch_fallback():
    # Mock API failure
    with mock_api_failure():
        price = fetch_current_price("AAPL", use_cache=True)
        assert price is not None  # Should use cache
```

### Integration Tests
```bash
# Test with real Week 7 data
python automated_rebalance.py --week 7 --dry-run

# Expected: Schema validation passes, confidence score present
```

### Prompt Regression Tests
```python
# Ensure few-shot examples produce expected outputs
def test_prompt_b_examples():
    for example in PROMPT_B_EXAMPLES:
        response = call_prompt_b(example.input)
        assert response.decision == example.expected_decision
        assert response.confidence >= 0.0 and response.confidence <= 1.0
```

---

## Risk Assessment

### Low Risk Changes:
- ✅ Adding confidence scoring (backward compatible)
- ✅ Adding few-shot examples (improves consistency)
- ✅ Adding token budgets (advisory only)

### Medium Risk Changes:
- ⚠️ JSON schema validation (could break existing workflows if strict)
- ⚠️ Error recovery protocols (requires testing edge cases)

### High Risk Changes:
- 🔴 Multi-turn reasoning (major prompt architecture change)

---

## Success Metrics

### Quantitative:
- Decision confidence scores consistently >0.7
- Schema validation pass rate: 100%
- Token budget compliance: >95%
- Price fetch success rate with fallback: >99%

### Qualitative:
- Clearer decision rationale in narratives
- Fewer edge case failures
- More consistent JSON outputs
- Better handling of market volatility

---

## References

- [OpenAI GPT-5 Prompting Guide](https://cookbook.openai.com/examples/gpt-5/gpt-5-1_prompting_guide)
- `Prompt/Prompt-B-v5.4B.md` (current version)
- `scripts/portfolio_automation.py` (lines 96-2850)
- `automated_rebalance.py` (lines 1-631)
- Azure OpenAI GPT-5.1-chat API documentation

---

**Document Version:** 1.0  
**Last Updated:** November 29, 2025  
**Next Review:** After Week 8 production run
