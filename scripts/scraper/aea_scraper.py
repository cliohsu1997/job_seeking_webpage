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
        soup = parser.get_soup()
        
        # AEA JOE structure: listings are grouped by institution
        # <div class="listing-institution-group-item">
        #   <h5 class="group-header-title">Institution Name</h5>
        #   <h6 class="group-sub-header-title">Department/Position Group</h6>
        #   <h6 class="listing-item-header-title">Job Title Link</h6>
        #   <div class="listing-item-body">Job Details</div>
        # </div>
        
        institution_groups = soup.find_all("div", class_="listing-institution-group-item")
        
        if not institution_groups:
            logger.warning("Could not find institution groups in AEA JOE HTML")
            return []
        
        logger.info(f"Found {len(institution_groups)} institution groups")
        
        # Process each institution group
        for group in institution_groups:
            # Extract institution name from h5
            institution_elem = group.find("h5", class_="group-header-title")
            institution = extract_text(institution_elem).strip() if institution_elem else "American Economic Association"
            
            # Find all job listings (each has a header title with link)
            # The first h6 with class="group-sub-header-title" is the department
            department_elem = group.find("h6", class_="group-sub-header-title")
            department = extract_text(department_elem).strip() if department_elem else ""
            
            # Find all job listings (h6 with class="listing-item-header-title")
            job_headers = group.find_all("h6", class_="listing-item-header-title")
            
            for idx, header in enumerate(job_headers):
                listing = self._extract_listing_from_header(
                    header, 
                    parser, 
                    institution=institution,
                    department=department
                )
                if listing:
                    listings.append(listing)
        
        return listings
    
    def _extract_listing_from_header(
        self, 
        header_elem, 
        parser: HTMLParser,
        institution: str = "",
        department: str = ""
    ) -> Dict[str, Any]:
        """
        Extract job listing from a header element.
        
        Args:
            header_elem: BeautifulSoup element containing job header
            parser: HTMLParser instance
            institution: Institution name
            department: Department name
        
        Returns:
            Job listing dictionary or None
        """
        # Extract title and link from header
        link_elem = header_elem.find("a", href=True)
        if not link_elem:
            return None
        
        title = extract_text(link_elem)
        href = link_elem.get("href", "")
        url = urljoin(self.BASE_URL, href) if href else ""
        
        # Find the corresponding body (next sibling div with class="listing-item-body")
        body_elem = header_elem.find_next_sibling("div", class_="listing-item-body")
        
        # Extract location from body and parse it
        location_dict = self._parse_location("")
        if body_elem:
            location_h6 = body_elem.find("h6", class_="meta-list-header")
            # Find the location header by checking for 'Location:' text
            for h6 in body_elem.find_all("h6", class_="meta-list-header"):
                if h6 and "Location:" in extract_text(h6):
                    location_text = extract_text(h6).replace("Location:", "").strip()
                    location_dict = self._parse_location(location_text)
                    break
        
        # Extract deadline from body
        deadline = ""
        if body_elem:
            deadline_div = body_elem.find("div", class_="application-deadline")
            if deadline_div:
                deadline_text = extract_text(deadline_div)
                # Parse deadline from text like "Application deadline: 01/15/2026"
                deadline = parser.extract_deadline(deadline_text)
        
        # Extract full description from body
        description = extract_text(body_elem) if body_elem else ""
        
        # Extract application link
        application_link = ""
        if body_elem:
            app_link = body_elem.find("a", class_="button", href=True)
            if app_link:
                app_href = app_link.get("href", "")
                application_link = urljoin(self.BASE_URL, app_href) if app_href else ""
        
        if not title:
            return None
        
        return {
            "title": title,
            "institution": institution,
            "institution_type": "job_portal",  # AEA JOE is a job portal, not a university or institute
            "department": department or "Not specified",  # Ensure non-empty string
            "department_category": "Economics",  # AEA JOE is specifically for economics
            "location": location_dict,
            "source": self.source_name,
            "source_url": url if url else self.BASE_URL,
            "description": description,
            "deadline": deadline,
            "application_link": application_link,
            "scraped_date": self._get_current_date(),
        }
    
    def _parse_location(self, location_str: str) -> Dict[str, str]:
        """
        Parse location string into components (city, state, country, region).
        
        Args:
            location_str: Location string like "Aalborg, DENMARK" or "Cambridge, MA"
        
        Returns:
            Dictionary with city, state, country, region keys
        """
        location_dict = {
            "city": None,
            "state": None,
            "country": None,
            "region": "other_countries"  # Default region
        }
        
        if not location_str:
            return location_dict
        
        # Split by comma
        parts = [p.strip() for p in location_str.split(",")]
        
        if len(parts) >= 1:
            location_dict["city"] = parts[0]
        
        if len(parts) >= 2:
            second_part = parts[1].upper()
            
            # Check if it's a state (2 letter code) or country
            if len(second_part) == 2 and second_part.isalpha():
                # Likely a US state
                location_dict["state"] = second_part
                location_dict["country"] = "United States"
                location_dict["region"] = "united_states"
            else:
                # Treat as country name
                location_dict["country"] = self._normalize_country(second_part)
                location_dict["region"] = self._get_region_for_country(location_dict["country"])
        
        return location_dict
    
    def _normalize_country(self, country_str: str) -> str:
        """
        Normalize country name from abbreviation or full name.
        
        Args:
            country_str: Country string
        
        Returns:
            Normalized country name
        """
        country_map = {
            "DENMARK": "Denmark",
            "SWEDEN": "Sweden",
            "GERMANY": "Germany",
            "UK": "United Kingdom",
            "UNITED KINGDOM": "United Kingdom",
            "USA": "United States",
            "US": "United States",
            "UNITED STATES": "United States",
            "CANADA": "Canada",
            "AUSTRALIA": "Australia",
            "CHINA": "China",
            "MAINLAND CHINA": "China",
        }
        
        upper_str = country_str.upper()
        return country_map.get(upper_str, country_str)
    
    def _get_region_for_country(self, country: str) -> str:
        """
        Get region for a given country.
        
        Args:
            country: Country name
        
        Returns:
            Region code
        """
        region_map = {
            "United States": "united_states",
            "Canada": "canada",
            "China": "mainland_china",
            "United Kingdom": "united_kingdom",
            "Australia": "australia",
        }
        
        return region_map.get(country, "other_countries")
    
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

