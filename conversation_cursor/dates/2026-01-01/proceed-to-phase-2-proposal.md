# Proposal: Proceeding to Phase 2 - TRANSFORM (Data Processing)

## Overview

This proposal outlines the strategy and structure for Phase 2: TRANSFORM - Data Processing, which bridges the gap between raw scraped HTML/XML data (Phase 1) and formatted output generation (Phase 3).

## Current State

### Phase 1 Completion Status

✅ **Phase 1 (LOAD - Data Collection) is COMPLETE:**
- Base scraper framework implemented with utilities (rate limiter, retry handler, user agent)
- Parser modules created (HTML parser, RSS parser, text extractor, date parser)
- AEA JOE scraper implemented (RSS/HTML fallback)
- Generic university scraper implemented (pattern-based extraction)
- Research institute scraper implemented
- Comprehensive test suite organized by category
- 176 accessible URLs configured (70% success rate)
- Raw HTML/XML data saved to `data/raw/` directory

### Data Flow Context

```
Phase 1 (LOAD) → Phase 2 (TRANSFORM) → Phase 3 (EXPORT)
    ↓                    ↓                      ↓
Raw HTML/XML    →  Structured JSON    →  HTML/JSON/CSV Output
```

## Phase 2 Objectives

Phase 2 transforms raw scraped data into clean, structured, and deduplicated job listings ready for output generation.

### Primary Goals

1. **Parse Raw Data**: Extract structured job information from raw HTML/XML files
2. **Normalize Data**: Standardize formats, dates, field names, and values
3. **Deduplicate Entries**: Identify and merge duplicate job listings from different sources
4. **Validate Data**: Ensure data quality and completeness against defined schema
5. **Enrich Data**: Add computed fields (e.g., ID generation, region detection, job type classification)
6. **Output Structured Data**: Save processed data to `data/processed/` as JSON and CSV

## Phase 2 Structure

### 1. Core Processing Pipeline

```
Raw Data (data/raw/)
    ↓
[0] Diagnostic Tracker (tracks issues throughout pipeline)
    ├─→ Track URL accessibility issues
    ├─→ Track scraping failures
    ├─→ Track parsing failures
    ├─→ Track extraction failures
    └─→ Generate diagnostic reports
    ↓
[1] Parser Manager
    ├─→ Load raw HTML/XML files
    ├─→ Route to appropriate parser (AEA, university, institute)
    ├─→ Extract structured data (using existing parsers from Phase 1)
    └─→ Track parsing success/failure per source
    ↓
[2] Data Normalizer
    ├─→ Normalize dates (YYYY-MM-DD format)
    ├─→ Normalize location formats
    ├─→ Standardize job types
    ├─→ Clean text fields
    ├─→ Normalize URL formats
    ├─→ Standardize department categories
    └─→ Track normalization issues (missing fields, format errors)
    ↓
[3] Data Enricher
    ├─→ Generate unique IDs (hash-based)
    ├─→ Detect regions from location
    ├─→ Classify job types (tenure-track, visiting, postdoc, etc.)
    ├─→ Extract specializations from description
    ├─→ Parse required materials
    ├─→ Add metadata (processing timestamp)
    └─→ Track enrichment failures (missing data for classification)
    ↓
[4] Deduplicator
    ├─→ Identify duplicates (institution + title + deadline)
    ├─→ Merge duplicate entries (keep most complete data)
    ├─→ Track source aggregation
    └─→ Flag new vs. existing listings
    ↓
[5] Data Validator
    ├─→ Validate against schema
    ├─→ Check required fields
    ├─→ Validate date formats
    ├─→ Validate URL formats
    ├─→ Flag incomplete entries
    └─→ Generate validation report
    ↓
[6] Diagnostic Report Generator
    ├─→ Analyze diagnostic data from all stages
    ├─→ Identify root causes (URL, scraping, parsing, extraction)
    ├─→ Generate diagnostic report with recommendations
    └─→ Output diagnostic report (data/processed/diagnostics/)
    ↓
Processed Data (data/processed/)
    ├─→ jobs.json (structured JSON)
    ├─→ jobs.csv (CSV for spreadsheet import)
    └─→ diagnostics/ (diagnostic reports and logs)
```

