# Diagnostic Analysis Report
**Generated:** 2026-01-02 18:00:30
**Pipeline Run:** Real data processing (176 files: 1 AEA, 7 institutes, 168 universities)

## Executive Summary

The pipeline successfully processed **667 raw job listings** from scraped webpages, deduplicated them to **500 unique listings**, but **0 listings passed full validation** due to missing required information from the source webpages.

### Key Statistics
- **Raw listings parsed:** 667
- **After deduplication:** 500 (167 duplicates merged)
- **Valid listings:** 0/500
- **Critical errors:** 3,565
- **Warnings:** 1,995
- **Total issues:** 3,774

## Problem Categories

### 1. Missing Required Fields (2,876 instances - 76.2% of all issues)

**Root Cause:** The scraped webpages do not contain all the required information, or the scrapers are not extracting it properly.

**Missing Fields:**
- `location` (city, state, country, region) - **Most common**
- `deadline` and `deadline_display` - **92 instances**
- `description` - Job description text
- `requirements` - Job requirements/qualifications
- `application_link` - Direct link to apply
- `source_url` - **283 instances** - Original webpage URL

**Why This Happens:**
- Many university job pages are listing pages that link to individual job postings, not the full job details
- Some webpages use JavaScript to load content dynamically (not captured in static HTML scraping)
- Job information may be spread across multiple pages
- Some universities don't publish complete information on their main job listing pages

### 2. Invalid URL Format (362 instances - 9.6% of all issues)

**Root Cause:** The scrapers are extracting relative URLs (e.g., `/jobs`, `/cp/index.cfm?...`) instead of absolute URLs.

**Examples:**
- `/cp/index.cfm?event=jobs.listJobs&jobListid=...`
- `/life-at-swinburne/careers-employment`
- `/ajo/jobs/30624`
- `mailto:academicpositions@harvard.edu`
- `javascript:void(0);`

**Why This Happens:**
- HTML pages contain relative URLs that need to be resolved against the base URL
- The normalizer is correctly flagging these as invalid, but they need to be resolved during scraping or normalization

### 3. Parsing Errors (7 instances - 0.2% of all issues)

**Root Cause:** Some files could not be read or parsed.

**Affected Files:**
- `australia_australian_national_university_economics.html`
- `australia_university_of_adelaide_economics.html`
- `australia_university_of_melbourne_management.html`
- `australia_university_of_western_australia_economics.html`
- `us_michigan_state_university_economics.html`
- `us_university_of_massachusetts_amherst_economics.html`
- `us_university_of_oregon_economics.html`

**Why This Happens:**
- File encoding issues
- Corrupted files
- Files may be empty or malformed

### 4. Deduplication Merges (123 instances)

**Note:** These are informational, not errors. The deduplicator successfully merged 167 duplicate listings into 500 unique ones.

## Issue Breakdown by Source

| Source | Issues | Failure Rate | Main Problem |
|--------|--------|--------------|--------------|
| `university_website` | 3,127 | 82.9% | Missing required fields (location, deadline, description, etc.) |
| `normalizer` | 362 | 9.6% | Invalid URL formats (relative URLs) |
| `research_institute` | 278 | 7.4% | Missing required fields |
| `university` (parser) | 7 | 0.2% | File read errors |

## Recommendations

### Immediate Actions

1. **Improve Scraper Extraction:**
   - Enhance university scrapers to extract more fields from job listing pages
   - Add logic to follow links to individual job postings when available
   - Improve location extraction from various page formats

2. **Resolve Relative URLs:**
   - Update normalizer to resolve relative URLs using the source URL as base
   - Store base URL during scraping for later resolution

3. **Handle Missing Data:**
   - Consider making some fields optional in validation (e.g., `deadline`, `description`) if they're truly not available
   - Add default values for missing optional fields
   - Flag listings with missing critical information but don't reject them entirely

4. **Fix File Reading Issues:**
   - Investigate the 7 files that couldn't be read
   - Add better error handling and encoding detection

### Long-term Improvements

1. **Enhanced Scraping:**
   - Implement JavaScript rendering for dynamic content (Selenium/Playwright)
   - Add multi-page scraping for job details
   - Improve pattern matching for different university website structures

2. **Data Quality:**
   - Add confidence scores for extracted data
   - Implement data enrichment from external sources (e.g., university location databases)
   - Create fallback mechanisms for missing critical fields

3. **Validation Strategy:**
   - Implement tiered validation (critical vs. optional fields)
   - Allow partial validation with quality scores
   - Generate separate outputs for complete vs. incomplete listings

## Output Files

- **CSV Output:** `data/processed/jobs.csv` (500 listings, but with validation issues)
- **JSON Output:** `data/processed/jobs.json` (500 listings)
- **Diagnostic Reports:** `data/processed/diagnostics/`
  - `diagnostics_summary_latest.txt` - Human-readable summary
  - `diagnostics_summary_latest.json` - Machine-readable summary
  - `diagnostics_validation_issues_*.json` - Detailed validation errors
  - `diagnostics_parsing_issues_*.json` - Parsing errors
  - `diagnostics_normalization_issues_*.json` - Normalization errors

## Conclusion

The pipeline is working correctly - it's successfully parsing, normalizing, enriching, and deduplicating the data. However, **the main issue is that the source webpages do not contain all the required information**, or the scrapers need improvement to extract it. The 0 valid listings are due to strict schema validation requiring fields that aren't available on many university job listing pages.

**Next Steps:**
1. Review the CSV output to see what data was successfully extracted
2. Decide which fields should be optional vs. required
3. Improve scrapers to extract more complete information
4. Add URL resolution for relative URLs
5. Consider implementing tiered validation (critical vs. optional fields)

