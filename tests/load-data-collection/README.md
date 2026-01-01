# Test Suite

Tests for Phase 1: LOAD - Data Collection.

## Run Tests

```bash
# All tests
poetry run python tests/load-data-collection/test_scrapers.py

# By category
poetry run python -m pytest tests/load-data-collection/scraper/
poetry run python -m pytest tests/load-data-collection/parser/
poetry run python -m pytest tests/load-data-collection/utils/
poetry run python -m pytest tests/load-data-collection/configuration/
```

## Organization

- **scraper/**: Base, AEA, University, Institute scrapers
- **parser/**: HTML, RSS, text extractor, date parser
- **configuration/**: Config loader
- **utils/**: Rate limiter, retry handler, user agent

## Status

✅ 61 tests passing (parser tests working)  
⚠️ Some scraper/utils tests need import path fixes (can run individually)
