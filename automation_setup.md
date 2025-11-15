# Weekly Portfolio Automation – Setup & Run Guide

Lightweight reference for generating a new weekly portfolio update (data, hero image, snippet card, full HTML post) using the integrated Python pipeline.

---
## 1. Overview
Pipeline (when API key present):
Prompt A (data update) → Hero Image (remote fetch or fallback) → Snippet Card → Prompt B (narrative) → Prompt C (visuals) → Prompt D (assembly + TLDR) → Index update.

### 1A. Workflow Chart

```mermaid
flowchart TD
  A[Start Weekly Run] --> B[Detect next week number]
  B --> C[Load previous week's master.json]
  C --> D{Data Source}
  D -->|alphavantage| D1[Fetch quotes + benchmarks (rate limited)] --> D2[Recalculate metrics & build new master.json]
  D -->|ai (Prompt A)| D3[Prompt A: Update master.json]
  D2 --> E[Generate hero image + snippet card]
  D3 --> E[Generate hero image + snippet card]
  E --> F{AI Narrative Enabled? (OPENAI_API_KEY)}
  F -->|Yes| G[Prompt B: Narrative + SEO] --> H[Prompt C: Table + Chart] --> I[Prompt D: Assemble HTML + Inject TLDR]
  F -->|No| J[Create data-only HTML]
  I --> K[Update index/posts pages (placeholder)]
  J --> K[Update index/posts pages (placeholder)]
  K --> L[Artifacts Written]

  subgraph Hero Image Generation
    E1[Try Pexels (PEXELS_API_KEY)] --> E2[Try Pixabay (PIXABAY_API_KEY)] --> E3[Try Lummi (stub)] --> E4[Fallback gradient]
  end
  E1 -->|success| E
  E2 -->|success| E
  E3 -->|success| E
  E4 --> E

  subgraph Outputs
    O1[Data/WN/master.json]
    O2[Media/WN.webp]
    O3[Media/WN-card.png]
    O4[Posts/Week-N HTML]
    O5[Data/archive/master-YYYYMMDD.json]
  end
  L --> O1 & O2 & O3 & O4 & O5

  classDef decision fill:#1e1e2e,stroke:#54546d,stroke-width:1px
  class D,F decision
```

Key Decision Points:
- Data Source: `--data-source alphavantage` skips Prompt A and uses live API; otherwise GPT Prompt A updates data.
- AI Narrative Enabled: Requires `OPENAI_API_KEY`; without it the pipeline writes a data-only HTML page.
- Hero Image Providers: Attempts remote sources in priority order; falls back to synthetic gradient if none succeed.

#### Workflow Diagram Assets
Rendered versions (generate via `scripts/render_workflow.ps1`):
- SVG: `Media/workflow.svg`
- PNG: `Media/workflow.png`
- Dark PNG: `Media/workflow-dark.png`

PowerShell one-liner (from repo root) if you prefer manual commands:
```powershell
npx mmdc -i workflow.mmd -o Media/workflow.svg -b transparent -w 1600 -H 1200; npx mmdc -i workflow.mmd -o Media/workflow.png -b transparent -w 1600 -H 1200
```

