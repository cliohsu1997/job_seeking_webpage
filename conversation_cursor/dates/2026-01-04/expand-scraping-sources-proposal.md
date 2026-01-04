# Proposal: Expand Scraping Sources for Global Coverage

**Date:** 2026-01-04  
**Phase:** Phase 1B - Expand Data Collection  
**Status:** In Implementation  
**Proposed by:** User (with GitHub Copilot assistance)  
**Current Implementation**: ACCESS → VALIDATE → REPLACE Strategy

## Overview

Expand the scraping source configuration to achieve better global coverage of economics faculty job listings. Currently, the accessible sources are heavily weighted toward US universities (~60 URLs) with limited international representation. This proposal aims to diversify sources by adding more universities from Europe, Asia, Canada, Latin America, and other regions, while also fixing existing problematic URLs.

## Current State Analysis

### Current Coverage (176 accessible URLs)
- **US Universities**: ~60 URLs (34%)
- **Mainland China**: 100+ URLs (57%)
- **Other Countries**: ~16 URLs (9%)
  - UK: 3 universities
  - Canada: 1 university
  - Australia: 6 universities
  - Germany: 2 universities
  - France: 1 university
  - Netherlands: 2 universities
  - Singapore: 1 university

### Known Issues (81 problematic URLs)
1. **US Universities** (30+): No job content verified on many URLs
2. **Chinese Universities** (40+): DNS resolution failures, connection errors
3. **International Universities** (10+): 403/404 errors, no job content
4. **Research Institutes** (3-5): Timeouts, no job content verified
5. **Wrong URL Type**: Many URLs point to general department pages, faculty directories, or homepage instead of actual job/career portals

### Root Cause: Wrong URL Types

**Critical Issue Identified**: Many existing URLs in scraping_sources.json point to the wrong type of page:

1. **General Department Pages** (e.g., `https://economics.{university}.edu/`)
   - Shows faculty profiles, research, courses
   - No job listings or career information
   - Result: "No job content verified"

2. **Faculty Directory Pages** (e.g., `https://{university}.edu/faculty/`)
   - Lists current faculty members
   - Not a recruitment page
   - Result: Parser finds names but no job postings

3. **University Homepage** (e.g., `https://{university}.edu/`)
   - General information about university
   - Job links buried deep in navigation
   - Result: Low content quality score

4. **Research Pages** (e.g., `https://{university}.edu/research/`)
   - Describes research centers and projects
   - No hiring information
   - Result: No job content verified

**What We Need**: Direct links to job/career portals:
- ✅ GOOD: `https://hr.{university}.edu/careers`
- ✅ GOOD: `https://{university}.edu/faculty-positions`
- ✅ GOOD: `https://jobs.{university}.edu/`
- ✅ GOOD: `https://careers.{university}.edu/faculty`
- ❌ BAD: `https://economics.{university}.edu/` (department homepage)
- ❌ BAD: `https://{university}.edu/faculty/` (faculty directory)
- ❌ BAD: `https://{university}.edu/` (university homepage)

**Impact**: This explains why 30+ US universities show "No job content verified" - we're looking at the wrong pages. The job postings exist, we just need to find the correct HR/career portal URLs.

### Coverage Gaps
- **Europe**: Limited coverage (5 universities total)
  - Missing: Spain, Italy, Switzerland, Scandinavia, Eastern Europe
- **Asia**: Only China and Singapore
  - Missing: Japan, South Korea, Hong Kong, Taiwan, India
- **Canada**: Only 1 university (McGill)
  - Missing: Toronto, UBC, Western, Queen's, etc.
- **Latin America**: Zero coverage
  - Missing: Brazil, Mexico, Chile, Argentina
- **Oceania**: Limited Australia (6), no New Zealand
- **Research Institutes**: Very limited (6 total, 3 with issues)

## Objectives

1. **Diversify geographic coverage** - Add universities from underrepresented regions
2. **Fix existing URLs** - Resolve the 81 problematic URLs with working alternatives
3. **Add research institutes** - Expand think tank and research organization coverage
4. **Enhance verification** - Implement redirect-following and deep content verification
5. **Improve Chinese university access** - Find working alternatives for DNS-blocked URLs

