# Configuration Guide

Configuration files for scraping sources and rules.

## IMPORTANT RULE

**Use the 3-category structure in `scraping_sources.json`:**
- `accessible_verified`: Confirmed accessible and content-validated
- `accessible_unverified`: Accessible but content not yet validated
- `potential_links`: Not yet tested; candidates for discovery/verification

URLs should only move into `accessible_verified` after passing content validation (Task 0B). Keep exploratory or unvalidated URLs in `accessible_unverified` or `potential_links` until verified.

## Files

- **`scraping_sources.json`**: All sources organized by verification status (3-category flat list)
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

Flat list grouped by category:

```json
{
  "accessible_verified": [
    {"id": "us_princeton", "name": "Princeton University", "type": "university", "url": "https://..."}
  ],
  "accessible_unverified": [
    {"id": "us_example", "name": "Example University", "type": "university", "url": "https://..."}
  ],
  "potential_links": [
    {"id": "discovery_candidate_1", "type": "university", "url": "https://..."}
  ]
}
```

## Adding a Source

1. Add entry to the appropriate category in `scraping_sources.json`:
  - `accessible_unverified` for new accessible URLs pending validation
  - `potential_links` for URLs that need accessibility testing
2. Run validation tools (Task 0B modules) or targeted tests to move items into `accessible_verified`

## Entry Format

```json
{
  "id": "us_example",
  "name": "Example University",
  "type": "university",
  "url": "https://example.edu/jobs",
  "scraping_method": "html_parser"
}
```

## Current Status

- **accessible_verified**: 127 URLs (validated)
- **accessible_unverified**: 83 URLs (accessible, pending validation)
- **potential_links**: 0 URLs (reserved for discovery)

The legacy hierarchical layout and the old `accessible`/`non_accessible` sections have been retired. The migration script `scripts/scraper/config/migrate_config_structure.py` is kept only as a legacy one-time tool.

See `docs/SCRAPING_GUIDE.md` for detailed adding instructions.
