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
│   │   ├── institutes/             # Research institute scraped files
│   │   └── documents/              # Downloaded documents (PDFs, Word, Excel, text files)
│   ├── processed/                  # Processed data (Phase 2 output)
│   │   ├── jobs.json               # Current listings
│   │   ├── jobs.csv                # Current listings (CSV)
│   │   ├── archive/                # Historical snapshots
│   │   └── diagnostics/            # Diagnostic reports
│   └── config/
│       ├── README.md               # Configuration guide with verification methodology
│       ├── scraping_sources.json   # ✅ FLAT structure: 127 accessible + 83 non-accessible = 210 entries
│       │                           # Format: {"accessible": [{"id": "...", "url": "...", "type": "...", ...}], "non_accessible": [...]}
│       ├── scraping_rules.json     # Scraping patterns
│       ├── processing_rules.json   # Processing rules
│       ├── url_replacements.json   # URL replacement patterns
│       └── url_verification/       # ✅ URL verification results and documentation
│           ├── README.md           # Folder documentation
│           └── verification_results.md  # Latest verification results summary
│
├── scripts/
│   ├── scraper/                    # Phase 1 - COMPLETE
│   │   ├── base_scraper.py         # Base scraper class
│   │   ├── aea_scraper.py          # AEA JOE scraper
│   │   ├── university_scraper.py   # University scraper
│   │   ├── institute_scraper.py    # Institute scraper
│   │   ├── parsers/                # HTML, RSS, text, date parsers
│   │   ├── utils/                  # Rate limiter, retry handler, user agent
│   │   └── config/                 # ✅ PHASE 1B - Configuration verification tools
│   │       ├── README.md                     # Documentation for verification tools
│   │       ├── url_access/                   # ✅ Task 0A - HTTP accessibility testing (COMPLETE)
│   │       │   ├── __init__.py               # Module exports
│   │       │   ├── test_accessibility.py     # ✅ HTTP connectivity testing
│   │       │   ├── redirect_handler.py       # ✅ Redirect following & chain tracking
│   │       │   ├── dns_resolver.py           # ✅ Chinese DNS fallback support
│   │       │   └── connectivity_report.py    # ✅ Generate accessibility reports
│   │       └── url_verification/             # Task 0B - Content validation (pending)
│   │           └── (to be implemented)       # Page classifier, content validator, quality scorer, etc.
│   ├── processor/                  # Phase 2 - ✅ COMPLETE
│   │   ├── pipeline.py            # Main pipeline (✅ Phase 2E - full integration with archive retention)
│   │   ├── parser_manager.py       # Route to parsers (✅ Phase 2A)
│   │   ├── normalizer.py           # Data normalization (✅ Phase 2B)
│   │   ├── enricher.py             # Data enrichment (✅ Phase 2B)
│   │   ├── deduplicator.py         # Deduplication (✅ Phase 2C)
│   │   ├── validator.py            # Data validation (✅ Phase 2D)
│   │   ├── schema.py               # Schema definition (✅ created)
│   │   ├── diagnostics.py          # Diagnostic tracking & reports (✅ Phase 2A, 2D)
│   │   └── utils/                  # ID generator (✅), location parser (✅), text cleaner (✅)
│   ├── generator/                  # Phase 3 - ✅ COMPLETE (MVP)
│   │   ├── __init__.py            # Generator module init (exports)
│   │   ├── build_site.py          # Static site builder (178 lines, CLI support)
│   │   └── template_renderer.py   # Jinja2 renderer with custom filters (313 lines + json_dumps)
│   └── scheduler.py                # Phase 4 - PENDING
│
├── tests/                          # Tests organized by phase
│   ├── setup-project/              # Phase 0 tests
│   ├── load-data-collection/       # Phase 1 tests
│   │   ├── README.md                       # Phase 1 test documentation
│   │   ├── config/                         # ✅ Configuration and URL verification tests
│   │   │   ├── test_scraping_sources.py    # Validate scraping sources config
│   │   │   ├── test_config_loader.py       # Test config loader utility
│   │   │   ├── url_access/                 # ✅ Task 0A - URL access verification tests
│   │   │   │   ├── test_accessibility.py   # Test HTTP connectivity
│   │   │   │   ├── test_redirects.py       # Test redirect following
│   │   │   │   └── test_connectivity_report.py  # Test report generation
│   │   │   └── url_verification/           # Task 0B - URL content validation tests (pending)
│   │   ├── scraper/                        # Scraper tests
│   │   ├── parser/                         # Parser tests
│   │   └── utils/                          # Utility tests
│   ├── transform-data-processing/  # Phase 2 tests
│   │   ├── parser/                 # Parser manager tests (✅ Phase 1 integration)
│   │   ├── utils/                  # Utility tests (✅ location parser, 41 tests)
│   │   ├── normalizer/             # Normalizer tests (✅ 28 tests, all passing)
│   │   ├── enricher/               # Enricher tests (✅ 24 tests, all passing)
│   │   ├── deduplicator/           # Deduplicator tests (✅ Phase 2C)
│   │   ├── validator/              # Validator tests (✅ Phase 2D, 26 tests)
│   │   └── integration/           # Integration tests (✅ Phase 2A components)
│   └── export-output-generation/   # Phase 3 tests (to be created)
│
├── templates/                      # HTML templates (Phase 3 - ✅ COMPLETE + specialization filter)
│   └── index.html.jinja           # Main page Jinja2 template (348 lines, all UI components + specialization filter)
├── static/                         # CSS, JS, images (Phase 3 - ✅ COMPLETE + specialization filter)
│   ├── index.html                 # Generated static page (✓ 25,448 insertions)
│   ├── css/
│   │   └── styles.css             # Responsive styles (mobile-first, 3 breakpoints)
│   ├── js/
│   │   ├── app.js                # Main app logic (355 lines, optimized - no debug logs)
│   │   ├── filters.js            # Filtering functionality (323 lines, optimized - no debug logs, 5 filter types)
│   │   └── search.js             # Search functionality (121 lines, optimized - no debug logs, debounced)
│   ├── data/
│   │   └── jobs.json             # Client-side data copy (211 listings with specializations)
│   └── images/                   # Icons, logos
│
└── conversation_cursor/            # Project management
    ├── dates/                      # Dated proposals
    ├── progress/latest.md         # High-level pipeline status
    ├── structure/latest.md         # This file - project structure
    └── to-do-list/                 # Detailed task lists

