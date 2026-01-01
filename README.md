# Economics Faculty Job Aggregator

A daily-updated webpage that aggregates economics department faculty recruiting information from AEA JOE and university websites.

## What This Project Does

1. **Scrapes** job listings from 176+ sources (AEA, universities, research institutes)
2. **Processes** raw data into structured format (Phase 2 - in progress)
3. **Generates** HTML webpage and JSON/CSV files (Phase 3 - planned)
4. **Updates** automatically on a schedule (Phase 4 - planned)

## Quick Start

```bash
# 1. Install dependencies
poetry install

# 2. Verify URLs in configuration
poetry run python scripts/scraper/check_config/verify_urls.py

# 3. Run scraper
poetry run python scripts/scraper/aea_scraper.py
```

**Output:** Raw HTML files saved to `data/raw/` (by source type: aea/, universities/, institutes/)

## Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1: LOAD** | ✅ Complete | Scraper framework with 176 accessible URLs |
| **Phase 2: TRANSFORM** | ⏸️ Ready | Parse, normalize, deduplicate data |
| **Phase 3: EXPORT** | ⏸️ Pending | Generate HTML/JSON/CSV outputs |
| **Phase 4: DEPLOY** | ⏸️ Pending | Automation and hosting |

## Documentation Map

**Start here** → Choose what you need:

| I want to... | Go to... |
|--------------|----------|
| **Get started quickly** | This file (Quick Start above) |
| **Add new sources or use scrapers** | [`docs/SCRAPING_GUIDE.md`](docs/SCRAPING_GUIDE.md) |
| **Configure scraping sources** | [`data/config/README.md`](data/config/README.md) |
| **Run or understand tests** | [`tests/load-data-collection/README.md`](tests/load-data-collection/README.md) |
| **See project structure** | [`conversation_cursor/structure/latest.md`](conversation_cursor/structure/latest.md) |
| **Check current progress** | [`conversation_cursor/progress/latest.md`](conversation_cursor/progress/latest.md) |
| **Read project rules** | [`read_it.md`](read_it.md) ⚠️ **Read first!** |
| **View design proposals** | [`conversation_cursor/dates/2025-12-31/`](conversation_cursor/dates/2025-12-31/) |

## Workflow: Load → Transform → Export

```
┌─────────┐    ┌──────────┐    ┌─────────┐
│  LOAD   │ →  │ TRANSFORM│ →  │ EXPORT  │
│ (Phase1)│    │ (Phase2) │    │ (Phase3)│
│  ✅     │    │  ⏸️      │    │  ⏸️     │
└─────────┘    └──────────┘    └─────────┘
```

1. **LOAD** (✅ Complete): Scrape from 176 sources → `data/raw/`
2. **TRANSFORM** (⏸️ Next): Parse & normalize → `data/processed/`
3. **EXPORT** (⏸️ Planned): Generate outputs → `jobs.html`, `jobs.json`, `jobs.csv`

## Current Coverage

**176 accessible URLs:**
- 🇨🇳 Mainland China: 100 universities
- 🇺🇸 United States: ~60 universities  
- 🌍 Other: UK, Canada, Australia, Germany, France, Netherlands, Singapore, Switzerland
- 🏛️ Research Institutes: NBER, CEPR, Federal Reserve Banks, etc.

## Project Structure

```
job-seeking-webpage/
├── data/              # Data storage (raw scraped, processed, config)
├── scripts/           # Automation (scraper ✅, processor ⏸️, generator ⏸️)
├── tests/             # Tests organized by phase
├── docs/              # Documentation guides
└── conversation_cursor/  # Project management (progress, structure, to-do)
```

**Detailed structure:** See [`conversation_cursor/structure/latest.md`](conversation_cursor/structure/latest.md)

## Common Tasks

| Task | Command / Location |
|------|-------------------|
| **Add new source** | Edit `data/config/scraping_sources.json` → See [`docs/SCRAPING_GUIDE.md`](docs/SCRAPING_GUIDE.md) |
| **Verify URLs** | `poetry run python scripts/scraper/check_config/verify_urls.py` |
| **Run scraper** | `poetry run python scripts/scraper/aea_scraper.py` |
| **Run tests** | `poetry run python tests/load-data-collection/test_scrapers.py` |
| **Check progress** | See [`conversation_cursor/progress/latest.md`](conversation_cursor/progress/latest.md) |

## Setup (First Time)

1. **Install Poetry**: https://python-poetry.org/docs/#installation
2. **Install dependencies**: `poetry install`
3. **Configure sources**: Edit `data/config/scraping_sources.json` (see [`data/config/README.md`](data/config/README.md))
4. **Run**: `poetry run python scripts/scraper/aea_scraper.py`

---

**⚠️ Important:** Read [`read_it.md`](read_it.md) first for project guidelines and workflow rules.