## Proposed Enhancements

### 1. Enhanced URL Verification System

**Current Limitations:**
- No redirect following (e.g., Brookings careers page redirects to ICIMS)
- Limited content depth verification
- No PDF/document detection and download
- Single-level URL checking
- **Not detecting wrong URL types** (department page vs. career portal)

**Proposed Improvements:**
```python
class EnhancedURLVerifier:
    def discover_career_portal_url(base_url):
        """Find the actual career/job portal from university homepage"""
        - Parse homepage and look for career/jobs links in navigation
        - Test common URL patterns: /careers, /jobs, /faculty-positions, /hr/careers, /employment
        - Look for "Careers", "Jobs", "Employment", "Faculty Positions" link text
        - Search for "Apply", "Work Here", "Join Us" sections
        - Rank discovered URLs by likelihood of being job portal
        - Return top 3 candidates with confidence scores
    
    def verify_url_with_redirects(url, max_redirects=5):
        """Follow redirects and verify final target page"""
        - Follow HTTP redirects (301, 302, 307, 308)
        - Check final destination for job content
        - Handle external career systems (ICIMS, Workday, PeopleAdmin)
        - Score content based on job keywords, links, PDFs
        - **Detect if URL is wrong type** (department vs. career page)
        
    def classify_url_type(url, content):
        """Classify if URL is career portal or wrong type"""
        - Check page title and meta description
        - Analyze navigation menu structure
        - Count job-related links vs. faculty/research links
        - Detect common patterns:
          * Career portal: "Apply", "Positions", "Openings", "Search Jobs"
          * Department page: "Faculty", "Research", "Courses", "Students"
          * Faculty directory: List of names with titles
        - Return classification: career_portal, department_page, faculty_directory, other
        - If wrong type, attempt to find correct career portal URL
    
    def detect_and_download_pdfs(url):
        """Find and download relevant job posting PDFs"""
        - Scan page for PDF links
        - Filter by keywords (economics, faculty, position)
        - Download to data/raw/documents/
        - Return metadata for scraping_sources.json
        
    def verify_chinese_university_urls(url):
        """Special handling for Chinese university URLs"""
        - Test alternative domain patterns (hr., rsc., job., etc.)
        - Handle Great Firewall restrictions
        - Detect language and verify Chinese keyword presence
        - Use retry with different DNS servers
```

**Implementation:**
- Modify `scripts/scraper/check_config/verify_urls.py`
- Add redirect following with requests `allow_redirects=True`
- Implement content depth scoring (0-100)
- Add PDF detection and download capability
- Create summary report with recommendations

### 2. International University Expansion

**Target Regions and Universities:**

#### Europe (Target: 30 universities)
**UK** (add 10 more):
- Oxford, LSE, Warwick, Manchester, UCL, Imperial College, Bristol, Glasgow, Nottingham, Southampton

**Germany** (add 5):
- Mannheim, Frankfurt, Humboldt, Free University Berlin, Cologne

**France** (add 3):
- Toulouse School of Economics, Sciences Po, HEC Paris

**Netherlands** (add 2):
- Tilburg, Maastricht

**Spain** (add 3):
- Barcelona GSE, Pompeu Fabra, Carlos III Madrid

**Switzerland** (add 2):
- University of Zurich, Geneva

**Scandinavia** (add 3):
- Stockholm School of Economics, Copenhagen, Oslo

**Italy** (add 2):
- Bocconi, Bologna

#### Asia-Pacific (Target: 25 universities)
**Japan** (add 5):
- University of Tokyo, Hitotsubashi, Waseda, Keio, Kyoto

**South Korea** (add 3):
- Seoul National University, Korea University, Yonsei

**Hong Kong** (add 4):
- HKU, HKUST, CUHK, CityU

**Taiwan** (add 3):
- National Taiwan University, Academia Sinica, National Chengchi

**Singapore** (already have NTU, add 2):
- NUS, SMU

**India** (add 4):
- Indian Statistical Institute, Delhi School of Economics, IIM Ahmedabad, IIM Bangalore

**Australia** (expand current 6, add 4):
- University of New South Wales, Queensland University of Technology, South Australia, Tasmania

