# To-Do List: 2025-12-31 - Load Data Collection

**Corresponds to**: Phase 1: LOAD - Data Collection in `conversation_cursor/progress/latest.md`

## Phase 1: LOAD - Data Collection Tasks

### Strategy & Planning
- [x] Created scraping strategy proposal (`design-scraping-strategy.md`)
- [x] Defined information to scrape (data fields and schema)
- [x] Determined coverage strategy (QS rankings, Economics priority, multiple departments)
- [x] Created `scraping_sources.json` structure for organizing sources
- [x] Updated project structure documentation

### Configuration Setup
- [x] Created configuration helper documentation (`data/config/README.md`)
- [x] Populated `scraping_sources.json` with initial examples (structure established)
  - [x] Added 5 top US universities (Harvard, MIT, Stanford, Chicago, Princeton)
  - [x] Added 2 UK universities (LSE, Oxford)
  - [x] Added 1 Canadian university (Toronto)
  - [x] Added 1 Australian university (Melbourne)
  - [x] Added NBER (US research institute)
  - [x] Added CEPR (UK research institute)
  - [x] Established entry structure with departments array
- [x] Created URL verification script (`scripts/scraper/check_config/verify_urls.py`)
- [x] Organized configuration verification scripts in `scripts/scraper/check_config/` subfolder
- [ ] Verify all URLs in initial entries (see `data/config/URL_VERIFICATION.md`)
- [ ] Compile remaining university lists from QS Economics & Econometrics rankings
  - [ ] Mainland China: Top 100 universities (start with top 20)
  - [ ] United States: Expand to top 100 universities (currently 5)
  - [ ] Other Countries: Expand to top 30 per country (currently 1-2 each)
- [ ] Identify additional research institutes and think tanks to include
  - [ ] US: Federal Reserve Banks, additional research institutes
  - [ ] International: IZA, additional institutes
- [ ] Complete `scraping_sources.json` population
  - [ ] Verify and update all department URLs
  - [ ] Handle multiple campuses separately if different posting pages
  - [ ] Document scraping methods and special considerations
- [ ] Update `scraping_rules.json` with additional patterns if needed

### Environment Setup
- [x] Installed all dependencies via Poetry (`poetry install` - 32 packages)
- [x] Updated `read_it.md` with dependency installation and update instructions
- [x] Virtual environment created and configured

### HTML Parsing Approach Analysis
- [x] Created sample download script (`scripts/scraper/download_samples.py`)
- [ ] Download sample HTML files from diverse sources
  - [ ] AEA JOE job listings page
  - [ ] Sample university job posting pages (different structures)
  - [ ] Research institute job pages
  - [ ] Save samples to `data/raw/samples/` for analysis
- [ ] Analyze HTML structures to compare parsing approaches
  - [ ] **Method 1: Class-based extraction** - Assign different CSS classes to HTML elements and extract by class
    - Evaluate efficiency and reliability
    - Assess one-time setup requirements
  - [ ] **Method 2: Pattern-based extraction** - Brute force finding common patterns in HTML
    - Evaluate flexibility and reliability
    - Assess maintenance requirements
- [ ] Document findings and determine optimal approach
  - [ ] Compare efficiency of both methods
  - [ ] Decide on primary approach (or hybrid)
  - [ ] Document decision rationale

### Base Scraper Framework
- [ ] Create base scraper abstract class (`scripts/scraper/base_scraper.py`)
  - [ ] Define common interface (fetch, parse, extract, save)
  - [ ] Implement rate limiting and retry logic
  - [ ] Add error handling and logging
  - [ ] Implement User-Agent rotation
- [ ] Create utility modules
  - [ ] `scripts/scraper/utils/rate_limiter.py` - Rate limiting and delays
  - [ ] `scripts/scraper/utils/retry_handler.py` - Retry logic with exponential backoff
  - [ ] `scripts/scraper/utils/user_agent.py` - User agent rotation
- [ ] Create parser modules (based on analysis findings)
  - [ ] `scripts/scraper/parsers/html_parser.py` - HTML parsing utilities (class-based or pattern-based)
  - [ ] `scripts/scraper/parsers/rss_parser.py` - RSS/XML feed parser
  - [ ] `scripts/scraper/parsers/text_extractor.py` - Text extraction and cleaning
  - [ ] `scripts/scraper/parsers/date_parser.py` - Date parsing with multiple formats

### AEA JOE Scraper (Priority)
- [ ] Create `scripts/scraper/aea_scraper.py`
  - [ ] Implement AEA JOE scraper class
  - [ ] Check for RSS/XML feed availability
  - [ ] Implement HTML scraping fallback
  - [ ] Handle pagination if needed
  - [ ] Extract job listings with all required fields
- [ ] Test AEA scraper
  - [ ] Validate data extraction
  - [ ] Test error handling
  - [ ] Verify rate limiting
- [ ] Save raw data to `data/raw/aea/listings.html`

### University Scraper
- [ ] Create `scripts/scraper/university_scraper.py`
  - [ ] Implement generic university scraper
  - [ ] Support multiple URL patterns per university
  - [ ] Handle multiple departments (Economics, Management, Marketing)
  - [ ] Support multiple campuses with separate postings
  - [ ] Implement pattern-based extraction
  - [ ] Support university-specific parsers
- [ ] Test with initial set of universities (top 10-20 per region)
- [ ] Refine parsers based on test results
- [ ] Save raw data to `data/raw/universities/{institution_name}.html`

### Research Institute & Think Tank Scraper
- [ ] Create `scripts/scraper/institute_scraper.py`
  - [ ] Implement scraper for research institutes
  - [ ] Implement scraper for think tanks
  - [ ] Handle different posting formats
- [ ] Test with initial set of institutes
- [ ] Save raw data to `data/raw/institutes/{institution_name}.html`

### Multi-Language Support
- [ ] Research Chinese language parsing requirements
- [ ] Implement Chinese text extraction if needed
- [ ] Test with mainland China universities
- [ ] Plan for other languages (if needed for Phase 1)

### Data Validation & Quality
- [ ] Implement data validation for extracted fields
- [ ] Create validation rules for required fields
- [ ] Flag incomplete entries
- [ ] Log validation results

### Testing
- [ ] Create test files in `tests/load-data-collection/`
  - [ ] Test base scraper functionality
  - [ ] Test AEA scraper
  - [ ] Test university scraper with sample universities
  - [ ] Test error handling and retry logic
  - [ ] Test rate limiting
- [ ] Run integration tests
- [ ] Validate extracted data quality

### Documentation
- [ ] Document scraper usage
- [ ] Document how to add new sources to `scraping_sources.json`
- [ ] Document scraping methods and patterns
- [ ] Update README with scraping information

### Incremental Expansion
- [ ] Start with top 20-30 universities per region
- [ ] Expand to top 50
- [ ] Expand to full coverage (top 100 for mainland/US, top 30 for others)
- [ ] Add more research institutes and think tanks incrementally

## Phase 1 Status: 🔄 IN PROGRESS

**Current Focus**: HTML parsing approach analysis

**Next Steps**:
1. Download sample HTML files from diverse sources (AEA JOE, universities, research institutes)
2. Analyze HTML structures to compare parsing approaches (class-based vs pattern-based)
3. Choose optimal parsing approach and document decision
4. Create base scraper framework using chosen approach
5. Implement AEA JOE scraper (priority)

