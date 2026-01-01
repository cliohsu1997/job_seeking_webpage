# Economics Faculty Job Aggregator

A daily-updated webpage that aggregates economics department faculty recruiting information from AEA JOE and university websites.

## Quick Start

```bash
# Install dependencies
poetry install

# Verify URLs in configuration
poetry run python scripts/scraper/check_config/verify_urls.py

# Run scraper
poetry run python scripts/scraper/aea_scraper.py
```

## Project Status

**Phase 1 (LOAD)**: ✅ Complete - 176 accessible URLs, scraper framework implemented  
**Phase 2 (TRANSFORM)**: ⏸️ Ready to begin  
**Phase 3 (EXPORT)**: ⏸️ Pending  
**Phase 4 (DEPLOY)**: ⏸️ Pending

## Documentation Map

### 🚀 Getting Started
- **This file** - Quick start and navigation
- **`docs/SCRAPING_GUIDE.md`** - How to add new sources and use scrapers

### ⚙️ Configuration
- **`data/config/README.md`** - Configuration file structure and examples

### 🧪 Testing
- **`tests/load-data-collection/README.md`** - Running tests and test organization

### 📋 Project Management
- **`conversation_cursor/progress/latest.md`** - Current progress and pipeline status
- **`conversation_cursor/structure/latest.md`** - Detailed project structure
- **`conversation_cursor/to-do-list/`** - Task lists by phase

### 📖 Detailed Documentation
- **`read_it.md`** - Project guidelines and workflow rules (read first!)
- **`conversation_cursor/dates/2025-12-31/`** - Design proposals and strategy documents

## Workflow

**Load → Transform → Export**

1. **LOAD**: Scrape job listings (176 sources: AEA, universities, institutes)
2. **TRANSFORM**: Parse, normalize, deduplicate (Phase 2)
3. **EXPORT**: Generate HTML/JSON/CSV outputs (Phase 3)

## Current Coverage

- **176 accessible URLs**:
  - Mainland China: 100 universities
  - United States: ~60 universities
  - Other: UK, Canada, Australia, Germany, France, Netherlands, Singapore, Switzerland
  - Research Institutes: NBER, CEPR, Federal Reserve Banks, etc.

## Common Tasks

**Add a new source:**
→ See `docs/SCRAPING_GUIDE.md`

**Configure scraping:**
→ See `data/config/README.md`

**Run tests:**
→ See `tests/load-data-collection/README.md`

**Understand project structure:**
→ See `conversation_cursor/structure/latest.md`

**Check project status:**
→ See `conversation_cursor/progress/latest.md`

## Setup

1. Install Poetry: https://python-poetry.org/docs/#installation
2. Install dependencies: `poetry install`
3. Configure sources: Edit `data/config/scraping_sources.json`
4. Run: `poetry run python scripts/scraper/aea_scraper.py`
