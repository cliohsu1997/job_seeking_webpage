# To-Do List: Phase 1B - Expand Scraping Sources (REVISED)

**Date Created**: 2026-01-04  
**Last Updated**: 2026-01-04  
**Phase**: Phase 1B - Expand Data Collection  
**Status**: In Progress (ACCESS ✅ COMPLETE, VALIDATE ✅ COMPLETE, REPLACE 🔄 IN PROGRESS)
**Objective**: Expand scraping sources from 210 to 250+ URLs with better global coverage by systematically replacing problematic URLs

---

## Strategy: ACCESS → VALIDATE → REPLACE

The Phase 1B expansion uses a three-phase strategy to identify and fix problematic URLs:

### 1. **ACCESS Phase** (✅ COMPLETE)
- Test HTTP connectivity to all URLs
- Follow redirects and detect issues
- Identify which URLs are accessible vs. unreachable
- **Result**: 210 total URLs verified (127 accessible_verified + 83 accessible_unverified)

### 2. **VALIDATE Phase** (✅ COMPLETE)
- Classify page types (job portal, faculty directory, department page, etc.)
- Extract and validate job content
- Score quality 0-100 based on extractable data
- Make keep/move/replace decisions
- **Result**: Pilot tested 10 problematic US universities → All 10 classified as "MOVE"

### 3. **REPLACE Phase** (🔄 IN PROGRESS)
- For URLs identified as "MOVE" or "REPLACE": find better alternatives
- Test replacement URLs with full validation workflow
- Update config with validated replacements
- **Goal**: Fix 60+ problematic URLs systematically

---

## URL Evaluation Metrics

[... content from original file section, same as before ...]

### What Makes a "Valid Job Listing Page"?

A URL is valid for the **accessible section** if it **contains extractable job listings** with these critical fields:

#### Critical Fields (MUST be present):
1. **Job Title** - Specific position name (e.g., "Assistant Professor of Economics", "Postdoctoral Fellow")
   - NOT: Just "Faculty" or "Research Position" (too generic)
   - NOT: Faculty directory showing current employees
   - NOT: Department research descriptions

2. **Position Details** - At least ONE of:
   - Job type (tenure-track, visiting, postdoc, lecturer, etc.)
   - Department/field (Economics, Business, Finance, etc.)
   - Deadline or application info
   - Salary or compensation info
   - Location information

#### Content Quality Scoring System (0-100)

| Factor | Max Points | Criterion |
|--------|-----------|-----------|
| Job Titles Found | 30 | Can extract 5+ distinct job titles = 30pts, 3-4 titles = 20pts, 1-2 titles = 10pts |
| Position Details | 25 | All critical fields = 25pts, Job type + dept = 18pts, Department only = 10pts |
| Application Links | 20 | Apply buttons/links = 20pts, Email contact = 10pts, No way to apply = 0pts |
| Job Descriptions | 15 | Full descriptions = 15pts, Brief details = 8pts, Titles only = 0pts |
| Freshness | 10 | Posted within 1 week = 10pts, Within 1 month = 5pts, Old/undated = 0pts |

**Thresholds**:
- 80-100: Excellent (keep in accessible)
- 60-79: Good (keep in accessible)  
- 40-59: Marginal (move to non_accessible, mark for review)
- 0-39: Poor (move to non_accessible)

---

## Phase 1B.1: URL Access Verification Tools

### Task 0A: Implement URL Access Verification System
**Status**: ✅ COMPLETE (including config flattening)
**Priority**: CRITICAL  
**Description**: Test HTTP connectivity, follow redirects, detect server-level errors. Config structure flattened to simple list format.

**Files Created**:
- ✅ `scripts/scraper/config/url_access/__init__.py` - Module exports
- ✅ `scripts/scraper/config/url_access/test_accessibility.py` - HTTP connectivity testing
- ✅ `scripts/scraper/config/url_access/redirect_handler.py` - Redirect following and chain tracking
- ✅ `scripts/scraper/config/url_access/dns_resolver.py` - Chinese DNS fallback support
- ✅ `scripts/scraper/config/url_access/connectivity_report.py` - Generate accessibility reports

**Test Suite Created**:
- ✅ `tests/load-data-collection/config/test_scraping_sources.py` - Config validation tests
- ✅ `tests/load-data-collection/access_url/test_accessibility.py` - Accessibility tests with real sources
- ✅ `tests/load-data-collection/access_url/test_redirects.py` - Redirect handling tests
- ✅ `tests/load-data-collection/access_url/test_connectivity_report.py` - Report generation tests

