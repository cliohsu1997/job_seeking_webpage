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
│       ├── scraping_sources.json   # All scraping sources organized by accessibility: accessible/non_accessible top-level categories
│       └── scraping_rules.json     # Scraping rules and patterns
│
├── scripts/                        # Automation scripts
│   ├── scraper/                    # Web scraping modules
│   │   ├── utils/                  # Utility modules
│   │   │   ├── config_loader.py    # Configuration loading utilities (load, filter, count URLs)
│   │   │   └── __init__.py         # Utils package init
│   │   ├── check_config/           # Configuration verification scripts
│   │   │   ├── verify_urls.py      # URL verification script (uses config_loader)
│   │   │   └── generate_accessible_config.py  # Generate accessible-only config file
│   │   └── download_samples.py     # Sample HTML download script (uses config_loader)
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
  - **scraping_sources.json**: Configuration file organized by accessibility at top level
    - Structure: `{"accessible": {...}, "non_accessible": {...}}`
    - Each section contains: job_portals, regions (mainland_china, united_states, other_countries)
    - Coverage: ~200+ institutions (100 China, ~60 US, 20 Australia, plus other countries and research institutes)
    - Each entry includes: institution name, department(s) [Economics, Management, Marketing], URL(s), scraping method, campus info, notes
    - No url_status field needed - accessibility is determined by top-level category
    - Current status: 171 accessible URLs, 79 non-accessible URLs (68% success rate)
    - Verification script only checks non_accessible section, moves items to accessible when verified
  - **Config Utility Module**: `scripts/scraper/utils/config_loader.py`
    - Provides functions: `load_config()`, `get_accessible_config()`, `get_non_accessible_config()`, `get_all_config()`, `save_config()`, `count_urls()`
    - Used by verification and download scripts for efficient config management

### Code Organization
- **Separation of concerns**: scraper → processor → generator
- **Templates**: Separate from code for easy styling updates
- **Static assets**: Organized by type (css/js/images)

#### download_samples.py Implementation Details

The `scripts/scraper/download_samples.py` script downloads sample HTML files from all accessible URLs in `scraping_sources.json` for parsing approach analysis.

**Key Functions:**

1. **`sanitize_filename(name)`**: Converts human-readable names to safe filenames
   - Removes special characters (keeps only word chars, spaces, hyphens)
   - Replaces spaces/hyphens with underscores
   - Converts to lowercase
   - Example: `"Harvard University - Economics"` → `"harvard_university_economics"`

2. **`extract_sources_from_config(config_data)`**: Extracts all accessible URLs from scraping_sources.json
   - Filters entries with `url_status == "accessible"`
   - Builds list of source dictionaries with: `name`, `url`, `filename`, `type`
   - Supports: job_portals, united_states (universities, research_institutes), other_countries regions

**Filename Patterns:**

Generated filenames follow structured patterns to identify source type and location:

- **Job Portals**: `portal_<sanitized_name>.html`
  - Example: `portal_aea_joe.html`

- **United States Universities**: `us_<university>_<department>.html`
  - Example: `us_harvard_university_economics.html`

- **United States Research Institutes**: `us_institute_<name>.html`
  - Example: `us_institute_nber.html`

- **Other Countries Universities**: `<country>_<university>_<department>.html`
  - Example: `uk_london_school_of_economics_economics.html`
  - Country codes: `uk`, `ca`, `au`, `de`, `fr`, `nl`, `sg`, `ch`, etc.

- **Other Countries Research Institutes**: `<country>_institute_<name>.html`
  - Example: `uk_institute_cepr.html`

**Usage:** Script automatically discovers and downloads from all 113+ accessible URLs in the configuration file.

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
- **2025-12-31**: Created `scripts/scraper/check_config/` subfolder for configuration verification scripts
- **2025-12-31**: Moved URL verification script to `scripts/scraper/check_config/verify_urls.py`
- **2025-12-31**: Updated verification script to add url_status labels directly to scraping_sources.json
- **2025-12-31**: Verified all initial URLs (20/20 accessible), added url_status="accessible" to each URL entry
- **2025-12-31**: Deleted deprecated files: universities.json (replaced by scraping_sources.json), url_verification_results.json (status now in scraping_sources.json)
- **2025-12-31**: Expanded scraping_sources.json to comprehensive coverage:
  - Mainland China: 100 universities
  - United States: ~60 universities
  - Australia: 20 universities
  - Other countries: Expanded UK, Canada, added Germany, France, Netherlands, Singapore, Switzerland
  - Research institutes: Added Federal Reserve Banks, Brookings, PIIE, IZA
- **2025-12-31**: Updated download_samples.py to automatically extract URLs from scraping_sources.json
- **2025-12-31**: Enhanced verify_urls.py to support mainland_china region extraction
- **2025-12-31**: Completed URL verification: 171/250 URLs accessible (68% success rate)
- **2025-12-31**: Enhanced verification script with Chinese keyword detection (18 Chinese job-related keywords)
- **2025-12-31**: Created config utility module (`scripts/scraper/utils/config_loader.py`) for efficient config management
- **2025-12-31**: Reorganized scraping_sources.json to accessible/non_accessible top-level structure for better efficiency
- **2025-12-31**: Created migration script (`scripts/scraper/check_config/migrate_config_structure.py`) and successfully migrated config
- **2025-12-31**: Updated config_loader.py for new structure (171 accessible, 79 non-accessible URLs)
- **2025-12-31**: Updated read_it.md with poetry run instructions for running Python scripts
- **2025-12-31**: Documented download_samples.py implementation details (filename patterns, functions) in structure/latest.md
