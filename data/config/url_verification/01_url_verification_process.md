# URL Verification Notes

## Important

The URLs in `scraping_sources.json` are initial entries and **need to be verified** before use. Many URLs are based on common patterns and may need adjustment.

## Verification Process

For each entry, verify:
1. URL is accessible
2. URL contains job postings (not just general department page)
3. Scraping method is appropriate (html_parser, javascript, rss)
4. Department URLs are correct (Economics, Management, Marketing)

## Common URL Patterns to Try

- `/faculty/positions`
- `/employment`
- `/jobs`
- `/careers`
- `/faculty-recruiting`
- `/open-positions`
- `/faculty/jobs`
- `/about/jobs`
- `/people/jobs`

## Next Steps

1. Verify all initial URLs
2. Update URLs that don't work
3. Add more universities incrementally
4. Test scraping with verified URLs

