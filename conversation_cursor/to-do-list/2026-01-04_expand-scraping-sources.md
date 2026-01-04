# To-Do List: Phase 1B - Expand Scraping Sources

**Date Created**: 2026-01-04  
**Phase**: Phase 1B - Expand Data Collection  
**Status**: In Progress  
**Objective**: Expand scraping sources from 176 to 250+ URLs with better global coverage and fix 81 problematic URLs

---

## URL Evaluation Metrics

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

#### Content Quality Indicators (at least 3 of 5):
- [ ] Multiple job listings on page (>3 listings visible or paginated)
- [ ] Application links or "Apply" buttons present
- [ ] Job descriptions with requirements or responsibilities
- [ ] Contact information or HR department details
- [ ] Date posted or updated timestamp visible

#### Invalid Page Types (automatically move to non-accessible):
- ❌ **Department Homepage** - General info about department, no job listings
- ❌ **Faculty Directory** - Lists current faculty members with bios
- ❌ **Course/Research Pages** - Describes programs, not hiring
- ❌ **General University Homepage** - No career section accessible
- ❌ **404 Error Pages** - URL not found
- ❌ **403 Forbidden** - Access denied
- ❌ **Redirect Loop** - URL redirects back to itself
- ❌ **Timeout/Connection Error** - Server unreachable
- ❌ **Broken External Career System** - ICIMS/Workday page not loading

### URL Classification Decision Tree

```
START: Test URL
│
├─ [ACCESSIBLE?] Can fetch page?
│  ├─ NO: Move to non_accessible with "access_error"
│  └─ YES: Continue
│
├─ [TYPE CHECK] Is this a career/job portal page?
│  ├─ NO (Department/Faculty/General): Attempt to discover career portal URL
│  │   ├─ Found alternative: Test alternative URL recursively
│  │   └─ Not found: Move to non_accessible with "wrong_page_type"
│  └─ YES: Continue
│
├─ [CONTENT CHECK] Does page contain job listings?
│  ├─ NO: Move to non_accessible with "no_job_content"
│  └─ YES: Continue
│
├─ [CRITICAL FIELDS] Can extract Job Title and Position Details?
│  ├─ NO: Move to non_accessible with "missing_critical_fields"
│  └─ YES: Continue
│
├─ [QUALITY SCORE] Content quality ≥ 60/100?
│  ├─ NO: Move to non_accessible with "low_quality_content"
│  └─ YES: Continue
│
├─ [REDIRECT CHECK] Any unresolved redirects?
│  ├─ YES, Multi-level: Document chain, keep track
│  └─ NO or Resolved: Continue
│
└─ RESULT: KEEP IN ACCESSIBLE ✅
   Add metadata: 
   - Verified date
   - Content quality score
   - Redirect chain (if any)
   - Critical fields found
   - Number of listings detected
```

### Scoring System (0-100)

**Content Quality Score** = (weighted sum of factors)

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

### Minimum Requirements for Accessible Section

✅ **MUST HAVE ALL**:
1. Accessible URL (responds with 200 OK)
2. Extractable job titles (≥1)
3. Position details (≥1 critical field)
4. Content quality score ≥ 60

✅ **EXAMPLES OF VALID PAGES**:
- `https://hr.stanford.edu/faculty-positions` - Lists 10+ faculty positions with titles, deadlines, apply links
- `https://careers.nyu.edu/economics` - Posts economics department jobs with application instructions
- `https://jobs.harvard.edu/` - Career portal with searchable job listings
- `https://careers-brookings.icims.com/` - ICIMS system with job postings and apply buttons

❌ **EXAMPLES OF INVALID PAGES** (move to non_accessible):
- `https://economics.stanford.edu/` - Department homepage, no job listings
- `https://upennecon.upenn.edu/faculty/` - Faculty directory with bios, not hiring
- `https://www.columbia.edu/` - General university page
- `https://hr.nyu.edu/faculty/` - Faculty directory, not job listings
- `https://research.yale.edu/open-positions` - Broken link (404)

---

## Overview

Diversify data sources beyond US-centric coverage by adding universities from Europe, Asia, Canada, Latin America, and expanding research institute coverage. Fix existing problematic URLs and implement enhanced verification with redirect following and PDF detection.

**Target**: 250+ accessible URLs with <40% from any single region

**Critical Rule**: Only keep URLs in accessible section that have extractable job titles and position details with ≥60 content quality score. Everything else goes to non_accessible with detailed reason codes.

---

## Phase 1B.1: Enhanced Verification Tools

### Task 0: Implement URL Discovery and Validation System with Evaluation Metrics
**Status**: Not Started  
**Priority**: CRITICAL

**Problem**: Many existing URLs point to wrong page types (department pages, faculty directories, general homepages) instead of actual career/job portals with extractable job listings. Need systematic way to validate and move URLs.

**Core Workflow**:
1. Test if URL is accessible
2. Classify page type (career portal vs. wrong type)
3. If wrong type: discover correct career portal URL
4. Extract and validate critical fields (job titles, position details)
5. Score content quality
6. Move URL to appropriate section (accessible or non_accessible with reason code)
7. Handle multi-level redirects

#### Subtask 0.1: Implement Content Extraction for Validation
**Details**:
- [ ] Create `extract_job_listings()` function in verify_urls.py:
  - Parse HTML for job title patterns: "Assistant Professor", "Postdoctoral", "Visiting Scholar", "Lecturer", "Research Fellow"
  - Look for job cards, list items, or announcement containers
  - Extract: job title, position type, department, deadline, application link
  - Return list of extracted jobs with confidence scores
  - Handle common formats: tables, cards, lists, paragraphs
  
- [ ] Create `validate_critical_fields()` function:
  - Check if extracted jobs have:
    * Job title (required)
    * At least 1 of: position type, department, deadline, location, salary info
  - Return validation result: PASS (has critical fields) or FAIL (missing critical fields)
  - Log what fields were found
  
- [ ] Create `calculate_content_quality_score()` function (0-100):
  - Count valid job listings found (max 30 pts)
  - Presence of application links/buttons (max 20 pts)
  - Quality of job descriptions (max 15 pts)
  - Presence of position details (max 25 pts)
  - Freshness of postings (max 10 pts)
  - Return score and breakdown of components
  - Score ≥60: KEEP, Score <60: MOVE TO NON_ACCESSIBLE

**Acceptance Criteria**:
- ✅ Can extract job titles from various HTML structures
- ✅ Validates presence of critical fields (job title + position details)
- ✅ Calculates quality score 0-100 with detailed breakdown
- ✅ 80%+ accuracy on test pages (manually verify 10 pages)

---

#### Subtask 0.2: Implement Page Type Classification and URL Discovery
**Details**:
- [ ] Create `classify_page_type()` function:
  - Analyze page title, meta description, URL path
  - Count job-related keywords vs. faculty/research keywords
  - Detect patterns:
    * "Faculty" + "Bio" + "Research" = faculty directory
    * "Economics" + "Department" + "Courses" = department page
    * "Apply" + "Jobs" + "Positions" = career portal
  - Return classification with confidence: CAREER_PORTAL, DEPARTMENT_PAGE, FACULTY_DIRECTORY, OTHER
  - Score: ≥80% confidence = reliable, <50% = ambiguous, test further
  
