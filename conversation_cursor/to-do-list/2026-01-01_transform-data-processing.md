# To-Do List: 2026-01-01 - Transform Data Processing

**Corresponds to**: Phase 2: TRANSFORM - Data Processing in `conversation_cursor/progress/latest.md`

## Phase 2: TRANSFORM - Data Processing Tasks

### Strategy & Planning
- [x] Created Phase 2 proposal (`proceed-to-phase-2-proposal.md`) with detailed structure and implementation strategy
- [x] Defined data schema and processing pipeline structure
- [x] Outlined module organization and responsibilities
- [x] Documented processing steps and data flow

### Foundation Setup
- [ ] Create `scripts/processor/` directory structure
- [ ] Create `scripts/processor/__init__.py`
- [ ] Create `scripts/processor/utils/` directory
- [ ] Create `scripts/processor/utils/__init__.py`
- [ ] Create `data/config/processing_rules.json` with initial processing rules
- [ ] Create `data/processed/diagnostics/` directory for diagnostic reports
- [ ] Create `tests/transform-data-processing/` directory structure

### Data Schema Definition
- [ ] Create `scripts/processor/schema.py` with data schema definition
- [ ] Define required fields and data types
- [ ] Define optional fields and default values
- [ ] Create schema validation functions
- [ ] Document schema structure and examples
- [ ] Test schema validation with sample data

### Phase 2A: Core Pipeline Foundation

