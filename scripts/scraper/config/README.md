# Configuration Verification Tools

Tools for verifying and maintaining scraping sources in the 3-category structure (accessible_verified, accessible_unverified, potential_links).

## Structure

```
config/
├── README.md                       # This file
├── migrate_config_structure.py     # Legacy one-time migration script (keep for history)
├── url_access/                     # ✅ Task 0A - HTTP accessibility testing (COMPLETE)
│   ├── __init__.py
│   ├── test_accessibility.py       # HTTP connectivity testing
│   ├── redirect_handler.py         # Redirect following & chain tracking
│   ├── dns_resolver.py             # Chinese DNS fallback support
│   └── connectivity_report.py      # Generate accessibility reports
└── url_verification/               # ✅ Task 0B - Content validation (COMPLETE)
    ├── __init__.py
    ├── content_validator.py        # Extract & validate job listings
    ├── page_classifier.py          # Classify page types
    ├── quality_scorer.py           # Score content quality (0-100)
    └── decision_engine.py          # Validation decision tree + suggestions
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
from scripts.scraper.config.url_access import generate_accessibility_report

report = generate_accessibility_report(
    "data/config/scraping_sources.json",
    "data/config/url_verification"
)
```

## Task 0B: URL Verification (✅ COMPLETE)

Content validation implemented in `url_verification/`:
- Page type classification
- Job content extraction and validation
- Quality scoring (0-100)
- Decision engine for category decisions and suggestions

## Configuration Files

See `data/config/` for:
- `scraping_sources.json` - Main configuration (3-category flat list)
- `scraping_rules.json` - Scraping patterns
- `processing_rules.json` - Processing rules
- `url_verification/` - Verification documentation and results

