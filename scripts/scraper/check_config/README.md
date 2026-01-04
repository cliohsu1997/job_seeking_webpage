# Configuration Verification Tools

Tools for verifying and maintaining scraping sources configuration.

## Current Scripts

### verify_urls.py
**Purpose**: Test all URLs in `data/config/scraping_sources.json` for accessibility and job content

**Functionality**:
- Tests HTTP accessibility (200 OK, 404, 403, timeouts, DNS errors)
- Verifies job content presence (keywords, links, PDFs)
- Moves invalid URLs to non_accessible section
- Updates `scraping_sources.json` with verification results

**Usage**:
```bash
poetry run python scripts/scraper/check_config/verify_urls.py
```

**Output**: 
- Updates `data/config/scraping_sources.json` (accessible/non_accessible sections)
- Prints verification summary to console

### find_url_replacements.py
**Purpose**: Find replacement URLs for broken sources by testing common URL patterns

**Functionality**:
- Tests alternative URL patterns (jobs.*, careers.*, hr.*, etc.)
- Ranks alternatives by confidence and test results
- Helps identify better URLs for problematic sources

**Usage**:
```bash
poetry run python scripts/scraper/check_config/find_url_replacements.py
```

## Phase 1B Enhancement Folders

### url_access/
**Purpose**: Separate tools for testing HTTP connectivity (Task 0A)

**Future Files**:
- `test_accessibility.py` - HTTP connectivity testing
- `redirect_handler.py` - Redirect following & chain tracking
- `dns_resolver.py` - Chinese DNS fallback support
- `connectivity_report.py` - Generate accessibility reports

### url_verification/
**Purpose**: Separate tools for content validation (Task 0B)

**Future Files**:
- `page_classifier.py` - Classify page type (career portal vs department)
- `url_discoverer.py` - Discover alternative career portal URLs
- `content_validator.py` - Extract & validate job content
- `quality_scorer.py` - Score content quality (0-100)
- `decision_engine.py` - Full validation decision tree
- `batch_processor.py` - Batch validation & configuration update

## Configuration Files

See `data/config/` for:
- `scraping_sources.json` - Main configuration (accessible and non_accessible URLs)
- `scraping_rules.json` - Scraping patterns
- `processing_rules.json` - Processing rules
- `url_verification/` - Verification documentation and results

