# To-Do List: Phase 1B - Expand Scraping Sources (REVISED)

**Date Created**: 2026-01-04  
**Last Updated**: 2026-01-04  
**Phase**: Phase 1B - Expand Data Collection  
**Status**: In Progress  
**Objective**: Expand scraping sources from 176 to 250+ URLs with better global coverage and fix 81 problematic URLs

---

## Revised Task Structure

The original Task 0 and Task 1 have been separated into distinct workflow components:

**URL Access Verification (Task 0A)**: Test HTTP connectivity, follow redirects, detect errors
- Files location: `scripts/scraper/check_config/url_access/`
- Config location: `data/config/url_verification/`

**URL Verification (Task 0B)**: Classify page type, validate content, score quality
- Files location: `scripts/scraper/check_config/url_verification/`
- Results location: `data/config/url_verification/`

This separation allows:
- Testing URL accessibility independently (no content parsing needed)
- Verifying content quality separately (only on accessible URLs)
- Easier maintenance and debugging
- Clear responsibility for each set of tools

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
**Status**: Not Started  
**Priority**: CRITICAL  
**Description**: Test HTTP connectivity, follow redirects, detect server-level errors

**Files to Create**:
- `scripts/scraper/check_config/url_access/test_accessibility.py` - HTTP connectivity testing
- `scripts/scraper/check_config/url_access/redirect_handler.py` - Redirect following and chain tracking
- `scripts/scraper/check_config/url_access/dns_resolver.py` - Chinese DNS fallback support
- `scripts/scraper/check_config/url_access/connectivity_report.py` - Generate accessibility reports
- `data/config/url_verification/accessibility_report.json` - Store accessibility results

#### Subtask 0A.1: Implement Basic Accessibility Testing
**Details**:
- [ ] Create `test_accessibility()` function in test_accessibility.py
- [ ] Test HTTP GET with 10-second timeout
- [ ] Record status codes, error messages
- [ ] Create `is_accessible()` wrapper with caching
- [ ] Respect rate limits (1+ second between requests)

**Acceptance Criteria**:
- ✅ Tests 100+ URLs efficiently
- ✅ Detects all error types (404, 403, timeout, DNS error, SSL error)
- ✅ Respects rate limits
- ✅ Timeout after 10 seconds

---

#### Subtask 0A.2: Implement Redirect Following and Chain Tracking
**Details**:
- [ ] Create `follow_redirects()` function in redirect_handler.py
- [ ] Use requests with `allow_redirects=True`
- [ ] Capture `response.history` for redirect chain
- [ ] Limit to max 5 redirects
- [ ] Detect redirect loops (URL appears twice)
- [ ] Record: original URL, each redirect URL, final URL, HTTP status codes
- [ ] Create `record_redirect_chain()` helper
- [ ] Identify external systems (ICIMS, Workday, PeopleSoft)

**Acceptance Criteria**:
- ✅ Follows redirects up to 5 hops
- ✅ Detects and logs redirect loops
- ✅ Identifies external systems
- ✅ Records complete chain for all URLs
- ✅ Tested on 10+ URLs with known redirects

---

#### Subtask 0A.3: Implement Chinese DNS Fallback
**Details**:
- [ ] Create `resolve_with_chinese_dns()` function in dns_resolver.py
- [ ] If initial DNS fails: retry with Chinese DNS servers
- [ ] Try in order: Alidns (223.5.5.5), DNSPod (119.29.29.29), Tencent (119.28.28.28)
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
**Status**: Not Started  
**Priority**: CRITICAL  
**Description**: Classify page type, validate content, score quality, implement decision engine

**Files to Create**:
- `scripts/scraper/check_config/url_verification/page_classifier.py` - Classify page type
- `scripts/scraper/check_config/url_verification/url_discoverer.py` - Discover career portals
- `scripts/scraper/check_config/url_verification/content_validator.py` - Extract & validate jobs
- `scripts/scraper/check_config/url_verification/quality_scorer.py` - Score content quality
- `scripts/scraper/check_config/url_verification/decision_engine.py` - Full validation decision tree
- `data/config/url_verification/verification_results.json` - Store all verification results
- `data/config/url_verification/discovery_suggestions.json` - Store discovered alternatives

#### Subtask 0B.1: Implement Content Extraction for Validation
**Details**:
- [ ] Create `extract_job_listings()` function in content_validator.py
- [ ] Parse HTML for job title patterns
- [ ] Look for job cards, list items, announcement containers
- [ ] Extract: job title, position type, department, deadline, application link
- [ ] Create `validate_critical_fields()` function
- [ ] Check for job title + position details
- [ ] Create `calculate_content_quality_score()` function (0-100)
- [ ] Implement scoring breakdown for all factors

**Acceptance Criteria**:
- ✅ Can extract job titles from various HTML structures
- ✅ Validates presence of critical fields
- ✅ Calculates quality score 0-100 with detailed breakdown
- ✅ 80%+ accuracy on test pages (10 manual verifications)

---

#### Subtask 0B.2: Implement Page Type Classification and URL Discovery
**Details**:
- [ ] Create `classify_page_type()` function in page_classifier.py
- [ ] Analyze page title, meta description, URL path
- [ ] Count job-related vs. faculty/research keywords
- [ ] Detect patterns (faculty directory, department page, career portal)
- [ ] Return classification with confidence score
- [ ] Create `discover_career_portal_url()` function in url_discoverer.py
- [ ] Parse page for career/jobs links
- [ ] Test common URL patterns (10+ patterns per institution)
- [ ] Handle external career systems (ICIMS, Workday)
- [ ] Track multi-level redirect chains
- [ ] Return top 3 discovered URLs ranked by quality score

**Acceptance Criteria**:
- ✅ Correctly classifies page types with ≥80% accuracy
- ✅ Successfully discovers career portals for 20+ department pages
- ✅ Handles multi-level redirects
- ✅ Returns ranked suggestions with confidence scores
- ✅ Tested on 10 problematic US universities

---

#### Subtask 0B.3: Implement URL Validation and Classification Decision Engine
**Details**:
- [ ] Create `validate_and_classify_url()` function in decision_engine.py
- [ ] Implement full decision tree:
  1. Test accessibility
  2. Classify page type
  3. If wrong type: attempt discovery
  4. Extract and validate critical fields
  5. Calculate quality score
  6. Check redirects
- [ ] Create reason codes for non_accessible section
- [ ] Assign appropriate reason codes based on validation results
- [ ] Log all validation steps and decisions
- [ ] Return actionable next_action recommendations
- [ ] Preserve all metadata for future re-verification

**Reason Codes**:
- `access_error`: URL not accessible (404, 403, timeout, DNS error)
- `wrong_page_type`: Page is department/faculty/general, not career portal
- `no_job_content`: Page accessible but has no job listings
- `missing_critical_fields`: Jobs found but no titles or position details
- `low_quality_content`: Quality score <60
- `redirect_loop`: Redirect chain loops back to itself
- `redirect_wrong_destination`: Redirects but final destination is wrong type
- `requires_javascript`: Page needs JS to load jobs
- `requires_login`: Page requires login to view jobs
- `requires_vpn`: Blocked outside China

**Acceptance Criteria**:
- ✅ Implements full decision tree for URL validation
- ✅ Assigns correct reason codes for each URL
- ✅ Logs all validation steps
- ✅ Returns actionable next_action recommendations
- ✅ Preserves all metadata

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

scripts/scraper/check_config/
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

