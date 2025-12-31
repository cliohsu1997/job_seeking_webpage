# Progress: High-Level Pipeline

## Pipeline Overview

The project follows a **Load → Transform → Export** workflow structure for aggregating economics faculty job listings.

## What We've Accomplished

### ✅ Phase 0: Project Setup (COMPLETED)
**Status**: All tasks completed
- Project structure designed and documented
- Complete folder structure created (data/, scripts/, templates/, static/, environment/)
- Configuration files initialized (universities.json, scraping_rules.json)
- Poetry virtual environment set up in `environment/python/venv/`
- All dependencies installed and locked
- Documentation framework established (read_it.md, .cursorrules, README.md)
- Environment management organized (tools/ and venv/ separation)
- Progress tracking system established (progress, structure, to-do lists)
- Test structure created with phase-based subfolders
- Python execution documented and tested
- **To-Do List**: `2025-12-31_project-setup.md` (all tasks completed)

## What's Next

### 🔄 Phase 1: LOAD - Data Collection (IN PROGRESS)
**Status**: Configuration setup in progress, ready for HTML parsing analysis
- [x] Scraping strategy proposal created and approved (`design-scraping-strategy.md`)
- [x] Scraping sources configuration structure designed (`scraping_sources.json`)
- [x] HTML parsing approach analysis task defined (class-based vs pattern-based comparison)
- [x] Project guidelines updated (`read_it.md` - token monitoring, proposal finding, dependency management, progress tracking, new conversation summary rule)
- [x] Initial configuration setup started (9 universities, 2 research institutes added to `scraping_sources.json`)
- [x] Dependencies installed (32 packages via Poetry)
- [x] Sample download script created (`scripts/scraper/download_samples.py`)
- [x] URL verification script created (`scripts/scraper/check_config/verify_urls.py`)
- [x] All URLs verified and updated in `scraping_sources.json` (20/20 accessible, url_status labels added)
- [ ] HTML parsing approach analysis (download samples, compare approaches)
- [ ] Base scraper framework created
- [ ] AEA JOE scraper implemented
- [ ] University scrapers implemented (Economics, Management, Marketing departments)
- [ ] Research institute and think tank scrapers implemented
- [ ] Multi-campus handling implemented
- [ ] Raw data storage validated
- **Coverage**: 
  - Mainland China: Top 100 universities (QS Economics ranking)
  - United States: Top 100 universities (QS Economics ranking)
  - Other Countries: Top 30 per country (QS Economics ranking)
  - Research institutes and think tanks
- **To-Do List**: `2025-12-31_load-data-collection.md`
- **Proposal**: `conversation_cursor/dates/2025-12-31/design-scraping-strategy.md`

### ⏸️ Phase 2: TRANSFORM - Data Processing (PENDING)
**Status**: Waiting for Phase 1
- [ ] HTML/XML parser implemented
- [ ] Data normalizer implemented
- [ ] Deduplicator implemented
- [ ] Data schema defined and validated
- **To-Do List**: To be created as `YYYY-MM-DD_transform-data-processing.md` when Phase 2 begins

### ⏸️ Phase 3: EXPORT - Output Generation (PENDING)
**Status**: Waiting for Phase 2
- [ ] HTML template created
- [ ] HTML generator implemented
- [ ] JSON/CSV generator implemented
- [ ] Webpage styling completed
- **To-Do List**: To be created as `YYYY-MM-DD_export-output-generation.md` when Phase 3 begins

## Pipeline Flow

```
[✅ COMPLETED] Setup → [🔄 NEXT] Load → [⏸️ PENDING] Transform → [⏸️ PENDING] Export
```

## Current Focus

**Phase 1: LOAD - Data Collection** is in progress. 

**Next Steps**:
1. Download sample HTML files from diverse sources (AEA JOE, universities, research institutes)
2. Analyze HTML structures to compare parsing approaches (class-based vs pattern-based)
3. Choose optimal parsing approach and document decision
4. Create base scraper framework using chosen approach
5. Implement AEA JOE scraper (priority)