**New Zealand** (add 2):
- University of Auckland, Victoria University of Wellington

#### North America (Target: 20 universities)
**Canada** (add 10):
- Toronto, UBC, Western, Queen's, Calgary, Alberta, McMaster, Waterloo, Simon Fraser, York

**US** (fix existing + add 10 top programs):
- Focus on replacing broken URLs for Princeton, UPenn, Columbia, NYU, Michigan, etc.
- Add: Duke, Brown, Johns Hopkins, Georgetown, Carnegie Mellon, Emory, Notre Dame, USC, Indiana, Arizona State

#### Latin America (Target: 10 universities)
**Brazil** (add 4):
- University of São Paulo, Fundação Getulio Vargas, PUC-Rio, University of Brasília

**Mexico** (add 2):
- ITAM, El Colegio de México

**Chile** (add 2):
- University of Chile, Pontifical Catholic University

**Argentina** (add 2):
- Universidad de Buenos Aires, Universidad Torcuato Di Tella

#### Middle East & Africa (Target: 5 universities)
**Israel** (add 2):
- Hebrew University, Tel Aviv University

**UAE** (add 1):
- American University of Sharjah

**South Africa** (add 2):
- University of Cape Town, Stellenbosch

### 3. Research Institutes & Think Tanks

**Target: 20 organizations**

**US-based** (add 10):
- Brookings Institution (fix with redirect support) ✓
- RAND Corporation
- Urban Institute
- American Enterprise Institute
- Cato Institute
- National Bureau of Economic Research (fix timeout)
- Federal Reserve Banks (all 12 districts)
- IMF
- World Bank
- Inter-American Development Bank

**International** (add 5):
- OECD (Paris)
- European Central Bank
- Bank of England
- Asian Development Bank
- Centre for Economic Policy Research (fix)

**Academic Research Centers** (add 5):
- NBER (fix)
- J-PAL (MIT)
- IZA (Germany)
- CEPR (fix)
- Bruegel (Belgium)

### 4. Job Portals & Aggregators

**Academic Job Boards** (expand current 5):
- Academic Jobs Online (AJO)
- INOMICS (Europe-focused)
- Jobs.ac.uk (UK-focused)
- HigherEdJobs.com (expand coverage) ✓
- Indeed (economics faculty filter)
- LinkedIn Jobs (API access)
- Glassdoor (academic positions)

### 5. Chinese University URL Fixes

**Strategy for DNS Resolution Failures:**
1. **Test alternative domain patterns**:
   - `hr.*.edu.cn` (HR portals) ✓ Already tried
   - `job.*.edu.cn` (Job portals)
   - `jobs.*.edu.cn`
   - `rsc.*.edu.cn` (Original, many failing)
   - `talent.*.edu.cn`
   - `www.*.edu.cn/jobs`

2. **Use VPN or Chinese DNS servers** (if accessible)
   - Alidns: 223.5.5.5, 223.6.6.6
   - DNSPod: 119.29.29.29
   - Test with different resolvers

3. **Search for official recruitment platforms**:
   - Many Chinese universities use unified platforms
   - Check university main sites for recruitment links
   - Look for "人才招聘" (talent recruitment) pages

4. **Alternative verification approach**:
   - Mark as "requires_vpn" if blocked outside China
   - Document working URLs from within China
   - Use web scraping services with Chinese IPs

### 6. PDF and Document Handling

**New Feature: Automatic PDF Discovery and Download**

When verifying URLs, automatically:
1. Scan pages for linked PDFs
2. Check if PDFs contain job-related content
3. Download relevant PDFs to `data/raw/documents/`
4. Store metadata in scraping_sources.json

**PDF Categories:**
- Faculty position announcements
- Department hiring brochures
- Business school job listings
- Research center opportunities
- Visiting scholar programs

**Storage Structure:**
```
data/raw/documents/
├── universities/
│   ├── {university_name}_{department}_{date}.pdf
├── institutes/
│   ├── {institute_name}_{date}.pdf
└── job_portals/
    ├── {portal_name}_{date}.pdf
```

## Implementation Plan

