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
    
    def __init__(
        self,
        university_name: str,
        url: str,
        department: str = "",
        output_dir: Path = None,
        follow_links: bool = True,
        max_links_to_follow: int = 20
    ):
        """
        Initialize university scraper.
        
        Args:
            university_name: Name of the university
            url: URL of the job listings page
            department: Department name (Economics, Management, etc.)
            output_dir: Directory to save raw HTML/data
            follow_links: Whether to follow links to detail pages (default: True)
            max_links_to_follow: Maximum number of detail page links to follow (default: 20)
        """
        if output_dir is None:
            output_dir = Path("data/raw/universities")
        super().__init__(output_dir=output_dir, rate_limit_delay=2.0, max_retries=3)
        
        self.university_name = university_name
        self.url = url
        self.department = department
        self.source_name = "university_website"
        self.follow_links = follow_links
        self.max_links_to_follow = max_links_to_follow
    
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
        
        If the page appears to be a listing page (multiple job links), 
        follows links to extract full job details.
        
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
        
        # Parse HTML to get initial listings
        listings = self.parse(html)
        
        # Check if this is a listing page (has multiple job links)
        if self.follow_links and self._is_listing_page(html, listings):
            logger.info(f"Detected listing page with {len(listings)} job links. Following links to extract full details...")
            detailed_listings = self._follow_links_for_details(listings)
            if detailed_listings:
                logger.info(f"Extracted full details from {len(detailed_listings)} detail pages")
                return detailed_listings
            else:
                logger.warning(f"Failed to extract details from links, using initial listings")
                return listings
        else:
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
    
    def _is_listing_page(self, html: str, listings: List[Dict[str, Any]]) -> bool:
        """
        Detect if the current page is a listing page (has multiple job links).
        
        Args:
            html: HTML content
            listings: Initial listings extracted from the page
        
        Returns:
            True if this appears to be a listing page
        """
        # If we found multiple listings with URLs, likely a listing page
        if len(listings) >= 2:
            urls_with_links = [l for l in listings if l.get("source_url") and l.get("source_url") != self.url]
            if len(urls_with_links) >= 2:
                return True
        
        # Check HTML for multiple job-related links
        parser = HTMLParser(html)
        job_keywords = ["job", "position", "faculty", "posting", "opening", "vacancy"]
        links = parser.extract_links(keywords=job_keywords)
        
        # Filter out navigation/header links (common patterns)
        filtered_links = [
            link for link in links
            if link.get("url") and 
            not any(skip in link["url"].lower() for skip in ["#", "mailto:", "javascript:", "/home", "/about", "/contact"])
        ]
        
        # If we have 3+ job-related links, likely a listing page
        return len(filtered_links) >= 3
    
    def _follow_links_for_details(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Follow links from listing page to extract full job details.
        
        Args:
            listings: Initial listings with URLs to detail pages
        
        Returns:
            List of detailed job listing dictionaries
        """
        detailed_listings = []
        links_followed = 0
        failed_links = 0
        
        for listing in listings[:self.max_links_to_follow]:
            detail_url = listing.get("source_url", "")
            if not detail_url or detail_url == self.url:
                # Skip if no URL or URL is the same as listing page
                detailed_listings.append(listing)  # Keep original
                continue
            
            # Resolve relative URLs
            if not detail_url.startswith(("http://", "https://")):
                detail_url = urljoin(self.url, detail_url)
            
            # Validate URL
            parsed = urlparse(detail_url)
            if not parsed.scheme or not parsed.netloc:
                detailed_listings.append(listing)  # Keep original
                continue
            
            # Skip invalid URL patterns
            if any(skip in detail_url.lower() for skip in ["mailto:", "javascript:", "#", "tel:"]):
                detailed_listings.append(listing)  # Keep original
                continue
            
            try:
                logger.debug(f"Following link to: {detail_url}")
                detail_html = self.fetch(detail_url)
                
                if detail_html:
                    detail_listing = self._extract_from_detail_page(detail_html, detail_url, listing)
                    if detail_listing:
                        detailed_listings.append(detail_listing)
                        links_followed += 1
                    else:
                        # Extraction failed, keep original
                        detailed_listings.append(listing)
                        failed_links += 1
                else:
                    logger.warning(f"Failed to fetch detail page: {detail_url}")
                    detailed_listings.append(listing)  # Keep original
                    failed_links += 1
            
            except Exception as e:
                logger.error(f"Error following link {detail_url}: {e}")
                detailed_listings.append(listing)  # Keep original
                failed_links += 1
        
        if links_followed > 0:
            logger.info(f"Successfully extracted details from {links_followed} pages, {failed_links} failed")
        
        return detailed_listings
    
    def _extract_from_detail_page(self, html: str, url: str, base_listing: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive job details from a detail page.
        
        Args:
            html: HTML content of detail page
            url: URL of the detail page
            base_listing: Base listing data from listing page
        
        Returns:
            Enhanced job listing dictionary with full details
        """
        parser = HTMLParser(html)
        soup = parser.get_soup()
        
        # Start with base listing data
        listing = base_listing.copy()
        listing["source_url"] = url
        
        # Extract title (try multiple selectors)
        title = None
        title_selectors = ["h1", "h2.title", ".job-title", ".position-title", "[class*='title']"]
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = extract_text(title_elem)
                if title and len(title) > 5:  # Valid title
                    break
        
        if title:
            listing["title"] = title
        
        # Extract full description
        description = None
        # Try main content area
        main_content = parser.get_main_content()
        if main_content:
            description = main_content
        else:
            # Fallback to common content selectors
            content_selectors = [
                ".job-description", ".position-description", ".description",
                "main", "article", ".content", "#content", ".main-content"
            ]
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    description = extract_text(content_elem)
                    if description and len(description) > 50:  # Valid description
                        break
        
        if description:
            listing["description"] = description
        
        # Extract deadline
        deadline = parser.extract_deadline(description)
        if deadline:
            listing["deadline"] = deadline
        
        # Extract application link (prioritize prominent links)
        application_link = None
        app_keywords = ["apply", "application", "submit", "apply now", "apply online"]
        
        # First, check for prominent application buttons/links
        prominent_selectors = [
            "a[class*='apply']", "a[class*='application']", 
            "a[id*='apply']", ".apply-button", ".application-link"
        ]
        for selector in prominent_selectors:
            app_elem = soup.select_one(selector)
            if app_elem and app_elem.get("href"):
                href = app_elem.get("href", "")
                application_link = urljoin(url, href)
                if application_link.startswith(("http://", "https://")):
                    listing["application_link"] = application_link
                    break
        
        # Fallback: search all links
        if not application_link:
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                link_text = extract_text(link).lower()
                
                if any(keyword in link_text for keyword in app_keywords) or \
                   any(keyword in href.lower() for keyword in app_keywords):
                    application_link = urljoin(url, href)
                    # Prefer absolute URLs
                    if application_link.startswith(("http://", "https://")):
                        listing["application_link"] = application_link
                        break
        
        # Extract contact information
        contact_email = None
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        text_content = soup.get_text()
        emails = email_pattern.findall(text_content)
        if emails:
            # Filter out common non-contact emails
            filtered_emails = [e for e in emails if not any(skip in e.lower() for skip in ["noreply", "donotreply", "example.com"])]
            if filtered_emails:
                contact_email = filtered_emails[0]
                listing["contact_email"] = contact_email
        
        # Extract location if not already present
        if not listing.get("location"):
            location_patterns = [
                r"location[:\s]+([^\.\n]+)",
                r"based in ([^\.\n]+)",
                r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})",  # City, State
            ]
            for pattern in location_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    if len(location) > 2 and len(location) < 100:
                        listing["location"] = location
                        break
        
        # Extract requirements/qualifications
        requirements = None
        req_keywords = ["requirements", "qualifications", "required", "must have"]
        for keyword in req_keywords:
            # Look for sections with these keywords
            for elem in soup.find_all(["div", "section", "p"], string=re.compile(keyword, re.I)):
                parent = elem.find_parent(["div", "section"])
                if parent:
                    requirements = extract_text(parent)
                    if requirements and len(requirements) > 20:
                        listing["requirements"] = requirements
                        break
            if requirements:
                break
        
        return listing


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

