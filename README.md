# Economics Faculty Job Aggregator

A daily-updated webpage that aggregates economics department faculty recruiting information from AEA (American Economic Association) job listings and individual university websites.

## Features

- **Automated Daily Updates**: Scrapes job postings daily from multiple sources
- **Comprehensive Information**: Displays application links, deadlines, and required materials
- **Multiple Sources**: Aggregates from AEA JOE and university economics department websites
- **Search & Filter**: Easy-to-use interface for finding relevant positions

## Project Structure

```
job-seeking-webpage/
├── data/                    # Data storage
│   ├── raw/                # Raw scraped data (latest only, overwrites daily)
│   ├── processed/          # Cleaned, structured data
│   └── config/             # Configuration files
├── scripts/                 # Automation scripts
│   ├── scraper/            # Web scraping modules
│   ├── processor/          # Data processing
│   └── generator/          # Output generation
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
└── jobs.html               # Generated job listings page
```

## Setup

1. Install Poetry (if not already installed):
```bash
# See https://python-poetry.org/docs/#installation for installation instructions
```

2. Install project dependencies using Poetry:
```bash
poetry install
```

3. Activate the Poetry shell:
```bash
poetry shell
```

Or run commands using Poetry:
```bash
poetry run python scripts/scheduler.py
```

3. Configure sources to scrape in `data/config/scraping_sources.json` (see `data/config/README.md`)

4. (Optional) Verify URLs before scraping:
```bash
poetry run python scripts/scraper/check_config/verify_urls.py
```

5. Run the scraper:
```bash
poetry run python scripts/scraper/aea_scraper.py
```

## Workflow

The project follows a **Load → Transform → Export** structure:

1. **LOAD**: Scrape job listings from AEA and university websites
2. **TRANSFORM**: Parse, normalize, and deduplicate the data
3. **EXPORT**: Generate HTML webpage and JSON/CSV files

## Scraping

### Current Coverage

- **176 accessible URLs** across multiple regions:
  - Mainland China: 100 universities
  - United States: ~60 universities
  - Other Countries: UK, Canada, Australia, Germany, France, Netherlands, Singapore, Switzerland
  - Research Institutes: NBER, CEPR, Federal Reserve Banks, and more

### Scraper Framework

The scraper framework includes:
- **AEA JOE Scraper**: RSS/HTML fallback for AEA job listings
- **University Scraper**: Generic scraper for university websites
- **Institute Scraper**: Scraper for research institutes and think tanks
- **Parsers**: HTML, RSS, text extraction, and date parsing
- **Utilities**: Rate limiting, retry handling, user agent rotation

### Usage

```bash
# Run AEA scraper
poetry run python scripts/scraper/aea_scraper.py

# Scrape all universities from configuration
poetry run python -c "from scripts.scraper.university_scraper import scrape_all_universities; scrape_all_universities()"

# Verify URLs in configuration
poetry run python scripts/scraper/check_config/verify_urls.py
```

### Documentation

- **Scraper Usage**: See `scripts/scraper/README.md` for detailed scraper documentation
- **Adding Sources**: See `docs/SCRAPING_GUIDE.md` for guide on adding new sources
- **Configuration**: See `data/config/README.md` for configuration file structure

## Daily Updates

The scraper runs automatically via scheduler (cron/Task Scheduler) to:
- Collect new job postings (raw data overwrites previous version)
- Process and structure the data
- Update the jobs.html webpage
- Archive processed data (raw data not archived, only latest kept)

## Documentation

See `conversation_cursor/dates/2025-12-31/` for:
- Detailed proposal: `create-econ-job-aggregator-proposal.md`
- Workflow illustration: `project-workflow-illustration.md`

