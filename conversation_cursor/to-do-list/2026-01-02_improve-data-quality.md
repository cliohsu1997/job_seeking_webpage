# To-Do List: 2026-01-02 - Improve Data Quality

**Corresponds to**: Phase 2F: IMPROVE DATA QUALITY in `conversation_cursor/progress/latest.md`

**Reference**: See `data/processed/DIAGNOSTIC_ANALYSIS.md` for detailed problem analysis, statistics, and recommendations.

## Context

After running the pipeline with real data (176 files), diagnostic analysis revealed:
- **0 valid listings** out of 500 after deduplication
- **3,565 critical errors** and **1,995 warnings**
- **Main issue**: Missing required fields from source webpages (2,876 instances - 76.2%)
- **Secondary issue**: Invalid URL formats - relative URLs (362 instances - 9.6%)
- **Minor issue**: File read errors (7 instances - 0.2%)

The pipeline is working correctly; the issues stem from incomplete data extraction from source webpages, not processing errors.

## Phase 2F: IMPROVE DATA QUALITY Tasks

### 📊 Analysis & Planning
- [ ] Review `data/processed/DIAGNOSTIC_ANALYSIS.md` in detail
- [ ] Analyze CSV output (`data/processed/jobs.csv`) to identify patterns in missing data
- [ ] Review diagnostic reports in `data/processed/diagnostics/` for specific error patterns
- [ ] Identify which fields should be critical vs. optional based on data availability
- [ ] Document data availability patterns by source type (university vs. institute vs. AEA)

### 🔧 Fix URL Resolution (362 instances - 9.6% of issues)

#### Normalizer URL Resolution
- [ ] Update `scripts/processor/normalizer.py` to resolve relative URLs
- [ ] Store base URL during scraping for later resolution
- [ ] Implement URL resolution logic using `urllib.parse.urljoin()` or similar
- [ ] Handle special cases: `mailto:`, `javascript:`, anchor links (`#`)
- [ ] Add validation to ensure resolved URLs are absolute
- [ ] Update tests to cover URL resolution scenarios
- [ ] Test with real data to verify URL resolution works

#### Scraper Base URL Storage
- [ ] Update scrapers to store base URL with each extracted listing
- [ ] Ensure `source_url` field contains absolute URL when available
- [ ] Pass base URL through parser manager to normalizer

### 📝 Improve Data Extraction (2,876 missing field instances - 76.2% of issues)

#### Link-Following Implementation ✅ COMPLETED
- [x] Add listing page detection logic (detects pages with multiple job links)
- [x] Implement link-following capability in university scraper
- [x] Implement link-following capability in institute scraper
- [x] Add configuration options (follow_links, max_links_to_follow)
- [x] Optimize URL validation and error handling
- [x] Test with real data ✅ - Results: 86.4% listings with full descriptions, 59.1% with application links
- [x] Create test file in proper test folder location

#### Location Extraction
- [x] Enhance scrapers to extract location information from detail pages
- [ ] Add fallback: extract location from university name/metadata if not in listing
- [ ] Use university location database or config file as fallback
- [ ] Improve location parser to handle more edge cases
- [ ] Test location extraction with real data

#### Deadline Extraction
- [x] Improve deadline extraction from detail pages
- [ ] Add pattern matching for common deadline formats
- [ ] Handle "rolling" or "open until filled" deadlines
- [x] Extract deadline from description text if not in structured format
- [ ] Test deadline extraction improvements

#### Description & Requirements Extraction
- [x] Enhance scrapers to extract full job descriptions from detail pages
- [x] Add logic to follow links to individual job postings when available
- [x] Improve text extraction from various HTML structures
- [ ] Handle multi-page job descriptions
- [x] Extract requirements from description text if not in separate field
- [ ] Test description/requirements extraction with real data

#### Application Link Extraction
- [x] Improve application link extraction with prominent link detection
- [x] Handle cases where application is via email (extract contact_email)
- [ ] Follow redirects to get final application URL
- [ ] Validate application links are accessible
- [ ] Test application link extraction with real data

#### Source URL Tracking
- [x] Ensure all listings have `source_url` field populated (detail page URL)
- [x] Store original scraped URL even if application_link is different
- [ ] Track URL resolution chain for debugging

### 🛠️ Implement Tiered Validation

#### Schema Updates
- [ ] Review `scripts/processor/schema.py` to identify critical vs. optional fields
- [ ] Mark truly optional fields (e.g., `deadline`, `description`, `requirements`) as optional
- [ ] Keep critical fields required (e.g., `id`, `title`, `institution`)
- [ ] Add field importance levels (critical, important, optional)
- [ ] Update schema documentation