To regenerate all:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/render_workflow.ps1
```

Failure Handling (embedded in script):
- Remote image fetch failures: Graceful fallback; continues pipeline.
- OpenAI errors: Exception halts AI portion; data-only fallback available via no key.
- Alpha Vantage rate limits: Logs warning; prior price reused for that asset.

Extensibility Hooks:
- `update_index_pages()` currently placeholder for inserting new post cards.
- Additional attribution sidecar and dashboards can hook after master.json creation.


Artifacts produced for Week N:
- `Data/WN/master.json` (updated dataset)
- `Media/WN.webp` (hero image)
- `Media/WN-card.png` (social/share card)
- `Posts/GenAi-Managed-Stocks-Portfolio-Week-N.html` (final post)
- `Data/archive/master-YYYYMMDD.json` (archived snapshot)

---
## 2. Prerequisites
- Python 3.10+ (recommended).
- Installed dependencies:
  ```powershell
  pip install -r scripts/requirements.txt
  ```
- OpenAI API key (for Prompts B–D) OR AlphaVantage key (for direct market data). Without OpenAI the pipeline falls back to data-only HTML.
- Optional image provider keys (for hero image remote fetch):
  - `PEXELS_API_KEY`
  - `PIXABAY_API_KEY`
  - (Future) `LUMMI_API_KEY`

---
## 3. Environment Variables (PowerShell Examples)
```powershell
$Env:OPENAI_API_KEY = "sk-..."          # Enables narrative + visuals
$Env:ALPHAVANTAGE_API_KEY = "AV-..."    # Use with --data-source alphavantage
$Env:PEXELS_API_KEY = "px-..."          # Optional hero image provider
$Env:PIXABAY_API_KEY = "pb-..."         # Optional hero image provider
```
If no image provider keys are set, hero image falls back to gradient style.

---
## 4. Quick Run (AI Data Engine)
Detect next week automatically:
```powershell
python scripts/portfolio_automation.py --week auto
```
Specify a week explicitly:
```powershell
python scripts/portfolio_automation.py --week 7
```
Manual date override (forces evaluation date in master.json):
```powershell
python scripts/portfolio_automation.py --week auto --eval-date 2025-11-20
```

---
## 5. Alternate Data Source (Alpha Vantage)
Use real-time API instead of Prompt A:
```powershell
python scripts/portfolio_automation.py --data-source alphavantage --week auto
```
Note: Rate-limited (12s pauses). Ensure `ALPHAVANTAGE_API_KEY` is set.

---
## 6. Generated Assets Details
Hero Image (`Media/WN.webp`):
- Tries Pexels → Pixabay → (future Lummi) → gradient fallback.
- Overlays Week badge, metrics (Week Change, Since Inception, Alpha vs SPX), date range, site brand.

Snippet Card (`Media/WN-card.png`):
- Always generated (Python Pillow).
- 1200×630 social preview with same metric trio.

Post HTML (`Posts/GenAi-Managed-Stocks-Portfolio-Week-N.html`):
- Assembled by Prompt D.
- Injects TLDR strip automatically (week, total, alpha) if missing.
- Embeds narrative + performance table + chart (positions derived from headings).

Archive (`Data/archive/master-YYYYMMDD.json`):
- Snapshot of master.json for reproducibility.

---
## 7. Folder Structure (Relevant Parts)
```
Data/WN/            # master.json (latest week)
Media/WN.webp       # hero image
Media/WN-card.png   # snippet card
Posts/Week-N.html   # final post
Prompt/Prompt-A...  # prompt specs (A–D)
scripts/portfolio_automation.py
scripts/hero_image_generator.py      # standalone hero tool (optional manual use)
scripts/snippet_card_generator.py    # standalone snippet tool (fallback/manual)
```

---
## 8. Standalone Asset Regeneration
Hero image (custom query):
```powershell
python scripts/hero_image_generator.py --week 7 --master Data/W6/master.json --out Media/W7.webp --query "futuristic finance networks"
```
Snippet card (custom title):
```powershell
python scripts/snippet_card_generator.py --week 7 --master Data/W6/master.json --out Media/W7-card.png --title "Week 7 Performance Snapshot"
```

---
## 9. Failure Recovery
| Issue | Action |
|-------|--------|
| OpenAI timeout / format error | Re-run automation; master.json already written—will reuse. |
| Image provider unavailable | Hero falls back automatically; no manual fix required. |
| Benchmark fetch fails (Alpha Vantage) | Fallback to prior value; check logs and optionally rerun next day. |
| TLDR missing | Assembler injects; no manual edit needed. |

Logs printed inline in PowerShell; no separate log file presently.

---
## 10. Extensibility Points
- Add attribution sidecar: After hero generation, create `Media/WN-hero-attribution.json` storing provider, original URL, photographer.
- Negative week palette shift: Adjust overlay color if `weekly_pct < 0`.
- Index card auto-insertion: Enhance `update_index_pages()` (currently placeholder) to parse `posts.html` and append new card.
- Risk dashboard SVG: Automate creation via separate script using normalized dispersion metrics.

---
## 11. Minimal Path Without AI (Data-Only Mode)
Unset `OPENAI_API_KEY` and run:
```powershell
python scripts/portfolio_automation.py --week auto
```
Outputs simplified HTML with raw master.json for auditing.

---
## 12. Common Commands Cheat Sheet
```powershell
# Full weekly generation (AI)
python scripts/portfolio_automation.py --week auto

# Alpha Vantage mode
python scripts/portfolio_automation.py --week auto --data-source alphavantage

# Manual asset refresh after data update
python scripts/hero_image_generator.py --week 8 --master Data/W7/master.json --out Media/W8.webp
python scripts/snippet_card_generator.py --week 8 --master Data/W7/master.json --out Media/W8-card.png
```

---
## 13. Security & Integrity Notes
- No external execution of untrusted code; only HTTP GET requests to vetted image APIs.
- Consider adding CSP & SRI when introducing external JS.
- Rate limits respected for Alpha Vantage (12s intervals).

---
## 14. Summary
Run one command; receive standardized data, visuals, and post. Optional provider keys enhance hero imagery; absence never blocks publication. All critical transforms deterministic and archived.

---
Revision: Integrated hero + snippet generation | Date: 2025-11-15