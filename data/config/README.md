# Configuration Guide

Configuration files for scraping sources and rules.

## IMPORTANT RULE

**Only URLs containing relevant job information should be in the accessible section.**

URLs in the `accessible` section must:
- Be accessible (HTTP 200 response)
- Contain actual job listings (verified through keyword detection, link analysis, and PDF detection)
- Have a verification score of at least 3 (based on job keywords, job links, and PDFs)

URLs that don't meet these criteria will be moved to the `non_accessible` section during verification.

## Files

- **`scraping_sources.json`**: All sources organized by accessibility and region
- **`scraping_rules.json`**: Patterns for extracting data (deadlines, keywords, dates)
- **`processing_rules.json`**: Processing rules (job types, specializations, regions)
- **`url_verification/`**: URL verification documentation and results

## Verification Documentation

See `url_verification/` folder for:
- `01_url_verification_process.md` - URL verification methodology and common patterns
- `02_verification_results_2026-01-03.md` - Latest verification results and problematic URLs

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
