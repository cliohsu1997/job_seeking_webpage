# Proposal: Scraping Strategy for Economics Faculty Job Listings

## Overview

This proposal outlines the strategy for scraping economics faculty job information from universities worldwide, organized by geographic regions with different coverage depths.

## 1. Information to Scrape

### Core Data Fields (Required)

Each job listing should capture the following information:

#### Basic Information
- **Job Title**: e.g., "Assistant Professor", "Associate Professor", "Postdoctoral Fellow"
- **Institution Name**: Full university/institution name
- **Department**: Department name (Economics, Management, Marketing, or other)
- **Location**: City, State/Province, Country
- **Job Type**: tenure-track, visiting, postdoc, lecturer, etc.
- **Institution Type**: "university", "research_institute", "think_tank"

#### Application Details
- **Application Deadline**: Date (normalized to YYYY-MM-DD format)
- **Application Link**: Direct URL to apply or job posting
- **Application Portal**: If different from direct link (e.g., Interfolio, AcademicJobsOnline)
- **Contact Email**: Department contact for questions
- **Contact Person**: Name of hiring contact (if available)

#### Required Materials
- **CV/Resume**: Required (yes/no)
- **Cover Letter**: Required (yes/no)
- **Research Statement**: Required (yes/no)
- **Teaching Statement**: Required (yes/no)
- **Research Papers**: Number of papers required (e.g., "3 papers", "Job Market Paper")
- **Letters of Recommendation**: Number required (e.g., "3 letters")
- **Other Materials**: Any additional requirements (transcripts, diversity statement, etc.)

#### Job Details
- **Full Description**: Complete job posting text
- **Requirements**: Qualifications, education level (PhD required, ABD acceptable, etc.)
- **Specializations**: Research fields/areas (e.g., "Macroeconomics", "Labor Economics")
- **Start Date**: When position begins (if specified)
- **Salary Range**: If disclosed (varies by country/region)

#### Metadata
- **Source**: Where the listing was found ("aea", "university_website", "other")
- **Source URL**: Original URL of the posting
- **Scraped Date**: Date when data was collected (YYYY-MM-DD)
- **Last Updated**: Date when posting was last modified (if available)
- **Is Active**: Whether listing is still open (for deduplication)

### Data Schema Example

```json
{
  "id": "unique_hash_based_on_institution_title_deadline",
  "title": "Assistant Professor of Economics",
  "institution": "Harvard University",
  "institution_type": "university",
  "department": "Department of Economics",
  "department_category": "Economics",
  "location": {
    "city": "Cambridge",
    "state": "MA",
    "country": "United States",
    "region": "united_states"
  },
  "job_type": "tenure-track",
  "deadline": "2025-01-15",
  "deadline_display": "January 15, 2025",
  "application_link": "https://academicpositions.harvard.edu/...",
  "application_portal": "Harvard Academic Positions",
  "contact_email": "econ-jobs@harvard.edu",
  "contact_person": "Dr. Jane Smith",
  "materials_required": {
    "cv": true,
    "cover_letter": true,
    "research_statement": true,
    "teaching_statement": true,
    "research_papers": "Job Market Paper + 2 additional papers",
    "letters_of_recommendation": 3,
    "other": ["Transcripts", "Diversity Statement"]
  },
  "description": "Full job description text...",
  "requirements": "PhD in Economics or related field required...",
  "specializations": ["Macroeconomics", "Monetary Economics"],
  "start_date": "2025-09-01",
  "salary_range": "Not disclosed",
  "source": "university_website",
  "source_url": "https://economics.harvard.edu/faculty/positions",
  "scraped_date": "2025-12-31",
  "last_updated": "2025-12-20",
  "is_active": true,
  "campus": "Cambridge" // If multiple campuses, specify which one
}
```

## 2. University Coverage Strategy

### Geographic Organization

Universities will be organized into three main categories:

