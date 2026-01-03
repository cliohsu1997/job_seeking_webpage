"""
Main script to scrape all job listings from all accessible sources.

This script scrapes:
- All universities (from accessible section of config)
- All research institutes (from accessible section of config)
- AEA JOE job listings

All scraped HTML files are saved to data/raw/ with subdirectories:
- data/raw/universities/
- data/raw/institutes/
- data/raw/aea/
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.scraper.university_scraper import scrape_all_universities
from scripts.scraper.institute_scraper import scrape_all_institutes
from scripts.scraper.aea_scraper import AEAScraper
from scripts.scraper.utils.config_loader import count_urls

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to scrape all job listings from accessible sources.
    """
    logger.info("=" * 70)
    logger.info("Starting scraping of all accessible job listings")
    logger.info("=" * 70)
    
    # Count URLs in configuration
    total_urls, accessible_urls = count_urls()
    logger.info(f"Configuration: {accessible_urls} accessible URLs (out of {total_urls} total)")
    logger.info("")
    
    all_listings = []
    
    # 1. Scrape AEA JOE
    logger.info("=" * 70)
    logger.info("Step 1/3: Scraping AEA JOE job listings")
    logger.info("=" * 70)
    try:
        aea_scraper = AEAScraper()
        aea_listings = aea_scraper.scrape()
        all_listings.extend(aea_listings)
        logger.info(f"✓ Scraped {len(aea_listings)} listings from AEA JOE")
    except Exception as e:
        logger.error(f"✗ Failed to scrape AEA JOE: {e}")
    
    logger.info("")
    
    # 2. Scrape all universities
    logger.info("=" * 70)
    logger.info("Step 2/3: Scraping university job listings")
    logger.info("=" * 70)
    try:
        university_listings = scrape_all_universities()
        all_listings.extend(university_listings)
        logger.info(f"✓ Scraped {len(university_listings)} listings from universities")
    except Exception as e:
        logger.error(f"✗ Failed to scrape universities: {e}")
    
    logger.info("")
    
    # 3. Scrape all research institutes
    logger.info("=" * 70)
    logger.info("Step 3/3: Scraping research institute job listings")
    logger.info("=" * 70)
    try:
        institute_listings = scrape_all_institutes()
        all_listings.extend(institute_listings)
        logger.info(f"✓ Scraped {len(institute_listings)} listings from research institutes")
    except Exception as e:
        logger.error(f"✗ Failed to scrape research institutes: {e}")
    
    # Final summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("Scraping Summary")
    logger.info("=" * 70)
    logger.info(f"Total listings scraped: {len(all_listings)}")
    logger.info(f"  - AEA JOE: {len([l for l in all_listings if l.get('source') == 'aea'])}")
    logger.info(f"  - Universities: {len([l for l in all_listings if l.get('source') == 'university_website'])}")
    logger.info(f"  - Research Institutes: {len([l for l in all_listings if l.get('source') == 'research_institute'])}")
    logger.info("")
    logger.info(f"Raw HTML files saved to:")
    logger.info(f"  - data/raw/universities/")
    logger.info(f"  - data/raw/institutes/")
    logger.info(f"  - data/raw/aea/")
    logger.info("=" * 70)
    
    return all_listings


if __name__ == "__main__":
    try:
        listings = main()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error during scraping: {e}", exc_info=True)
        sys.exit(1)

