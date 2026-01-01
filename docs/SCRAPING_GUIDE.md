# Scraping Guide: Adding New Sources

This guide explains how to add new sources to the scraping configuration.

## Overview

Job listings are scraped from three main source types:
1. **Job Portals**: AEA JOE and similar aggregators
2. **Universities**: Individual university economics department websites
3. **Research Institutes**: Think tanks and research organizations

## Configuration File Structure

The configuration file `data/config/scraping_sources.json` is organized as:

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
  "non_accessible": {
    "job_portals": { ... },
    "regions": { ... }
  }
}
```

## Adding a University

### Step 1: Find the Job Postings URL

1. Go to the university's economics department website
2. Look for pages like:
   - "Faculty Positions"
   - "Job Openings"
   - "Employment"
   - "Careers"
   - "Recruitment"
3. For Chinese universities, look for:
   - "招聘" (recruitment)
   - "职位" (positions)
   - "人才招聘" (talent recruitment)

### Step 2: Verify the URL

Run the URL verification script:

```bash
poetry run python scripts/scraper/check_config/verify_urls.py
```

This will:
- Check if the URL is accessible
- Detect if the page contains job-related keywords
- Move verified URLs from `non_accessible` to `accessible`

### Step 3: Add to Configuration

Add the university entry to the appropriate region in `scraping_sources.json`:

#### United States Example

```json
{
  "accessible": {
    "regions": {
      "united_states": {
        "universities": [
          {
            "name": "Example University",
            "departments": [
              {
                "name": "Economics",
                "url": "https://economics.example.edu/faculty/positions",
                "scraping_method": "html_parser"
              }
            ]
          }
        ]
      }
    }
  }
}
```

#### Mainland China Example

```json
{
  "accessible": {
    "regions": {
      "mainland_china": {
        "universities": [
          {
            "name": "示例大学",
            "departments": [
              {
                "name": "经济学",
                "url": "https://www.example.edu.cn/econ/recruitment",
                "scraping_method": "html_parser",
                "notes": "Chinese language page"
              }
            ]
          }
        ]
      }
    }
  }
}
```

#### Other Countries Example

```json
{
  "accessible": {
    "regions": {
      "other_countries": {
        "countries": {
          "united_kingdom": {
            "universities": [
              {
                "name": "Example University",
                "departments": [
                  {
                    "name": "Economics",
                    "url": "https://www.example.ac.uk/economics/jobs",
                    "scraping_method": "html_parser"
                  }
                ]
              }
            ]
          }
        }
      }
    }
  }
}
```

### Step 4: Multiple Departments

If a university has multiple departments with separate job pages:

```json
{
  "name": "Example University",
  "departments": [
    {
      "name": "Economics",
      "url": "https://economics.example.edu/jobs",
      "scraping_method": "html_parser"
    },
    {
      "name": "Management",
      "url": "https://business.example.edu/careers",
      "scraping_method": "html_parser"
    },
    {
      "name": "Marketing",
      "url": "https://marketing.example.edu/positions",
      "scraping_method": "html_parser"
    }
  ]
}
```

## Adding a Research Institute

Add to the appropriate region:

```json
{
  "accessible": {
    "regions": {
      "united_states": {
        "research_institutes": [
          {
            "name": "Example Research Institute",
            "url": "https://www.example.org/careers",
            "scraping_method": "html_parser"
          }
        ]
      }
    }
  }
}
```

## Adding a Job Portal

Add to the job_portals section:

```json
{
  "accessible": {
    "job_portals": {
      "example_portal": {
        "name": "Example Job Portal",
        "url": "https://www.example-jobs.com/economics",
        "scraping_method": "rss",
        "notes": "Provides RSS feed"
      }
    }
  }
}
```

## Scraping Methods

### html_parser

Default method for most websites. Uses pattern-based extraction to find job listings.

**Use when:**
- Standard HTML website
- No RSS feed available
- JavaScript not required to load content

### rss

For websites that provide RSS or Atom feeds.

**Use when:**
- RSS/Atom feed is available
- Feed URL is known
- More reliable than HTML parsing

**Example:**
```json
{
  "scraping_method": "rss",
  "rss_url": "https://example.com/jobs/rss.xml"
}
```

### javascript

For websites that require JavaScript to load content (requires Selenium).

**Use when:**
- Content is loaded dynamically with JavaScript
- Standard HTML parsing doesn't work
- Note: Not yet implemented in current framework

## URL Verification

Before adding URLs to the `accessible` section, verify them:

1. **Manual Check**: Visit the URL and confirm it shows job listings
2. **Automated Check**: Run `verify_urls.py` to check URLs in `non_accessible`
3. **Keyword Detection**: The script checks for job-related keywords:
   - English: job, position, faculty, posting, opening, vacancy, employment
   - Chinese: 招聘, 职位, 岗位, 人才, 工作, etc.

## Best Practices

1. **Start with non_accessible**: Add new URLs to `non_accessible` first, then verify
2. **Use descriptive names**: Clear university/institute names help with debugging
3. **Add notes**: Include any special considerations in the `notes` field
4. **Test before adding**: Download a sample HTML file to verify structure
5. **Check periodically**: URLs change, verify periodically that sources still work

## Testing New Sources

After adding a new source:

1. **Download sample HTML**:
   ```bash
   poetry run python scripts/scraper/download_samples.py
   ```

2. **Test scraper manually**:
   ```python
   from scripts.scraper.university_scraper import UniversityScraper
   
   scraper = UniversityScraper(
       university_name="Test University",
       url="https://example.com/jobs"
   )
   listings = scraper.scrape()
   print(f"Found {len(listings)} listings")
   ```

3. **Check raw HTML**: Review `data/raw/universities/` to see what was scraped

## Troubleshooting

### URL Not Accessible

- Check if URL requires authentication
- Verify URL hasn't changed
- Check if website blocks automated access
- Try accessing from different network

### No Job Listings Found

- Website structure may have changed
- Check if JavaScript is required
- Verify the URL shows job listings when visited manually
- Review HTML sample in `data/raw/samples/`

### Parsing Errors

- Download sample HTML and analyze structure
- Update parsing logic if needed
- Check if website uses non-standard HTML structure

## Related Documentation

- Configuration Guide: `data/config/README.md`
- Scraper Usage: `scripts/scraper/README.md`
- Testing: `tests/load-data-collection/README.md`

