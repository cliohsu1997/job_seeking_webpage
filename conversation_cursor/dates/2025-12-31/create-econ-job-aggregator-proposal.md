# Proposal: Daily Updated Economics Faculty Job Aggregator Webpage

## Project Overview

Create an automated, daily-updated webpage that aggregates economics department faculty recruiting information from multiple sources (AEA job listings and individual school websites), displaying key information including application links, deadlines, and required materials.

## Objectives

1. **Data Collection**: Automatically scrape/collect job postings from:
   - AEA (American Economic Association) Job Openings for Economists (JOE) listings
   - Individual university economics department websites
   
2. **Information Extraction**: Parse and extract:
   - Job title and institution
   - Application deadline
   - Link to apply
   - Required application materials (CV, cover letter, research papers, letters of recommendation, etc.)
   - Job description/requirements
   - Contact information

3. **Daily Updates**: Automate the collection process to run daily and update the webpage

4. **User Interface**: Display all jobs in an organized, searchable, and filterable format

## Technical Approach

### Architecture: Load → Transform → Export

Following the project's default workflow structure:

1. **LOAD**: 
   - Scrape AEA JOE listings (RSS feed or web scraping)
   - Scrape individual economics department websites
   - Store raw data in structured format

2. **TRANSFORM**:
   - Parse HTML/XML content
   - Extract structured data (deadlines, links, materials)
   - Normalize dates and formats
   - Deduplicate entries
   - Categorize by job type (tenure-track, visiting, postdoc, etc.)

3. **EXPORT**:
   - Generate HTML webpage with all listings
   - Create JSON/CSV data files for programmatic access
   - Update the main index.html or create dedicated job listings page

### Technology Stack Options

**Option A: Python-based (Recommended)**
- **Scraping**: BeautifulSoup4, Scrapy, or Selenium for dynamic content
- **Data Processing**: Pandas for data manipulation
- **Scheduling**: Cron jobs (Linux/Mac) or Task Scheduler (Windows)
- **Web**: Generate static HTML or use Flask/FastAPI for dynamic site

**Option B: JavaScript/Node.js**
- **Scraping**: Puppeteer, Cheerio, or Playwright
- **Data Processing**: Native JavaScript or libraries
- **Scheduling**: Node-cron
- **Web**: Generate static HTML or use Express.js

**Option C: Hybrid**
- Python for scraping and data processing
- JavaScript for frontend display
- Static site generation

## Data Sources

### Primary Sources
1. **AEA JOE (Job Openings for Economists)**
   - URL: https://www.aeaweb.org/joe/
   - Format: Likely HTML listings, possibly RSS feed
   - Update frequency: Daily/weekly

2. **University Economics Department Websites**
   - Common patterns: `/faculty/positions`, `/employment`, `/jobs`
   - Examples: Harvard, MIT, Stanford, Chicago, etc.
   - Update frequency: Varies by institution

### Data Collection Strategy
- Start with AEA JOE as primary source (centralized, reliable)
- Add top-tier economics departments incrementally
- Use configurable list of department URLs for easy expansion

## Proposed Folder Structure

```
job-seeking-webpage/
├── .cursorrules
├── read_it.md
├── index.html                    # Main landing page
├── jobs.html                     # Job listings page (generated)
├── data/                         # Raw and processed data
│   ├── raw/                      # Raw scraped data (latest only, overwrites daily)
│   │   ├── aea/                  # AEA scrapes
│   │   │   └── listings.html     # Latest raw HTML (overwrites)
│   │   └── universities/         # University scrapes
│   │       └── *.html            # Latest scrapes per university (overwrites)
│   ├── processed/                # Cleaned, structured data
│   │   ├── jobs.json             # Current job listings (JSON)
│   │   ├── jobs.csv              # Current job listings (CSV)
│   │   └── archive/              # Historical data
│   └── config/                   # Configuration files
│       ├── universities.json     # List of department URLs to scrape
│       └── scraping_rules.json   # Site-specific scraping rules
├── scripts/                      # Automation scripts
│   ├── scraper/                  # Scraping modules
│   │   ├── aea_scraper.py       # AEA JOE scraper
│   │   ├── university_scraper.py # Generic university scraper
│   │   └── base_scraper.py      # Base scraper class
│   ├── processor/                # Data processing
│   │   ├── parser.py            # Parse raw HTML/XML
│   │   ├── normalizer.py        # Normalize dates, formats
│   │   └── deduplicator.py      # Remove duplicates
│   ├── generator/                # Output generation
│   │   ├── html_generator.py    # Generate jobs.html
│   │   └── json_generator.py    # Generate JSON/CSV
│   └── scheduler.py             # Main script to run daily
├── templates/                    # HTML templates
│   ├── jobs_template.html       # Template for job listings page
│   └── job_card.html            # Template for individual job card
├── static/                       # Static assets
│   ├── css/
│   │   └── styles.css           # Styling for job listings
│   ├── js/
│   │   └── filter.js            # Client-side filtering/search
│   └── images/
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
└── conversation_cursor/          # Existing project management
    ├── dates/
    ├── progress/
    ├── structure/
    └── to-do-list/
```

## Implementation Phases

### Phase 1: Foundation (Days 1-2)
- Set up folder structure
- Create base scraper framework
- Implement AEA JOE scraper (test with sample data)
- Create data storage structure

### Phase 2: Data Processing (Days 3-4)
- Build parser for extracted data
- Implement date normalization
- Create deduplication logic
- Design data schema (JSON structure)

### Phase 3: Output Generation (Days 5-6)
- Create HTML template for job listings
- Build HTML generator
- Implement JSON/CSV export
- Add basic styling

### Phase 4: University Scrapers (Days 7-10)
- Create generic university scraper
- Add top 20 economics departments
- Handle different website structures
- Test and refine scraping rules

### Phase 5: Automation & Polish (Days 11-12)
- Set up daily scheduler
- Add error handling and logging
- Implement search/filter functionality
- Add metadata (last updated timestamp)
- Create README with setup instructions

### Phase 6: Enhancement (Ongoing)
- Add more universities
- Improve parsing accuracy
- Add email notifications for new postings
- Create API endpoint for programmatic access
- Add analytics/tracking

## Key Features

1. **Daily Automated Updates**: Script runs automatically to fetch latest postings
2. **Comprehensive Information**: Links, deadlines, materials all in one place
3. **Search & Filter**: Filter by deadline, institution, job type
4. **Archive**: Keep historical data for reference
5. **Responsive Design**: Mobile-friendly interface
6. **Export Options**: JSON/CSV for further analysis

## Technical Considerations

### Scraping Ethics
- Respect robots.txt
- Implement rate limiting
- Cache data to avoid excessive requests
- Consider using official APIs if available

### Data Quality
- Handle missing information gracefully
- Validate dates and URLs
- Flag incomplete entries
- Manual review process for edge cases

### Maintenance
- Monitor scraping success rates
- Update scraping rules as websites change
- Log errors for debugging
- Version control for scraping logic

## Success Metrics

- Successfully scrape 100+ job postings daily
- 95%+ accuracy in extracting deadlines and links
- Page loads in < 2 seconds
- Zero manual intervention required for daily updates

## Next Steps

1. Review and approve this proposal
2. Set up initial folder structure
3. Begin Phase 1 implementation
4. Test with AEA JOE as proof of concept
5. Iterate based on results

