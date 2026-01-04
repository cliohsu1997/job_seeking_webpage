# URL Verification Results

**Last Updated**: 2026-01-03  
**Total URLs Checked**: 255  
**URLs with Issues**: 81

## Summary

URL verification was last run on 2026-01-03:
- **47 URLs moved from accessible to non_accessible** (job content not verified, errors, or forbidden)
- **2 URLs moved from non_accessible to accessible** 
- **34 URLs in non_accessible** still have issues
- **Total problematic URLs requiring fixes**: 81

## Issue Categories

### Problematic URL Types
1. **Wrong page type** - Department/faculty pages instead of career portals (30+ US universities)
2. **Connection errors** - DNS failures, timeouts, SSL errors (40+ Chinese universities)
3. **Access denied** - 403 Forbidden or similar restrictions
4. **Not found** - 404 errors or missing pages
5. **No job content** - Page accessible but contains no job listings

## Next Steps

1. Run `scripts/scraper/check_config/verify_urls.py` to re-verify all URLs
2. Use URL discovery to find correct career portal URLs for wrong page types
3. Test alternative URL patterns for problematic universities
4. For Chinese URLs: test alternative domains and use DNS fallback
5. Update results after fixes are implemented

## Verification Methodology

See main `README.md` in parent folder for complete verification methodology including:
- Verification process steps
- Common URL patterns to test
- Scoring rules
- Common issues and solutions