#### Category 1: Mainland China (Top 100)
- **Coverage**: Top 100 universities in mainland China
- **Ranking Source**: QS World University Rankings (prioritizing Economics & Econometrics subject ranking)
- **Departments**: Economics, Management, Marketing departments
- **Language**: Chinese (Simplified)
- **Special Considerations**: 
  - May need Chinese language parsing
  - Different application systems (may use Chinese portals)
  - Different date formats and terminology

#### Category 2: United States (Top 100)
- **Coverage**: Top 100 universities in the United States
- **Ranking Source**: QS World University Rankings (prioritizing Economics & Econometrics subject ranking)
- **Departments**: Economics, Management, Marketing departments
- **Language**: English
- **Special Considerations**:
  - Many use standardized portals (Interfolio, AcademicJobsOnline, HigherEdJobs)
  - AEA JOE will cover many of these, but direct scraping ensures completeness

#### Category 3: Other Countries (Top 30 per country)
- **Coverage**: Top 30 universities in each country (outside mainland China and US)
- **Ranking Source**: QS World University Rankings (prioritizing Economics & Econometrics subject ranking)
- **Departments**: Economics, Management, Marketing departments
- **Target Countries**: To be prioritized (e.g., UK, Canada, Australia, Germany, France, Japan, etc.)
- **Language**: Varies by country (English, local languages)
- **Special Considerations**:
  - Multi-language support may be needed
  - Different application systems and formats
  - May need country-specific parsing rules

### University Selection Criteria

**Approved Approach:**
- **Ranking System**: QS World University Rankings
- **Priority**: Economics & Econometrics subject ranking (fall back to general QS ranking if subject ranking not available)
- **Departments**: Include Economics, Management, and Marketing departments from each university
- **Multiple Campuses**: Treat separately if they have different job posting pages/URLs
- **Research Institutions**: Include research institutes and think tanks (e.g., Federal Reserve Banks, NBER, CEPR, etc.)
- **Organization**: All scraping sources stored in `data/config/scraping_sources.json`, organized by region and job nature

## 3. How to Scrape

### Scraping Methods

#### Method 1: AEA JOE (Primary Source)
- **URL**: https://www.aeaweb.org/joe/
- **Method**: 
  - Check for RSS/XML feed first
  - If not available, scrape HTML listings
  - May need pagination handling
- **Advantages**: 
  - Centralized source
  - Standardized format
  - Covers many US and international positions
- **Frequency**: Daily (likely updates frequently during hiring season)

#### Method 2: University Department Websites (Direct Scraping)
- **Common URL Patterns**:
  - `/faculty/positions`
  - `/employment`
  - `/jobs`
  - `/careers`
  - `/faculty-recruiting`
  - `/open-positions`
- **Methods**:
  - **HTML Parsing**: For static pages (BeautifulSoup4)
  - **JavaScript Rendering**: For dynamic content (Selenium/Playwright)
  - **RSS/XML Feeds**: If available
  - **API Access**: If universities provide APIs (rare)
- **Challenges**:
  - Each university has different HTML structure
  - Need custom parsers per university or pattern-based extraction
  - Some sites require authentication or have anti-bot measures

#### Method 3: Academic Job Portals (Secondary Sources)
- **Portals to Consider**:
  - AcademicJobsOnline (AJO)
  - HigherEdJobs
  - Interfolio
  - Chronicle of Higher Education
  - EconJobMarket (EJM)
- **Method**: Scrape portal listings as backup/verification
- **Advantages**: Standardized format, covers multiple institutions
- **Note**: May require API access or careful scraping to respect terms of service

### Technical Implementation

#### Base Scraper Framework

```python
# Proposed structure
scripts/scraper/
├── base_scraper.py          # Abstract base class
├── aea_scraper.py           # AEA JOE specific scraper
├── university_scraper.py    # Generic university scraper
├── portal_scraper.py        # Academic portal scrapers
├── parsers/
│   ├── html_parser.py       # HTML parsing utilities
│   ├── rss_parser.py        # RSS/XML feed parser
│   └── text_extractor.py   # Text extraction and cleaning
└── utils/
    ├── rate_limiter.py      # Rate limiting and delays
    ├── retry_handler.py     # Retry logic
    └── user_agent.py        # User agent rotation
```

