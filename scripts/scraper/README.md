# Scraper Documentation

This directory contains the web scraping framework for collecting economics faculty job listings from various sources.

## Overview

The scraper framework follows a modular design with:
- **Base Scraper**: Abstract base class providing common functionality
- **Specialized Scrapers**: AEA, University, and Institute scrapers
- **Parsers**: HTML, RSS, text extraction, and date parsing utilities
- **Utilities**: Rate limiting, retry handling, and user agent rotation

## Architecture

```
scripts/scraper/
├── base_scraper.py          # Abstract base class for all scrapers
├── aea_scraper.py           # AEA JOE scraper (RSS/HTML fallback)
├── university_scraper.py    # Generic university scraper
├── institute_scraper.py     # Research institute scraper
├── parsers/                 # Parsing modules
│   ├── html_parser.py      # HTML parsing with BeautifulSoup
│   ├── rss_parser.py       # RSS/Atom feed parsing
│   ├── text_extractor.py  # Text extraction and cleaning
│   └── date_parser.py      # Date parsing utilities
├── utils/                   # Utility modules
│   ├── rate_limiter.py     # Rate limiting between requests
│   ├── retry_handler.py    # Retry logic with exponential backoff
│   ├── user_agent.py      # User agent rotation
│   └── config_loader.py   # Configuration loading utilities
└── check_config/           # Configuration management
    ├── verify_urls.py      # URL verification script
    └── migrate_config_structure.py  # Config migration (historical)
```

## Usage

### Basic Scraper Usage

#### AEA JOE Scraper

```python
from scripts.scraper.aea_scraper import AEAScraper

# Initialize scraper
scraper = AEAScraper()

# Scrape job listings (checks RSS first, falls back to HTML)
listings = scraper.scrape()

# Or scrape from specific URL
listings = scraper.extract("https://www.aeaweb.org/joe/listings.php", save_raw=True)
```

#### University Scraper

```python
from scripts.scraper.university_scraper import UniversityScraper

# Initialize for a specific university
scraper = UniversityScraper(
    university_name="Harvard University",
    url="https://economics.harvard.edu/faculty/positions",
    department="Economics"
)

# Scrape job listings
listings = scraper.scrape()
```

#### Institute Scraper

```python
from scripts.scraper.institute_scraper import InstituteScraper

# Initialize for a research institute
scraper = InstituteScraper(
    institute_name="NBER",
    url="https://www.nber.org/careers"
)

# Scrape job listings
listings = scraper.scrape()
```

### Scraping All Sources

```python
from scripts.scraper.university_scraper import scrape_all_universities
from scripts.scraper.institute_scraper import scrape_all_institutes

# Scrape all universities from configuration
all_university_listings = scrape_all_universities()

# Scrape all research institutes
all_institute_listings = scrape_all_institutes()
```

### Using Parsers Directly

#### HTML Parser

```python
from scripts.scraper.parsers.html_parser import HTMLParser

html_content = "<html>...</html>"
parser = HTMLParser(html_content)

# Extract by CSS selector
title = parser.select_one("h1.title")

# Extract all matching elements
items = parser.select_all(".job-listing")

# Extract links with keywords
job_links = parser.extract_links(keywords=["job", "position", "faculty"])

# Extract deadline
deadline = parser.extract_deadline()
```

#### RSS Parser

```python
from scripts.scraper.parsers.rss_parser import parse_feed

rss_xml = """<?xml version="1.0"?><rss>...</rss>"""
listings = parse_feed(rss_xml)
```

#### Date Parser

```python
from scripts.scraper.parsers.date_parser import parse_date, extract_deadline

# Parse date string
date = parse_date("January 15, 2025")  # Returns "2025-01-15"

# Extract deadline from text
text = "Application deadline: January 15, 2025"
deadline = extract_deadline(text)  # Returns "2025-01-15"
```

## Configuration

