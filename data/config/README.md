# Configuration Guide

Configuration files for scraping sources and rules.

## Files

- **`scraping_sources.json`**: All sources organized by accessibility and region
- **`scraping_rules.json`**: Patterns for extracting data (deadlines, keywords, dates)

## Structure

```json
{
  "accessible": {
    "job_portals": { ... },
    "regions": {
      "united_states": { ... },
      "mainland_china": { ... },
      "other_countries": { ... }
    }
  },
  "non_accessible": { ... }
}
```

## Adding a Source

1. Add entry to appropriate region in `scraping_sources.json`
2. Run `scripts/scraper/check_config/verify_urls.py` to verify
3. Verified URLs move from `non_accessible` to `accessible`

## Entry Format

```json
{
  "name": "University Name",
  "departments": [{
    "name": "Economics",
    "url": "https://example.edu/jobs",
    "scraping_method": "html_parser"
  }]
}
```

## Current Status

- **176 accessible URLs** (70% success rate)
- **74 non-accessible URLs** (pending verification)

See `docs/SCRAPING_GUIDE.md` for detailed adding instructions.
