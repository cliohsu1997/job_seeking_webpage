# Structure: Project Organization

## Project Structure Overview

```
job-seeking-webpage/
├── read_it.md                      # Project guidelines (read first - contains workflow rules)
├── pyproject.toml                  # Poetry configuration and dependencies
├── poetry.lock                     # Poetry lock file (dependency versions)
├── README.md                       # Project documentation
│
├── data/                           # Data storage
│   ├── raw/                        # Raw scraped data (latest only, overwrites daily)
│   │   ├── aea/                    # AEA JOE scraped HTML files
│   │   ├── universities/           # University scraped HTML files
│   │   ├── institutes/             # Research institutes scraped HTML files
│   │   └── samples/                # Sample HTML files (176 files) for parsing analysis
│   ├── processed/                  # Cleaned, structured data (to be generated in Phase 2)
│   │   ├── jobs.json               # Current listings (not in git)
│   │   ├── jobs.csv                # Current listings (not in git)
│   │   └── archive/                # Historical processed data
│   └── config/                     # Configuration files
│       ├── scraping_sources.json   # All scraping sources (171 accessible, 79 non-accessible URLs)
│       └── scraping_rules.json     # Scraping patterns and rules (deadlines, keywords, date formats)
│
├── scripts/                        # Automation scripts
│   ├── scraper/                    # Web scraping modules (Phase 1 - COMPLETE)
│   │   ├── base_scraper.py         # Abstract base class for all scrapers (fetch, parse, extract, save)
│   │   ├── aea_scraper.py          # AEA JOE scraper (RSS/HTML fallback)
│   │   ├── university_scraper.py   # Generic university scraper (pattern-based extraction)
│   │   ├── institute_scraper.py    # Research institute/think tank scraper
│   │   ├── download_samples.py     # Downloads sample HTML files from all accessible URLs
│   │   ├── utils/                  # Utility modules
│   │   │   ├── config_loader.py    # Load/filter/save scraping_sources.json config
│   │   │   ├── rate_limiter.py     # Rate limiting between requests
│   │   │   ├── retry_handler.py    # Retry logic with exponential backoff
│   │   │   └── user_agent.py       # User agent rotation for requests
│   │   ├── parsers/                # Parsing modules
│   │   │   ├── html_parser.py      # HTML parsing with hybrid extraction (pattern + class-based)
│   │   │   ├── rss_parser.py       # RSS/Atom feed parsing
│   │   │   ├── text_extractor.py   # Text extraction and cleaning utilities
│   │   │   └── date_parser.py      # Date parsing with multiple format support
│   │   └── check_config/           # Configuration verification scripts
│   │       ├── verify_urls.py      # Verify URLs in non_accessible section, move to accessible when verified
│   │       └── migrate_config_structure.py  # One-time migration script (historical)
│   ├── processor/                  # Data processing modules (Phase 2 - PENDING)
│   ├── generator/                  # Output generation modules (Phase 3 - PENDING)
│   └── scheduler.py                # Main scheduler (Phase 4 - PENDING)
│
├── tests/                          # Test files organized by phase
│   ├── setup-project/              # Phase 0 tests
│   ├── load-data-collection/       # Phase 1 tests
│   │   └── test_scrapers.py        # Tests for scraper utilities and parsers
│   ├── transform-data-processing/  # Phase 2 tests (to be created)
│   └── export-output-generation/   # Phase 3 tests (to be created)
│
├── templates/                      # HTML templates (Phase 3 - PENDING)
├── static/                         # Static web assets (Phase 3 - PENDING)
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript files
│   └── images/                     # Image assets
│
├── environment/                    # Environment management
│   ├── python/
│   │   ├── tools/                  # Poetry configs (source of truth)
│   │   │   ├── poetry.lock         # Dependency lock file
│   │   │   ├── pyproject.toml      # Poetry configuration
│   │   │   └── README.md           # Tools documentation
│   │   └── venv/                   # Virtual environment (managed by Poetry)
│   └── README.md                   # Environment documentation
│
└── conversation_cursor/            # Project management and documentation
    ├── dates/                      # Dated conversation records and proposals
    ├── progress/
    │   └── latest.md               # High-level pipeline status (what's done, what's next)
    ├── structure/
    │   └── latest.md               # This file - project structure documentation
    └── to-do-list/                 # Explicit task lists (one per phase)
        ├── 2025-12-31_project-setup.md
        └── 2025-12-31_load-data-collection.md
```

