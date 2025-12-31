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
├── tests/                          # Test files organized by phase
│   ├── setup-project/              # Phase 0 tests
│   ├── load-data-collection/       # Phase 1 tests
│   ├── transform-data-processing/  # Phase 2 tests
│   └── export-output-generation/   # Phase 3 tests
│
├── environment/                    # Environment management tools
│   ├── python/
│   │   ├── tools/                 # Environment management tool configs
│   │   │   ├── poetry.lock        # Poetry lock file (also in root)
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
- **Environment tools**: Lock files and configs stored in `./environment/python/tools/`
- **Configuration**: `pyproject.toml` (package-mode = false) - kept in root (Poetry requirement)
- **Lock file**: `poetry.lock` - stored in `environment/python/tools/` and root (Poetry requirement)
- **Dependencies**: All installed and locked

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
