# AI Lead Finder — Backend

FastAPI service that discovers local businesses (via the official Google
Places API), crawls their public websites, detects automation gaps, scores
them as sales leads, and serves everything to the React frontend.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # then fill in your Google API keys
uvicorn main:app --reload
```

API docs: http://127.0.0.1:8000/docs

## Required API keys

- **`GOOGLE_PLACES_API_KEY`** — required for business discovery. Enable
  "Places API" in a Google Cloud project and set up billing (Google provides
  a recurring free monthly credit that covers moderate usage).
- **`GOOGLE_CUSTOM_SEARCH_API_KEY`** / **`GOOGLE_CUSTOM_SEARCH_CX`** —
  optional. Used only to supplement discovery when Places doesn't return
  enough results for a niche business type or region.

Both are official Google APIs — this project does not scrape Google search
result pages, which would violate Google's Terms of Service.

## What it deliberately does NOT do

- Never scrapes LinkedIn. Publicly-linked LinkedIn URLs found on a business's
  own site are stored as a reference only — never visited or scraped.
- Never attempts to solve or bypass CAPTCHAs / bot-detection. A blocked
  domain is skipped and logged, not retried harder.
- Always checks `robots.txt` before crawling a page (toggle:
  `RESPECT_ROBOTS_TXT`).
- Rate-limits requests per-domain (configurable per job from the UI's
  Advanced Settings).

## Layout

```
app/
  core/       config, logging, rate limiter, robots.txt checker
  db/         SQLAlchemy async session + declarative base
  models/     ScrapeJob, Lead, StaffMember, SearchHistoryEntry
  schemas/    Pydantic request/response models
  discovery/  Google Places + Custom Search clients
  scrapers/   httpx/Playwright fetcher, site crawler, link discovery
  extractors/ contact info, social links, tech/widget detection, staff parsing
  scoring/    decision-maker ranking, pain-point rules, lead score, recommendations
  services/   job orchestrator, progress pub/sub, pause/resume/cancel control
  exports/    CSV / XLSX / JSON / SQLite / PDF audit generators
  api/routers/ jobs, leads, exports, settings, search-history, dashboard
```

## Tests

```bash
pytest
```
