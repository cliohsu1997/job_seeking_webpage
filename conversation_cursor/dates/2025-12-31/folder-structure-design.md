# Folder Structure Design for Economics Job Aggregator

## Complete Directory Tree

```
job-seeking-webpage/
│
├── .cursorrules                          # Cursor AI rules
├── .gitkeep                              # Git placeholder
├── read_it.md                            # Project guidelines
├── index.html                            # Main landing page
├── jobs.html                             # Generated job listings (auto-created)
├── README.md                             # Project documentation
├── requirements.txt                      # Python dependencies
│
├── data/                                 # All data storage
│   ├── raw/                             # Raw scraped data (unprocessed)
│   │   ├── aea/                         # AEA JOE scrapes
│   │   │   ├── .gitkeep
│   │   │   └── YYYY-MM-DD/              # Daily folders (created on run)
│   │   │       └── listings.html        # Raw HTML from AEA
│   │   │
│   │   └── universities/                # University website scrapes
│   │       ├── .gitkeep
│   │       └── YYYY-MM-DD/              # Daily folders
│   │           ├── harvard.html
│   │           ├── mit.html
│   │           └── stanford.html
│   │
│   ├── processed/                       # Cleaned, structured data
│   │   ├── jobs.json                    # Current job listings (JSON)
│   │   ├── jobs.csv                     # Current job listings (CSV)
│   │   └── archive/                     # Historical data
│   │       ├── .gitkeep
│   │       └── YYYY-MM-DD/              # Archived by date
│   │
│   └── config/                          # Configuration files
│       ├── universities.json            # List of universities to scrape
│       └── scraping_rules.json          # Site-specific scraping rules
│
├── scripts/                             # Automation scripts
│   ├── scraper/                         # Web scraping modules
│   │   ├── .gitkeep
│   │   ├── base_scraper.py             # Base scraper class
│   │   ├── aea_scraper.py              # AEA JOE scraper
│   │   └── university_scraper.py        # Generic university scraper
│   │
│   ├── processor/                       # Data processing modules
│   │   ├── .gitkeep
│   │   ├── parser.py                   # Parse HTML/XML to structured data
│   │   ├── normalizer.py               # Normalize dates, formats, text
│   │   └── deduplicator.py             # Remove duplicate entries
│   │
│   ├── generator/                       # Output generation modules
│   │   ├── .gitkeep
│   │   ├── html_generator.py           # Generate jobs.html
│   │   └── json_generator.py           # Generate JSON/CSV files
│   │
│   └── scheduler.py                    # Main script (runs daily)
│
├── templates/                           # HTML templates
│   ├── .gitkeep
│   ├── jobs_template.html              # Main template for job listings
│   └── job_card.html                   # Template for individual job card
│
├── static/                              # Static web assets
│   ├── css/
│   │   ├── .gitkeep
│   │   └── styles.css                  # Styling for job listings page
│   │
│   ├── js/
│   │   ├── .gitkeep
│   │   └── filter.js                   # Client-side filtering/search
│   │
│   └── images/
│       └── .gitkeep
│
└── conversation_cursor/                 # Project management (existing)
    ├── dates/
    │   └── 2025-12-31/
    │       ├── create-econ-job-aggregator-proposal.md
    │       ├── project-workflow-illustration.md
    │       └── folder-structure-design.md
    ├── progress/
    ├── structure/
    └── to-do-list/
```

## Directory Purposes

### `/data`
- **Purpose**: Store all data (raw scrapes, processed data, configuration)
- **Structure**: Separated by data type and processing stage
- **Archive**: Keep historical data for reference and analysis

### `/scripts`
- **Purpose**: All automation and processing code
- **Structure**: Organized by function (scrape → process → generate)
- **Entry Point**: `scheduler.py` runs the full pipeline

### `/templates`
- **Purpose**: HTML templates for generating the webpage
- **Reusability**: Templates allow easy styling updates without code changes

### `/static`
- **Purpose**: CSS, JavaScript, and images for the webpage
- **Separation**: Keeps presentation separate from data and logic

## File Naming Conventions

- **Python scripts**: `snake_case.py`
- **Config files**: `snake_case.json`
- **Data files**: `snake_case.json` or `snake_case.csv`
- **HTML files**: `kebab-case.html`
- **Daily folders**: `YYYY-MM-DD/` format

## Data Flow Through Folders

```
1. Scraper writes → data/raw/aea/YYYY-MM-DD/
2. Parser reads → data/raw/ and writes → data/processed/jobs.json
3. Generator reads → data/processed/jobs.json and writes → jobs.html
4. Archive script moves old data → data/processed/archive/YYYY-MM-DD/
```

## Expansion Points

- **Add more sources**: Add new scrapers in `scripts/scraper/`
- **Add more universities**: Update `data/config/universities.json`
- **Customize output**: Modify templates in `templates/`
- **Add features**: Extend processors in `scripts/processor/`