### 2. Module Organization

```
scripts/processor/
├── __init__.py
├── pipeline.py              # Main processing pipeline orchestrator
├── parser_manager.py        # Routes raw data to appropriate parsers
├── normalizer.py            # Data normalization (dates, formats, etc.)
├── enricher.py              # Data enrichment (IDs, classifications, metadata)
├── deduplicator.py          # Duplicate detection and merging
├── validator.py             # Schema validation and quality checks
├── schema.py                # Data schema definition and validation rules
├── diagnostics.py           # Diagnostic tracking and root cause analysis
└── utils/
    ├── __init__.py
    ├── id_generator.py      # Generate unique IDs for job listings
    ├── location_parser.py   # Parse and normalize location data
    └── text_cleaner.py      # Text cleaning utilities
```

### 3. Data Schema Definition

#### Required Fields

**Core Identification:**
- `id`: Unique identifier (hash-based on institution + title + deadline)
- `title`: Job title
- `institution`: Institution name
- `institution_type`: "university", "research_institute", "think_tank", "job_portal"
- `department`: Department name
- `department_category`: "Economics", "Management", "Marketing", "Other"

**Location:**
- `location`: Object with `city`, `state`/`province`, `country`, `region`

**Job Details:**
- `job_type`: "tenure-track", "visiting", "postdoc", "lecturer", "other"
- `deadline`: ISO date format (YYYY-MM-DD)
- `deadline_display`: Human-readable date format
- `start_date`: When position begins (if specified, YYYY-MM-DD)
- `description`: Full job description text
- `requirements`: Qualifications and requirements
- `specializations`: Array of research fields/areas

**Application Information:**
- `application_link`: Direct URL to apply
- `application_portal`: Portal name if different (e.g., "Interfolio", "AcademicJobsOnline")
- `contact_email`: Contact email
- `contact_person`: Contact name (if available)
- `materials_required`: Object with required materials details

**Metadata:**
- `source`: Source identifier ("aea", "university_website", "institute_website")
- `source_url`: Original URL where listing was found
- `sources`: Array of sources (for deduplicated entries)
- `scraped_date`: Date when data was collected (YYYY-MM-DD)
- `processed_date`: Date when data was processed (YYYY-MM-DD)
- `last_updated`: Date when posting was last modified (if available)
- `is_active`: Whether listing is still open
- `is_new`: Whether this is a new listing (compared to previous run)

#### Schema Example

```json
{
  "id": "abc123def456...",
  "title": "Assistant Professor of Economics",
  "institution": "Harvard University",
  "institution_type": "university",
  "department": "Department of Economics",
  "department_category": "Economics",
  "location": {
    "city": "Cambridge",
    "state": "MA",
    "country": "United States",
    "region": "united_states"
  },
  "job_type": "tenure-track",
  "deadline": "2025-01-15",
  "deadline_display": "January 15, 2025",
  "start_date": "2025-09-01",
  "application_link": "https://academicpositions.harvard.edu/...",
  "application_portal": "Harvard Academic Positions",
  "contact_email": "econ-jobs@harvard.edu",
  "contact_person": "Dr. Jane Smith",
  "materials_required": {
    "cv": true,
    "cover_letter": true,
    "research_statement": true,
    "teaching_statement": true,
    "research_papers": "Job Market Paper + 2 additional papers",
    "letters_of_recommendation": 3,
    "other": ["Transcripts", "Diversity Statement"]
  },
  "description": "Full job description text...",
  "requirements": "PhD in Economics or related field required...",
  "specializations": ["Macroeconomics", "Monetary Economics"],
  "salary_range": "Not disclosed",
  "source": "university_website",
  "source_url": "https://economics.harvard.edu/faculty/positions",
  "sources": ["university_website"],
  "scraped_date": "2025-12-31",
  "processed_date": "2026-01-01",
  "last_updated": "2025-12-20",
  "is_active": true,
  "is_new": true
}
```

### 4. Processing Steps Detail

#### Step 1: Parser Manager

**Purpose**: Orchestrate extraction of structured data from raw HTML/XML files