### Phase 1: Enhanced Verification Tools
**Timeline:** Days 1-2

1. **Enhance verify_urls.py**:
   - Add redirect following (max 5 redirects)
   - Implement content depth scoring
   - Add PDF detection and download
   - Improve Chinese URL handling
   - Generate detailed verification report

2. **Create URL replacement script**:
   - Automated search for alternative URLs
   - Test common patterns systematically
   - Suggest replacements with confidence scores
   - Batch update capability

3. **Testing**:
   - Test on Brookings (redirect example)
   - Test on 10 problematic Chinese universities
   - Test on 5 international universities with errors
   - Verify PDF download functionality

### Phase 2: URL Research & Addition
**Timeline:** Days 3-5

1. **Research universities** (manual + automated):
   - Use QS Rankings, Times Higher Education
   - Find official career/HR pages
   - Verify job posting presence
   - Document URL patterns

2. **Add to scraping_sources.json**:
   - Europe: 30 universities
   - Asia-Pacific: 25 universities
   - North America: 20 universities (including fixes)
   - Latin America: 10 universities
   - Middle East & Africa: 5 universities
   - Research institutes: 20 organizations
   - **Total new entries: ~110 URLs**

3. **Organize by priority**:
   - Tier 1: Top 50 global economics programs (high priority)
   - Tier 2: Regional leaders (medium priority)
   - Tier 3: Specialized schools (low priority)

### Phase 3: Verification & Validation
**Timeline:** Days 6-7

1. **Run enhanced verification** on all URLs:
   - Existing 176 accessible URLs (re-verify)
   - 81 problematic URLs (fix or replace)
   - ~110 new URLs (verify before adding)
   - **Target: 250+ accessible URLs**

2. **Fix or replace broken URLs**:
   - US universities: Find working career pages
   - Chinese universities: Alternative domains or mark as VPN-required
   - International universities: Test alternative paths
   - Research institutes: Handle redirect destinations

3. **Generate comprehensive report**:
   - Success rate by region
   - Content quality scores
   - URL patterns that work
   - Recommendations for manual review

### Phase 4: Documentation & Testing
**Timeline:** Day 8

1. **Consolidate verification documentation**:
   - Merge URL_VERIFICATION.md and URL_VERIFICATION_RESULTS.md
   - Create single `url_verification.md` with:
     - Verification methodology
     - Current results summary
     - Known issues and solutions
     - URL pattern guidelines

2. **Update configuration**:
   - Move fixed URLs from non_accessible to accessible
   - Add all verified new URLs to accessible
   - Document URLs requiring special handling
   - Update region distribution statistics

3. **Test scraping** on sample of new URLs:
   - Select 10 new URLs per region
   - Run scrapers and verify data extraction
   - Check for parsing issues
   - Measure success rate

## Expected Outcomes

### Quantitative Goals
- **Accessible URLs**: Increase from 176 to 250+ (42% growth)
- **Regional Balance**: 
  - US: 70 URLs (28%)
  - China: 100 URLs (40%)
  - Europe: 35 URLs (14%)
  - Asia-Pacific: 30 URLs (12%)
  - Latin America: 10 URLs (4%)
  - Other: 5 URLs (2%)
- **Fix Rate**: Resolve 60+ of 81 problematic URLs (75% success)
- **Research Institutes**: Increase from 6 to 25+ (4x growth)

### Qualitative Improvements
1. **Better geographic diversity** - Reduce US-centric bias
2. **More international opportunities** - Better serve global audience
3. **Improved data quality** - URLs with verified job content
4. **Robust verification** - Handle redirects and deep content
5. **PDF support** - Extract from documents, not just HTML

### Impact on Job Listings
- **Current**: 211 unique listings from 176 URLs (1.2 jobs/URL)
- **Projected**: 350-400 listings from 250+ URLs (1.4-1.6 jobs/URL)
- **New listings per region**:
  - Europe: +30-40 listings
  - Asia-Pacific: +25-35 listings
  - Latin America: +10-15 listings
  - Research institutes: +20-30 listings

## Technical Considerations

### 1. Rate Limiting & Politeness
- Respect robots.txt for all new domains
- Adjust rate limits for international servers
- Stagger requests across regions
- Add delays for shared hosting platforms

