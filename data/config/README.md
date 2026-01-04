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

See `url_verification/` folder for latest verification results and detailed findings.

## Verification Methodology

### URL Verification Process

For each URL entry, verify:
1. **Accessibility**: URL is accessible (HTTP 200 OK, not 404/403/timeout)
2. **Job Content**: URL contains actual job postings (not just general department page)
3. **Scraping Method**: Appropriate parser is selected (html_parser, javascript, rss)
4. **Department URLs**: Correct and accessible for each department (Economics, Management, etc.)

### Common URL Patterns to Try

When verifying or discovering URLs, test these patterns in order:
- `/faculty/positions`
- `/employment`
- `/jobs`
- `/careers`
- `/faculty-recruiting`
- `/open-positions`
- `/faculty/jobs`
- `/about/jobs`
- `/people/jobs`
- `/hr/careers`
- `/hiring`

### Verification Scoring

- **Score 0-2**: Move to non_accessible (no job content or inaccessible)
- **Score 3+**: Keep in accessible (job keywords, links, or PDFs found)

### Common Issues & Solutions

| Issue | Indicator | Solution |
|-------|-----------|----------|
| Wrong page type | Department/faculty page, no jobs | Use URL discovery to find career portal |
| Access denied | 403 Forbidden | Try alternative URL patterns |
| Not found | 404 error | Check if URL needs updating |
| Timeout | Connection timeout | May require VPN or alternative domain |
| No job content | Page accessible but no jobs | Verify page has actual listings |

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