#### Validator Updates
- [ ] Update `scripts/processor/validator.py` to support tiered validation
- [ ] Implement validation levels: strict, standard, lenient
- [ ] Add quality scores based on completeness
- [ ] Generate separate validation reports for each level
- [ ] Update tests for tiered validation

#### Pipeline Integration
- [ ] Update `scripts/processor/pipeline.py` to use tiered validation
- [ ] Generate separate outputs: complete listings, partial listings, minimal listings
- [ ] Add quality metrics to output metadata
- [ ] Update archive to include quality scores

### 🔄 Handle Missing Data Gracefully

#### Default Values
- [ ] Define sensible defaults for optional fields
- [ ] Add default location based on institution if not available
- [ ] Add default deadline handling (e.g., "Not specified")
- [ ] Implement fallback mechanisms for missing critical fields

#### Data Enrichment
- [ ] Create university location database/config file
- [ ] Add enrichment step to fill missing location data
- [ ] Implement enrichment from external sources if available
- [ ] Add confidence scores for enriched data

#### Error Handling
- [ ] Improve error handling for missing data
- [ ] Add warnings instead of errors for missing optional fields
- [ ] Log missing data patterns for analysis
- [ ] Track data completeness metrics

### 🐛 Fix File Reading Issues (7 instances - 0.2%)

#### File Reading Improvements
- [ ] Investigate the 7 files that couldn't be read
- [ ] Add better encoding detection (try multiple encodings)
- [ ] Handle corrupted or empty files gracefully
- [ ] Add retry logic for file reading
- [ ] Improve error messages for file read failures
- [ ] Test with problematic files

#### Parser Manager Updates
- [ ] Update `scripts/processor/parser_manager.py` to handle encoding issues
- [ ] Add encoding detection and conversion
- [ ] Handle malformed HTML/XML gracefully
- [ ] Add better error reporting for file issues

### 📈 Testing & Validation

#### Unit Tests
- [ ] Add tests for URL resolution functionality
- [ ] Add tests for improved data extraction
- [ ] Add tests for tiered validation
- [ ] Add tests for default values and fallbacks
- [ ] Add tests for file reading improvements
- [ ] Ensure all existing tests still pass

#### Integration Tests
- [ ] Run pipeline with real data after improvements
- [ ] Compare validation results before/after improvements
- [ ] Verify URL resolution works correctly
- [ ] Verify data extraction improvements increase valid listings
- [ ] Check that quality scores are accurate

#### Data Quality Metrics
- [ ] Track improvement in validation pass rate
- [ ] Track reduction in missing field errors
- [ ] Track URL resolution success rate
- [ ] Generate before/after comparison report

### 📚 Documentation

#### Code Documentation
- [ ] Document URL resolution logic
- [ ] Document tiered validation approach
- [ ] Document default values and fallbacks
- [ ] Update docstrings for improved functions

#### Process Documentation
- [ ] Document data extraction improvements
- [ ] Document validation strategy changes
- [ ] Update README with new validation approach
- [ ] Create guide for handling missing data

### 🎯 Success Criteria

- [ ] Validation pass rate increases significantly (target: >50% valid listings)
- [ ] Missing field errors reduced by at least 50%
- [ ] All relative URLs resolved to absolute URLs
- [ ] File read errors resolved or handled gracefully
- [ ] Quality scores accurately reflect data completeness
- [ ] All tests passing
- [ ] Documentation updated

## Dependencies

- May need additional libraries for URL resolution (already available in stdlib)
- May need encoding detection libraries (e.g., `chardet`)
- May need university location database/config file

## Configuration Files

- [ ] Create/update `data/config/university_locations.json` for location fallbacks
- [ ] Update `data/config/processing_rules.json` with new extraction patterns
- [ ] Update `scripts/processor/schema.py` with field importance levels

## Phase 2F Status: 🚀 IN PROGRESS

**Summary**: Addressing data quality issues identified in diagnostic analysis. Focus areas: URL resolution, improved data extraction, tiered validation, and graceful handling of missing data.

**Key Objectives**:
1. Resolve relative URLs to absolute URLs (362 instances)
2. Improve extraction of missing fields (2,876 instances)
3. Implement tiered validation (critical vs. optional fields)
4. Handle missing data gracefully with defaults and fallbacks
5. Fix file reading issues (7 instances)

**Expected Outcome**: Significant increase in validation pass rate, with most listings having complete or near-complete data.

