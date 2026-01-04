# URL Verification Results
**Date**: 2026-01-03
**Total URLs Checked**: 255
**URLs with Issues**: 81

## Summary

After running URL verification on all configured URLs:
- **47 URLs moved from accessible to non_accessible** (job content not verified, errors, or forbidden)
- **2 URLs moved from non_accessible to accessible** (Sichuan Normal University, Southwest Jiaotong University)
- **34 URLs in non_accessible** still have issues
- **Total problematic URLs**: 81 requiring replacement or fixes

## Issue Breakdown by Category

### Job Portals (1 URL)
- **Chronicle Vitae**: 403 Forbidden
  - URL: `https://chroniclevitae.com/job_search?job_search%5Bquery%5D=economics`
  - Status: Moved to non_accessible

### US Universities (30+ URLs)
**Major Universities with Issues**:
- Princeton University - No job content verified
- University of Pennsylvania (Economics, Management) - No job content verified
- Columbia University (Economics, Management) - No job content verified
- NYU (Economics, Management) - No job content verified
- University of Michigan (Economics, Management) - No job content verified
- University of Wisconsin-Madison - No job content verified
- Penn State - No job content verified
- Ohio State University - No job content verified
- University of Virginia - No job content verified
- Vanderbilt University - No job content verified
- Rice University - No job content verified
- University of Arizona - No job content verified
- Louisiana State University - No job content verified
- University of Massachusetts Amherst - HTTP 202 error
- Michigan State University - HTTP 202 error
- University of Oregon - HTTP 202 error
- Temple University - No job content verified
- Washington State University - No job content verified
- University of Texas at Austin - 404 Not Found (non_accessible)

### Chinese Universities (40+ URLs)
**Issues**: Primarily connection errors (DNS resolution failures), timeouts, SSL certificate errors

**Universities with Connection Errors**:
- Tsinghua University - 404 Not Found
- Nanjing University - DNS resolution failure
- Shandong University - DNS resolution failure
- Jilin University - DNS resolution failure
- Xi'an Jiaotong University - DNS resolution failure
- Central University of Finance and Economics - DNS resolution failure
- Shanghai University of Finance and Economics - DNS resolution failure
- Zhongnan University of Economics and Law - SSL certificate error
- Dalian University of Technology - DNS resolution failure
- South China Normal University - Connection aborted
- Beijing Institute of Technology - DNS resolution failure
- Beijing University of Technology - DNS resolution failure
- Lanzhou University - DNS resolution failure
- Yunnan University - DNS resolution failure
- Xinjiang University - DNS resolution failure
- Beijing Jiaotong University - DNS resolution failure
- China University of Mining and Technology - DNS resolution failure
- China University of Petroleum - DNS resolution failure
- East China University of Science and Technology - DNS resolution failure
- And 20+ more universities with similar DNS resolution failures

**Note**: Many Chinese university `rsc.*.edu.cn` domains cannot be resolved, likely due to geographic restrictions or DNS issues.

### International Universities (10+ URLs)

**UK**:
- University of Cambridge - 403 Forbidden
- University of Edinburgh - 404 Not Found

**Australia**:
- University of Sydney - HTTP 500 error
- University of Queensland - Connection error
- Monash University - 403 Forbidden
- University of Technology Sydney - 404 Not Found
- Macquarie University - 404 Not Found
- Griffith University - 404 Not Found
- Deakin University - 403 Forbidden
- University of Wollongong - 404 Not Found
- Curtin University - 404 Not Found
- RMIT University - 404 Not Found
- James Cook University - 403 Forbidden
- University of Newcastle - 403 Forbidden
- University of Melbourne - No job content verified / HTTP 202 error
- Australian National University - HTTP 202 error
- University of Western Australia - HTTP 202 error
- University of Adelaide - HTTP 202 error
- La Trobe University - No job content verified

**Other Countries**:
- Ludwig Maximilian University of Munich (Germany) - 404 Not Found
- University of Bonn (Germany) - 404 Not Found
- Paris School of Economics (France) - HTTP 418 error
- Erasmus University Rotterdam (Netherlands) - 404 Not Found
- Nanyang Technological University (Singapore) - 404 Not Found

### Research Institutes (3 URLs)
- National Bureau of Economic Research (NBER) - Timeout
- Federal Reserve Bank of San Francisco - No job content verified
- Brookings Institution - No job content verified
- Peterson Institute for International Economics (PIIE) - 403 Forbidden (non_accessible)
- Centre for Economic Policy Research (CEPR) - No job content verified

## Issue Types

1. **403 Forbidden** (10 URLs): Chronicle Vitae, Cambridge, Monash, Deakin, James Cook, Newcastle, PIIE, etc.
2. **404 Not Found** (15 URLs): Edinburgh, UTS, Griffith, Wollongong, Curtin, RMIT, Munich, Bonn, etc.
3. **Connection Errors** (40+ URLs): Many Chinese universities (DNS resolution failures)
4. **No Job Content Verified** (30+ URLs): URLs accessible but job listing detection failed (Princeton, UPenn, Columbia, NYU, UMich, etc.)
5. **HTTP 202/500 Errors** (7 URLs): UMass Amherst, MSU, UOregon, Sydney, Melbourne, ANU, UWA, Adelaide
6. **Timeouts** (2 URLs): NBER, North China Electric Power University

## Next Steps

1. **Search for replacement URLs** - Use web search and common URL patterns to find working alternatives
2. **Test replacement URLs** - Verify new URLs are accessible and contain job listings
3. **Download business school PDFs** - **IMPORTANT**: When searching/testing URLs:
   - Identify any PDF files or downloadable documents on pages
   - Check if they are business school oriented (job postings, faculty positions, business/economics departments)
   - If yes, download to `data/raw/documents/` directory
   - Save with descriptive filenames
4. **Update scraping_sources.json** - Replace problematic URLs with working alternatives
5. **Re-run verification** - Verify all new URLs work correctly

## Reference Files

- **Configuration file**: `data/config/scraping_sources.json` (check `non_accessible` section for complete list)
- **Verification script**: `scripts/scraper/check_config/verify_urls.py`
- **Replacement finder script**: `scripts/scraper/check_config/find_url_replacements.py`
- **Verification documentation**: `data/config/URL_VERIFICATION.md`

## Tools

Run URL verification:
```bash
poetry run python scripts/scraper/check_config/verify_urls.py
```

Find URL replacements (helper script):
```bash
poetry run python scripts/scraper/check_config/find_url_replacements.py
```

