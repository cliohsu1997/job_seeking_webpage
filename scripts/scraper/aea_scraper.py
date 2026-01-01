"""
AEA JOE (American Economic Association Job Openings for Economists) scraper.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper
from .parsers.html_parser import HTMLParser
from .parsers.rss_parser import parse_feed
from .parsers.text_extractor import extract_text

logger = logging.getLogger(__name__)


class AEAScraper(BaseScraper):
    """Scraper for AEA JOE job listings."""
    
    BASE_URL = "https://www.aeaweb.org"
    LISTINGS_URL = "https://www.aeaweb.org/joe/listings.php"
    RSS_URL = "https://www.aeaweb.org/joe/rss.php"  # Common RSS feed pattern
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize AEA scraper.
        
        Args:
            output_dir: Directory to save raw HTML/data
        """
        if output_dir is None:
            output_dir = Path("data/raw/aea")
        super().__init__(output_dir=output_dir, rate_limit_delay=2.0, max_retries=3)
        self.source_name = "aea"
    
    def check_rss_feed(self) -> List[Dict[str, Any]]:
        """
        Check if RSS feed is available and parse it.
        
        Returns:
            List of job listings from RSS feed, or empty list if not available
        """
        try:
            html = self.fetch(self.RSS_URL)
            if html and ("<?xml" in html or "<rss" in html or "<feed" in html):
                logger.info("RSS feed found, parsing...")
                listings = parse_feed(html)
                # Normalize RSS listings to our format
                return [self._normalize_rss_listing(listing) for listing in listings]
        except Exception as e:
            logger.debug(f"RSS feed not available or failed: {e}")
        
        return []
    
    def _normalize_rss_listing(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize RSS listing to our standard format."""
        return {
            "title": listing.get("title", ""),
            "source": self.source_name,
            "source_url": listing.get("url", ""),
            "description": listing.get("description", ""),
            "published_date": listing.get("published_date", ""),
            "scraped_date": self._get_current_date(),
        }
    
    def parse(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse AEA JOE HTML and extract job listings.
        
        Args:
            html: HTML content
        
        Returns:
            List of job listing dictionaries
        """
        parser = HTMLParser(html)
        listings = []
        
        # Try to find job listings - AEA JOE structure may vary
        # Look for common patterns: links to job details, listing containers, etc.
        
        # Method 1: Look for links that might be job listings
        # AEA JOE typically has links to individual job postings
        links = parser.extract_links(keywords=["job", "position", "listing", "faculty"])
        
        # Extract job information from the page structure
        # This is a basic implementation - may need refinement based on actual HTML structure
        soup = parser.get_soup()
        
        # Try to find job listing containers (this will need to be adjusted based on actual structure)
        job_containers = soup.find_all(["div", "article", "li"], class_=re.compile("job|listing|position", re.I))
        
        if not job_containers:
            # Fallback: look for any structured data that might contain jobs
            # For now, extract all text and look for job-related content
            full_text = parser.get_full_text()
            
            # This is a placeholder - actual implementation would need to parse the specific AEA JOE format
            logger.warning("Could not find structured job listings. AEA JOE HTML structure may need specific parsing.")
            
            # Return empty list for now - this needs to be implemented based on actual AEA JOE structure
            return []
        
        # Process each job container
        for container in job_containers:
            listing = self._extract_listing_from_element(container, parser)
            if listing:
                listings.append(listing)
        
        return listings
    
    def _extract_listing_from_element(self, element, parser: HTMLParser) -> Dict[str, Any]:
        """
        Extract job listing from a container element.
        
        Args:
            element: BeautifulSoup element containing job listing
            parser: HTMLParser instance
        
        Returns:
            Job listing dictionary or None
        """
        # Extract title
        title_elem = element.find(["h1", "h2", "h3", "h4", "a"])
        title = extract_text(title_elem) if title_elem else ""
        
        # Extract link
        link_elem = element.find("a", href=True)
        url = ""
        if link_elem:
            href = link_elem.get("href", "")
            url = urljoin(self.BASE_URL, href)
        
        # Extract description
        description = extract_text(element)
        
        # Extract deadline if present
        deadline = parser.extract_deadline(description)
        
        if not title and not url:
            return None
        
        return {
            "title": title,
            "source": self.source_name,
            "source_url": url,
            "description": description[:500] if description else "",  # Limit description length
            "deadline": deadline,
            "scraped_date": self._get_current_date(),
        }
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method: check RSS first, then fall back to HTML scraping.
        
        Returns:
            List of job listing dictionaries
        """
        logger.info("Starting AEA JOE scraper...")
        
        # Try RSS feed first
        listings = self.check_rss_feed()
        
        if listings:
            logger.info(f"Found {len(listings)} listings from RSS feed")
            return listings
        
        # Fall back to HTML scraping
        logger.info("RSS feed not available, scraping HTML...")
        html = self.fetch(self.LISTINGS_URL)
        
        if not html:
            logger.error("Failed to fetch AEA JOE listings page")
            return []
        
        # Save raw HTML
        self.save_raw_html(html, "listings.html")
        
        # Parse HTML
        listings = self.parse(html)
        
        logger.info(f"Scraped {len(listings)} job listings from AEA JOE")
        return listings
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