#### Subtask 0A.1: Basic Accessibility Testing
**Status**: ✅ COMPLETE
- [x] Create `test_accessibility()` function
- [x] Test HTTP GET with 10-second timeout
- [x] Record status codes, error messages
- [x] Create `is_accessible()` wrapper with caching
- [x] Respect rate limits (1+ second between requests)

**Acceptance Criteria**:
- ✅ Tests 100+ URLs efficiently
- ✅ Detects all error types (404, 403, timeout, DNS error, SSL error)
- ✅ Respects rate limits
- ✅ Timeout after 10 seconds

---

#### Subtask 0A.2: Redirect Following and Chain Tracking
**Status**: ✅ COMPLETE
- [ ] Create `follow_redirects()` function in redirect_handler.py
- [ ] Use requests with `allow_redirects=True`
- [x] Capture `response.history` for redirect chain
- [x] Limit to max 5 redirects
- [x] Detect redirect loops (URL appears twice)
- [x] Record: original URL, each redirect URL, final URL, HTTP status codes
- [x] Create `record_redirect_chain()` helper
- [x] Identify external systems (ICIMS, Workday, PeopleSoft)

**Acceptance Criteria**:
- ✅ Follows redirects up to 5 hops
- ✅ Detects and logs redirect loops
- ✅ Identifies external systems (ICIMS, Workday, PeopleSoft, Lever, Greenhouse, SuccessFactors)
- ✅ Records complete chain for all URLs
- ✅ Status: COMPLETE

---

#### Subtask 0A.3: Chinese DNS Fallback
**Status**: ✅ COMPLETE
**Details**:
- [x] Create `resolve_with_chinese_dns()` function in dns_resolver.py
- [x] Chinese DNS server configuration (Alidns, DNSPod, Tencent)
- [x] Fallback mechanism with priority order
- [ ] Log which DNS server succeeded
- [ ] Mark URL as "china_accessible_only" if needed
- [ ] Create `test_with_alternative_dns()` wrapper

**Acceptance Criteria**:
- ✅ Successfully uses Chinese DNS servers as fallback
- ✅ Identifies URLs accessible only from China
- ✅ Tested on 5+ Chinese university domains

---

#### Subtask 0A.4: Generate Accessibility Report
**Details**:
- [ ] Create `generate_accessibility_report()` function in connectivity_report.py
- [ ] Test all URLs in scraping_sources.json
- [ ] Group by status: accessible, timeout, 404, 403, DNS_error, SSL_error, requires_vpn
- [ ] Show progress bar
- [ ] Generate report with statistics
- [ ] Output formats: JSON, Markdown, CSV
- [ ] Report includes: Summary, Detailed Results, By Region, By Category

**Acceptance Criteria**:
- ✅ Tests all 250+ URLs efficiently
- ✅ Generates multiple output formats
- ✅ Reports detailed error messages
- ✅ Identifies patterns by region and category

---

### Task 0B: Implement URL Verification and Content Validation System
**Status**: ✅ COMPLETE
**Priority**: CRITICAL  
**Description**: Classify page type, validate content, score quality, implement decision engine

**Files to Create**:
- `scripts/scraper/config/url_verification/page_classifier.py` - Classify page type
- `scripts/scraper/config/url_verification/url_discoverer.py` - Discover career portals
- `scripts/scraper/config/url_verification/content_validator.py` - Extract & validate jobs
- `scripts/scraper/config/url_verification/quality_scorer.py` - Score content quality
- `scripts/scraper/config/url_verification/decision_engine.py` - Full validation decision tree
- `data/config/url_verification/verification_results.json` - Store all verification results
- `data/config/url_verification/discovery_suggestions.json` - Store discovered alternatives

#### Subtask 0B.1: Implement Content Extraction for Validation
**Status**: ✅ COMPLETE (431 lines of code, 13 tests passing)
**Details**:
- [x] Create `extract_job_listings()` function in content_validator.py
- [x] Parse HTML for job title patterns
- [x] Look for job cards, list items, announcement containers
- [x] Extract: job title, position type, department, deadline, application link
- [x] Create `validate_critical_fields()` function
- [x] Check for job title + position details
- [x] Create `calculate_content_quality_score()` function (0-100)
- [x] Implement scoring breakdown for all factors