#### Scraping Workflow

1. **Configuration Loading**
   - Load `data/config/scraping_sources.json` with all scraping sources (organized by region/job nature)
   - Load `data/config/scraping_rules.json` for parsing patterns
   - Load region-specific configurations

2. **Rate Limiting & Ethics**
   - Respect robots.txt
   - Implement delays between requests (2+ seconds)
   - Use appropriate User-Agent headers
   - Handle errors gracefully (retry with exponential backoff)

3. **Data Collection**
   - For each university:
     - Try multiple URL patterns
     - Attempt RSS feed first (if available)
     - Fall back to HTML scraping
     - Extract structured data using patterns/rules
   - For AEA JOE:
     - Scrape main listings page
     - Handle pagination if needed
     - Extract individual job details

4. **Data Storage**
   - Save raw HTML/XML to `data/raw/universities/{institution_name}.html`
   - Save raw AEA data to `data/raw/aea/listings.html`
   - Save raw research institute/think tank data to `data/raw/institutes/{institution_name}.html`
   - Overwrite previous versions (keep only latest)

5. **Error Handling**
   - Log failed scrapes
   - Continue with other universities if one fails
   - Track success/failure rates
   - Alert on persistent failures

### Parsing Strategy

**Note**: Before implementing parsers, we need to analyze sample HTML files to determine the most efficient approach.

#### Two Approaches to Evaluate

**Method 1: Class-Based Extraction**
- Assign different CSS classes to HTML elements
- Extract information by targeting specific classes
- **Advantages**: Efficient, reliable, one-time setup per source
- **Disadvantages**: Requires HTML structure to have consistent classes

**Method 2: Pattern-Based Extraction (Brute Force)**
- Find common patterns in HTML structure
- Use regex and structural analysis to extract data
- **Advantages**: More flexible, works with varied structures
- **Disadvantages**: May be less reliable, requires ongoing maintenance

#### Analysis Task (Before Implementation)

1. **Download Sample HTML Files**
   - Download from diverse sources (AEA JOE, various universities, research institutes)
   - Save samples to `data/raw/samples/` for analysis
   - Include sources with different HTML structures

2. **Compare Approaches**
   - Analyze HTML structures to identify patterns
   - Test both class-based and pattern-based extraction on samples
   - Evaluate efficiency, reliability, and maintenance requirements
   - Document findings and decide on optimal approach

3. **Implementation Decision**
   - Choose primary approach (or hybrid)
   - Document decision rationale
   - Implement chosen approach in parser modules

#### Pattern-Based Extraction (If Chosen)

Use `scraping_rules.json` to define:
- **Deadline Patterns**: Regex patterns for finding deadlines
- **Link Patterns**: How to identify application links
- **Material Patterns**: Keywords for required materials
- **Date Formats**: Region-specific date parsing

#### Class-Based Extraction (If Chosen)

Use `scraping_sources.json` to define:
- **CSS Class Mappings**: Map data fields to CSS classes
- **Selector Patterns**: CSS selectors for each field
- **Structure Templates**: HTML structure templates per source type

#### Institution-Specific Parsers

For institutions with unique structures:
- Create custom parser functions
- Store parser configuration in `scraping_sources.json`
- Fall back to generic parser if custom fails

#### Text Extraction & Cleaning

- Extract main content from HTML
- Remove navigation, headers, footers
- Clean whitespace and formatting
- Handle special characters and encoding

### Tools & Libraries

**Proposed Python Stack:**
- **Requests**: HTTP library for fetching pages
- **BeautifulSoup4**: HTML parsing
- **Selenium/Playwright**: JavaScript rendering (if needed)
- **lxml**: Fast XML/HTML parsing
- **dateutil**: Flexible date parsing
- **pandas**: Data manipulation (for transform phase)
- **logging**: Error tracking and debugging

