# Structure: Project Organization

## Project Structure Overview

```
job-seeking-webpage/
├── read_it.md                      # Project guidelines (read first)
├── pyproject.toml                  # Poetry configuration
├── README.md                       # Project documentation
│
├── data/
│   ├── raw/                        # Raw scraped HTML/XML (Phase 1 output)
│   │   ├── aea/                    # AEA JOE scraped files
│   │   ├── universities/           # University scraped files
│   │   └── institutes/             # Research institute scraped files
│   ├── processed/                  # Processed data (Phase 2 output)
│   │   ├── jobs.json               # Current listings
│   │   ├── jobs.csv                # Current listings (CSV)
│   │   ├── archive/                # Historical snapshots
│   │   └── diagnostics/            # Diagnostic reports
│   └── config/
│       ├── scraping_sources.json   # Scraping sources (176 accessible URLs)
│       ├── scraping_rules.json     # Scraping patterns
│       └── processing_rules.json   # Processing rules (job types, specializations, regions)
│
├── scripts/
│   ├── scraper/                    # Phase 1 - COMPLETE
│   │   ├── base_scraper.py         # Base scraper class
│   │   ├── aea_scraper.py          # AEA JOE scraper
│   │   ├── university_scraper.py   # University scraper
│   │   ├── institute_scraper.py    # Institute scraper
│   │   ├── parsers/                # HTML, RSS, text, date parsers
│   │   └── utils/                  # Rate limiter, retry handler, user agent
│   ├── processor/                  # Phase 2 - IN PROGRESS
│   │   ├── pipeline.py            # Main pipeline (✅ Phase 2A)
│   │   ├── parser_manager.py       # Route to parsers (✅ Phase 2A)
│   │   ├── normalizer.py           # Data normalization (✅ Phase 2A - basic)
│   │   ├── enricher.py             # Data enrichment (to be created)
│   │   ├── deduplicator.py         # Deduplication (to be created)
│   │   ├── validator.py            # Data validation (to be created)
│   │   ├── schema.py               # Schema definition (✅ created)
│   │   ├── diagnostics.py          # Diagnostic tracking (✅ Phase 2A)
│   │   └── utils/                  # ID generator (✅), location parser, text cleaner (✅)
│   ├── generator/                  # Phase 3 - PENDING
│   └── scheduler.py                # Phase 4 - PENDING
│
├── tests/                          # Tests organized by phase
│   ├── setup-project/              # Phase 0 tests
│   ├── load-data-collection/       # Phase 1 tests
│   ├── transform-data-processing/  # Phase 2 tests (✅ Phase 2A component tests)
│   └── export-output-generation/   # Phase 3 tests (to be created)
│
├── templates/                      # HTML templates (Phase 3)
├── static/                         # CSS, JS, images (Phase 3)
│
└── conversation_cursor/            # Project management
    ├── dates/                      # Dated proposals
    ├── progress/latest.md         # High-level pipeline status
    ├── structure/latest.md         # This file - project structure
    └── to-do-list/                 # Detailed task lists
```

## Key Files & Modules

### Configuration
- **`data/config/scraping_sources.json`**: 176 accessible URLs across job portals, universities, research institutes
- **`data/config/scraping_rules.json`**: Scraping patterns (deadlines, keywords, date formats)
- **`data/config/processing_rules.json`**: Processing rules (job type keywords, specialization keywords, region mapping, materials parsing)

### Scraper Framework (Phase 1 - Complete)
- **`scripts/scraper/base_scraper.py`**: Abstract base class (fetch, parse, extract, save)
- **`scripts/scraper/aea_scraper.py`**: AEA JOE scraper (RSS/HTML fallback)
- **`scripts/scraper/university_scraper.py`**: Generic university scraper (pattern-based)
- **`scripts/scraper/institute_scraper.py`**: Research institute scraper
- **`scripts/scraper/parsers/`**: HTML, RSS, text extractor, date parser
- **`scripts/scraper/utils/`**: Rate limiter, retry handler, user agent, config loader

### Processor Framework (Phase 2 - In Progress)
- **`scripts/processor/pipeline.py`**: Main processing pipeline orchestrator
- **`scripts/processor/parser_manager.py`**: Routes raw data to parsers
- **`scripts/processor/normalizer.py`**: Normalizes dates, locations, formats, text
- **`scripts/processor/enricher.py`**: Enriches data (IDs, classifications, metadata)
- **`scripts/processor/deduplicator.py`**: Identifies and merges duplicate listings
- **`scripts/processor/validator.py`**: Validates data against schema (to be created)
- **`scripts/processor/diagnostics.py`**: Diagnostic tracking and root cause analysis ✅ Phase 2A
- **`scripts/processor/schema.py`**: Data schema definition (29 fields, validation functions) ✅
- **`scripts/processor/utils/`**: ID generator ✅, location parser (to be created), text cleaner ✅
- **`scripts/processor/pipeline.py`**: Main processing pipeline orchestrator ✅ Phase 2A
- **`scripts/processor/parser_manager.py`**: Routes raw data to parsers ✅ Phase 2A
- **`scripts/processor/normalizer.py`**: Basic data normalization ✅ Phase 2A

## Workflow

**Load → Transform → Export**
1. **LOAD (Phase 1 - ✅)**: Scrape raw HTML from sources
2. **TRANSFORM (Phase 2 - 🚀)**: Process, normalize, deduplicate, validate data
3. **EXPORT (Phase 3 - ⏸️)**: Generate HTML/JSON/CSV outputs
4. **DEPLOY (Phase 4 - ⏸️)**: Automation and hosting

## Environment

- **Python**: 3.13.5 (via Poetry)
- **Virtual Environment**: `./environment/python/venv/`
- **Run**: `poetry run python scripts/scraper/aea_scraper.py`
