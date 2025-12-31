# Structure: Project Organization

## Project Structure Overview

```
job-seeking-webpage/
├── .cursorrules                    # Cursor AI rules
├── .gitignore                      # Git ignore rules
├── read_it.md                      # Project guidelines (read first)
├── pyproject.toml                  # Poetry configuration
├── poetry.lock                     # Poetry lock file
├── requirements.txt                # Legacy requirements (kept for reference)
├── README.md                       # Project documentation
├── index.html                      # Main landing page
├── jobs.html                       # Generated job listings (not in git)
│
├── data/                           # Data storage
│   ├── raw/                        # Raw scraped data (latest only)
│   │   ├── aea/                    # AEA JOE scrapes
│   │   └── universities/           # University scrapes
│   ├── processed/                  # Cleaned, structured data
│   │   ├── jobs.json               # Current listings (not in git)
│   │   ├── jobs.csv                # Current listings (not in git)
│   │   └── archive/                # Historical processed data
│   └── config/                     # Configuration files
│       ├── universities.json       # University URLs to scrape
│       └── scraping_rules.json     # Scraping rules and patterns
│
├── scripts/                        # Automation scripts
│   ├── scraper/                    # Web scraping modules
│   ├── processor/                  # Data processing modules
│   ├── generator/                  # Output generation modules
│   └── scheduler.py                # Main scheduler (to be created)
│
├── templates/                      # HTML templates
├── static/                         # Static web assets
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript files
│   └── images/                     # Image assets
│
└── conversation_cursor/             # Project management
    ├── dates/                      # Dated conversation records
    ├── progress/                   # High-level pipeline status
    ├── structure/                  # Project structure documentation
    └── to-do-list/                 # Explicit task lists (dated)
```

## Environment Management

**Tool**: Poetry
- Virtual environment: Managed by Poetry (location: `C:\Users\clioh\AppData\Local\pypoetry\Cache\virtualenvs\`)
- Configuration: `pyproject.toml`
- Lock file: `poetry.lock`
- Dependencies: All installed and locked

## Key Structural Decisions

### Data Storage
- **Raw data**: Only latest version kept (overwrites daily)
- **Processed data**: Can be archived for historical reference
- **Config**: Centralized in `data/config/`

### Code Organization
- **Separation of concerns**: scraper → processor → generator
- **Templates**: Separate from code for easy styling updates
- **Static assets**: Organized by type (css/js/images)

### Workflow Structure
- Follows `load → transform → export` pattern
- Each phase has dedicated folder in `scripts/`

## Recent Structural Changes

- **2025-12-31**: Migrated from venv to Poetry for environment management
- **2025-12-31**: Created complete folder structure
- **2025-12-31**: Set up configuration files and templates directories