### 2. Character Encoding
- Handle UTF-8 for international sites
- Support Chinese (GB2312, UTF-8), Japanese (Shift-JIS), Korean (EUC-KR)
- Test encoding detection on sample pages

### 3. Redirect Handling
- Follow HTTP 301/302 redirects
- Handle JavaScript redirects (limited support)
- Track redirect chains for debugging
- Detect redirect loops

### 4. External Career Systems
Many universities use third-party systems:
- **ICIMS** (Brookings, many US universities)
- **Workday** (major corporations, some universities)
- **PeopleAdmin/PageUp** (US universities)
- **Taleo** (Oracle)

Strategy:
- Detect system type from URL patterns
- Create system-specific parsers if needed
- Document systems in use for future reference

### 5. Accessibility & Compliance
- Handle CAPTCHAs (manual review when detected)
- Respect cookie consent (EU GDPR)
- Handle login-protected pages (mark as restricted)
- Monitor for IP blocking

## Risk Assessment

### Risks & Mitigations

1. **Chinese URL blocking** (HIGH)
   - **Risk**: Many Chinese universities block foreign IPs
   - **Mitigation**: Mark as "requires_vpn", document alternative access methods
   - **Fallback**: Use aggregator sites, job portals that list Chinese positions

2. **External career systems** (MEDIUM)
   - **Risk**: ICIMS/Workday pages may be dynamic (JavaScript)
   - **Mitigation**: Implement link-following to detail pages, PDF download
   - **Fallback**: Manual monitoring for major institutions

3. **Verification time** (MEDIUM)
   - **Risk**: Verifying 250+ URLs may take hours
   - **Mitigation**: Parallel processing, caching, incremental verification
   - **Fallback**: Prioritize Tier 1 universities first

4. **URL churn** (LOW)
   - **Risk**: URLs may change frequently
   - **Mitigation**: Regular re-verification (monthly), pattern-based URL discovery
   - **Fallback**: User reporting system for broken links

5. **Content quality** (LOW)
   - **Risk**: New sources may have poor data quality
   - **Mitigation**: Pilot test on 10 URLs per region before bulk addition
   - **Fallback**: Remove low-quality sources after analysis

## Success Metrics

1. **Coverage**: 250+ accessible URLs across all regions
2. **Balance**: No region >40% of total URLs
3. **Quality**: 80%+ URLs return valid job listings
4. **Fix Rate**: 75%+ of problematic URLs resolved
5. **Scraping Success**: 70%+ of new URLs successfully scraped

## Next Steps

1. ✅ **Approve proposal** - Review and approve expansion plan
2. 🔄 **Create to-do list** - Break down into actionable tasks
3. 🔄 **Update progress tracking** - Add Phase 1B to pipeline
4. 🔄 **Begin implementation** - Start with enhanced verification tools
5. ⏸️ **Research universities** - Compile list of target institutions
6. ⏸️ **Verify and add URLs** - Test and add to configuration
7. ⏸️ **Test scraping** - Validate data extraction from new sources
8. ⏸️ **Document results** - Update verification documentation

## References

- **QS World University Rankings** - Economics & Econometrics 2024
- **Times Higher Education Rankings** - Economics & Business 2024
- **RePEc Rankings** - Top Economics Departments
- **EconJobMarket** - Participating institutions list
- **AEA Directory** - Economics departments worldwide

## Appendix: URL Pattern Examples

### Working Patterns
```
# US Universities
https://{university}.edu/hr/careers
https://{university}.edu/faculty/positions
https://hr.{university}.edu/faculty-openings

# Chinese Universities  
https://hr.{university}.edu.cn/
https://job.{university}.edu.cn/

# UK Universities
https://www.jobs.{university}.ac.uk/
https://www.{university}.ac.uk/jobs/

# Research Institutes
https://careers.{institute}.org/
https://www.{institute}.org/careers
```

### Redirect Patterns
```
# ICIMS
https://{university}.edu/careers → https://careers-{university}.icims.com/

# Workday
https://{university}.edu/jobs → https://{university}.wd1.myworkdayjobs.com/
```