.github/                            # GitHub configuration
└── workflows/
    └── gh-pages.yml               # GitHub Pages workflow (✅ active, deploys /static)
```

## Key Files & Modules

### Configuration
- **`data/config/scraping_sources.json`**: 176+ accessible URLs across job portals (AEA JOE, HigherEdJobs, EconJobMarket, EJMR, AEA Scramble), universities, research institutes. **Rule**: Only URLs containing relevant job information should be in accessible section. **Status**: 81 URLs currently have issues (47 moved to non_accessible, 34 in non_accessible with issues) - see verification results. **Phase 1B Challenge**: Many URLs point to wrong page types (department pages, faculty directories) instead of actual career portals - requires URL discovery to find correct job pages. **IMPORTANT**: Only update URLs in `non_accessible` section - accessible URLs are working fine and should remain unchanged. Initial fixes completed for Chinese and international universities in non_accessible section; remaining URLs (US universities, etc.) to be fixed later.
- **`data/config/scraping_rules.json`**: Scraping patterns (deadlines, keywords, date formats)
- **`data/config/processing_rules.json`**: Processing rules (job type keywords, specialization keywords, region mapping, materials parsing)
- **`scripts/scraper/check_config/verify_urls.py`**: URL verification script that checks accessible and non_accessible URLs, verifies job content (keywords, links, PDFs), and moves invalid URLs to non_accessible section
- **`scripts/scraper/check_config/find_url_replacements.py`**: Helper script to find replacement URLs by testing common URL patterns (jobs.*, careers.*, etc.) for problematic universities
- **`data/config/URL_VERIFICATION.md`**: Documentation for URL verification process and common patterns

### Scraper Framework (Phase 1 - Complete, Phase 1B - In Progress)
- **`scripts/scraper/main.py`**: Main script to scrape all accessible sources (universities, institutes, AEA) with one command ✅
- **Phase 1B - Expand Sources** (🔄 In Progress): Expanding from 176 to 250+ URLs with better global coverage
- **`scripts/scraper/base_scraper.py`**: Abstract base class (fetch, parse, extract, save)
- **`scripts/scraper/aea_scraper.py`**: AEA JOE scraper (RSS/HTML fallback). **Phase 2F**: Immediate URL resolution ✅
- **`scripts/scraper/university_scraper.py`**: Generic university scraper (pattern-based, **link-following enabled** - automatically follows links to detail pages to extract full job information). **Phase 2F**: Enhanced requirements and materials extraction, always sets source_url, immediate URL resolution ✅
- **`scripts/scraper/institute_scraper.py`**: Research institute scraper (**link-following enabled** - automatically follows links to detail pages). **Phase 2F**: Always sets source_url, immediate URL resolution ✅
- **`scripts/scraper/parsers/html_parser.py`**: HTML parser with **immediate URL resolution** - extract_links() resolves relative URLs to absolute URLs immediately using base_url parameter ✅
- **`scripts/scraper/parsers/`**: HTML, RSS, text extractor, date parser
- **`scripts/scraper/utils/`**: Rate limiter, retry handler, user agent, config loader

### Processor Framework (Phase 2 - ✅ Complete)
- **`scripts/processor/pipeline.py`**: Main processing pipeline orchestrator (full workflow: parse → normalize → enrich → deduplicate → validate → diagnostics, JSON/CSV output, archive with retention)
- **`scripts/processor/parser_manager.py`**: Routes raw data to parsers ✅ Phase 2A. **Phase 2F**: Base URL lookup from config (with partial name matching), ensures source fields always set, enhanced file reading with chardet ✅
- **`scripts/processor/normalizer.py`**: Normalizes dates, locations, formats, text, job types, departments, contact info, materials ✅ Phase 2B. **Phase 2F**: Enhanced URL resolution with base URLs from parser manager (highest priority), relative URL resolution with fallbacks, better handling of relative URLs with/without leading `/` ✅
- **`scripts/processor/enricher.py`**: Enriches data (IDs, classifications, metadata, specializations) ✅ Phase 2B. **Phase 2F**: Sets default values for optional fields ✅
- **`scripts/processor/deduplicator.py`**: Identifies and merges duplicate listings (fuzzy matching, merge logic, new/active detection) ✅ Phase 2C
- **`scripts/processor/validator.py`**: Validates data against schema (schema validation, date/URL validation, completeness/quality/consistency checks, batch validation) ✅ Phase 2D. **Phase 2F**: Tiered validation - optional fields treated as warnings instead of critical errors ✅
- **`scripts/processor/diagnostics.py`**: Diagnostic tracking and root cause analysis ✅ Phase 2A, report generation (root cause analysis, category statistics, JSON/text output, file saving) ✅ Phase 2D
- **`scripts/processor/schema.py`**: Data schema definition (29 fields, validation functions) ✅. **Phase 2F**: Moved non-critical fields (deadline, description, requirements, specializations, application_link, materials_required) to optional ✅
- **`scripts/processor/utils/`**: ID generator ✅, location parser ✅, text cleaner ✅
- **`scripts/processor/pipeline.py`**: Main processing pipeline orchestrator ✅ Phase 2A
- **`scripts/processor/parser_manager.py`**: Routes raw data to parsers ✅ Phase 2A (Phase 1 integration complete)
- **`scripts/processor/normalizer.py`**: Basic data normalization ✅ Phase 2A

## Workflow

**Load → Transform → Export**
1. **LOAD**:
   - **Phase 1 (✅)**: Scrape raw HTML from sources (176 URLs)
   - **Phase 1B (🔄)**: Expand sources to 250+ URLs with better global coverage
2. **TRANSFORM (Phase 2 - ✅)**: Process, normalize, deduplicate, validate data (complete pipeline with archive retention)
3. **EXPORT (Phase 3 - ✅)**: Generate static webpage with filters, search, and responsive design (static/index.html, styles.css, app.js, filters.js, search.js)
4. **DEPLOY (Phase 4 - ⏸️)**: Automation and hosting (GitHub Pages)

## Environment

- **Python**: 3.13.5 (via Poetry)
- **Virtual Environment**: `./environment/python/venv/`
- **Run**: `poetry run python scripts/scraper/aea_scraper.py`