#### Diagnostic Tracker
- [ ] Create `scripts/processor/diagnostics.py`
- [ ] Implement diagnostic tracking class to track issues throughout pipeline
- [ ] Implement tracking for URL issues (not accessible, errors, moved)
- [ ] Implement tracking for scraping issues (HTTP errors, timeouts, empty responses)
- [ ] Implement tracking for parsing issues (HTML structure changed, parser can't find elements)
- [ ] Implement tracking for extraction issues (data found but extraction failed, missing fields)
- [ ] Implement tracking for normalization issues (invalid formats, unparseable data)
- [ ] Implement tracking for enrichment issues (insufficient data for classification)
- [ ] Store diagnostic data in structured format (JSON)
- [ ] Test diagnostic tracking with various failure scenarios

#### Parser Manager
- [ ] Create `scripts/processor/parser_manager.py`
- [ ] Implement function to scan `data/raw/` directory for HTML/XML files
- [ ] Implement source type identification (AEA, university, institute)
- [ ] Implement routing logic to appropriate extraction methods
- [ ] Create wrapper to adapt scraper output format to processor input format
- [ ] Implement batch processing of multiple files
- [ ] Add logging for parsing statistics (success/failure counts)
- [ ] Handle parsing errors gracefully
- [ ] **Integrate diagnostic tracking**: Track which sources failed parsing and why
  - Check if raw HTML file exists (scraping issue)
  - Check if HTML is empty or malformed (scraping/parsing issue)
  - Check if parser found expected elements (parsing/extraction issue)
  - Check if extracted data has required fields (extraction issue)
- [ ] Test parser manager with sample raw data files

#### Basic Normalizer
- [ ] Create `scripts/processor/normalizer.py`
- [ ] Implement date normalization (convert to YYYY-MM-DD, generate display format)
- [ ] Implement text cleaning (whitespace, encoding, special characters)
- [ ] Implement basic URL normalization (format, resolve relative URLs)
- [ ] Add logging for normalization changes
- [ ] Test normalizer with various data formats

#### ID Generator
- [ ] Create `scripts/processor/utils/id_generator.py`
- [ ] Implement unique hash-based ID generation (SHA256 of institution + title + deadline)
- [ ] Handle edge cases (missing fields, variations)
- [ ] Test ID generation and uniqueness

#### Simple Pipeline
- [ ] Create `scripts/processor/pipeline.py` with basic structure
- [ ] Implement basic pipeline orchestrator that calls parser manager
- [ ] Integrate normalizer and ID generator
- [ ] Implement basic output to JSON format
- [ ] Test pipeline with small sample dataset
- [ ] Verify output structure matches schema

### Phase 2B: Complete Normalization & Enrichment

#### Complete Normalizer
- [ ] Implement location normalization (parse city, state/province, country, region)
- [ ] Implement job type normalization (standardize variations)
- [ ] Implement department category mapping (Economics, Management, Marketing, Other)
- [ ] Implement contact information normalization (email formats, contact person parsing)
- [ ] Implement materials required parsing from text
- [ ] Add comprehensive error handling for edge cases
- [ ] **Integrate diagnostic tracking**: Track normalization failures
  - Track sources with invalid date formats
  - Track sources with unparseable location data
  - Track sources with missing required fields after normalization
- [ ] Test normalizer with diverse data formats and edge cases

#### Location Parser Utility
- [ ] Create `scripts/processor/utils/location_parser.py`
- [ ] Implement location parsing for different countries/regions
- [ ] Handle various location formats (city/state/country, city/country, etc.)
- [ ] Implement region detection from location data
- [ ] Test location parsing with diverse formats

#### Text Cleaner Utility
- [ ] Create `scripts/processor/utils/text_cleaner.py`
- [ ] Implement text cleaning functions (whitespace, encoding, HTML tags)
- [ ] Implement special character handling
- [ ] Test text cleaner with various text formats

#### Data Enricher
- [ ] Create `scripts/processor/enricher.py`
- [ ] Implement region detection from location (united_states, mainland_china, other_countries)
- [ ] Implement job type classification from title/description keywords
- [ ] Implement specialization extraction from description (keyword matching)
- [ ] Implement materials parsing (extract required materials from description/requirements)
- [ ] Implement metadata addition (processing timestamp, source tracking)
- [ ] Implement campus detection for multi-campus universities
- [ ] Add configuration support for enrichment rules (from processing_rules.json)
- [ ] Handle cases where enrichment fails (mark as unknown/other)
- [ ] **Integrate diagnostic tracking**: Track enrichment failures
  - Track sources where region detection failed
  - Track sources where job type classification failed
  - Track sources where specialization extraction failed
- [ ] Test enricher with diverse job listings

### Phase 2C: Deduplication

#### Deduplicator Implementation
- [ ] Create `scripts/processor/deduplicator.py`
- [ ] Implement matching criteria (institution + title + deadline with fuzzy matching)
- [ ] Implement fuzzy string matching for title variations (use fuzzywuzzy or rapidfuzz)
- [ ] Implement merge logic (keep most complete entry, prefer entries with more filled fields)
- [ ] Implement source aggregation (combine sources array for merged entries)
- [ ] Implement conflict resolution (prefer more recent data, prefer AEA > university > institute)
- [ ] Add logging for deduplication decisions
- [ ] Test deduplicator with overlapping sources

#### New Listing Detection
- [ ] Implement comparison against previous processed data (from archive)
- [ ] Implement is_new flag detection
- [ ] Implement is_active detection (compare with previous listings)
- [ ] Test new listing detection with historical data

### Phase 2D: Validation & Quality

#### Data Validator
- [ ] Create `scripts/processor/validator.py`
- [ ] Implement schema validation (required fields, types)
- [ ] Implement date validation (valid dates, correct format)
- [ ] Implement URL validation (format validation, optional accessibility check)
- [ ] Implement completeness checks (flag entries missing critical fields)
- [ ] Implement data quality checks (suspicious values, inconsistencies)
- [ ] Separate critical vs. warning-level validation issues
- [ ] Allow partial validation (some fields optional)
- [ ] **Integrate diagnostic tracking**: Track validation failures
  - Track sources with schema validation errors
  - Track sources with invalid data formats
  - Track sources with incomplete data
- [ ] Test validator with various data quality scenarios

#### Validation Report Generator
- [ ] Implement validation report generation
- [ ] Log validation results and statistics
- [ ] Create summary report (total listings, validation issues, completeness metrics)
- [ ] Test validation reporting

#### Diagnostic Report Generator
- [ ] Implement diagnostic report generator in `scripts/processor/diagnostics.py`
- [ ] Aggregate diagnostic data from all pipeline stages
- [ ] Identify root causes (URL issues, scraping issues, parsing issues, extraction issues)
- [ ] Categorize issues by type and severity
- [ ] Generate actionable recommendations for fixing issues
- [ ] Create human-readable diagnostic reports
- [ ] Generate summary statistics
- [ ] Output structured diagnostic data (JSON format)
- [ ] Output category-specific diagnostic files (url_issues.json, scraping_issues.json, etc.)
- [ ] Output high-level summary report
- [ ] Test diagnostic report generation with various failure scenarios

### Phase 2E: Integration & Testing

#### Complete Pipeline Integration
- [ ] Integrate all components into main pipeline (`pipeline.py`)
- [ ] Implement full workflow: parse → normalize → enrich → deduplicate → validate → generate diagnostics
- [ ] Integrate diagnostic tracker throughout pipeline (wrap each stage)
- [ ] Implement output to JSON format (`data/processed/jobs.json`)
- [ ] Implement output to CSV format (`data/processed/jobs.csv`)
- [ ] Implement archive functionality (save historical snapshots to `data/processed/archive/`)
- [ ] Implement diagnostic output to `data/processed/diagnostics/`
- [ ] Add comprehensive error handling throughout pipeline
- [ ] Add logging at each stage
- [ ] Test end-to-end pipeline with full dataset
- [ ] Verify diagnostic reports accurately identify root causes

#### Testing
- [ ] Create `tests/transform-data-processing/test_schema.py`
- [ ] Create `tests/transform-data-processing/test_normalizer.py`
- [ ] Create `tests/transform-data-processing/test_enricher.py`
- [ ] Create `tests/transform-data-processing/test_deduplicator.py`
- [ ] Create `tests/transform-data-processing/test_validator.py`
- [ ] Create `tests/transform-data-processing/test_diagnostics.py`
- [ ] Create `tests/transform-data-processing/test_pipeline.py`
- [ ] Write unit tests for each module
- [ ] Write integration tests for pipeline
- [ ] Test diagnostic tracking with various failure scenarios
- [ ] Test diagnostic report generation
- [ ] Test with edge cases and error scenarios
- [ ] Test with various input data quality levels
- [ ] Run full test suite and ensure all tests pass

#### Performance & Optimization
- [ ] Optimize processing performance (batch processing, efficient data structures)
- [ ] Implement incremental processing (process only new/changed files)
- [ ] Add performance metrics and logging
- [ ] Test with large datasets

#### Documentation
- [ ] Document processor module usage
- [ ] Document data schema and field descriptions
- [ ] Document processing rules configuration
- [ ] Update README with processor information
- [ ] Document how to extend processor with new rules

### Data Quality Validation
- [ ] Process sample dataset and review output quality
- [ ] Validate deduplication accuracy manually
- [ ] Validate normalization results
- [ ] Validate enrichment results
- [ ] Review validation reports and fix any issues
- [ ] Iterate on processing rules based on results

## Phase 2 Status: 🚀 IN PROGRESS

**Summary**: Phase 2 proposal created with detailed structure. Implementation beginning with foundation setup and core pipeline.

**Key Objectives**:
1. Parse raw HTML/XML data into structured format
2. Normalize all data formats and values
3. Enrich data with computed fields and classifications
4. Deduplicate listings from multiple sources
5. Validate data quality and completeness
6. Output processed data in JSON and CSV formats

**Current Phase**: Phase 2A - Foundation Setup

**Next Steps**: Create processor module structure and begin with parser manager implementation

## Dependencies to Add

- [ ] Add `jsonschema` for schema validation (if using JSON Schema)
- [ ] Add `fuzzywuzzy` or `rapidfuzz` for fuzzy string matching in deduplication
- [ ] Optional: Consider `pydantic` for data validation and parsing (alternative to custom schema)
- [ ] Update `pyproject.toml` with new dependencies
- [ ] Run `poetry lock` and `poetry install`

## Configuration Files

- [ ] Create `data/config/processing_rules.json` with:
  - Job type classification keywords
  - Specialization extraction keywords
  - Materials parsing patterns
  - Region mapping rules
  - Location parsing patterns