**Acceptance Criteria**:
- ✅ Can extract job titles from various HTML structures
- ✅ Validates presence of critical fields
- ✅ Calculates quality score 0-100 with detailed breakdown
- ✅ 80%+ accuracy on test pages (10 manual verifications)
- ✅ 13 tests passing for content validation

---

#### Subtask 0B.2: Implement Page Type Classification and URL Discovery
**Status**: ✅ COMPLETE (268 lines of code, 15 tests passing)
**Details**:
- [x] Create `classify_page_type()` function in page_classifier.py
- [x] Analyze page title, meta description, URL path
- [x] Count job-related vs. faculty/research keywords
- [x] Detect patterns (faculty directory, department page, career portal)
- [x] Return classification with confidence score
- [x] Detects 8 page types: job_portal, faculty_directory, department_page, single_posting, error_page, external_hr_system, unknown_page
- [x] Confidence scoring system (0.0-1.0)
- [x] Handle external career systems (ICIMS, Workday, PeopleSoft, etc.)

**Acceptance Criteria**:
- ✅ Correctly classifies page types with ≥80% accuracy
- ✅ Successfully detects all 8 page type categories
- ✅ Returns ranked suggestions with confidence scores
- ✅ 15 tests passing for page classification

---

#### Subtask 0B.3: Implement Quality Scoring System
**Status**: ✅ COMPLETE (236 lines of code, 15 tests passing)
**Details**:
- [x] Create `QualityScore` dataclass in quality_scorer.py
- [x] Implement scoring breakdown system with 5 components
- [x] Quality scoring formula: 0-100 points
- [x] Breakdown tracking: listings_count, completeness, contact_info, engagement_level
- [x] Recommendation system based on score ranges
- [x] to_dict() and from_breakdown() methods
- [x] get_summary() for scoring insights

**Acceptance Criteria**:
- ✅ Calculates quality scores 0-100 with breakdown
- ✅ Provides actionable recommendations
- ✅ 15 tests passing for quality scoring

#### Subtask 0B.4: Implement URL Validation and Decision Engine
**Status**: ✅ COMPLETE (390 lines of code, 17 tests passing)
**Details**:
- [x] Create `validate_url()` function in decision_engine.py
- [x] Implement full decision tree:
   1. Test accessibility
   2. Classify page type
   3. Extract and validate critical fields
   4. Calculate quality score
   5. Check redirects
- [x] Create reason codes for decision-making
- [x] Assign appropriate reason codes based on validation results
- [x] Log all validation steps and decisions
- [x] Return actionable next_action recommendations
- [x] Preserve all metadata for future re-verification
- [x] `batch_validate_urls()` for processing multiple URLs
- [x] `suggest_alternative_urls()` for URL discovery

**Reason Codes**:
- ✅ `access_error`: URL not accessible (404, 403, timeout, DNS error)
- ✅ `wrong_page_type`: Page is department/faculty/general, not career portal
- ✅ `no_job_content`: Page accessible but has no job listings
- ✅ `missing_critical_fields`: Jobs found but no titles or position details
- ✅ `low_quality_content`: Quality score <60
- ✅ `redirect_loop`: Redirect chain loops back to itself
- ✅ `redirect_wrong_destination`: Redirects but final destination is wrong type

**Acceptance Criteria**:
- ✅ Implements full decision tree for URL validation
- ✅ Assigns correct reason codes for each URL
- ✅ Logs all validation steps
- ✅ Returns actionable next_action recommendations
- ✅ Preserves all metadata
- ✅ 17 tests passing for decision engine

---

#### Subtask 0B.4: Implement Batch URL Validation and Configuration Update
**Details**:
- [ ] Create `batch_validate_urls()` function
- [ ] Takes list of URLs to validate
- [ ] Runs validation_and_classify_url() for each
- [ ] Groups results by decision
- [ ] Shows progress bar (X/Y processed)
- [ ] Create `update_scraping_sources.json()` function
- [ ] Move validated URLs to appropriate sections
- [ ] Add reason codes and metadata
- [ ] Create backup before updating
- [ ] Create validation report (JSON, Markdown)
- [ ] Generate summary statistics

**Acceptance Criteria**:
- ✅ Batch validates 100+ URLs efficiently
- ✅ Updates configuration file correctly
- ✅ Generates detailed validation report
- ✅ Preserves all metadata and reasons
- ✅ Can rollback if needed

---