Scrapers use the configuration file at `data/config/scraping_sources.json`. The configuration is organized into:
- **accessible**: URLs that have been verified and are accessible
- **non_accessible**: URLs that failed verification or are pending

See `data/config/README.md` for detailed configuration documentation.

## Scraping Methods

### Pattern-Based Extraction

The scrapers use a hybrid approach combining:
1. **Pattern-based extraction**: Searches for common patterns (job keywords, links, containers)
2. **Class-based fallback**: Uses CSS classes when available

This approach provides flexibility across different website structures.

### Rate Limiting

All scrapers include built-in rate limiting (default: 2 seconds between requests) to:
- Avoid overwhelming target servers
- Reduce risk of being blocked
- Be respectful of website resources

### Retry Logic

Failed requests are automatically retried with exponential backoff:
- Default: 3 retries
- Base delay: 1 second
- Maximum delay: 60 seconds

### User Agent Rotation

User agents are rotated to reduce detection risk and appear more like regular browser traffic.

## Output

Scraped data is saved to:
- **Raw HTML**: `data/raw/{source_type}/{filename}.html`
  - AEA: `data/raw/aea/listings.html`
  - Universities: `data/raw/universities/{university_name}_{department}.html`
  - Institutes: `data/raw/institutes/{institute_name}.html`

## Error Handling

Scrapers handle errors gracefully:
- Network errors: Retried with exponential backoff
- Parsing errors: Logged and skipped
- Missing data: Fields set to empty strings or None

All errors are logged for debugging and monitoring.

## Testing

Run tests with:
```bash
poetry run python tests/load-data-collection/test_scrapers.py
```

Or run tests by category:
```bash
poetry run python -m pytest tests/load-data-collection/scraper/
poetry run python -m pytest tests/load-data-collection/parser/
```

See `tests/load-data-collection/README.md` for detailed testing documentation.

## Adding New Scrapers

To add a new scraper:

1. Create a new scraper class inheriting from `BaseScraper`:

```python
from scripts.scraper.base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def parse(self, html: str):
        # Implement parsing logic
        pass
    
    def scrape(self):
        # Implement main scraping method
        pass
```

2. Implement the required methods:
   - `parse(html)`: Parse HTML and extract job listings
   - `scrape()`: Main scraping method (fetch + parse)

3. Use base class methods:
   - `fetch(url)`: Fetch HTML with rate limiting and retries
   - `save_raw_html(content, filename)`: Save raw HTML
   - `extract(url, save_raw, filename)`: Fetch and parse in one call

## Best Practices

1. **Always use rate limiting**: Don't disable rate limiting unless absolutely necessary
2. **Handle errors gracefully**: Don't let one failed scrape stop the entire process
3. **Save raw HTML**: Helps with debugging and analysis
4. **Log important events**: Use the logging module for debugging
5. **Test with sample data**: Test parsers with real HTML samples before full scraping
6. **Respect robots.txt**: Check and respect website robots.txt files
7. **Monitor for changes**: Website structures change, monitor for parsing failures

## Troubleshooting

### Common Issues

**Scraper returns empty results:**
- Check if the website structure has changed
- Verify the URL is still accessible
- Check if the page requires JavaScript (may need Selenium)
- Review HTML samples in `data/raw/samples/`

**Rate limiting too aggressive:**
- Adjust `rate_limit_delay` parameter when initializing scraper
- Default is 2 seconds, increase if needed

**Parsing errors:**
- Check raw HTML files in `data/raw/`
- Test parser with sample HTML
- Update parsing logic if website structure changed

**Import errors:**
- Ensure you're running from project root
- Check that Poetry environment is activated
- Verify all dependencies are installed: `poetry install`

## Related Documentation

- Configuration: `data/config/README.md`
- Testing: `tests/load-data-collection/README.md`
- Project Structure: `conversation_cursor/structure/latest.md`
- Progress: `conversation_cursor/progress/latest.md`