**Responsibilities**:
- Scan `data/raw/` directory for HTML/XML files
- Identify source type (AEA, university, institute) based on file location/structure
- Route to appropriate extraction logic (reuse Phase 1 parsers)
- Extract job listings into structured dictionaries
- Handle parsing errors gracefully

**Implementation Notes**:
- Reuse existing parsers from `scripts/scraper/parsers/`
- Create wrapper to adapt scraper output format to processor input format
- Support batch processing of multiple files
- Log parsing statistics (success/failure counts)

#### Step 2: Data Normalizer

**Purpose**: Standardize all data formats and values

**Normalization Tasks**:
- **Dates**: Convert all date formats to YYYY-MM-DD, generate human-readable display format
- **Locations**: Parse and structure location data (city, state/province, country, region)
- **Job Types**: Standardize job type classifications (normalize variations like "Tenure Track" → "tenure-track")
- **Text Fields**: Clean whitespace, normalize encoding, handle special characters
- **URLs**: Normalize URL formats, resolve relative URLs, validate URLs
- **Department Categories**: Map department names to standard categories (Economics, Management, Marketing, Other)
- **Contact Information**: Normalize email formats, parse contact person names

**Implementation Notes**:
- Use existing date parser from Phase 1
- Create location parsing rules for different countries/regions
- Handle edge cases and ambiguous data gracefully
- Log normalization changes for debugging
- **Diagnostic Integration**: Track normalization failures
  - Track sources with invalid date formats
  - Track sources with unparseable location data
  - Track sources with missing required fields after normalization

#### Step 3: Data Enricher

**Purpose**: Add computed fields and enrich data with additional information

**Enrichment Tasks**:
- **ID Generation**: Create unique hash-based IDs (SHA256 of institution + title + deadline)
- **Region Detection**: Auto-detect region from location data (united_states, mainland_china, other_countries)
- **Job Type Classification**: Classify job types from title/description keywords
- **Specialization Extraction**: Extract research fields from description using keyword matching
- **Materials Parsing**: Parse required materials from description/requirements text
- **Metadata Addition**: Add processing timestamp, source tracking
- **Campus Detection**: Extract campus information for multi-campus universities

**Implementation Notes**:
- Use keyword matching and pattern recognition for classification
- Keep enrichment rules configurable (consider `data/config/processing_rules.json`)
- Handle cases where enrichment fails (mark as unknown/other)
- Make enrichment extensible for future improvements
- **Diagnostic Integration**: Track enrichment failures
  - Track sources where region detection failed
  - Track sources where job type classification failed
  - Track sources where specialization extraction failed

#### Step 4: Deduplicator

**Purpose**: Identify and merge duplicate job listings from multiple sources

**Deduplication Strategy**:
- **Matching Criteria**: Match on institution + title + deadline (with fuzzy matching for title variations)
- **Merge Logic**: Keep most complete entry (prefer entry with more filled fields)
- **Source Aggregation**: Combine sources array to track all sources for merged entries
- **New Listing Detection**: Compare against previous processed data to flag new listings
- **Conflict Resolution**: When merging, prefer more recent data or data from primary sources (AEA > university > institute)

**Implementation Notes**:
- Use fuzzy string matching for title variations (fuzzywuzzy or similar)
- Handle edge cases (e.g., same job posted with different deadlines)
- Maintain deduplication log for transparency
- Support incremental processing (compare against previous run)

#### Step 5: Data Validator

**Purpose**: Validate processed data against schema and quality standards

**Validation Checks**:
- **Schema Validation**: Ensure all required fields present, types correct
- **Date Validation**: Verify dates are valid and in correct format
- **URL Validation**: Check URLs are valid and accessible (optional, can be slow)
- **Completeness Check**: Flag entries missing critical fields
- **Data Quality**: Check for suspicious values, inconsistencies
- **Generate Validation Report**: Log validation results, statistics

**Implementation Notes**:
- Use JSON Schema or custom validation logic
- Separate critical vs. warning-level validation issues
- Allow partial validation (some fields can be optional)
- Generate validation report for review
- **Diagnostic Integration**: Track validation failures
  - Track sources with schema validation errors
  - Track sources with invalid data formats
  - Track sources with incomplete data

