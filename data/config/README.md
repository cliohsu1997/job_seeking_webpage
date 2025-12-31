# Configuration Files Guide

## scraping_sources.json

This file contains all sources for scraping job listings, organized by region and job nature.

### Structure

Each university/institution entry should include:
- `name`: Full institution name
- `departments`: Array of department objects with:
  - `name`: Department name (Economics, Management, Marketing)
  - `url`: URL to job postings page
  - `scraping_method`: html_parser, rss, or javascript
- `location`: Object with city, state/province, country
- `campus`: Campus name if multiple campuses (only if separate posting pages)
- `scraping_method`: Primary scraping method
- `notes`: Any special considerations

### Example Entry

```json
{
  "name": "Harvard University",
  "departments": [
    {
      "name": "Economics",
      "url": "https://economics.harvard.edu/faculty/positions",
      "scraping_method": "html_parser"
    },
    {
      "name": "Management",
      "url": "https://www.hbs.edu/faculty/positions",
      "scraping_method": "html_parser"
    }
  ],
  "location": {
    "city": "Cambridge",
    "state": "MA",
    "country": "United States"
  },
  "scraping_method": "html_parser",
  "notes": "Check for faculty positions page"
}
```

## scraping_rules.json

Contains patterns and rules for extracting data from HTML:
- Deadline patterns (regex)
- Link patterns
- Material keywords
- Date formats

## Compilation Process

1. Use QS World University Rankings - Economics & Econometrics subject ranking
2. For each university, find:
   - Economics department job posting URL
   - Management/Business school job posting URL
   - Marketing department job posting URL (if separate)
3. Verify URLs are accessible
4. Note any special considerations (authentication, JavaScript, etc.)

