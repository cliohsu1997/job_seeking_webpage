"""
Research institute and think tank scraper for job listings.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from .base_scraper import BaseScraper
from .parsers.html_parser import HTMLParser
from .parsers.text_extractor import extract_text
from .utils.config_loader import get_accessible_config

logger = logging.getLogger(__name__)


class InstituteScraper(BaseScraper):
    """Generic scraper for research institute and think tank job listings."""
    
    def __init__(self, institute_name: str, url: str, output_dir: Path = None):
        """
        Initialize institute scraper.
        
        Args:
            institute_name: Name of the institute
            url: URL of the job listings page
            output_dir: Directory to save raw HTML/data
        """
        if output_dir is None:
            output_dir = Path("data/raw/institutes")
        super().__init__(output_dir=output_dir, rate_limit_delay=2.0, max_retries=3)
        
        self.institute_name = institute_name
        self.url = url
        self.source_name = "research_institute"
    
    def parse(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse institute job listings HTML.
        
        Args:
            html: HTML content
        
        Returns:
            List of job listing dictionaries
        """
        parser = HTMLParser(html)
        listings = []
        
        soup = parser.get_soup()
        
        # Look for job listings using similar strategy as university scraper
        job_keywords = ["job", "position", "faculty", "posting", "opening", "vacancy", "employment", "researcher"]
        links = parser.extract_links(keywords=job_keywords)
        
        # Look for structured containers
        job_containers = soup.find_all(
            ["div", "article", "li", "section"],
            class_=re.compile("|".join(["job", "listing", "position", "posting", "opening"]), re.I)
        )
        
        if job_containers:
            for container in job_containers:
                listing = self._extract_listing_from_element(container, parser)
                if listing:
                    listings.append(listing)
        else:
            # Fallback: create listings from links
            for link in links[:20]:
                listing = {
                    "title": link.get("text", "") or "Research Position",
                    "source": self.source_name,
                    "source_url": urljoin(self.url, link.get("url", "")),
                    "institution": self.institute_name,
                    "institution_type": "research_institute",
                    "scraped_date": self._get_current_date(),
                }
                listings.append(listing)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_listings = []
        for listing in listings:
            url = listing.get("source_url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_listings.append(listing)
        
        return unique_listings
    
    def _extract_listing_from_element(self, element, parser: HTMLParser) -> Optional[Dict[str, Any]]:
        """Extract job listing from a container element."""
        title_elem = element.find(["h1", "h2", "h3", "h4", "h5", "a"])
        title = extract_text(title_elem) if title_elem else ""
        
        link_elem = element.find("a", href=True)
        url = ""
        if link_elem:
            href = link_elem.get("href", "")
            url = urljoin(self.url, href)
        
        description = extract_text(element)
        deadline = parser.extract_deadline(description)
        
        if not title and not url:
            return None
        
        return {
            "title": title or "Research Position",
            "source": self.source_name,
            "source_url": url,
            "description": description[:500] if description else "",
            "deadline": deadline,
            "institution": self.institute_name,
            "institution_type": "research_institute",
            "scraped_date": self._get_current_date(),
        }
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method: fetch and parse job listings."""
        logger.info(f"Scraping job listings from {self.institute_name}")
        
        html = self.fetch(self.url)
        
        if not html:
            logger.error(f"Failed to fetch {self.institute_name} job listings")
            return []
        
        # Save raw HTML
        filename = self._sanitize_filename(f"{self.institute_name}.html")
        self.save_raw_html(html, filename)
        
        # Parse HTML
        listings = self.parse(html)
        
        logger.info(f"Scraped {len(listings)} job listings from {self.institute_name}")
        return listings
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename."""
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '_', name)
        return name.lower()
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")


def scrape_all_institutes(output_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Scrape job listings from all research institutes in the configuration."""
    config = get_accessible_config()
    all_listings = []
    
    regions = config.get("regions", {})
    
    # United States research institutes
    if "united_states" in regions and "research_institutes" in regions["united_states"]:
        for inst in regions["united_states"]["research_institutes"]:
            if "url" in inst:
                scraper = InstituteScraper(
                    institute_name=inst["name"],
                    url=inst["url"],
                    output_dir=output_dir
                )
                try:
                    listings = scraper.scrape()
                    all_listings.extend(listings)
                except Exception as e:
                    logger.error(f"Failed to scrape {inst['name']}: {e}")
    
    # Other countries research institutes
    if "other_countries" in regions:
        for country, country_data in regions["other_countries"].items():
            if "research_institutes" in country_data:
                for inst in country_data["research_institutes"]:
                    if "url" in inst:
                        scraper = InstituteScraper(
                            institute_name=inst["name"],
                            url=inst["url"],
                            output_dir=output_dir
                        )
                        try:
                            listings = scraper.scrape()
                            all_listings.extend(listings)
                        except Exception as e:
                            logger.error(f"Failed to scrape {inst['name']}: {e}")
    
    return all_listings

