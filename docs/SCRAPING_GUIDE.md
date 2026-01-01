# Scraping Guide

Complete guide for using scrapers and adding new sources.

## Quick Reference

**Use scrapers:**
```python
from scripts.scraper.aea_scraper import AEAScraper
scraper = AEAScraper()
listings = scraper.scrape()
```

**Add new source:** Edit `data/config/scraping_sources.json` → Run `verify_urls.py`

## Scraper Usage

### AEA JOE Scraper
```python
from scripts.scraper.aea_scraper import AEAScraper
scraper = AEAScraper()
listings = scraper.scrape()  # Checks RSS first, falls back to HTML
```

### University Scraper
```python
from scripts.scraper.university_scraper import UniversityScraper
scraper = UniversityScraper(
    university_name="Harvard University",
    url="https://economics.harvard.edu/faculty/positions",
    department="Economics"
)
listings = scraper.scrape()
```

### Scrape All Sources
```python
from scripts.scraper.university_scraper import scrape_all_universities
from scripts.scraper.institute_scraper import scrape_all_institutes

all_listings = scrape_all_universities() + scrape_all_institutes()
```

## Adding New Sources

### Step 1: Find Job Postings URL
Look for pages like "Faculty Positions", "Job Openings", "Employment", or "招聘" (Chinese).

### Step 2: Add to Configuration
Edit `data/config/scraping_sources.json`:

**United States:**
```json
{
  "accessible": {
    "regions": {
      "united_states": {
        "universities": [{
          "name": "Example University",
          "departments": [{
            "name": "Economics",
            "url": "https://example.edu/econ/jobs",
            "scraping_method": "html_parser"
          }]
        }]
      }
    }
  }
}
```

**Mainland China:**
```json
{
  "accessible": {
    "regions": {
      "mainland_china": {
        "universities": [{
          "name": "示例大学",
          "departments": [{
            "name": "经济学",
            "url": "https://example.edu.cn/econ/招聘",
            "scraping_method": "html_parser"
          }]
        }]
      }
    }
  }
}
```

**Other Countries:**
```json
{
  "accessible": {
    "regions": {
      "other_countries": {
        "countries": {
          "united_kingdom": {
            "universities": [{
              "name": "Example University",
              "departments": [{
                "name": "Economics",
                "url": "https://example.ac.uk/jobs"
              }]
            }]
          }
        }
      }
    }
  }
}
```

### Step 3: Verify URL
```bash
poetry run python scripts/scraper/check_config/verify_urls.py
```
This checks accessibility and moves verified URLs from `non_accessible` to `accessible`.

### Step 4: Test
```python
from scripts.scraper.university_scraper import UniversityScraper
scraper = UniversityScraper("Test University", "https://example.com/jobs")
listings = scraper.scrape()
print(f"Found {len(listings)} listings")
```

## Scraping Methods

- **html_parser**: Default for most websites (pattern-based extraction)
- **rss**: For RSS/Atom feeds (more reliable when available)

## Architecture

```
scripts/scraper/
├── base_scraper.py       # Abstract base class
├── aea_scraper.py        # AEA JOE scraper
├── university_scraper.py # University scraper
├── institute_scraper.py  # Institute scraper
├── parsers/              # HTML, RSS, text, date parsers
└── utils/                # Rate limiting, retries, user agents
```

## Features

- **Rate Limiting**: 2 seconds between requests (configurable)
- **Retry Logic**: Exponential backoff (3 retries by default)
- **User Agent Rotation**: Reduces detection risk
- **Error Handling**: Graceful failures with logging

## Troubleshooting

**Empty results?**
- Check if website structure changed
- Verify URL is accessible
- Review HTML in `data/raw/samples/`

**Import errors?**
- Run from project root
- Activate Poetry: `poetry shell`
- Install dependencies: `poetry install`

**Need help?**
- See `data/config/README.md` for configuration details
- See `conversation_cursor/structure/latest.md` for project structure