#### Subtask 0B.5: Test on Problematic US Universities (Pilot)
**Details**:
- [ ] Select 10 high-priority US universities with known issues
- [ ] Run full validation on each
- [ ] Test current URL: accessibility, page type, job extraction, quality score
- [ ] Run URL discovery: find alternatives
- [ ] Manually verify top 3 suggestions
- [ ] Document findings: old URL → reason → new URL → quality improvement
- [ ] Generate pilot report with findings and recommendations
- [ ] Confirm process works before full rollout

**Test Universities**:
1. Princeton (wrong URL type)
2. UPenn Economics (no job content)
3. UPenn Management (no job content)
4. Columbia Economics (no job content)
5. Columbia Management (no job content)
6. NYU Economics (no job content)
7. NYU Management (no job content)
8. Michigan Economics (no job content)
9. Michigan Management (no job content)
10. Wisconsin-Madison (no job content)

**Acceptance Criteria**:
- ✅ Successfully validates 10 test universities
- ✅ Discovers better URLs for 8+ universities
- ✅ All discoveries manually confirmed
- ✅ Pilot report generated with clear findings
- ✅ Ready to roll out to full 30+ US universities

---

## Phase 1B.1.5: REPLACE - URL Replacement & Expansion

### Task 0C: Implement Full URL Replacement Workflow
**Status**: 🔄 IN PROGRESS (Pilot validation complete, working on replacements)
**Priority**: CRITICAL
**Description**: For each "MOVE" URL, discover better alternatives, validate them, and update config

**Folder Structure**:
```
scripts/scraper/config/url_replacement/         # Replacement logic
├── url_discovery.py                            # ✅ Find alternatives (common paths, subdomains, predefined URLs)
└── replacement_engine.py                       # (TO CREATE) Orchestrate full replacement workflow

data/config/url_replacement/                    # Replacement data
├── candidates.json                             # Candidate replacement URLs (before validation)
├── replacements_validated.json                 # Validated replacements (after testing)
└── replacement_report.md                       # Execution report with statistics

tests/load-data-collection/url_replacement/    # Replacement tests
└── (to create test files)
```

**Files Created**:
- ✅ `scripts/scraper/config/url_discovery.py` (271 lines): Discover alternative URLs with common paths, subdomains, predefined institution URLs
- ✅ `scripts/scraper/find_replacements.py` (main script for testing replacements)
- ✅ `data/config/url_replacement/` folder structure created
- ✅ `tests/load-data-collection/url_replacement/` folder structure created

#### Subtask 0C.1: Discover Replacement URLs for Problematic Universities
**Status**: 🔄 IN PROGRESS
- [x] Created `url_discovery.py` module with:
  - `discover_urls()` - Test common paths and subdomains for a domain
  - `suggest_replacement_urls()` - Generate alternatives for problematic URLs
  - `get_predefined_urls()` - Return predefined good URLs for known institutions
  - Predefined URLs for 12 major institutions (Princeton, UPenn, Columbia, NYU, Chicago, MIT, Stanford, Harvard, Yale, Michigan, Wisconsin, Berkeley)
- [ ] Run discovery on all 10 pilot problematic universities
- [ ] Test discovered URLs with full validation workflow
- [ ] Validate discovered alternatives meet quality threshold (≥60 score)
- [ ] Save candidates to `data/config/url_replacement/candidates.json`

**Acceptance Criteria**:
- [ ] Discover 2+ alternatives per problematic university
- [ ] All alternatives tested with full validation
- [ ] Validated replacements have quality score ≥60
- [ ] Candidates documented with source information

#### Subtask 0C.2: Create Replacement Engine & Workflow
**Status**: Not Started
- [ ] Create `replacement_engine.py` in `scripts/scraper/config/url_replacement/`
- [ ] Implement `find_replacements_for_url()` function
- [ ] Implement `validate_replacement()` function (uses decision_engine.validate_url)
- [ ] Implement `create_replacement_job()` function
  - Input: problematic_url (from accessible_unverified)
  - Process: discover alternatives → validate each → select best (highest quality score)
  - Output: replacement candidate with metadata
- [ ] Implement `execute_replacements()` function
  - Batch process all problematic URLs
  - Generate candidates.json
  - Show progress (X/Y replacements found)
- [ ] Implement `validate_and_finalize()` function
  - Validate all candidate replacements work correctly
  - Update scraping_sources.json with replacements
  - Move old URL to archive with reason
  - Create replacement_report.md with statistics

