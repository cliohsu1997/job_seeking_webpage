# Test Suite: Phase 1 - LOAD (Data Collection)

Tests for data collection phase including scrapers, parsers, configuration validation, and URL verification.

## Structure

```
load-data-collection/
├── README.md                    # This file
├── config/                      # Configuration and URL verification tests
│   ├── test_scraping_sources.py      # Validate scraping_sources.json structure
│   ├── test_config_loader.py         # Test config loader utility
│   ├── url_access/                   # Task 0A - URL access verification tests
│   │   ├── test_accessibility.py
│   │   ├── test_redirects.py
│   │   └── test_connectivity_report.py
│   └── url_verification/             # Task 0B - URL content validation tests (pending)
├── scraper/                     # Scraper tests
├── parser/                      # Parser tests
└── utils/                       # Utility tests
```

## Run Tests

### All Configuration Tests
```bash
poetry run python -m pytest tests/load-data-collection/config/
```

### URL Access Verification Tests
```bash
poetry run python -m pytest tests/load-data-collection/config/url_access/
```

### Specific Test Files
```bash
# Test scraping sources config validation
poetry run python -m pytest tests/load-data-collection/config/test_scraping_sources.py

# Test HTTP accessibility
poetry run python -m pytest tests/load-data-collection/config/url_access/test_accessibility.py

# Test redirect handling
poetry run python -m pytest tests/load-data-collection/config/url_access/test_redirects.py

# Test report generation
poetry run python -m pytest tests/load-data-collection/config/url_access/test_connectivity_report.py
```

### Other Test Categories
```bash
# Scraper tests
poetry run python -m pytest tests/load-data-collection/scraper/

# Parser tests
poetry run python -m pytest tests/load-data-collection/parser/

# Utils tests
poetry run python -m pytest tests/load-data-collection/utils/
```

## Test Coverage

### ✅ Configuration Tests (COMPLETE)
- Scraping sources structure validation
- URL format validation
- Config loader functionality

### ✅ URL Access Verification Tests (COMPLETE - Task 0A)
- HTTP connectivity testing with real sources
- Redirect chain tracking
- Accessibility report generation

### ⏸️ URL Content Validation Tests (PENDING - Task 0B)
- Page type classification
- Job content extraction
- Quality scoring

## Status

✅ Configuration and URL access verification tests complete
⏸️ URL content validation tests pending (Task 0B)
