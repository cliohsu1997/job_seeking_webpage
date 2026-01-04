# Proposal: Complete Phase 1B URL Replacement Expansion

**Date**: 2026-01-04  
**Status**: Ready for Implementation  
**Objective**: Complete the REPLACE phase by validating replacements and expanding global coverage

## Executive Summary

Phase 1B REPLACE infrastructure is now complete and ready for production use. The replacement engine has been successfully implemented and pilot-tested on 10 problematic US universities, discovering 30 replacement candidates with 100% coverage. The next step is to complete the validation and expansion to reach the goal of 250+ sources with improved global coverage.

## Current Status

### ✅ Completed
- **Replacement Engine** (570 lines): Complete workflow with 6 core functions
- **URL Discovery** (282 lines): Predefined URLs for 12 major institutions
- **Pilot Execution**: 10 problematic URLs → 30 candidates identified
- **Infrastructure**: Validation workflow, reporting, config updates
- **Documentation**: Comprehensive guides and analysis

### ⚠️ Blocked by Network Issues
- Full validation of 30 replacement candidates (SSL errors, 403 Forbidden, DNS failures)
- Config updates pending successful validation
- Scraping tests with new URLs

## Phase 1B REPLACE Completion Plan

### Step 1: Resolve Network Issues & Complete Pilot Validation
**Timeline**: 1-2 hours (pending network stability)
**Task**: Re-run validation with stable network
- Execute `poetry run python validate_replacements.py`
- Review validation results
- Select replacements with quality score ≥60
- Document success rate and quality improvements

### Step 2: Update Configuration with Validated Replacements
**Timeline**: 30 minutes
**Task**: Apply validated replacements to scraping_sources.json
- Run `engine.validate_and_finalize(jobs, backup=True)`
- Verify config updates
- Create replacement log

### Step 3: Test Scraping with New URLs
**Timeline**: 1-2 hours
**Task**: Verify data extraction works with new URLs
- Run scraper on sample of 5-10 new URLs
- Verify data extraction quality
- Document any issues

### Step 4: Expand Global Coverage (240+ sources)
**Timeline**: 2-3 hours
**Task**: Systematically add new sources in 4 regions

#### 4A: European Universities (30+ URLs)
- Target universities in: UK, France, Germany, Netherlands, Switzerland, Nordic countries
- Known institutions: Oxford, Cambridge, LSE, Sorbonne, TU Munich, Amsterdam, Zurich, Stockholm, etc.
- Methods: Google Scholar faculty listings, university career pages, department job boards

#### 4B: Research Institutes (15+ URLs)
- Target: Major US research organizations
- Known institutes: NBER, Brookings, American Enterprise Institute, IMF, World Bank, etc.
- Methods: Center career pages, fellowship listings, research job boards

#### 4C: Asia-Pacific Universities (20+ URLs)
- Target: Major universities in China, Japan, Singapore, Australia, India
- Known institutions: Tsinghua, Peking, Tokyo, NUS, Melbourne, IIT, etc.
- Methods: English career pages, faculty recruitment portals

#### 4D: Latin America & Other Regions (10+ URLs)
- Target: Major universities in Brazil, Mexico, Chile
- Methods: University career pages, department job boards

### Implementation Strategy

```
1. Use url_discovery.py to test common paths:
   /careers, /jobs, /employment, /opportunities

2. Use predefined institution mapping to find main university sites

3. Validate each new source with decision_engine

4. Update scraping_sources.json with successful URLs

5. Generate expansion report with coverage statistics
```

## Expected Outcomes

### Coverage Expansion
- **Current**: 210 sources (127 accessible_verified + 83 accessible_unverified)
- **After Pilot**: 200-210 sources (10 problematic URLs replaced)
- **After Expansion**: 250+ sources globally distributed

### Regional Distribution Target
- **US**: 80-90 sources (including universities, research institutes, career sites)
- **Europe**: 40-50 sources (diverse university systems)
- **Asia-Pacific**: 30-40 sources (major research universities)
- **Other**: 20-30 sources (Latin America, others)

### Quality Improvements
- **Accessibility**: 85%+ URLs returning job content
- **Data Quality**: 60+ score on content validation
- **Global Coverage**: More balanced regional representation
- **Replacement Success Rate**: 80%+ of problematic URLs successfully replaced

## Risk Assessment

### Network Issues ⚠️
- **Risk**: SSL errors, DNS failures, 403 responses during validation
- **Mitigation**: 
  - Validate with VPN if needed
  - Skip unreachable URLs, find alternatives
  - Use fallback discovery methods (common paths, subdomains)

### Time Constraints
- **Risk**: Expansion may take longer than estimated
- **Mitigation**:
  - Prioritize high-impact sources first
  - Use batch validation for efficiency
  - Can be done iteratively

### Data Quality
- **Risk**: New sources may have low quality job content
- **Mitigation**:
  - Set quality threshold at 60 minimum
  - Manual review of borderline cases
  - Can move low-quality sources to "review" category

## Success Criteria

✅ **Pilot Validation**
- All 30 replacement candidates validated
- Success rate documented
- Quality improvements measured

✅ **Configuration Updated**
- 10 problematic URLs replaced with better alternatives
- Config backup preserved
- Replacement log created

✅ **Scraping Verified**
- New URLs produce extractable job content
- No errors in scraping workflow
- Data quality meets standards

✅ **Expansion Complete**
- 250+ total sources
- Regional distribution 60/40/25/25 (US/Europe/Asia-Pacific/Other)
- All sources have quality score ≥60
- Comprehensive expansion report generated

## Next Steps (In Order)

1. **Immediate** (When network allows):
   - Re-run `validate_replacements.py`
   - Review results
   - Update config with validated replacements
   - Test scraping with new URLs

2. **Short-term** (Next work session):
   - Implement Tasks 1A-1E for full expansion
   - Add 30 EU universities
   - Add 15 research institutes
   - Add 20 Asia-Pacific universities
   - Add 10 Latin America sources

3. **Follow-up**:
   - Final verification of all 250+ sources
   - Generate comprehensive expansion report
   - Plan Phase 4: Deployment (automated scheduling)

## Conclusion

The Phase 1B REPLACE infrastructure is production-ready and successfully demonstrated on the pilot. Once network stability allows, the validation and expansion can be completed in 4-6 hours, bringing the project to 250+ global sources with improved data quality and regional coverage.

The systematic approach with predefined URLs, discovery methods, and validation ensures sustainable, maintainable expansion that can be repeated for future URL verification cycles.

---

**Estimated Completion**: 2026-01-04 to 2026-01-05 (pending network stability)  
**Owner**: Project Lead  
**Status**: Ready for Execution
