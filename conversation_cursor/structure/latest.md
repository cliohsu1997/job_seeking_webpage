# Structure Notes

- Maintained the separation between `conversation_cursor/progress`, `/structure`, and `/to-do-list` at the root, while nesting dated summaries inside `conversation_cursor/dates/YYYY-MM-DD`.
- Added `.gitkeep` placeholders to preserve the empty directories plus a proposal/execution pairing per conversation.
- **NEW**: Established complete folder structure for Economics Job Aggregator:
  - `/data`: Raw scrapes, processed data, and configuration files
    - `/data/raw/aea/` and `/data/raw/universities/` for daily scrapes
    - `/data/processed/` for cleaned JSON/CSV outputs
    - `/data/config/` for scraping configuration
  - `/scripts`: Organized by function (scraper/, processor/, generator/)
  - `/templates`: HTML templates for webpage generation
  - `/static`: CSS, JS, and images for frontend
  - Structure supports `load → transform → export` workflow


