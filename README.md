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

3. Configure universities to scrape in `data/config/universities.json`

4. Run the scraper:
```bash
python scripts/scheduler.py
```

## Workflow

The project follows a **Load → Transform → Export** structure:

1. **LOAD**: Scrape job listings from AEA and university websites
2. **TRANSFORM**: Parse, normalize, and deduplicate the data
3. **EXPORT**: Generate HTML webpage and JSON/CSV files

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

