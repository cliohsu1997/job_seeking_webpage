# Structure: Project Organization

## Project Structure Overview

```
job-seeking-webpage/
├── .cursorrules                    # Cursor AI rules
├── .gitignore                      # Git ignore rules
├── read_it.md                      # Project guidelines (read first)
├── pyproject.toml                  # Poetry configuration
├── poetry.lock                     # Poetry lock file (also in environment/python/tools/)
├── requirements.txt                # Legacy requirements (kept for reference)
├── README.md                       # Project documentation
├── index.html                      # Main landing page
├── jobs.html                       # Generated job listings (not in git)
│
├── data/                           # Data storage
│   ├── raw/                        # Raw scraped data (latest only)
│   │   ├── aea/                    # AEA JOE scrapes
│   │   ├── universities/           # University scrapes
│   │   ├── institutes/             # Research institutes and think tanks scrapes
│   │   └── samples/                # Sample HTML files for parsing approach analysis
│   ├── processed/                  # Cleaned, structured data
│   │   ├── jobs.json               # Current listings (not in git)
│   │   ├── jobs.csv                # Current listings (not in git)
│   │   └── archive/                # Historical processed data
│   └── config/                     # Configuration files
│       ├── scraping_sources.json   # All scraping sources organized by region/job nature
│       ├── universities.json       # Legacy: University URLs (deprecated, use scraping_sources.json)
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
├── tests/                          # Test files organized by phase
│   ├── setup-project/              # Phase 0 tests
│   ├── load-data-collection/       # Phase 1 tests
│   ├── transform-data-processing/  # Phase 2 tests
│   └── export-output-generation/   # Phase 3 tests
│
├── environment/                    # Environment management tools
│   ├── python/
│   │   ├── tools/                 # Environment management tool configs (source of truth)
│   │   │   ├── poetry.lock        # Poetry lock file
│   │   │   ├── pyproject.toml     # Poetry configuration (copy, root version required by Poetry)
│   │   │   └── README.md         # Tools documentation
│   │   └── venv/                 # Actual virtual environment (managed by Poetry)
│   └── README.md                  # Environment folder documentation
│
└── conversation_cursor/             # Project management
    ├── dates/                      # Dated conversation records
    ├── progress/                   # High-level pipeline status
    ├── structure/                  # Project structure documentation
    └── to-do-list/                 # Explicit task lists (dated with phase names)
```

## Environment Management

**Tool**: Poetry
- **Poetry Location**: `C:\Users\clioh\AppData\Roaming\pypoetry\venv\Scripts\poetry.exe`
- **Python Location**: `C:\Users\clioh\AppData\Local\Programs\Python\Python313\python.exe` (Python 3.13.5)
- **Virtual environment**: Configured to use `./environment/python/venv/` folder
- **Environment tools**: All Poetry-related files stored in `./environment/python/tools/` (source of truth)
- **Poetry Rule**: All Poetry-related files (poetry.lock, pyproject.toml, configs) must be kept in `environment/python/tools/`
- **Configuration**: `pyproject.toml` must also exist in root (Poetry requirement), but tools/ version is authoritative
- **Lock file**: `poetry.lock` - stored in `environment/python/tools/` (source of truth)
- **Dependencies**: All installed and locked

## Key Structural Decisions

### Data Storage
- **Raw data**: Only latest version kept (overwrites daily)
  - Organized by source type: `aea/`, `universities/`, `institutes/`
- **Processed data**: Can be archived for historical reference
- **Config**: Centralized in `data/config/`
  - **scraping_sources.json**: All scraping sources organized by region (mainland_china, united_states, other_countries) and job nature (universities, research_institutes, think_tanks, job_portals)
  - Each entry includes: institution name, department(s) [Economics, Management, Marketing], URL(s), scraping method, campus info, notes

### Code Organization
- **Separation of concerns**: scraper → processor → generator
- **Templates**: Separate from code for easy styling updates
- **Static assets**: Organized by type (css/js/images)

### Workflow Structure
- Follows `load → transform → export` pattern
- Each phase has dedicated folder in `scripts/`

### To-Do List Naming
- Format: `YYYY-MM-DD_phase-name.md` (e.g., `2025-12-31_setup-project.md`)
- Phase names start with verb, are informative (e.g., `setup-project`, `load-data-collection`)
- Name corresponds to the phase in progress
- Each to-do list contains subtasks for one complete phase

## Current Structure Status

✅ **Complete**: All folders and configuration files are in place
✅ **Environment**: Poetry virtual environment configured and dependencies installed
✅ **Documentation**: All documentation files created and organized
⏸️ **Code**: Scripts folders ready but empty (waiting for Phase 1)

## Recent Structural Changes

- **2025-12-31**: Phase 0 (Project Setup) completed
- **2025-12-31**: Organized environment folder: `python/tools/` for management tools, `python/venv/` for virtual environment
- **2025-12-31**: Cleaned up unnecessary .gitkeep files
- **2025-12-31**: Renamed to-do list to match phase name (`2025-12-31_project-setup.md`)
- **2025-12-31**: Reorganized progress to show "What We've Accomplished" and "What's Next"
- **2025-12-31**: Created test folder structure with phase-based subfolders (`tests/setup-project/`, `tests/load-data-collection/`, etc.)
- **2025-12-31**: Created `scraping_sources.json` to organize all scraping sources by region and job nature
- **2025-12-31**: Updated data structure to include research institutes and think tanks
- **2025-12-31**: Expanded department coverage to include Economics, Management, and Marketing
- **2025-12-31**: Added `data/raw/samples/` folder for HTML parsing approach analysis
- **2025-12-31**: Updated `read_it.md` with token monitoring reminder and proposal finding workflow
- **2025-12-31**: Created Phase 1 scraping strategy proposal (`design-scraping-strategy.md`)
