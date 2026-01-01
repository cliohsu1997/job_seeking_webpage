"""
Generic university scraper for job listings.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper
from .parsers.html_parser import HTMLParser
from .parsers.text_extractor import extract_text
from .utils.config_loader import get_accessible_config

logger = logging.getLogger(__name__)


class UniversityScraper(BaseScraper):
    """Generic scraper for university job listings."""
    
    def __init__(self, university_name: str, url: str, department: str = "", output_dir: Path = None):
        """
        Initialize university scraper.
        
        Args:
            university_name: Name of the university
            url: URL of the job listings page
            department: Department name (Economics, Management, etc.)
            output_dir: Directory to save raw HTML/data
        """
        if output_dir is None:
            output_dir = Path("data/raw/universities")
        super().__init__(output_dir=output_dir, rate_limit_delay=2.0, max_retries=3)
        
        self.university_name = university_name
        self.url = url
        self.department = department
        self.source_name = "university_website"
    
    def parse(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse university job listings HTML.
        
        Uses pattern-based extraction to find job listings.
        
        Args:
            html: HTML content
        
        Returns:
            List of job listing dictionaries
        """
        parser = HTMLParser(html)
        listings = []
        
        # Try to find job listings using multiple strategies
        soup = parser.get_soup()
        
        # Strategy 1: Look for links with job-related keywords
        job_keywords = ["job", "position", "faculty", "posting", "opening", "vacancy", "employment"]
        links = parser.extract_links(keywords=job_keywords)
        
        # Strategy 2: Look for structured containers (articles, divs with job classes)
        job_containers = soup.find_all(
            ["div", "article", "li", "section"],
            class_=re.compile("|".join(["job", "listing", "position", "posting", "opening"]), re.I)
        )
        
        # If we found containers, extract from them
        if job_containers:
            for container in job_containers:
                listing = self._extract_listing_from_element(container, parser)
                if listing:
                    listings.append(listing)
        else:
            # Fallback: create listings from links
            for link in links[:20]:  # Limit to avoid too many false positives
                listing = {
                    "title": link.get("text", "") or "Faculty Position",
                    "source": self.source_name,
                    "source_url": urljoin(self.url, link.get("url", "")),
                    "institution": self.university_name,
                    "department": self.department,
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
        """
        Extract job listing from a container element.
        
        Args:
            element: BeautifulSoup element containing job listing
            parser: HTMLParser instance
        
        Returns:
            Job listing dictionary or None
        """
        # Extract title
        title_elem = element.find(["h1", "h2", "h3", "h4", "h5", "a"])
        title = extract_text(title_elem) if title_elem else ""
        
        # Extract link
        link_elem = element.find("a", href=True)
        url = ""
        if link_elem:
            href = link_elem.get("href", "")
            url = urljoin(self.url, href)
        
        # Extract description
        description = extract_text(element)
        
        # Extract deadline if present
        deadline = parser.extract_deadline(description)
        
        if not title and not url:
            return None
        
        return {
            "title": title or "Faculty Position",
            "source": self.source_name,
            "source_url": url,
            "description": description[:500] if description else "",
            "deadline": deadline,
            "institution": self.university_name,
            "department": self.department,
            "scraped_date": self._get_current_date(),
        }
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method: fetch and parse job listings.
        
        Returns:
            List of job listing dictionaries
        """
        logger.info(f"Scraping job listings from {self.university_name} ({self.department})")
        
        html = self.fetch(self.url)
        
        if not html:
            logger.error(f"Failed to fetch {self.university_name} job listings")
            return []
        
        # Save raw HTML
        filename = self._sanitize_filename(f"{self.university_name}_{self.department}.html")
        self.save_raw_html(html, filename)
        
        # Parse HTML
        listings = self.parse(html)
        
        logger.info(f"Scraped {len(listings)} job listings from {self.university_name}")
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


def scrape_all_universities(output_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Scrape job listings from all universities in the configuration.
    
    Args:
        output_dir: Optional output directory
    
    Returns:
        List of all job listings from all universities
    """
    config = get_accessible_config()
    all_listings = []
    
    # Extract universities from config
    regions = config.get("regions", {})
    
    # United States universities
    if "united_states" in regions and "universities" in regions["united_states"]:
        for uni in regions["united_states"]["universities"]:
            if "departments" in uni:
                for dept in uni["departments"]:
                    if "url" in dept:
                        scraper = UniversityScraper(
                            university_name=uni["name"],
                            url=dept["url"],
                            department=dept.get("name", ""),
                            output_dir=output_dir
                        )
                        try:
                            listings = scraper.scrape()
                            all_listings.extend(listings)
                        except Exception as e:
                            logger.error(f"Failed to scrape {uni['name']}: {e}")
    
    # Other countries universities (similar structure)
    if "other_countries" in regions:
        for country, country_data in regions["other_countries"].items():
            if "universities" in country_data:
                for uni in country_data["universities"]:
                    if "departments" in uni:
                        for dept in uni["departments"]:
                            if "url" in dept:
                                scraper = UniversityScraper(
                                    university_name=uni["name"],
                                    url=dept["url"],
                                    department=dept.get("name", ""),
                                    output_dir=output_dir
                                )
                                try:
                                    listings = scraper.scrape()
                                    all_listings.extend(listings)
                                except Exception as e:
                                    logger.error(f"Failed to scrape {uni['name']}: {e}")
    
    return all_listings

