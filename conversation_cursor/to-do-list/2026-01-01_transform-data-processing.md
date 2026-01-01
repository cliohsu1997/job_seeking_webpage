# To-Do List: 2026-01-01 - Transform Data Processing

**Corresponds to**: Phase 2: TRANSFORM - Data Processing in `conversation_cursor/progress/latest.md`

## Phase 2: TRANSFORM - Data Processing Tasks

### ✅ Strategy & Planning (COMPLETED)
- [x] Created Phase 2 proposal (`proceed-to-phase-2-proposal.md`) with detailed structure and implementation strategy
- [x] Defined data schema and processing pipeline structure
- [x] Outlined module organization and responsibilities
- [x] Documented processing steps and data flow

### 📁 Foundation Setup
- [x] Create `scripts/processor/` directory structure
- [x] Create `scripts/processor/__init__.py`
- [x] Create `scripts/processor/utils/` directory
- [x] Create `scripts/processor/utils/__init__.py`
- [x] Create `data/config/processing_rules.json` with initial processing rules
- [x] Create `data/processed/diagnostics/` directory for diagnostic reports
- [x] Create `tests/transform-data-processing/` directory structure with `__init__.py`

### 📋 Data Schema Definition
- [x] Create `scripts/processor/schema.py` with data schema definition
- [x] Define required fields and data types (id, title, institution, location, deadline, etc.)
- [x] Define optional fields and default values
- [x] Create schema validation functions
- [x] Document schema structure and examples in docstrings

### 🔧 Phase 2A: Core Pipeline Foundation

#### Diagnostic Tracker
- [x] Create `scripts/processor/diagnostics.py`
- [x] Implement `DiagnosticTracker` class to track issues throughout pipeline
- [x] Implement tracking methods for: URL issues, scraping issues, parsing issues, extraction issues, normalization issues, enrichment issues
- [x] Store diagnostic data in structured format (dictionary/JSON)
- [x] Add methods to retrieve diagnostic data by category

#### Text Cleaner Utility
- [x] Create `scripts/processor/utils/text_cleaner.py`
- [x] Implement text cleaning functions (whitespace, encoding, HTML tags removal)
- [x] Implement special character handling

#### ID Generator
- [x] Create `scripts/processor/utils/id_generator.py`
- [x] Implement unique hash-based ID generation (SHA256 of institution + title + deadline)
- [x] Handle edge cases (missing fields, variations)

#### Basic Normalizer
- [x] Create `scripts/processor/normalizer.py`
- [x] Implement date normalization (convert to YYYY-MM-DD, generate display format) - reuse Phase 1 date parser
- [x] Implement text cleaning (use text_cleaner utility)
- [x] Implement basic URL normalization (format, resolve relative URLs)
- [x] Add logging for normalization changes
- [x] Integrate diagnostic tracking for normalization failures

#### Parser Manager
- [x] Create `scripts/processor/parser_manager.py`
- [x] Implement function to scan `data/raw/` directory for HTML/XML files
- [x] Implement source type identification (AEA, university, institute) based on directory structure
- [x] Implement routing logic structure (placeholder for Phase 1 parser integration)
- [x] Create wrapper structure for scraper output format adaptation
- [x] Implement batch processing of multiple files
- [x] Add logging for parsing statistics (success/failure counts)
- [x] Integrate diagnostic tracking: Track which sources failed parsing and why

#### Simple Pipeline
- [x] Create `scripts/processor/pipeline.py` with basic structure
- [x] Implement basic pipeline orchestrator that calls parser manager → normalizer → ID generator
- [x] Implement basic output to JSON format (`data/processed/jobs.json`)
- [ ] Test pipeline with small sample dataset (pending Phase 1 parser integration)
- [ ] Verify output structure matches schema (pending Phase 1 parser integration)

### 🔄 Phase 2B: Complete Normalization & Enrichment

#### Location Parser Utility
- [x] Create `scripts/processor/utils/location_parser.py`
- [x] Implement location parsing for different countries/regions
- [x] Handle various location formats (city/state/country, city/country, etc.)
- [x] Implement region detection from location data (united_states, mainland_china, other_countries)
- [x] Create comprehensive test suite (`tests/transform-data-processing/test_location_parser.py`) with 41 tests, all passing

#### Complete Normalizer
- [ ] Extend `scripts/processor/normalizer.py` with:
  - Location normalization (use location_parser utility)
  - Job type normalization (standardize variations using processing_rules.json)
  - Department category mapping (Economics, Management, Marketing, Other)
  - Contact information normalization (email formats, contact person parsing)
  - Materials required parsing from text
- [ ] Add comprehensive error handling for edge cases
- [ ] Integrate diagnostic tracking for normalization failures

#### Data Enricher
- [ ] Create `scripts/processor/enricher.py`
- [ ] Implement region detection from location (use location_parser)
- [ ] Implement job type classification from title/description keywords (use processing_rules.json)
- [ ] Implement specialization extraction from description (keyword matching from processing_rules.json)
- [ ] Implement materials parsing (extract required materials from description/requirements)
- [ ] Implement metadata addition (processing timestamp, source tracking)
- [ ] Add configuration support for enrichment rules (from processing_rules.json)
- [ ] Handle cases where enrichment fails (mark as unknown/other)
- [ ] Integrate diagnostic tracking for enrichment failures