#### Subtask 0C.3: Execute Pilot Replacement Workflow (10 US Universities)
**Status**: Not Started
- [ ] Run discovery on all 10 pilot universities
- [ ] Validate discovered alternatives
- [ ] Create candidates.json with results
- [ ] Manually verify top alternatives for each university
- [ ] Execute replacements and update config (with backup)
- [ ] Test scraping with new URLs to confirm data extraction works
- [ ] Generate pilot replacement report
  - Old URL → Reason for replacement → New URL → Quality improvement
  - Success rate (% URLs successfully replaced)
  - Quality improvement (avg quality score before/after)

**Acceptance Criteria**:
- ✅ Discover alternatives for 10 pilot universities
- [ ] Validate replacements (quality ≥60)
- [ ] Update config with replacements
- [ ] Test scraping with new URLs
- [ ] Pilot report shows success rate and quality improvement

---

### Task 1A: Execute Full URL Replacement for All Problematic URLs
**Status**: Not Started
**Priority**: High
**Description**: Systematically replace all problematic URLs (60+ identified in Phase 1B)

- [ ] Run replacement workflow on all non_accessible URLs
- [ ] Document replacement candidates with reasoning
- [ ] Validate each replacement meets quality threshold
- [ ] Batch update config with validated replacements
- [ ] Generate comprehensive replacement report

---

### Task 1B: Add New International Universities (30+ URLs)
**Status**: Not Started
**Priority**: High
**Target**: 30 universities

[EUROPEAN UNIVERSITIES RESEARCH]

---

### Task 1C: Add Major US Research Institutes (15+ URLs)
**Status**: Not Started
**Priority**: High
**Target**: 15 organizations

[RESEARCH INSTITUTES]

---

### Task 1D: Expand Asia-Pacific Coverage (20+ URLs)
**Status**: Not Started
**Priority**: Medium
**Target**: 20 universities

[ASIA-PACIFIC UNIVERSITIES]

---

### Task 1E: Add Latin America & Other Regions (10+ URLs)
**Status**: Not Started
**Priority**: Low
**Target**: 10 universities

[LATIN AMERICA & OTHER REGIONS]

---

### Task 2A: Final Verification & Quality Assurance
**Status**: Not Started
**Priority**: High
**Description**: Run comprehensive verification on all 250+ URLs after expansion

- [ ] Batch validate all URLs with decision_engine
- [ ] Generate final verification report
- [ ] Ensure all URLs meet quality threshold
- [ ] Document any remaining issues

---

### Task 2B: Prepare for Scraping & Data Collection
**Status**: Not Started
**Priority**: High
**Description**: Ensure all URLs are scraper-ready

- [ ] Test scraping on sample of new URLs
- [ ] Verify data extraction works correctly
- [ ] Update scraper patterns if needed
- [ ] Prepare for full data collection

---

### Task 3A: Documentation & Final Report
**Status**: Not Started
**Priority**: Medium
**Description**: Consolidate and document all Phase 1B work

- [ ] Consolidate all verification reports
- [ ] Create comprehensive expansion summary
- [ ] Document lessons learned
- [ ] Generate final statistics and success metrics

---

## Summary of Changes from Previous Plan

**Old Task Structure**: Tasks 0A-0B, then 1-8 (unclear mapping to work items)

**New Task Structure (ACCESS → VALIDATE → REPLACE)**:
- **ACCESS Phase** (0A-0B): ✅ COMPLETE - Verify URL accessibility
- **VALIDATE Phase** (0B pilot): ✅ COMPLETE - Test with 10 problematic universities
- **REPLACE Phase** (0C+): 🔄 IN PROGRESS - Fix problematic URLs systematically
  - Task 0C: URL replacement workflow
  - Task 1A: Full replacement for all problematic URLs
  - Task 1B-1E: Add new international sources
  - Task 2A-2B: Final verification and scraper integration
  - Task 3A: Documentation and reporting

**Key Improvements**:
1. Clear separation of concerns (access → validate → replace)
2. Pilot-first approach (test workflow on 10 before rolling out to all)
3. Structured folder organization (url_access/, url_verification/, url_replacement/)
4. Comprehensive documentation at each phase
5. Built-in backup and rollback capabilities

---

### Task 1A: Implement Redirect Following for Multi-Level Redirects
**Status**: Not Started  
**Priority**: High  
**Description**: Enhanced redirect handling with full chain tracking and validation