#### Step 6: Diagnostic Report Generator

**Purpose**: Analyze diagnostic data and generate reports identifying root causes of data extraction failures

**Responsibilities**:
- Aggregate diagnostic data from all pipeline stages
- Identify root causes (URL issues, scraping issues, parsing issues, extraction issues)
- Categorize issues by type and severity
- Generate actionable recommendations for fixing issues
- Create human-readable diagnostic reports
- Generate summary statistics

**Diagnostic Analysis**:
- **URL Issues**: Identify URLs that are not accessible, return errors, or have moved
- **Scraping Issues**: Identify sources where scraping failed (HTTP errors, timeouts, empty responses)
- **Parsing Issues**: Identify sources where HTML structure changed or parser can't find elements
- **Extraction Issues**: Identify sources where data was found but extraction failed or returned incomplete data
- **Normalization Issues**: Identify sources with invalid formats that couldn't be normalized
- **Enrichment Issues**: Identify sources where enrichment failed due to insufficient data

**Output Reports**:
- `diagnostics_YYYY-MM-DD.json`: Structured diagnostic data (machine-readable)
- `diagnostics_YYYY-MM-DD_report.txt`: Human-readable diagnostic report
- `url_issues.json`: URLs with accessibility problems
- `scraping_issues.json`: Sources with scraping failures
- `parsing_issues.json`: Sources with parsing failures
- `extraction_issues.json`: Sources with extraction failures
- `normalization_issues.json`: Sources with normalization problems
- `enrichment_issues.json`: Sources with enrichment failures
- `summary_report.txt`: High-level summary with statistics and recommendations

**Implementation Notes**:
- Track source URL, institution name, and stage where failure occurred
- Provide recommendations (e.g., "Check if URL is still valid", "HTML structure may have changed", "Parser needs update")
- Group similar issues together for easier review
- Include statistics (total sources, successful, failed by category)

### 5. Output Format

**Primary Output**: `data/processed/jobs.json`
- Single JSON file containing array of all processed job listings
- Sorted by deadline (ascending) with active listings first
- Includes metadata about processing run

**Secondary Output**: `data/processed/jobs.csv`
- CSV format for spreadsheet import and analysis
- Flattened structure (nested objects converted to columns)
- Includes all key fields

**Archive**: `data/processed/archive/YYYY-MM-DD_jobs.json`
- Historical snapshots for tracking changes over time
- Used for new listing detection and trend analysis

## Implementation Strategy

### Phase 2A: Foundation (Core Pipeline)

1. Create processor module structure
2. Define data schema in `schema.py`
3. Implement parser manager (reuse Phase 1 parsers)
4. Implement basic normalizer (dates, text cleaning)
5. Implement ID generator
6. Create simple pipeline to process sample data
7. Test with small dataset

### Phase 2B: Normalization & Enrichment

1. Complete normalizer (locations, job types, URLs, departments)
2. Implement enricher (region detection, job type classification)
3. Implement specialization extraction
4. Implement materials parsing
5. Test normalization and enrichment logic

### Phase 2C: Deduplication

1. Implement deduplicator with matching logic
2. Implement merge logic
3. Implement new listing detection (compare against archive)
4. Test deduplication with overlapping sources

### Phase 2D: Validation & Quality

1. Implement validator with schema checks
2. Create validation report generator
3. Implement completeness checks
4. Test validation with various data quality scenarios

### Phase 2E: Integration & Testing

1. Integrate all components into main pipeline
2. Create comprehensive test suite
3. Process full dataset end-to-end
4. Validate output quality
5. Performance optimization

## Testing Strategy

### Unit Tests

- Test each module independently (normalizer, enricher, deduplicator, validator)
- Test edge cases and error handling
- Test with various data formats and quality levels

### Integration Tests

- Test pipeline with real scraped data
- Test end-to-end processing workflow
- Test deduplication with overlapping sources
- Test validation and error reporting

### Data Quality Tests

- Validate output schema
- Check data completeness
- Verify deduplication accuracy
- Test with various input data quality levels

## Dependencies

### New Dependencies (if needed)