### 🔗 Phase 2C: Deduplication

#### Deduplicator Implementation
- [ ] Create `scripts/processor/deduplicator.py`
- [ ] Implement matching criteria (institution + title + deadline with fuzzy matching)
- [ ] Implement fuzzy string matching for title variations (use rapidfuzz library)
- [ ] Implement merge logic (keep most complete entry, prefer entries with more filled fields)
- [ ] Implement source aggregation (combine sources array for merged entries)
- [ ] Implement conflict resolution (prefer more recent data, prefer AEA > university > institute)
- [ ] Add logging for deduplication decisions

#### New Listing Detection
- [ ] Implement comparison against previous processed data (from archive)
- [ ] Implement `is_new` flag detection
- [ ] Implement `is_active` detection (compare with previous listings)

### ✅ Phase 2D: Validation & Quality

#### Data Validator
- [ ] Create `scripts/processor/validator.py`
- [ ] Implement schema validation (required fields, types) - use jsonschema or custom validation
- [ ] Implement date validation (valid dates, correct format)
- [ ] Implement URL validation (format validation, optional accessibility check)
- [ ] Implement completeness checks (flag entries missing critical fields)
- [ ] Implement data quality checks (suspicious values, inconsistencies)
- [ ] Separate critical vs. warning-level validation issues
- [ ] Allow partial validation (some fields optional)
- [ ] Integrate diagnostic tracking for validation failures

#### Validation Report Generator
- [ ] Implement validation report generation in `scripts/processor/validator.py`
- [ ] Log validation results and statistics
- [ ] Create summary report (total listings, validation issues, completeness metrics)

#### Diagnostic Report Generator
- [ ] Extend `scripts/processor/diagnostics.py` with report generation
- [ ] Aggregate diagnostic data from all pipeline stages
- [ ] Identify root causes (URL issues, scraping issues, parsing issues, extraction issues)
- [ ] Categorize issues by type and severity
- [ ] Generate actionable recommendations for fixing issues
- [ ] Create human-readable diagnostic reports
- [ ] Generate summary statistics
- [ ] Output structured diagnostic data (JSON format) to `data/processed/diagnostics/`
- [ ] Output category-specific diagnostic files (url_issues.json, scraping_issues.json, etc.)
- [ ] Output high-level summary report

### 🧪 Phase 2E: Integration & Testing

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
- [ ] Test with edge cases and error scenarios
- [ ] Run full test suite and ensure all tests pass

#### Performance & Optimization
- [ ] Optimize processing performance (batch processing, efficient data structures)
- [ ] Implement incremental processing (process only new/changed files)
- [ ] Add performance metrics and logging

#### Documentation
- [ ] Document processor module usage in docstrings
- [ ] Document data schema and field descriptions
- [ ] Document processing rules configuration
- [ ] Update README with processor information

### 📊 Data Quality Validation
- [ ] Process sample dataset and review output quality
- [ ] Validate deduplication accuracy manually
- [ ] Validate normalization results
- [ ] Validate enrichment results
- [ ] Review validation reports and fix any issues
- [ ] Iterate on processing rules based on results

## Dependencies to Add

- [ ] Add `jsonschema` for schema validation
- [ ] Add `rapidfuzz` for fuzzy string matching in deduplication
- [ ] Update `pyproject.toml` with new dependencies
- [ ] Run `poetry lock` and `poetry install`

## Configuration Files

- [ ] Create `data/config/processing_rules.json` with:
  - Job type classification keywords
  - Specialization extraction keywords
  - Materials parsing patterns
  - Region mapping rules
  - Location parsing patterns

## Phase 2 Status: 🚀 IN PROGRESS

**Summary**: Phase 2 proposal created with detailed structure. Implementation beginning with foundation setup and core pipeline.

**Key Objectives**:
1. Parse raw HTML/XML data into structured format
2. Normalize all data formats and values
3. Enrich data with computed fields and classifications
4. Deduplicate listings from multiple sources
5. Validate data quality and completeness
6. Output processed data in JSON and CSV formats

**Current Phase**: Phase 2A - Core Pipeline Foundation (✅ COMPLETED), Phase 2B - Complete Normalization & Enrichment (🚀 IN PROGRESS)

**Phase 2A Status**: All core pipeline foundation components implemented and tested successfully.
- ✅ Diagnostics tracker
- ✅ Text cleaner utility  
- ✅ ID generator utility
- ✅ Basic normalizer
- ✅ Parser manager (file scanning and routing structure)
- ✅ Basic pipeline orchestrator
- ✅ Component tests created and passing

**Phase 2B Status**: Location parser utility completed.
- ✅ Location parser utility (`utils/location_parser.py`)
  - ✅ US location parsing (all 50 states + DC)
  - ✅ China location parsing (Chinese characters and English)
  - ✅ Generic location parsing (other countries)
  - ✅ Region detection (united_states, mainland_china, united_kingdom, canada, australia, other_countries)
  - ✅ Comprehensive test suite (41 tests, all passing)

**Next Steps**: 
- Option 1: Integrate Phase 1 parsers into parser manager for actual extraction
- Option 2: Continue Phase 2B - integrate location parser into normalizer, complete normalizer, implement enricher