## 4. Implementation Phases

### Phase 1A: HTML Parsing Approach Analysis (First Step)
- Download sample HTML files from diverse sources
- Analyze HTML structures
- Compare class-based vs pattern-based extraction approaches
- Determine optimal parsing strategy
- Document findings and decision

### Phase 1B: AEA JOE Scraper (Priority)
- Implement AEA JOE scraper using chosen parsing approach
- Test and validate data extraction
- Handle edge cases and errors

### Phase 1B: US Universities (Top 100)
- Start with top 20 US universities
- Develop pattern-based extraction
- Expand to top 100 incrementally
- Test and refine parsers

### Phase 1C: Mainland China Universities (Top 100)
- Research Chinese university job posting formats
- Implement Chinese language parsing (if needed)
- Start with top 20, expand to top 100
- Handle Chinese date formats and terminology

### Phase 1D: Other Countries (Top 30 per country)
- Prioritize English-speaking countries first (UK, Canada, Australia)
- Expand to other major countries
- Implement multi-language support as needed
- Handle country-specific formats

## 5. Challenges & Solutions

### Challenge 1: Diverse HTML Structures
**Solution**: 
- Pattern-based extraction with fallback to generic parser
- University-specific parser configurations
- Machine learning approach (future enhancement)

### Challenge 2: Dynamic Content (JavaScript)
**Solution**: 
- Use Selenium/Playwright for JavaScript-heavy sites
- Identify which sites need JS rendering
- Cache rendered content when possible

### Challenge 3: Rate Limiting & Blocking
**Solution**: 
- Implement respectful rate limiting
- Rotate User-Agents
- Use proxies if necessary (future)
- Respect robots.txt

### Challenge 4: Multi-Language Support
**Solution**: 
- Use translation APIs for non-English content (optional)
- Focus on English and Chinese first
- Expand language support incrementally

### Challenge 5: Data Quality & Validation
**Solution**: 
- Implement validation rules
- Flag incomplete entries
- Manual review process for edge cases
- Confidence scoring for extracted data

## 6. Data Organization

### Scraping Sources Configuration

All scraping sources will be stored in `data/config/scraping_sources.json`, organized by:
- **Region**: Mainland China, United States, Other Countries
- **Job Nature**: Academic (universities), Research Institutes, Think Tanks, Job Portals

### Structure of scraping_sources.json

```json
{
  "job_portals": {
    "aea": {
      "name": "American Economic Association JOE",
      "url": "https://www.aeaweb.org/joe/",
      "scraping_method": "rss_or_html",
      "region": "global",
      "job_nature": "portal"
    }
  },
  "regions": {
    "mainland_china": {
      "universities": [...],
      "research_institutes": [...],
      "think_tanks": [...]
    },
    "united_states": {
      "universities": [...],
      "research_institutes": [...],
      "think_tanks": [...]
    },
    "other_countries": {
      "uk": {
        "universities": [...],
        "research_institutes": [...],
        "think_tanks": [...]
      },
      "canada": {...},
      "australia": {...}
    }
  }
}
```

Each entry includes:
- Institution name
- Department(s): Economics, Management, Marketing
- URL(s) for job postings
- Scraping method
- Campus information (if multiple campuses with separate postings)
- Notes and special considerations

## Next Steps

1. ✅ **Proposal approved** with requirements:
   - QS rankings (prioritizing Economics & Econometrics)
   - Include Economics, Management, Marketing departments
   - Multiple campuses treated separately if different postings
   - Include research institutes and think tanks
   - All sources stored in `data/config/scraping_sources.json`

2. **Create scraping_sources.json structure** with organized format

3. **Compile initial source lists** (top 20-30 per category to start)

4. **Begin Phase 1A**: Implement AEA JOE scraper

5. **Test and validate** scraping approach

6. **Expand incrementally** to full coverage

---

**Status**: Draft for review
**Date**: 2025-12-31
**Related Phase**: Phase 1 - LOAD (Data Collection)