- [ ] Create `discover_career_portal_url()` function:
  - If page is DEPARTMENT_PAGE or OTHER, discover correct URL
  - **Step 1 - Parse page for career links**:
    * Scan navigation menu, footer, sidebar for links with text:
      - "Careers", "Jobs", "Employment", "Faculty Positions", "Work Here"
      - "HR", "Human Resources", "Recruiting", "Apply", "Join Us"
    * Extract all matching links and URLs
  
  - **Step 2 - Test common patterns** (in priority order):
    * Test these patterns for same domain:
      1. `https://careers.{domain}/`
      2. `https://jobs.{domain}/`
      3. `https://hr.{domain}/careers` or `/faculty-careers`
      4. `https://hr.{domain}/`
      5. `https://{domain}/careers`
      6. `https://{domain}/jobs`
      7. `https://{domain}/faculty-positions`
      8. `https://{domain}/employment`
      9. `https://{domain}/faculty/positions`
      10. `https://{domain}/hr/careers`
    * For each pattern: fetch page, classify type, calculate quality score
    * Record results: found URL, classification, score
  
  - **Step 3 - Handle external career systems**:
    * If redirects to ICIMS: Likely correct (e.g., Brookings → careers-brookings.icims.com)
    * If redirects to Workday/PeopleSoft: Likely correct (common university systems)
    * Log redirect chain, keep track of final URL
    * Test final destination for job content
  
  - **Step 4 - Multi-level redirect handling**:
    * Some URLs may redirect multiple times
    * Max 5 redirects, track full chain
    * If chain leads to correct page: Use final URL, document chain
    * If chain leads to wrong page: Keep original, flag as "redirect_wrong_destination"
    * If chain has loop: Flag as "redirect_loop", don't use
  
  - Return top 3 discovered URLs ranked by:
    1. Classification (CAREER_PORTAL = best)
    2. Content quality score (higher = better)
    3. Link prominence (found in main nav = higher priority)

**Examples of Discovery in Action**:
```
Input: https://economics.stanford.edu/
1. Classify: DEPARTMENT_PAGE (faculty list, research info, courses)
2. Discover:
   - Found "Careers" link → https://careers.stanford.edu/
   - Classify discovered: CAREER_PORTAL ✅
   - Extract jobs: 50+ positions found, quality score: 92
   - Result: SUGGEST REPLACEMENT with 95% confidence
   
Input: https://hr.nyu.edu/faculty/
1. Classify: FACULTY_DIRECTORY (bios, photos, department listings)
2. Discover:
   - Found "Apply" link → https://hr.nyu.edu/career-opportunities/
   - Classify: CAREER_PORTAL ✅
   - Extract jobs: 20+ economics positions, quality score: 75
   - Result: SUGGEST REPLACEMENT with 85% confidence
   
Input: https://www.brookings.edu/careers/
1. Classify: CAREER_PORTAL ✅
2. Redirects: https://careers-brookings.icims.com/jobs/search
3. Classify final: CAREER_PORTAL ✅
4. Extract: 30+ positions, quality score: 88
5. Result: KEEP WITH REDIRECT CHAIN DOCUMENTED
```

**Acceptance Criteria**:
- ✅ Correctly classifies page types with ≥80% accuracy
- ✅ Successfully discovers career portals for 20+ department pages
- ✅ Handles multi-level redirects (ICIMS, Workday, etc.)
- ✅ Returns ranked suggestions with confidence scores
- ✅ Documents redirect chains and discovery attempts
- ✅ Tested on 10 problematic US universities with correct discoveries

---

#### Subtask 0.3: Implement URL Validation and Classification Decision Engine
**Details**:
- [ ] Create `validate_and_classify_url()` function that implements decision tree:
  
  ```
  def validate_and_classify_url(url):
      # STEP 1: Test accessibility
      if not is_accessible(url):
          return DECISION(
              action="MOVE_TO_NON_ACCESSIBLE",
              reason="access_error",
              details=error_message,
              next_action="Try alternative patterns or mark as blocked"
          )
      
      # STEP 2: Classify page type
      page_type = classify_page_type(url)
      if page_type != CAREER_PORTAL:
          # Attempt discovery
          alternatives = discover_career_portal_url(url)
          if alternatives:
              # Recursively validate top candidate
              return validate_and_classify_url(alternatives[0]['url'])
          else:
              return DECISION(
                  action="MOVE_TO_NON_ACCESSIBLE",
                  reason="wrong_page_type",
                  details=f"Page type: {page_type}, no career portal found",
                  next_action="Manual review needed"
              )
      
      # STEP 3: Extract and validate critical fields
      jobs = extract_job_listings(url)
      if not jobs:
          return DECISION(
              action="MOVE_TO_NON_ACCESSIBLE",
              reason="no_job_content",
              details="No job listings could be extracted",
              next_action="Check if page is working correctly"
          )
      
      valid_jobs = [j for j in jobs if validate_critical_fields(j)]
      if not valid_jobs:
          return DECISION(
              action="MOVE_TO_NON_ACCESSIBLE",
              reason="missing_critical_fields",
              details="Jobs found but missing title or position details",
              next_action="May need custom parser"
          )
      
      # STEP 4: Calculate quality score
      quality_score = calculate_content_quality_score(jobs, url)
      if quality_score < 60:
          return DECISION(
              action="MOVE_TO_NON_ACCESSIBLE",
              reason="low_quality_content",
              details=f"Quality score: {quality_score}/100",
              score_breakdown=breakdown,
              next_action="Improve extraction or find better URL"
          )
      
      # STEP 5: All checks passed
      return DECISION(
          action="KEEP_IN_ACCESSIBLE",
          reason="valid_job_listing_page",
          details=f"Quality score: {quality_score}/100, {len(valid_jobs)} valid jobs",
          metadata={
              "verified_date": today,
              "quality_score": quality_score,
              "jobs_found": len(valid_jobs),
              "critical_fields": list_of_fields,
              "redirect_chain": chain_if_any
          }
      )
  ```