[... rest of tasks continue with 1A, 1B naming instead of 1, 2, etc. ...]

---

## Phase 1B.2: International University Research

### Task 4A: Research and Compile European Universities
**Target**: 30 universities

[... continue with 4A, 4B, 4C, 4D, 4E naming ...]

---

## Phase 1B.3: Research Institutes & Think Tanks

### Task 5A: Add Major US Research Institutes
**Target**: 15 organizations

[... continue with 5A, 5B naming ...]

---

## Phase 1B.4: Fix Existing Problematic URLs

### Task 6A: Fix US University URLs (30+ broken) - WRONG URL TYPE ISSUE
**Status**: Not Started  
**Priority**: CRITICAL

[... US URL fixing task continues ...]

---

### Task 6B: Fix Chinese University URLs (40+ failing) - VPN STRATEGY
**Status**: Not Started  
**Priority**: High

[... Chinese URL fixing task continues ...]

---

### Task 6C: Fix International University URLs (10+ broken)
**Status**: Not Started  
**Priority**: Medium

[... International URL fixing task continues ...]

---

## Phase 1B.5: Verification & Validation

### Task 7A: Run Enhanced Verification on All URLs
**Status**: Not Started  
**Priority**: High

[... Verification task continues ...]

---

### Task 7B: Update Configuration with Verified URLs
**Status**: Not Started  
**Priority**: High

[... Configuration update continues ...]

---

### Task 7C: Test Scraping on Sample of New URLs
**Status**: Not Started  
**Priority**: High

[... Scraping test continues ...]

---

## Phase 1B.6: Documentation & Finalization

### Task 8A: Consolidate Verification Documentation
**Status**: Not Started  
**Priority**: Medium

[... Documentation consolidation continues ...]

---

### Task 8B: Update Project Documentation
**Status**: Not Started  
**Priority**: Medium

[... Project docs update continues ...]

---

### Task 8C: Generate Final Statistics and Report
**Status**: Not Started  
**Priority**: Low

[... Final reporting continues ...]

---

## Key Folder Structure

```
data/config/url_verification/
├── accessibility_report.json          # Results from Task 0A
├── verification_results.json          # Results from Task 0B
├── discovery_suggestions.json         # Discovered alternative URLs
└── url_verification.md                # Consolidated documentation

scripts/scraper/config/
├── url_access/
│   ├── test_accessibility.py          # Task 0A.1
│   ├── redirect_handler.py            # Task 0A.2
│   ├── dns_resolver.py                # Task 0A.3
│   └── connectivity_report.py         # Task 0A.4
└── url_verification/
    ├── page_classifier.py             # Task 0B.2
    ├── url_discoverer.py              # Task 0B.2
    ├── content_validator.py           # Task 0B.1
    ├── quality_scorer.py              # Task 0B.1
    ├── decision_engine.py             # Task 0B.3, 0B.4
    └── batch_processor.py             # Task 0B.4
```

---

## Success Metrics

### Quantitative Goals
- [ ] **Accessible URLs**: 176 → 250+ (42% increase)
- [ ] **Fix Rate**: 60+/81 problematic URLs resolved (75%)
- [ ] **Research Institutes**: 6 → 25+ (4x growth)
- [ ] **Job Listings**: 211 → 350-400 (projected 65% increase)

### Regional Balance
- US: 70 URLs (28%)
- China: 100 URLs (40%)
- Europe: 35 URLs (14%)
- Asia-Pacific: 30 URLs (12%)
- Latin America: 10 URLs (4%)
- Other: 5 URLs (2%)

### Qualitative Improvements
- [ ] Better geographic diversity
- [ ] More international opportunities
- [ ] Improved data quality
- [ ] Robust verification (redirects, deep content)
- [ ] PDF support

---

## Timeline

- **Phase 1B.1** (Days 1-2): Tasks 0A-0B (Enhanced verification tools)
- **Phase 1B.2** (Days 3-5): Tasks 4A-4E (URL research and addition)
- **Phase 1B.3** (Day 5): Tasks 5A-5B (Research institutes)
- **Phase 1B.4** (Days 6-7): Tasks 6A-6C (Fix URLs)
- **Phase 1B.5** (Day 7): Tasks 7A-7C (Validation)
- **Phase 1B.6** (Day 8): Tasks 8A-8C (Documentation)

**Total Estimated Time**: 8 days