## File Summaries

### Core Configuration Files

**`read_it.md`**
- Project guidelines and workflow rules
- Environment setup instructions
- Coding standards and conventions
- **Must read first** before starting any work

**`data/config/scraping_sources.json`**
- Master configuration for all scraping sources
- Organized by accessibility: `accessible` / `non_accessible` top-level categories
- Contains 171 accessible URLs across job portals, universities, and research institutes
- Each entry includes: institution name, department(s), URL(s), scraping method, notes

**`data/config/scraping_rules.json`**
- Scraping patterns and rules
- Deadline keywords, application link keywords, material keywords
- Date format definitions

### Scraper Framework (Phase 1 - Complete)

**`scripts/scraper/base_scraper.py`**
- Abstract base class for all scrapers with common interface (fetch, parse, extract, save)

**`scripts/scraper/aea_scraper.py`**
- AEA JOE scraper (checks RSS feed first, falls back to HTML scraping)

**`scripts/scraper/university_scraper.py`**
- Generic university scraper using pattern-based extraction

**`scripts/scraper/institute_scraper.py`**
- Research institute and think tank scraper

### Scraper Utilities

**`scripts/scraper/utils/config_loader.py`**
- Load and filter `scraping_sources.json` configuration

**`scripts/scraper/utils/rate_limiter.py`**
- Enforces delays between HTTP requests
- Prevents rate limiting and blocking

**`scripts/scraper/utils/retry_handler.py`**
- Retry logic with exponential backoff
- Handles transient errors gracefully

**`scripts/scraper/utils/user_agent.py`**
- Rotates user agents for requests
- Reduces detection risk

### Parser Modules

**`scripts/scraper/parsers/html_parser.py`**
- HTML parsing using BeautifulSoup with hybrid extraction (pattern + class-based)

**`scripts/scraper/parsers/rss_parser.py`**
- Parses RSS and Atom XML feeds (auto-detects feed type)

**`scripts/scraper/parsers/text_extractor.py`**
- Text extraction and cleaning utilities

**`scripts/scraper/parsers/date_parser.py`**
- Flexible date parsing with multiple format support

### Configuration Management Scripts

**`scripts/scraper/download_samples.py`**
- Downloads sample HTML files from all accessible URLs for analysis

**`scripts/scraper/check_config/verify_urls.py`**
- Verifies URLs and updates config (moves verified URLs from non_accessible to accessible)

**`scripts/scraper/check_config/migrate_config_structure.py`**
- One-time migration script (historical)
- Migrated config from url_status field to accessible/non_accessible structure

### Testing

**`tests/load-data-collection/test_scrapers.py`**
- Unit tests for scraper utilities and parsers
- Tests: rate limiter, user agent rotator, text extractor, date parser, HTML parser

### Project Management

**`conversation_cursor/progress/latest.md`**
- High-level pipeline status
- What's been accomplished, what's next
- Phase completion status

**`conversation_cursor/to-do-list/YYYY-MM-DD_phase-name.md`**
- Detailed task lists for each phase
- Checkboxes for tracking progress
- One file per phase

**`conversation_cursor/structure/latest.md`**
- This file - project structure documentation
- File summaries and organization

## Environment Management

**Tool**: Poetry
- **Python**: `C:\Users\clioh\AppData\Local\Programs\Python\Python313\python.exe` (3.13.5)
- **Virtual environment**: `./environment/python/venv/` (managed by Poetry)
- **Configuration source of truth**: `./environment/python/tools/` (poetry.lock, pyproject.toml)
- **Root pyproject.toml**: Required by Poetry, but tools/ version is authoritative

**Run Python scripts**:
```bash
poetry run python scripts/scraper/aea_scraper.py
```

## Workflow Structure

Follows **Load → Transform → Export** pattern:
1. **LOAD (Phase 1 - ✅ Complete)**: Scrape raw HTML from sources
2. **TRANSFORM (Phase 2 - Pending)**: Process and normalize data
3. **EXPORT (Phase 3 - Pending)**: Generate HTML/JSON/CSV outputs
4. **DEPLOY (Phase 4 - Pending)**: Automation and hosting

## Current Status

✅ **Phase 1 (LOAD)**: Complete - Scraper framework implemented
⏸️ **Phase 2 (TRANSFORM)**: Ready to begin
⏸️ **Phase 3 (EXPORT)**: Pending
⏸️ **Phase 4 (DEPLOY)**: Pending
