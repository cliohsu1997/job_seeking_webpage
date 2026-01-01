"""
Base scraper abstract class for web scraping.
"""

import logging
import requests
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .utils.rate_limiter import RateLimiter
from .utils.retry_handler import RetryHandler
from .utils.user_agent import UserAgentRotator

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for web scrapers."""
    
    def __init__(
        self,
        rate_limit_delay: float = 2.0,
        max_retries: int = 3,
        timeout: int = 30,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize base scraper.
        
        Args:
            rate_limit_delay: Delay between requests in seconds
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            output_dir: Directory to save raw HTML/data
        """
        self.rate_limiter = RateLimiter(rate_limit_delay)
        self.retry_handler = RetryHandler(max_retries=max_retries)
        self.user_agent_rotator = UserAgentRotator()
        self.timeout = timeout
        self.output_dir = output_dir or Path("data/raw")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up session
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent_rotator.get_default(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
    
    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from URL with retry logic and rate limiting.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content as string or None if failed
        """
        self.rate_limiter.wait_if_needed()
        
        def _fetch():
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch {url}: {e}")
                raise
        
        try:
            return self.retry_handler.execute(_fetch, operation_name=f"Fetch {url}")
        except Exception as e:
            logger.error(f"Failed to fetch {url} after retries: {e}")
            return None
    
    def save_raw_html(self, content: str, filename: str) -> Path:
        """
        Save raw HTML content to file.
        
        Args:
            content: HTML content to save
            filename: Filename (relative to output_dir)
        
        Returns:
            Path to saved file
        """
        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Saved raw HTML to {filepath}")
        return filepath
    
    @abstractmethod
    def parse(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse HTML content and extract job listings.
        
        Args:
            html: HTML content as string
        
        Returns:
            List of job listing dictionaries
        """
        pass
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method: fetch, parse, and return job listings.
        
        Returns:
            List of job listing dictionaries
        """
        pass
    
    def extract(self, url: str, save_raw: bool = False, filename: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract job listings from a URL (fetch + parse).
        
        Args:
            url: URL to scrape
            save_raw: Whether to save raw HTML
            filename: Optional filename for saved HTML
        
        Returns:
            List of job listing dictionaries
        """
        html = self.fetch(url)
        
        if html is None:
            return []
        
        if save_raw and filename:
            self.save_raw_html(html, filename)
        
        try:
            listings = self.parse(html)
            logger.info(f"Extracted {len(listings)} job listings from {url}")
            return listings
        except Exception as e:
            logger.error(f"Failed to parse HTML from {url}: {e}")
            return []

