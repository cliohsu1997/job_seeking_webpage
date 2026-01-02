"""
Test script to verify link-following functionality with real data.
Tests a small subset of universities to verify the link-following works correctly.
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraper.university_scraper import UniversityScraper
from scripts.scraper.institute_scraper import InstituteScraper
from scripts.scraper.utils.config_loader import get_accessible_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_university_link_following(limit: int = 3):
    """Test link-following with a small number of universities."""
    logger.info("=" * 70)
    logger.info("Testing University Scraper Link-Following")
    logger.info("=" * 70)
    
    config = get_accessible_config()
    all_listings = []
    
    # Get a small sample of universities
    regions = config.get("regions", {})
    test_count = 0
    
    # Test US universities first
    if "united_states" in regions and "universities" in regions["united_states"]:
        for uni in regions["united_states"]["universities"][:limit]:
            if "departments" in uni:
                for dept in uni["departments"][:1]:  # Just first department
                    if "url" in dept and test_count < limit:
                        logger.info(f"\n[{test_count + 1}/{limit}] Testing: {uni['name']} - {dept.get('name', '')}")
                        logger.info(f"URL: {dept['url']}")
                        
                        scraper = UniversityScraper(
                            university_name=uni["name"],
                            url=dept["url"],
                            department=dept.get("name", ""),
                            follow_links=True,
                            max_links_to_follow=5  # Limit for testing
                        )
                        
                        try:
                            listings = scraper.scrape()
                            logger.info(f"✓ Scraped {len(listings)} listings")
                            
                            # Check data quality
                            listings_with_description = [l for l in listings if l.get("description") and len(l.get("description", "")) > 100]
                            listings_with_application = [l for l in listings if l.get("application_link")]
                            listings_with_contact = [l for l in listings if l.get("contact_email")]
                            
                            logger.info(f"  - Listings with full description (>100 chars): {len(listings_with_description)}/{len(listings)}")
                            logger.info(f"  - Listings with application link: {len(listings_with_application)}/{len(listings)}")
                            logger.info(f"  - Listings with contact email: {len(listings_with_contact)}/{len(listings)}")
                            
                            all_listings.extend(listings)
                            test_count += 1
                            
                        except Exception as e:
                            logger.error(f"✗ Failed to scrape {uni['name']}: {e}")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Test Summary: {len(all_listings)} total listings scraped")
    logger.info("=" * 70)
    
    return all_listings


def test_institute_link_following(limit: int = 2):
    """Test link-following with a small number of institutes."""
    logger.info("\n" + "=" * 70)
    logger.info("Testing Institute Scraper Link-Following")
    logger.info("=" * 70)
    
    config = get_accessible_config()
    all_listings = []
    
    regions = config.get("regions", {})
    test_count = 0
    
    # Test US institutes
    if "united_states" in regions and "research_institutes" in regions["united_states"]:
        for inst in regions["united_states"]["research_institutes"][:limit]:
            if "url" in inst and test_count < limit:
                logger.info(f"\n[{test_count + 1}/{limit}] Testing: {inst['name']}")
                logger.info(f"URL: {inst['url']}")
                
                scraper = InstituteScraper(
                    institute_name=inst["name"],
                    url=inst["url"],
                    follow_links=True,
                    max_links_to_follow=5  # Limit for testing
                )
                
                try:
                    listings = scraper.scrape()
                    logger.info(f"✓ Scraped {len(listings)} listings")
                    
                    # Check data quality
                    listings_with_description = [l for l in listings if l.get("description") and len(l.get("description", "")) > 100]
                    listings_with_application = [l for l in listings if l.get("application_link")]
                    
                    logger.info(f"  - Listings with full description (>100 chars): {len(listings_with_description)}/{len(listings)}")
                    logger.info(f"  - Listings with application link: {len(listings_with_application)}/{len(listings)}")
                    
                    all_listings.extend(listings)
                    test_count += 1
                    
                except Exception as e:
                    logger.error(f"✗ Failed to scrape {inst['name']}: {e}")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Test Summary: {len(all_listings)} total listings scraped")
    logger.info("=" * 70)
    
    return all_listings


def main():
    """Run link-following tests."""
    logger.info("Starting link-following functionality test")
    logger.info("This will test a small subset of sources to verify link-following works\n")
    
    # Test universities
    university_listings = test_university_link_following(limit=3)
    
    # Test institutes
    institute_listings = test_institute_link_following(limit=2)
    
    # Summary
    all_listings = university_listings + institute_listings
    
    logger.info("\n" + "=" * 70)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total listings scraped: {len(all_listings)}")
    
    if all_listings:
        # Data quality metrics
        with_description = [l for l in all_listings if l.get("description") and len(l.get("description", "")) > 100]
        with_application = [l for l in all_listings if l.get("application_link")]
        with_contact = [l for l in all_listings if l.get("contact_email")]
        with_location = [l for l in all_listings if l.get("location")]
        with_requirements = [l for l in all_listings if l.get("requirements")]
        
        logger.info(f"\nData Quality Metrics:")
        logger.info(f"  - Listings with full description (>100 chars): {len(with_description)}/{len(all_listings)} ({100*len(with_description)/len(all_listings):.1f}%)")
        logger.info(f"  - Listings with application link: {len(with_application)}/{len(all_listings)} ({100*len(with_application)/len(all_listings):.1f}%)")
        logger.info(f"  - Listings with contact email: {len(with_contact)}/{len(all_listings)} ({100*len(with_contact)/len(all_listings):.1f}%)")
        logger.info(f"  - Listings with location: {len(with_location)}/{len(all_listings)} ({100*len(with_location)/len(all_listings):.1f}%)")
        logger.info(f"  - Listings with requirements: {len(with_requirements)}/{len(all_listings)} ({100*len(with_requirements)/len(all_listings):.1f}%)")
        
        # Save sample output
        output_file = Path("data/raw/test_link_following_output.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_listings, f, indent=2, ensure_ascii=False)
        logger.info(f"\n✓ Sample output saved to: {output_file}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Test completed!")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()

