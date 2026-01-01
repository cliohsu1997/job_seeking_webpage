# Load Data Collection Tests

Test suite for Phase 1: LOAD - Data Collection components.

## Test Organization

Tests are organized into subfolders by category:

### 📁 scraper/
Tests for scraper classes:
- `test_base_scraper.py` - Base scraper abstract class
- `test_aea_scraper.py` - AEA JOE scraper
- `test_university_scraper.py` - University scraper
- `test_institute_scraper.py` - Research institute scraper

### 📁 parser/
Tests for parser modules:
- `test_html_parser.py` - HTML parsing with BeautifulSoup
- `test_rss_parser.py` - RSS/Atom feed parsing
- `test_text_extractor.py` - Text extraction and cleaning utilities
- `test_date_parser.py` - Date parsing and deadline extraction

### 📁 configuration/
Tests for configuration utilities:
- `test_config_loader.py` - Configuration loading and filtering

### 📁 utils/
Tests for utility modules:
- `test_rate_limiter.py` - Rate limiting functionality
- `test_retry_handler.py` - Retry logic with exponential backoff
- `test_user_agent.py` - User agent rotation

## Running Tests

### Run All Tests
```bash
poetry run python -m pytest tests/load-data-collection/
# or
poetry run python tests/load-data-collection/test_scrapers.py
```

### Run Tests by Category
```bash
# Scraper tests
poetry run python -m pytest tests/load-data-collection/scraper/

# Parser tests
poetry run python -m pytest tests/load-data-collection/parser/

# Configuration tests
poetry run python -m pytest tests/load-data-collection/configuration/

# Utils tests
poetry run python -m pytest tests/load-data-collection/utils/
```

### Run Individual Test Files
```bash
poetry run python tests/load-data-collection/scraper/test_base_scraper.py
poetry run python tests/load-data-collection/parser/test_html_parser.py
# etc.
```

## Test Structure

Each test file:
- Tests its component independently
- Includes multiple test cases covering edge cases
- Uses mocking where appropriate (for HTTP requests, file I/O)
- Can be run individually or as part of the full suite

