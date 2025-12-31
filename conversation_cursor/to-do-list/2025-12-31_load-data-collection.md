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
- [x] Updated verification script to add url_status labels directly to `scraping_sources.json`
- [x] Verified all URLs in initial entries (20/20 accessible, all marked with url_status="accessible")
- [x] Deleted deprecated files (universities.json, url_verification_results.json)
- [x] Compiled comprehensive university lists from QS Economics & Econometrics rankings
  - [x] Mainland China: 100 universities added to scraping_sources.json
  - [x] United States: Expanded to ~60 universities (target: 100)
  - [x] Other Countries: Expanded coverage - UK (5), Canada (4), Australia (20), added Germany (2), France (1), Netherlands (2), Singapore (2), Switzerland (1)
- [x] Identified and added additional research institutes and think tanks
  - [x] US: Federal Reserve Banks (NY, San Francisco, Chicago), Brookings Institution, PIIE
  - [x] International: IZA (Germany)
- [x] Completed major `scraping_sources.json` population
  - [x] Added ~200+ university entries across all regions
  - [x] Verified and updated department URLs (113/139 accessible, 81% success rate)
  - [x] Fixed 40 problematic URLs with alternative paths
  - [x] All URLs marked with url_status (accessible, not_found, forbidden, error, pending_verification)
  - [x] Handled multiple departments per university (Economics, Management, Marketing)
- [x] Enhanced URL verification script with Chinese keyword detection (18 Chinese job-related keywords: 招聘, 职位, 岗位, 人才, etc.)
- [x] Updated verification script to re-check Chinese URLs for keyword detection
- [x] Completed Chinese university URL verification with improved keyword detection
  - [x] 58 Chinese university URLs newly verified
  - [x] Many Chinese URLs now properly detect Chinese job-related keywords (招聘, 岗位, 人才, 工作, 人才招聘, etc.)
  - [x] Final status: 172/250 URLs accessible (69% success rate)
- [ ] Update `scraping_rules.json` with additional patterns if needed

### Environment Setup
- [x] Installed all dependencies via Poetry (`poetry install` - 32 packages)
- [x] Updated `read_it.md` with dependency installation and update instructions
- [x] Virtual environment created and configured

### HTML Parsing Approach Analysis
- [x] Created sample download script (`scripts/scraper/download_samples.py`)
- [x] Updated download script to read from scraping_sources.json (extracts all accessible URLs automatically)
- [ ] Download sample HTML files from diverse sources (113 accessible URLs ready)
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

**Current Focus**: Complete URL verification, then HTML parsing approach analysis

**Next Steps**:
1. Complete Chinese university URL verification (100+ URLs with pending_verification status)
2. Download sample HTML files from diverse sources (113 accessible URLs ready, more after Chinese verification)
3. Analyze HTML structures to compare parsing approaches (class-based vs pattern-based)
4. Choose optimal parsing approach and document decision
5. Create base scraper framework using chosen approach
6. Implement AEA JOE scraper (priority)

