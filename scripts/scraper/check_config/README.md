# Configuration Verification Tools

Tools for verifying and maintaining scraping sources configuration.

## Structure

```
check_config/
├── README.md                    # This file
├── url_access/                  # ✅ Task 0A - HTTP accessibility testing (COMPLETE)
│   ├── __init__.py
│   ├── test_accessibility.py   # HTTP connectivity testing
│   ├── redirect_handler.py     # Redirect following & chain tracking
│   ├── dns_resolver.py         # Chinese DNS fallback support
│   └── connectivity_report.py  # Generate accessibility reports
└── url_verification/            # Task 0B - Content validation (pending)
    └── (to be implemented)
```

## Task 0A: URL Access Verification (✅ COMPLETE)

### test_accessibility.py
Tests HTTP connectivity with rate limiting and timeout detection.

**Key Functions**:
- `test_accessibility(url, timeout=10)` - Test HTTP GET with error categorization
- `is_accessible(url)` - Quick boolean check

**Features**:
- Rate limiting (1+ second between requests)
- Error categorization (404, 403, timeout, SSL, connection errors)
- Response time tracking

### redirect_handler.py
Follows and tracks redirect chains.

**Key Functions**:
- `follow_redirects(url, max_redirects=5)` - Follow redirect chain
- `record_redirect_chain(url)` - Alias for clearer intent

**Features**:
- Max 5 redirect hops
- Redirect loop detection
- External HR system identification (ICIMS, Workday, PeopleSoft, etc.)

### dns_resolver.py
Chinese DNS fallback for Great Firewall bypass.

**Key Functions**:
- `resolve_with_chinese_dns(hostname)` - Try Chinese DNS servers
- `test_with_alternative_dns(url)` - Test URL with alternative DNS

**Features**:
- Fallback servers: Alidns, DNSPod, Tencent
- System DNS first, then Chinese servers

### connectivity_report.py
Generate comprehensive accessibility reports.

**Key Functions**:
- `generate_accessibility_report(sources_json_path, output_dir, output_formats=['json', 'markdown'])`

**Features**:
- Multiple output formats (JSON, CSV, Markdown)
- Grouping by region, category, error type
- Integration with scraping_sources.json

**Usage**:
```python
from scripts.scraper.check_config.url_access import generate_accessibility_report

report = generate_accessibility_report(
    "data/config/scraping_sources.json",
    "data/config/url_verification"
)
```

## Task 0B: URL Verification (Pending)

Content validation tools will be implemented in `url_verification/`:
- Page type classification
- URL discovery for career portals
- Job content extraction and validation
- Quality scoring (0-100)
- Decision engine for accessible/non_accessible classification

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