- `jsonschema`: For schema validation
- `fuzzywuzzy` or `rapidfuzz`: For fuzzy string matching in deduplication
- `pydantic`: Optional, for data validation and parsing (alternative to custom schema)

### Existing Dependencies (reuse from Phase 1)

- All parser modules from `scripts/scraper/parsers/`
- Date parsing utilities
- Text extraction utilities

## Configuration

### New Configuration File: `data/config/processing_rules.json`

Define rules for:
- Job type classification keywords
- Specialization extraction keywords
- Materials parsing patterns
- Region mapping rules
- Location parsing patterns

Example structure:
```json
{
  "job_type_keywords": {
    "tenure-track": ["tenure track", "tenure-track", "assistant professor"],
    "visiting": ["visiting", "temporary"],
    "postdoc": ["postdoc", "post-doctoral", "postdoctoral"]
  },
  "specialization_keywords": {
    "macroeconomics": ["macro", "monetary", "fiscal"],
    "labor": ["labor", "employment", "wage"],
    "microeconomics": ["micro", "game theory", "auction"]
  },
  "region_mapping": {
    "united_states": ["United States", "USA", "US"],
    "mainland_china": ["China", "PRC", "People's Republic of China"],
    "united_kingdom": ["United Kingdom", "UK", "Britain"]
  }
}
```

## Challenges & Solutions

### Challenge 1: Parsing Inconsistent Data Formats

**Solution**: 
- Robust normalization with fallback values
- Pattern matching for various formats
- Manual review and adjustment of edge cases

### Challenge 2: Accurate Deduplication

**Solution**:
- Fuzzy matching for title variations
- Multiple matching criteria (institution, title, deadline, location)
- Manual review queue for ambiguous cases

### Challenge 3: Data Quality Variations

**Solution**:
- Comprehensive validation with severity levels
- Flag incomplete entries instead of rejecting
- Validation reports for manual review

### Challenge 4: Performance with Large Datasets

**Solution**:
- Batch processing
- Efficient data structures
- Parallel processing where possible
- Incremental processing (process only new/changed files)

## Success Criteria

Phase 2 is complete when:

1. ✅ All raw HTML/XML files can be parsed into structured data
2. ✅ All data is normalized to standard formats
3. ✅ Duplicate listings are accurately identified and merged
4. ✅ Data validation ensures quality and completeness
5. ✅ Processed data is saved in JSON and CSV formats
6. ✅ Diagnostic tracking identifies root causes of data extraction failures
7. ✅ Diagnostic reports provide actionable recommendations for fixing issues
8. ✅ Comprehensive test suite passes
9. ✅ Processing pipeline handles errors gracefully with diagnostic tracking
10. ✅ Documentation is complete

## Next Steps After Phase 2

Once Phase 2 is complete, we'll proceed to **Phase 3: EXPORT - Output Generation**, which will:
- Generate HTML webpage from processed JSON
- Create styled, filterable job listings page
- Export to JSON/CSV formats for programmatic access
- Implement search and filtering functionality

## Files to Create

1. `scripts/processor/pipeline.py` - Main pipeline orchestrator
2. `scripts/processor/parser_manager.py` - Route raw data to parsers
3. `scripts/processor/normalizer.py` - Data normalization
4. `scripts/processor/enricher.py` - Data enrichment
5. `scripts/processor/deduplicator.py` - Deduplication logic
6. `scripts/processor/validator.py` - Data validation
7. `scripts/processor/schema.py` - Schema definition
8. `scripts/processor/diagnostics.py` - Diagnostic tracking and root cause analysis
9. `scripts/processor/utils/id_generator.py` - ID generation
10. `scripts/processor/utils/location_parser.py` - Location parsing
11. `scripts/processor/utils/text_cleaner.py` - Text cleaning
12. `data/config/processing_rules.json` - Processing rules configuration
13. Test files in `tests/transform-data-processing/`

---

**Status**: Proposal for review
**Date**: 2026-01-01
**Related Phase**: Phase 2 - TRANSFORM (Data Processing)
**Previous Phase**: Phase 1 - LOAD (Data Collection) ✅ COMPLETE
**Next Phase**: Phase 3 - EXPORT (Output Generation)