- [ ] Create reason codes for non_accessible section:
  - `access_error`: URL not accessible (404, 403, timeout, DNS error)
  - `wrong_page_type`: Page is department/faculty/general, not career portal
  - `no_job_content`: Page accessible but has no job listings
  - `missing_critical_fields`: Jobs found but no titles or position details
  - `low_quality_content`: Quality score <60
  - `redirect_loop`: Redirect chain loops back to itself
  - `redirect_wrong_destination`: Redirects but final destination is wrong type
  - `requires_javascript`: Page needs JS to load jobs (can't parse static HTML)
  - `requires_login`: Page requires login to view jobs
  - `requires_vpn`: Blocked outside China (mark as potential)

**Acceptance Criteria**:
- ✅ Implements full decision tree for URL validation
- ✅ Assigns correct reason codes for each URL
- ✅ Logs all validation steps and decisions
- ✅ Returns actionable next_action recommendations
- ✅ Preserves all metadata for future re-verification

---

#### Subtask 0.4: Implement Batch URL Validation and Configuration Update
**Details**:
- [ ] Create `batch_validate_urls()` function:
  - Takes list of URLs to validate
  - Runs validation_and_classify_url() for each
  - Groups results by decision (KEEP_IN_ACCESSIBLE, MOVE_TO_NON_ACCESSIBLE)
  - Shows progress bar (X/Y URLs processed)
  - Logs all discoveries and suggestions
  - Returns summary: kept count, moved count, discovered alternatives
  
- [ ] Create `update_scraping_sources.json()` function:
  - Move validated URLs to appropriate sections
  - Add reason codes and metadata to non_accessible URLs
  - For non_accessible URLs: store original URL + suggested alternatives
  - Update verification date for all entries
  - Preserve all existing metadata
  - Create backup before updating
  - Log all changes
  
- [ ] Create validation report:
  - Summary statistics: total URLs, moved count, kept count, success rate
  - Grouped by reason codes (how many access_error, wrong_page_type, etc.)
  - List of discovered alternatives (old URL → new URL → quality score)
  - Redirect chains documented
  - Recommendations for manual review
  - Export as JSON and Markdown

**Acceptance Criteria**:
- ✅ Can batch validate 100+ URLs efficiently
- ✅ Updates configuration file correctly
- ✅ Generates detailed validation report
- ✅ Preserves all metadata and reasons
- ✅ Can rollback if needed

---

#### Subtask 0.5: Test on Problematic US Universities (Pilot)
**Details**:
- [ ] Select 10 high-priority US universities with known issues:
  1. Princeton: Currently wrong URL type (department page)
  2. UPenn Economics: No job content verified
  3. UPenn Management: No job content verified
  4. Columbia Economics: No job content verified
  5. Columbia Management: No job content verified
  6. NYU Economics: No job content verified
  7. NYU Management: No job content verified
  8. Michigan Economics: No job content verified
  9. Michigan Management: No job content verified
  10. Wisconsin-Madison: No job content verified

- [ ] For each university, perform detailed validation:
  - [ ] Test current URL:
    * Is it accessible?
    * What page type is it?
    * Can we extract jobs?
    * What's the quality score?
    * Why did it fail before?
  
  - [ ] Run discovery:
    * Parse page for career links
    * Test common URL patterns
    * Check redirect destinations
    * Rank alternatives
  
  - [ ] Manual verification:
    * Visit top suggested URL manually
    * Confirm it has job listings
    * Verify job titles and positions extractable
    * Check if quality score ≥60
  
  - [ ] Document findings:
    * Old URL → reason for failure
    * Discovered URL → confirmation it works
    * Quality score with breakdown
    * Redirect chain (if any)
    * Recommendation: ACCEPT or NEED_MANUAL_REVIEW

- [ ] Generate pilot report:
  - How many universities improved?
  - How many URLs successfully discovered?
  - What patterns worked best?
  - Any failures or unexpected issues?
  - Recommendations for full rollout

**Example Output**:
```
PRINCETON UNIVERSITY
─────────────────────
Current URL: https://economics.princeton.edu/
├─ Accessible: YES ✅
├─ Page Type: DEPARTMENT_PAGE ❌
├─ Jobs Found: 0 ❌
├─ Quality Score: 5/100 ❌
├─ Reason: Shows faculty directory, courses, research

Discovery Results:
├─ Found "careers" link: https://www.princeton.edu/careers
├─ Found "Apply" link: https://hr.princeton.edu/
│
├─ Alternative 1: https://www.princeton.edu/careers/faculty-positions
│  ├─ Accessible: YES ✅
│  ├─ Page Type: CAREER_PORTAL ✅
│  ├─ Jobs Found: 8 ✅
│  ├─ Quality Score: 78/100 ✅
│  ├─ DECISION: ACCEPT ✅
│  └─ Redirect Chain: None
│
├─ Alternative 2: https://hr.princeton.edu/faculty-openings
│  ├─ Accessible: YES ✅
│  ├─ Page Type: CAREER_PORTAL ✅
│  ├─ Jobs Found: 12 ✅
│  ├─ Quality Score: 85/100 ✅
│  ├─ DECISION: ACCEPT (BETTER) ✅
│  └─ Redirect Chain: None

FINAL RECOMMENDATION:
├─ Move old URL to non_accessible (wrong_page_type)
├─ Add new URL: https://hr.princeton.edu/faculty-openings
├─ Quality Score: 85/100
└─ Status: Ready for scraping ✅
```

**Acceptance Criteria**:
- ✅ Successfully validates 10 test universities
- ✅ Discovers better URLs for 8+ universities
- ✅ All discoveries manually confirmed
- ✅ Pilot report generated with clear findings
- ✅ Ready to roll out to full 30+ US universities

---



### Task 1: Enhance URL Verification Script with Redirect Following and Evaluation Metrics
**Status**: Not Started  
**Priority**: High

**Detailed Plan**:

- [ ] **Step 1.1: Set up redirect tracking** in verify_urls.py:
  - Use requests library with `allow_redirects=True`
  - Capture `response.history` to track all redirects
  - Store: original URL, redirect chain, final URL
  - Max 5 redirects allowed, detect loops (URL appears twice)
  - Test on: `https://www.brookings.edu/careers/` (should lead to ICIMS)
  
- [ ] **Step 1.2: Classify each URL in redirect chain**:
  - Test first URL: Is it accessible? What type is it?
  - Test each redirect destination: Same classification tests
  - If any step is error page (404, 403): Mark and stop
  - If any step is wrong type but not error: Continue (may be intermediate step)
  - If final URL is CAREER_PORTAL: SUCCESS
  - If final URL is wrong type: FAILURE, move to non_accessible
  
- [ ] **Step 1.3: Extract and validate from final destination**:
  - Only if final destination is accessible
  - Extract jobs using functions from Task 0
  - Validate critical fields
  - Calculate quality score
  - Record full chain in metadata
  
- [ ] **Step 1.4: Integrate with Task 0 validation**:
  - If URL fails validation: Run URL discovery (Task 0)
  - If discovery finds alternative: Recursively validate alternative
  - Track all alternatives and their validation results
  - Choose best alternative (highest quality score)
  
- [ ] **Step 1.5: Update scraping_sources.json with redirect information**:
  - Store redirect chain as metadata
  - Mark if URL is: direct (no redirects), single_redirect, multi_redirect, loop_detected
  - For ICIMS/Workday systems: Document platform name
  - Keep original URL + final URL for comparison
  
- [ ] **Step 1.6: Test on 5 problematic URLs**:
  - `https://www.brookings.edu/careers/` → should find ICIMS system
  - `https://hr.nyu.edu/faculty/` → should discover jobs page
  - `https://economics.stanford.edu/` → should discover career portal
  - `https://www.columbia.edu/careers` → should find actual jobs
  - `https://upennecon.upenn.edu/` → should find correct careers page

**Acceptance Criteria**:
- ✅ Follows redirects up to 5 hops, detects loops
- ✅ Logs complete redirect chain with classifications
- ✅ Successfully handles Brookings → ICIMS redirect
- ✅ Validates job content at final destination
- ✅ Integrates with Task 0 URL discovery and validation
- ✅ Updates configuration with redirect metadata
- ✅ All 5 test URLs handled correctly

**Files to Modify**:
- `scripts/scraper/check_config/verify_urls.py`

**Example Output**:
```
URL: https://www.brookings.edu/careers/
├─ Step 1: Original URL
│  ├─ Accessible: YES ✅
│  ├─ Type: CAREER_PORTAL ✅
│  └─ But redirects → continue
│
├─ Step 2: Redirect 1
│  ├─ URL: https://careers.brookings.edu/
│  ├─ Status: 302 Found
│  └─ Redirects → continue
│
├─ Step 3: Final URL
│  ├─ URL: https://careers-brookings.icims.com/jobs/search
│  ├─ Type: CAREER_PORTAL ✅
│  ├─ Jobs: 30+ positions
│  ├─ Quality: 88/100
│  └─ Valid: YES ✅
│
└─ DECISION: KEEP IN ACCESSIBLE
   Metadata: redirect_chain_length=2, platform=ICIMS, final_url=icims, quality=88
```

---

### Task 2: Implement Content Depth Scoring with Quality Thresholds
**Status**: Not Started  
**Priority**: High

**Detailed Plan**:

- [ ] **Step 2.1: Create scoring system** (0-100 total):
  - **Job Titles Found** (max 30 pts):
    * 5+ distinct titles = 30 pts
    * 3-4 titles = 20 pts
    * 1-2 titles = 10 pts
    * 0 titles = 0 pts
  
  - **Position Details** (max 25 pts):
    * All critical fields (title + type + dept) = 25 pts
    * Job type + department = 18 pts
    * Department only = 10 pts
    * None = 0 pts
  
  - **Application Methods** (max 20 pts):
    * Apply buttons/links present = 20 pts
    * Email contact info = 10 pts
    * No way to apply = 0 pts
  
  - **Job Descriptions** (max 15 pts):
    * Full descriptions with requirements = 15 pts
    * Brief details present = 8 pts
    * Titles only, no details = 0 pts
  
  - **Freshness** (max 10 pts):
    * Posted within 1 week = 10 pts
    * Posted within 1 month = 5 pts
    * Old or no date = 0 pts
  
  - **Total**: 30 + 25 + 20 + 15 + 10 = 100 pts

- [ ] **Step 2.2: Define thresholds**:
  - **80-100 (Excellent)**: KEEP IN ACCESSIBLE
    * Example: Stanford careers portal with 50+ positions, full descriptions, apply buttons
  
  - **60-79 (Good)**: KEEP IN ACCESSIBLE
    * Example: NYU HR with 20+ economics positions, dates, contact info
  
  - **40-59 (Marginal)**: MOVE TO NON_ACCESSIBLE
    * Reason: "low_quality_content"
    * Recommendation: Manual review needed
    * Example: Page with few jobs, minimal details
  
  - **0-39 (Poor)**: MOVE TO NON_ACCESSIBLE
    * Reason: "low_quality_content" or "no_job_content"
    * Do not use for scraping
    * Example: Department page with no actual jobs

- [ ] **Step 2.3: Generate score breakdown**:
  - Show which components contributed to score
  - Identify weak areas (e.g., "no application links found")
  - Provide specific recommendations
  - Example:
    ```
    URL: https://hr.stanford.edu/faculty-positions
    ├─ Job Titles: 30/30 (50+ distinct titles found)
    ├─ Position Details: 25/25 (all fields present)
    ├─ Application: 20/20 (apply buttons found)
    ├─ Descriptions: 15/15 (full requirements listed)
    ├─ Freshness: 9/10 (posted 3 days ago)
    └─ TOTAL: 99/100 (EXCELLENT)
    ```

- [ ] **Step 2.4: Handle edge cases**:
  - Multi-page listings: Check pagination, count total jobs
  - Dynamic loading: Note if jobs loaded via JavaScript (can't parse static)
  - Filters required: If need to filter by department/school
  - Apply redirects: If "Apply" leads to external system (ICIMS, etc.)

- [ ] **Step 2.5: Test on sample URLs**:
  - Test 10 good URLs (should score 60+)
  - Test 10 bad URLs (should score <60)
  - Verify threshold works correctly
  - Adjust if needed

**Acceptance Criteria**:
- ✅ Scoring system 0-100 with clear breakdown
- ✅ Thresholds properly defined (60 = minimum for accessible)
- ✅ Score breakdown shows contributing factors
- ✅ 90%+ accuracy on test set (8+/10 good URLs score ≥60, 8+/10 bad URLs score <60)
- ✅ Edge cases handled appropriately

---

### Task 3: Add PDF Detection and Download Capability
**Status**: Not Started  
**Priority**: Medium

**Detailed Plan**:

- [ ] **Step 3.1: Scan pages for PDFs**:
  - Find all `<a href="*.pdf">` links
  - Filter by keywords: "economics", "faculty", "position", "hiring", "job", "recruitment", "application", "announcement"
  - Store: URL, link text, confidence score
  - Test on sample pages

- [ ] **Step 3.2: Download relevant PDFs**:
  - Create directory structure: `data/raw/documents/{source}/{date}_{name}.pdf`
  - Download only high-confidence PDFs (score ≥70)
  - Respect rate limits (1 second delay between downloads)
  - Log all downloads with metadata
  - Skip if already downloaded (check by content hash)

- [ ] **Step 3.3: Extract metadata from PDFs**:
  - Try to extract text from PDF
  - Look for: position titles, departments, application info
  - Record in verification report
  - Mark if PDF contains job postings

- [ ] **Step 3.4: Include PDFs in content quality score**:
  - If PDFs with job content found: +10 bonus points to quality score
  - Add "pdf_count" to metadata
  - Document PDF sources for future reference

- [ ] **Step 3.5: Add --no-pdf flag**:
  - Allow users to skip PDF downloads if desired
  - Usage: `verify_urls.py --no-pdf`
  - Useful for quick verification without downloads

**Acceptance Criteria**:
- ✅ Detects PDF links on job pages
- ✅ Downloads only job-related PDFs
- ✅ Saves to organized directory structure
- ✅ Logs PDF downloads in verification report
- ✅ PDFs properly included in content quality score

---

### Task 4: Improve Chinese University URL Verification
**Status**: Not Started  
**Priority**: High

**Detailed Plan**:

- [ ] **Step 4.1: Test alternative domain patterns** for Chinese universities:
  - For each failing Chinese URL, systematically test:
    1. Original: `rsc.{domain}.edu.cn` (likely failing)
    2. Alternative 1: `hr.{domain}.edu.cn` (HR portal)
    3. Alternative 2: `job.{domain}.edu.cn` (Job portal)
    4. Alternative 3: `jobs.{domain}.edu.cn`
    5. Alternative 4: `talent.{domain}.edu.cn` (Talent recruitment)
    6. Alternative 5: `www.{domain}.edu.cn/jobs` (Jobs page)
    7. Alternative 6: `www.{domain}.edu.cn/rczp` (Recruitment page, Chinese)
  - Retry each pattern multiple times (connection may be unstable)
  - Log results: accessible, page type, jobs found

- [ ] **Step 4.2: Handle Great Firewall blocking**:
  - Detect timeout patterns (typical for GFW block)
  - Use Chinese DNS servers:
    * Alidns: 223.5.5.5, 223.6.6.6
    * DNSPod: 119.29.29.29
    * Tencent DNS: 119.28.28.28
  - Retry with different DNS
  - If still blocked after retries: Mark as "requires_vpn"
  - Document which patterns work best

- [ ] **Step 4.3: Verify Chinese language content**:
  - For Chinese pages that load: Check for recruitment keywords
    * 人才招聘 (talent recruitment)
    * 教师招聘 (teacher recruitment)
    * 岗位 (positions)
    * 申请 (apply)
    * 截止 (deadline)
  - If keywords found: Content is likely valid

- [ ] **Step 4.4: Document working patterns**:
  - For each university: record which pattern worked
  - Identify trends: which pattern works for which region
  - Create lookup table for future reference
  - Document any universities that require VPN

- [ ] **Step 4.5: Test on 10 Chinese universities**:
  - Universities known to fail:
    1. Tsinghua University
    2. Nanjing University
    3. Shandong University
    4. Jilin University
    5. Xi'an Jiaotong University
    6. Central University of Finance and Economics
    7. Shanghai University of Finance and Economics
    8. Zhongnan University of Economics and Law
    9. Dalian University of Technology
    10. South China Normal University
  - For each: document which pattern works, quality score
  - Mark if VPN required

**Acceptance Criteria**:
- ✅ Successfully verifies 5+ Chinese universities that previously failed
- ✅ Tests all domain pattern variations
- ✅ Uses Chinese DNS servers when needed
- ✅ Detects and marks VPN-required URLs
- ✅ Verifies Chinese language content
- ✅ Documents working patterns for each region

---

### Task 5: Create Automated URL Replacement Finder and Suggestions
**Status**: Not Started  
**Priority**: Medium

**Detailed Plan**:

- [ ] **Step 5.1: Enhance find_url_replacements.py**:
  - Takes a failing URL as input
  - Extracts domain and institution name
  - Tests common patterns systematically:
    * Extract patterns: `https://careers.{domain}/`
    * HR patterns: `https://hr.{domain}/`, `https://hr.{domain}/faculty/`
    * Jobs patterns: `https://jobs.{domain}/`, `https://jobs.{domain}/faculty-positions`
    * Faculty patterns: `https://{domain}/faculty-positions`, `https://{domain}/faculty/careers`
    * General patterns: `https://{domain}/careers`, `https://{domain}/jobs`
  - Test each pattern:
    * Is it accessible?
    * What page type?
    * How many jobs?
    * Quality score?
  - Rank by quality score
  - Return top 3 suggestions

- [ ] **Step 5.2: Batch mode for multiple URLs**:
  - Accept file with list of failing URLs
  - Process each URL: find replacements, test, rank
  - Generate report: old URL → suggestions ranked by score
  - Show success rate, common patterns, recommendations

- [ ] **Step 5.3: Interactive mode**:
  - For each URL: show top 3 suggestions
  - User can: accept, reject, skip
  - Save confirmed replacements
  - Generate final configuration update

- [ ] **Step 5.4: Test on problematic URLs**:
  - Run on 30 broken US university URLs
  - Review suggestions manually
  - Confirm which work before updating config

**Acceptance Criteria**:
- ✅ Tests 10+ common URL patterns per institution
- ✅ Returns ranked replacement suggestions with quality scores
- ✅ Supports batch processing
- ✅ Successfully finds replacements for 20+ URLs
- ✅ Manual review confirms replacements work

---

### Task 6: Generate Enhanced Verification Report
**Status**: Not Started  
**Priority**: Medium

**Detailed Plan**:

- [ ] **Step 6.1: Create comprehensive report structure**:
  - **Summary Section**:
    * Total URLs tested
    * URLs kept in accessible
    * URLs moved to non_accessible
    * Overall success rate (%)
    * URLs with issues by category
  
  - **Regional Breakdown**:
    * Accessible URLs per region
    * Non_accessible URLs per region
    * Success rate per region
    * Top issues per region
  
  - **Detailed Results**:
    * Each URL with: status, reason, quality score, metadata
    * For failed URLs: reason code + recommendation
    * For successful URLs: quality score + critical fields found
  
  - **Discovery Results**:
    * URLs that were moved due to discovery
    * Original URL → new URL → quality improvement
    * Success rate of discovery process
  
  - **Redirect Analysis**:
    * URLs with redirects
    * Redirect chains documented
    * External systems detected (ICIMS, Workday)
    * Redirect success rate

- [ ] **Step 6.2: Multiple output formats**:
  - **Markdown** (url_verification.md): Human-readable, organized
  - **JSON**: Machine-readable for programmatic access
  - **CSV**: Spreadsheet for analysis
  - Each format includes: URL, status, reason, quality, metadata

- [ ] **Step 6.3: Actionable recommendations**:
  - For non_accessible URLs: what to do next
    * Try alternative patterns (Task 5)
    * Manual review recommended
    * May need special handling (VPN, JavaScript)
  - For low-quality URLs: how to improve
    * Discovery may find better URL
    * Content quality too low, skip for now
  - For good URLs: confidence level
    * Excellent: 80+/100
    * Good: 60-79/100

- [ ] **Step 6.4: Merge old verification files**:
  - Combine `URL_VERIFICATION.md` + `URL_VERIFICATION_RESULTS.md`
  - Create single `data/config/url_verification.md`
  - Delete old files after merge
  - All information preserved in new file

**Acceptance Criteria**:
- ✅ Report includes all key sections (summary, regional, detailed, discovery, redirect)
- ✅ Multiple output formats available
- ✅ Actionable recommendations for each URL
- ✅ Clear visualization of statistics
- ✅ Old files merged into single consolidated file

---

## Phase 1B.2: International University Research

### Task 7: Research and Compile European Universities
**Status**: Not Started  
**Priority**: High

**Target**: 30 universities

**Subtasks**:
- [ ] **UK** (10 universities): Oxford, LSE, Warwick, Manchester, UCL, Imperial, Bristol, Glasgow, Nottingham, Southampton
- [ ] **Germany** (5): Mannheim, Frankfurt, Humboldt, Free University Berlin, Cologne
- [ ] **France** (3): Toulouse School of Economics, Sciences Po, HEC Paris
- [ ] **Netherlands** (2): Tilburg, Maastricht
- [ ] **Spain** (3): Barcelona GSE, Pompeu Fabra, Carlos III Madrid
- [ ] **Switzerland** (2): Zurich, Geneva
- [ ] **Scandinavia** (3): Stockholm School of Economics, Copenhagen, Oslo
- [ ] **Italy** (2): Bocconi, Bologna
- [ ] Find official career/HR pages for each
- [ ] Verify job postings are present
- [ ] Document URL patterns by country

**Acceptance Criteria**:
- ✅ 30 European universities identified
- ✅ All URLs verified for job content
- ✅ URLs added to scraping_sources.json
- ✅ Country-specific patterns documented

---

### Task 8: Research and Compile Asia-Pacific Universities
**Status**: Not Started  
**Priority**: High

**Target**: 25 universities

**Subtasks**:
- [ ] **Japan** (5): Tokyo, Hitotsubashi, Waseda, Keio, Kyoto
- [ ] **South Korea** (3): Seoul National, Korea, Yonsei
- [ ] **Hong Kong** (4): HKU, HKUST, CUHK, CityU
- [ ] **Taiwan** (3): National Taiwan University, Academia Sinica, National Chengchi
- [ ] **Singapore** (2): NUS, SMU (already have NTU)
- [ ] **India** (4): ISI, Delhi School of Economics, IIM Ahmedabad, IIM Bangalore
- [ ] **Australia** (4): UNSW, QUT, South Australia, Tasmania (expand current 6)
- [ ] **New Zealand** (2): Auckland, Victoria University of Wellington
- [ ] Find career pages for each
- [ ] Handle language barriers (Japanese, Korean, Chinese)
- [ ] Verify English job postings availability

**Acceptance Criteria**:
- ✅ 25 Asia-Pacific universities identified
- ✅ All URLs verified for accessibility
- ✅ URLs added to scraping_sources.json
- ✅ Language notes documented for non-English sites

---

### Task 9: Research and Compile Canadian Universities
**Status**: Not Started  
**Priority**: High

**Target**: 10 universities (currently only McGill)

**Subtasks**:
- [ ] **Top programs** (10): Toronto, UBC, Western, Queen's, Calgary, Alberta, McMaster, Waterloo, Simon Fraser, York
- [ ] Find HR/career portals for each
- [ ] Verify economics department job listings
- [ ] Document common Canadian URL patterns
- [ ] Check for bilingual (English/French) requirements

**Acceptance Criteria**:
- ✅ 10 Canadian universities identified
- ✅ All URLs verified for job content
- ✅ URLs added to scraping_sources.json
- ✅ Bilingual sites handled appropriately

---

### Task 10: Research and Compile Latin American Universities
**Status**: Not Started  
**Priority**: Medium

**Target**: 10 universities (currently zero)

**Subtasks**:
- [ ] **Brazil** (4): São Paulo, Fundação Getulio Vargas, PUC-Rio, Brasília
- [ ] **Mexico** (2): ITAM, El Colegio de México
- [ ] **Chile** (2): University of Chile, Pontifical Catholic University
- [ ] **Argentina** (2): Buenos Aires, Torcuato Di Tella
- [ ] Find career pages (may be in Spanish/Portuguese)
- [ ] Verify if English positions are posted
- [ ] Document language requirements

**Acceptance Criteria**:
- ✅ 10 Latin American universities identified
- ✅ All URLs verified for accessibility
- ✅ URLs added to scraping_sources.json
- ✅ Language notes documented

---

### Task 11: Add Middle East & African Universities
**Status**: Not Started  
**Priority**: Low

**Target**: 5 universities

**Subtasks**:
- [ ] **Israel** (2): Hebrew University, Tel Aviv
- [ ] **UAE** (1): American University of Sharjah
- [ ] **South Africa** (2): Cape Town, Stellenbosch
- [ ] Find career portals
- [ ] Verify economics programs and job postings

**Acceptance Criteria**:
- ✅ 5 universities from Middle East/Africa identified
- ✅ All URLs verified
- ✅ URLs added to scraping_sources.json

---

## Phase 1B.3: Research Institutes & Think Tanks

### Task 12: Add Major US Research Institutes
**Status**: Not Started  
**Priority**: High

**Target**: 15 organizations

**Subtasks**:
- [ ] Fix **Brookings Institution** (redirect to ICIMS)
- [ ] Add **RAND Corporation**
- [ ] Add **Urban Institute**
- [ ] Add **American Enterprise Institute**
- [ ] Add **Cato Institute**
- [ ] Fix **National Bureau of Economic Research** (timeout issue)
- [ ] Add **Federal Reserve Banks** (all 12 districts)
- [ ] Fix **Federal Reserve Bank of San Francisco** (no job content verified)
- [ ] Add **IMF**
- [ ] Add **World Bank**
- [ ] Add **Inter-American Development Bank**
- [ ] Verify career pages
- [ ] Handle external career systems (ICIMS, Workday)

**Acceptance Criteria**:
- ✅ 15 US research institutes added
- ✅ Brookings redirect handled correctly
- ✅ Federal Reserve banks all added
- ✅ All URLs verified for job content

---

### Task 13: Add International Research Organizations
**Status**: Not Started  
**Priority**: Medium

**Target**: 10 organizations

**Subtasks**:
- [ ] Add **OECD** (Paris)
- [ ] Add **European Central Bank**
- [ ] Add **Bank of England**
- [ ] Add **Asian Development Bank**
- [ ] Fix **Centre for Economic Policy Research** (CEPR)
- [ ] Add **Bruegel** (Belgium)
- [ ] Add **IZA** (Germany)
- [ ] Fix **Peterson Institute** (PIIE - 403 Forbidden)
- [ ] Add **J-PAL** (MIT)
- [ ] Add **International Growth Centre**
- [ ] Verify career portals
- [ ] Handle international sites

**Acceptance Criteria**:
- ✅ 10 international organizations added
- ✅ All URLs verified for accessibility
- ✅ CEPR and PIIE issues resolved
- ✅ URLs added to scraping_sources.json

---

## Phase 1B.4: Fix Existing Problematic URLs

### Task 14: Fix US University URLs (30+ broken) - WRONG URL TYPE ISSUE
**Status**: Not Started  
**Priority**: CRITICAL

**Root Cause**: Most "broken" URLs are actually pointing to wrong page types:
- Department homepages (e.g., `https://economics.{university}.edu/`)
- Faculty directories (e.g., `https://{university}.edu/faculty/`)
- General university pages instead of HR/career portals

**Detailed Step-by-Step Plan**:

#### Step 14.1: Pilot Test on 3 Major Universities
- [ ] **Princeton University**:
  - Current URL: `https://economics.princeton.edu/`
  - Issue: DEPARTMENT_PAGE, no job listings
  - Run Task 0 discovery: Find actual career portal
  - Test alternatives: `/careers`, `/hr/`, `/faculty-positions`
  - Manual verification: Visit top 3 suggestions, confirm jobs present
  - Select best: Record URL, quality score, redirect chain (if any)
  - Update config: old → non_accessible (wrong_page_type), new → accessible
  
- [ ] **University of Pennsylvania** (Economics):
  - Current URL: `https://upennecon.upenn.edu/`
  - Issue: DEPARTMENT_PAGE, no job listings
  - Run discovery, test alternatives, manually verify
  - Update config with best URL
  
- [ ] **Columbia University** (Economics):
  - Current URL: `https://www.columbia.edu/cgi-bin/am?page=columbia/economics`
  - Issue: DEPARTMENT_PAGE, no job listings  
  - Run discovery, test alternatives, manually verify
  - Update config with best URL

**Pilot Acceptance Criteria**:
- ✅ All 3 universities have better URLs discovered
- ✅ All discovered URLs verified to have job listings
- ✅ Quality scores ≥60 for all new URLs
- ✅ Configuration successfully updated
- ✅ Old URLs marked with "wrong_page_type" reason code
- ✅ Process documented for full rollout

#### Step 14.2: Process for Each University (if pilot successful)
For each of 30+ broken US universities, repeat this workflow:

1. **Identify Current Problem**:
   - [ ] Get current URL from scraping_sources.json
   - [ ] Log why it's marked as broken
   - [ ] Classify as: department_page, faculty_directory, general_page, or other

2. **Run URL Discovery** (Task 0):
   - [ ] Call `discover_career_portal_url(current_url)`
   - [ ] Get top 3 suggestions ranked by score
   - [ ] Record: URL, classification, quality score, confidence

3. **Test Top Suggestions**:
   - [ ] Manually visit each top suggestion
   - [ ] Check for: job titles, positions, departments, deadlines, apply buttons
   - [ ] Count visible jobs (should be >3)
   - [ ] Verify extractable critical fields (title + position details)
   - [ ] Estimate quality score manually

4. **Verify Automatically**:
   - [ ] Run validation_and_classify_url() from Task 0
   - [ ] Check: Accessible? Type correct? Jobs extractable? Quality ≥60?
   - [ ] If not ≥60: Try next suggestion
   - [ ] If ≥60: ACCEPT this URL

5. **Update Configuration**:
   - [ ] Add new URL to accessible section with metadata:
     * verified_date: today
     * quality_score: X/100
     * previous_url: old_url
     * reason_changed: "wrong_page_type → career_portal"
     * redirect_chain: chain_if_any
   - [ ] Move old URL to non_accessible with:
     * reason: "wrong_page_type"
     * reason_detail: "department_page" or "faculty_directory"
     * suggestion: new_url
     * next_action: "fixed_in_phase1b"

6. **Log Results**:
   - [ ] Record: university, old_url, new_url, quality_improvement, success

#### Step 14.3: Target Universities (30+)
Process in this order (by region/tier):

**Tier 1 - Top Tier Universities (10)**:
- Princeton, UPenn (Econ+Mgmt=2), Columbia (Econ+Mgmt=2), NYU (Econ+Mgmt=2), Michigan (Econ+Mgmt=2)

**Tier 2 - Major State Universities (10)**:
- Wisconsin-Madison, Penn State, Ohio State, Virginia, Texas Austin, Illinois, Indiana, Arizona, UC Berkeley, USC

**Tier 3 - Other Universities (10+)**:
- Vanderbilt, Rice, Arizona, UMass Amherst, Michigan State, Oregon, Temple, Washington State, North Carolina, Georgia Tech, Duke, Brown

#### Step 14.4: Batch Processing and Automation
Once workflow proven, optimize:
- [ ] Automate discovery for all 30+ URLs simultaneously
- [ ] Generate batch report: current → discovered → quality scores
- [ ] Highlight: 90%+ success (27+) as goal
- [ ] Mark for manual review: any <60 score URLs

#### Step 14.5: Quality Assurance
Before final update:
- [ ] Spot check 5 random fixed URLs (manually visit)
- [ ] Confirm all have visible job listings
- [ ] Verify extraction works on new URLs (try parser on sample)
- [ ] Check no typos in configuration
- [ ] Backup old configuration before update

**Detailed University List**:
```
Priority Order for Fixing:
──────────────────────────

TIER 1 (10 universities):
1. Princeton
2. UPenn Economics
3. UPenn Management
4. Columbia Economics
5. Columbia Management
6. NYU Economics
7. NYU Management
8. Michigan Economics
9. Michigan Management
10. Wisconsin-Madison

TIER 2 (10 universities):
11. Penn State
12. Ohio State
13. Virginia
14. Texas Austin
15. Illinois
16. Indiana
17. Arizona
18. UC Berkeley
19. USC
20. Duke

TIER 3 (10+ universities):
21. Vanderbilt
22. Rice
23. Brown
24. UMass Amherst
25. Michigan State
26. Oregon
27. Temple
28. Washington State
29. North Carolina
30. Georgia Tech
... (and more as needed)
```

**Acceptance Criteria**:
- ✅ 27+ (90%) of broken US URLs fixed with correct career portal URLs
- ✅ All fixes verified to have actual job listings
- ✅ All new URLs scored ≥60 quality
- ✅ Configuration updated with all fixes
- ✅ Old URLs marked with "wrong_page_type" reason code
- ✅ Process documented for future maintenance
- ✅ Spot-check confirms fixes work correctly

**Expected Outcome**: 
- `https://economics.princeton.edu/` → `https://careersearch.princeton.edu/` (quality: 85/100)
- `https://upennecon.upenn.edu/` → `https://hr.upenn.edu/faculty-positions` (quality: 78/100)
- `https://www.columbia.edu/economics/` → `https://careers.columbia.edu/` (quality: 82/100)
- Result: +27 working URLs, +25 correct URLs moved to accessible, old URLs properly archived

---

### Task 15: Fix Chinese University URLs (40+ failing) - VPN STRATEGY
**Status**: Not Started  
**Priority**: High

**Root Cause Analysis**: 40+ Chinese universities have DNS resolution failures or timeouts, likely due to:
- Great Firewall blocking certain domain patterns (rsc.*.edu.cn)
- DNS routing issues for Chinese domains from outside China
- Server firewall restrictions

**Detailed Step-by-Step Plan**:

#### Step 15.1: Pre-Test Analysis
- [ ] Categorize failing URLs by error type:
  - DNS resolution errors (unable to resolve hostname)
  - Connection timeouts (no response after 30+ seconds)
  - SSL certificate errors
  - 503/502 errors (server errors)
  - Access denied (likely GFW)
- [ ] Identify patterns: which domain patterns fail most?
  - `rsc.*.edu.cn` vs `hr.*.edu.cn` vs others
  - Geographic regions with more failures
  - Universities with worse failure rates

#### Step 15.2: Test Alternative Domain Patterns
For each failing university, test in order:

1. **Original pattern** (usually failing):
   - e.g., `https://rsc.tsinghua.edu.cn/`
   
2. **HR Portal** (likely to work):
   - `https://hr.{university}.edu.cn/`
   
3. **Job Portal** (likely to work):
   - `https://job.{university}.edu.cn/` or `https://jobs.{university}.edu.cn/`
   
4. **Talent Recruitment** (likely to work):
   - `https://talent.{university}.edu.cn/`
   
5. **Via Main Domain**:
   - `https://www.{university}.edu.cn/jobs`
   - `https://www.{university}.edu.cn/rczp` (Chinese for recruitment)
   - `https://www.{university}.edu.cn/hr/`
   
6. **Alternative patterns**:
   - `https://{university}.edu.cn/jobs`
   - `https://{university}.edu.cn/careers`

For each pattern:
- [ ] Test accessibility
- [ ] Record success/failure
- [ ] If accessible: classify page type
- [ ] If job content found: calculate quality score

#### Step 15.3: Use Chinese DNS Servers for Retry
If initial DNS fails, retry with Chinese DNS servers:
- [ ] Alidns: 223.5.5.5, 223.6.6.6 (Alibaba)
- [ ] DNSPod: 119.29.29.29 (Tencent)
- [ ] Tencent DNS: 119.28.28.28
- [ ] ChinaCache: 180.154.128.1

Retry pattern:
1. First attempt: Default DNS
2. If fails: Retry with Alidns
3. If fails: Retry with DNSPod
4. If fails: Retry with Tencent DNS
5. If all fail: Mark as "requires_vpn" or "gfw_blocked"

#### Step 15.4: Detect and Mark VPN-Required URLs
If URL fails all DNS/domain patterns:
- [ ] Mark as "requires_vpn: true"
- [ ] Add reason: "gfw_blocked" or "dns_resolution_failure"
- [ ] Document which patterns were tested
- [ ] Keep in non_accessible section
- [ ] Note: "May be accessible within China or with VPN"

#### Step 15.5: Verify Chinese Language Content
For URLs that successfully load (using alternative patterns or Chinese DNS):
- [ ] Verify Chinese recruitment keywords present:
  - 人才招聘 (talent recruitment)
  - 教师招聘 (teacher recruitment)  
  - 岗位招聘 (position recruitment)
  - 岗位 (position/job)
  - 申请 (apply)
  - 截止 (deadline)
  - 报名 (registration)
- [ ] If keywords found: Likely has job listings
- [ ] Extract jobs and calculate quality score

#### Step 15.6: Document Working Patterns
For universities where alternative pattern worked:
- [ ] Record: old_pattern → new_pattern
- [ ] Identify if pattern is consistent by region:
  - Northern vs. Southern China
  - Top-tier vs. lower-tier universities
  - Economics schools vs. others
- [ ] Create lookup table:
  ```
  Pattern Success by Region:
  ├─ hr.*.edu.cn: 80% success rate
  ├─ job.*.edu.cn: 60% success rate
  ├─ talent.*.edu.cn: 50% success rate
  └─ www.*.edu.cn/rczp: 40% success rate
  ```

#### Step 15.7: Test on Pilot Set (10 Universities)
- [ ] Tsinghua University (404 Not Found)
- [ ] Nanjing University (DNS failure)
- [ ] Shandong University (DNS failure)
- [ ] Jilin University (DNS failure)
- [ ] Xi'an Jiaotong University (DNS failure)
- [ ] Central University of Finance and Economics (DNS failure)
- [ ] Shanghai University of Finance and Economics (DNS failure)
- [ ] Zhongnan University of Economics and Law (SSL error)
- [ ] Dalian University of Technology (DNS failure)
- [ ] South China Normal University (connection aborted)

For each:
- [ ] Try all alternative patterns
- [ ] Use Chinese DNS servers if needed
- [ ] Document what worked
- [ ] If found: update config with new URL
- [ ] If not found: mark as requires_vpn

#### Step 15.8: Full Rollout (40+ Universities)
Once pilot proves successful:
- [ ] Batch test all failing Chinese university URLs
- [ ] Apply same pattern testing logic
- [ ] Update configuration with all working alternatives
- [ ] Move fixed URLs from non_accessible to accessible
- [ ] Mark VPN-required URLs appropriately

**Acceptance Criteria**:
- ✅ Successfully finds alternatives for 20+ (50%+) of failing Chinese universities
- ✅ Chinese DNS server fallback works reliably
- ✅ VPN-required URLs clearly marked
- ✅ Working domain patterns documented by region
- ✅ Configuration updated with all fixes and VPN flags
- ✅ Quality scores verified for all working URLs

**Expected Outcome**:
- Tsinghua: `rsc.*.edu.cn` → `hr.tsinghua.edu.cn/` (quality: 72/100)
- Nanjing: DNS failure → `job.nju.edu.cn/` (quality: 68/100)
- CUFE: DNS failure → `talent.cufe.edu.cn/` (quality: 75/100)
- Result: 20+ fixed URLs, 20+ marked as requires_vpn (for future access)

---

### Task 16: Fix International University URLs (10+ broken)
**Status**: Not Started  
**Priority**: Medium

**Detailed Plan**:

#### Step 16.1: By Country - UK (2 broken URLs)
- [ ] **University of Cambridge**:
  - Current: `https://www.cam.ac.uk/jobs/` (403 Forbidden)
  - Test alternatives: `/hr/`, `/careers/`, `/positions/`
  - If still 403: Likely restricted, try `/research/`
  - Check if Cambridge has department-specific portals
  
- [ ] **University of Edinburgh**:
  - Current: `https://www.ed.ac.uk/jobs/` (404 Not Found)
  - Test alternatives: `/hr/jobs/`, `/careers/`, `/positions/`
  - Check if redirects to external system
  - Document working URL or mark as blocked

#### Step 16.2: By Country - Australia (12+ broken URLs)
Strategy: Many Australian URLs fail with 404/403/500 errors
- [ ] Test all failing URLs for alternative patterns
- [ ] For each: Try `/careers`, `/jobs`, `/hr/careers`, `/employment`
- [ ] Check if uses external system (seek.com.au, etc.)
- [ ] Document working URLs or mark as inaccessible

Universities to fix:
- Sydney, Queensland, Monash, UTS, Macquarie, Griffith, Deakin, Wollongong, Curtin, RMIT, James Cook, Newcastle

#### Step 16.3: By Country - Germany (2 URLs)
- [ ] **Ludwig Maximilian University of Munich**: Fix `/aktuelles/stellenangebote/`
- [ ] **University of Bonn**: Fix `/en/university/administration/jobs`

#### Step 16.4: By Country - France, Netherlands, Singapore
- [ ] France: Paris School of Economics (418 error)
- [ ] Netherlands: Erasmus Rotterdam (404 error)
- [ ] Singapore: NTU (404 error)

#### Step 16.5: Quality Assurance
- [ ] For all international fixes:
  - Manual verification (visit page manually)
  - Verify extractable job titles and positions
  - Calculate quality score
  - Handle non-English content appropriately

**Acceptance Criteria**:
- ✅ 60%+ (7+) of broken international URLs fixed
- ✅ All fixes verified to have job content
- ✅ Configuration updated with corrected URLs
- ✅ Non-English sites handled appropriately

---

**Subtasks**:
- [ ] **UK**: Fix Cambridge (403), Edinburgh (404)
- [ ] **Australia**: Fix Sydney (500), Queensland (error), Monash (403), UTS (404), Macquarie (404), Griffith (404), Deakin (403), Wollongong (404), Curtin (404), RMIT (404), James Cook (403), Newcastle (403)
- [ ] **Germany**: Fix Munich (404), Bonn (404)
- [ ] **France**: Fix Paris School of Economics (418)
- [ ] **Netherlands**: Fix Erasmus Rotterdam (404)
- [ ] **Singapore**: Fix NTU (404)
- [ ] Test replacement URLs
- [ ] Verify job content on new URLs
- [ ] Update configuration

**Acceptance Criteria**:
- ✅ 60%+ (7+) of broken international URLs fixed
- ✅ All fixes verified
- ✅ Configuration updated with working URLs

---

## Phase 1B.5: Verification & Validation

### Task 17: Run Enhanced Verification on All URLs
**Status**: Not Started  
**Priority**: High

**Subtasks**:
- [ ] Run enhanced verify_urls.py on:
  - 176 existing accessible URLs (re-verify)
  - 81 problematic URLs (test fixes)
  - ~110 new URLs (verify before adding)
- [ ] Generate comprehensive verification report
- [ ] Review results and identify issues
- [ ] Create action plan for remaining problems

**Acceptance Criteria**:
- ✅ All URLs verified with enhanced script
- ✅ Report generated with detailed metrics
- ✅ Success rate by region documented
- ✅ Remaining issues identified with solutions

**Command**:
```bash
poetry run python scripts/scraper/check_config/verify_urls.py --enhanced --follow-redirects --detect-pdfs
```

---

### Task 18: Update Configuration with Verified URLs
**Status**: Not Started  
**Priority**: High

**Subtasks**:
- [ ] Move fixed URLs from non_accessible to accessible
- [ ] Add all verified new URLs to accessible section
- [ ] Organize by region and institution type
- [ ] Add metadata for each URL:
  - Verification date
  - Content quality score
  - Redirect information (if applicable)
  - VPN requirement (if applicable)
  - PDFs found (if any)
- [ ] Update statistics in configuration comments

**Acceptance Criteria**:
- ✅ All verified URLs in accessible section
- ✅ Non_accessible contains only truly broken URLs
- ✅ Metadata complete for all entries
- ✅ Configuration well-organized and documented

**Files to Modify**:
- `data/config/scraping_sources.json`

---

### Task 19: Test Scraping on Sample of New URLs
**Status**: Not Started  
**Priority**: High

**Subtasks**:
- [ ] Select 10 URLs per region for pilot test
- [ ] Run university_scraper.py on each
- [ ] Check data extraction quality:
  - Job titles extracted correctly
  - Descriptions present (>80% coverage)
  - Deadlines parsed (if available)
  - Application links found (>60% coverage)
- [ ] Identify parsing issues or patterns
- [ ] Calculate success rate by region
- [ ] Document findings

**Acceptance Criteria**:
- ✅ 50+ new URLs tested with scrapers
- ✅ Success rate >70% for data extraction
- ✅ Parsing issues documented
- ✅ Recommendations for scraper improvements

**Command**:
```bash
poetry run python scripts/scraper/university_scraper.py --test-mode --urls-file test_urls.txt
```

---

## Phase 1B.6: Documentation & Finalization

### Task 20: Consolidate Verification Documentation
**Status**: Not Started  
**Priority**: Medium

**Subtasks**:
- [ ] Merge URL_VERIFICATION.md and URL_VERIFICATION_RESULTS.md
- [ ] Create single `url_verification.md` with sections:
  - **Verification Methodology** (how verification works)
  - **Current Results Summary** (statistics, success rates)
  - **Regional Breakdown** (by country/region)
  - **Known Issues** (problematic URL patterns)
  - **Solutions** (fixes implemented, VPN requirements)
  - **URL Pattern Guidelines** (working patterns by region)
  - **Maintenance Schedule** (how often to re-verify)
- [ ] Delete old verification files
- [ ] Update read_it.md to reference new file

**Acceptance Criteria**:
- ✅ Single consolidated url_verification.md file exists
- ✅ All information from old files preserved
- ✅ Document well-organized and searchable
- ✅ Old files removed

**Files to Create**:
- `data/config/url_verification.md`

**Files to Remove**:
- `data/config/URL_VERIFICATION.md`
- `data/config/URL_VERIFICATION_RESULTS.md`

---

### Task 21: Update Project Documentation
**Status**: Not Started  
**Priority**: Medium

**Subtasks**:
- [ ] Update `conversation_cursor/progress/latest.md`:
  - Add Phase 1B section
  - Document accomplishments
  - Update coverage statistics
- [ ] Update `conversation_cursor/structure/latest.md`:
  - Add Phase 1B to structure
  - Update file descriptions
  - Add new verification tools section
- [ ] Update `README.md`:
  - Update coverage statistics
  - Add Phase 1B to pipeline overview
  - Link to url_verification.md
- [ ] Update `docs/SCRAPING_GUIDE.md` (if needed):
  - Add section on redirect handling
  - Document PDF extraction process
  - Add international scraping tips

**Acceptance Criteria**:
- ✅ All documentation files updated
- ✅ Statistics current and accurate
- ✅ Phase 1B clearly documented
- ✅ Links between documents working

**Files to Modify**:
- `conversation_cursor/progress/latest.md`
- `conversation_cursor/structure/latest.md`
- `README.md`

---

### Task 22: Generate Final Statistics and Report
**Status**: Not Started  
**Priority**: Low

**Subtasks**:
- [ ] Calculate final metrics:
  - Total accessible URLs (target: 250+)
  - URLs by region (percentage breakdown)
  - URLs by institution type (university vs. institute)
  - Fix rate for problematic URLs (target: 75%)
  - Content quality score distribution
  - Estimated job listings increase
- [ ] Generate visualization (optional):
  - Regional distribution pie chart
  - Success rate by region bar chart
  - Content quality histogram
- [ ] Create summary report for stakeholders
- [ ] Document lessons learned and recommendations

**Acceptance Criteria**:
- ✅ All metrics calculated and documented
- ✅ Comparison with initial state (before Phase 1B)
- ✅ Summary report created
- ✅ Recommendations for future maintenance

---

## Success Metrics

### Quantitative Goals
- [ ] **Accessible URLs**: 176 → 250+ (42% increase)
- [ ] **Regional Balance**:
  - US: 70 URLs (28%)
  - China: 100 URLs (40%)
  - Europe: 35 URLs (14%)
  - Asia-Pacific: 30 URLs (12%)
  - Latin America: 10 URLs (4%)
  - Other: 5 URLs (2%)
- [ ] **Fix Rate**: 60+/81 problematic URLs resolved (75%)
- [ ] **Research Institutes**: 6 → 25+ (4x growth)
- [ ] **Job Listings**: 211 → 350-400 (projected 65% increase)

### Qualitative Improvements
- [ ] Better geographic diversity (reduce US-centric bias)
- [ ] More international opportunities for global audience
- [ ] Improved data quality (verified job content)
- [ ] Robust verification (handles redirects, deep content)
- [ ] PDF support (extract from documents)

---

## Notes

- **Priority**: Focus on Tasks 1-6 (verification tools) first, then Tasks 7-13 (URL research), then Tasks 14-16 (fixes)
- **Testing**: Pilot test each region before bulk addition (Task 19)
- **Documentation**: Keep url_verification.md updated throughout (Task 20)
- **Review**: Check progress against success metrics after each phase

---

## Timeline

- **Days 1-2**: Tasks 1-6 (Enhanced verification tools)
- **Days 3-5**: Tasks 7-13 (URL research and addition)
- **Days 6-7**: Tasks 14-19 (Fix URLs and validation)
- **Day 8**: Tasks 20-22 (Documentation and reporting)

**Total Estimated Time**: 8 days
