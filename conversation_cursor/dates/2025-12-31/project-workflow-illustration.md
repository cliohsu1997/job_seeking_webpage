# Economics Job Aggregator: Project Workflow Illustration

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DAILY AUTOMATION WORKFLOW                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │  1. LOAD: Data Collection Phase     │
        └─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│ AEA JOE      │        │ University   │
│ Scraper      │        │ Scrapers     │
└──────────────┘        └──────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
        ┌─────────────────────────────┐
        │  Raw Data Storage           │
        │  data/raw/aea/listings.html │
        │  data/raw/universities/*.html│
        │  (overwrites latest only)   │
        └─────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────┐
        │  2. TRANSFORM: Data Processing     │
        └─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│ HTML/XML     │        │ Data         │
│ Parser       │        │ Normalizer   │
└──────────────┘        └──────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
        ┌──────────────┐
        │ Deduplicator │
        └──────────────┘
                    │
                    ▼
        ┌─────────────────────────────┐
        │  Processed Data Storage     │
        │  data/processed/jobs.json   │
        └─────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────────────────┐
        │  3. EXPORT: Output Generation       │
        └─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│ HTML         │        │ JSON/CSV     │
│ Generator    │        │ Generator    │
└──────────────┘        └──────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
        ┌─────────────────────────────┐
        │  Web Output                 │
        │  jobs.html                  │
        │  data/processed/jobs.json    │
        └─────────────────────────────┘
```

## Detailed Process Flow

### Phase 1: LOAD (Data Collection)

```
Scheduler Triggers (Daily at 6 AM)
    │
    ├─→ AEA Scraper
    │   ├─→ Fetch AEA JOE listings
    │   ├─→ Parse HTML/XML
    │   └─→ Save to data/raw/aea/listings.html (overwrites previous)
    │
    └─→ University Scrapers (Parallel)
        ├─→ Harvard Economics
        ├─→ MIT Economics
        ├─→ Stanford Economics
        └─→ ... (20+ universities)
            └─→ Save to data/raw/universities/*.html (overwrites previous)
```

### Phase 2: TRANSFORM (Data Processing)

```
Raw Data Files
    │
    ├─→ Parser Module
    │   ├─→ Extract: Title, Institution, Deadline
    │   ├─→ Extract: Application Link
    │   ├─→ Extract: Required Materials
    │   └─→ Extract: Job Description
    │
    ├─→ Normalizer Module
    │   ├─→ Standardize date formats (YYYY-MM-DD)
    │   ├─→ Validate URLs
    │   ├─→ Clean text (remove extra whitespace)
    │   └─→ Categorize job types
    │
    └─→ Deduplicator Module
        ├─→ Compare by title + institution
        ├─→ Compare by application URL
        └─→ Keep most recent/complete entry
```

### Phase 3: EXPORT (Output Generation)

```
Processed JSON Data
    │
    ├─→ HTML Generator
    │   ├─→ Load template (templates/jobs_template.html)
    │   ├─→ Inject job data
    │   ├─→ Apply styling (static/css/styles.css)
    │   └─→ Write to jobs.html
    │
    └─→ JSON/CSV Generator
        ├─→ Generate jobs.json (for API access)
        └─→ Generate jobs.csv (for spreadsheet import)
```

## Data Schema

### Job Entry Structure (JSON)

```json
{
  "id": "unique_identifier",
  "title": "Assistant Professor of Economics",
  "institution": "Harvard University",
  "department": "Department of Economics",
  "deadline": "2025-01-15",
  "deadline_display": "January 15, 2025",
  "application_link": "https://...",
  "materials_required": [
    "CV",
    "Cover Letter",
    "Research Papers",
    "3 Letters of Recommendation",
    "Teaching Statement"
  ],
  "job_type": "tenure-track",
  "description": "Full job description text...",
  "contact_email": "econ-jobs@harvard.edu",
  "source": "aea" | "university_website",
  "source_url": "https://...",
  "scraped_date": "2025-12-31",
  "is_new": true
}
```

## Component Interactions

```
┌─────────────┐
│  Scheduler  │──→ Triggers daily execution
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Scraper   │──→ Collects raw data
│   Manager   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Processor  │──→ Cleans and structures data
│   Pipeline  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generator  │──→ Creates output files
│   Manager   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Webpage   │──→ Displays to users
└─────────────┘
```

## Error Handling Flow

```
Each Step
    │
    ├─→ Success → Continue to next step
    │
    └─→ Error → Log error
                │
                ├─→ Retry (3 attempts)
                │
                └─→ If still fails
                    ├─→ Log to error log
                    ├─→ Continue with other sources
                    └─→ Send notification (optional)
```

## Update Cycle

```
Daily Schedule:
├─→ 6:00 AM: Run scraper
├─→ 6:15 AM: Process data
├─→ 6:20 AM: Generate outputs
└─→ 6:25 AM: Update webpage

Weekly Maintenance:
├─→ Archive old processed data (keep last 90 days in archive/)
├─→ Raw data automatically overwrites (no archiving needed)
├─→ Update scraping rules if needed
└─→ Review error logs
```

