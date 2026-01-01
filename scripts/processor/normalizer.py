"""
Data normalization module for standardizing formats and values.

This module normalizes dates, text fields, URLs, and other data formats
to ensure consistency across all job listings.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse

# Import Phase 1 date parser
import sys
from pathlib import Path

# Add scraper/parsers to path for date parser import
_scraper_parsers_path = Path(__file__).parent.parent.parent / "scraper" / "parsers"
if str(_scraper_parsers_path) not in sys.path:
    sys.path.insert(0, str(_scraper_parsers_path))

try:
    from date_parser import parse_date
except ImportError:
    # Fallback: try absolute import
    from scripts.scraper.parsers.date_parser import parse_date

# Import processor utilities
from .utils.text_cleaner import clean_text_field, clean_text
from .diagnostics import DiagnosticTracker

logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Normalizes job listing data to standardized formats.
    """
    
    def __init__(self, diagnostics: Optional[DiagnosticTracker] = None):
        """
        Initialize the normalizer.
        
        Args:
            diagnostics: Optional DiagnosticTracker instance for tracking normalization issues
        """
        self.diagnostics = diagnostics
    
    def normalize_date(self, date_str: Optional[str], field_name: str = "date") -> Tuple[Optional[str], Optional[str]]:
        """
        Normalize a date string to YYYY-MM-DD format and generate display format.
        
        Args:
            date_str: Date string to normalize
            field_name: Name of the field (for error logging)
        
        Returns:
            Tuple of (normalized_date (YYYY-MM-DD), display_date (human-readable))
            Returns (None, None) if normalization fails
        """
        if not date_str:
            return None, None
        
        # Use Phase 1 date parser
        normalized = parse_date(str(date_str))
        
        if not normalized:
            # Track normalization failure
            if self.diagnostics:
                self.diagnostics.track_normalization_issue(
                    source="normalizer",
                    field=field_name,
                    original_value=date_str,
                    error="Failed to parse date format"
                )
            logger.warning(f"Failed to normalize date '{date_str}' for field '{field_name}'")
            return None, None
        
        # Generate display format (e.g., "January 15, 2025")
        try:
            date_obj = datetime.strptime(normalized, "%Y-%m-%d")
            display_format = date_obj.strftime("%B %d, %Y")
            # Remove leading zero from day
            display_format = re.sub(r'(\d+)', lambda m: str(int(m.group(1))), display_format)
            display_format = re.sub(r' 0(\d)', r' \1', display_format)
        except (ValueError, TypeError):
            display_format = normalized
        
        return normalized, display_format
    
    def normalize_text(self, text: Optional[str], field_name: str = "text") -> Optional[str]:
        """
        Normalize text field by cleaning whitespace, encoding, and HTML tags.
        
        Args:
            text: Text to normalize
            field_name: Name of the field (for error logging)
        
        Returns:
            Normalized text string or None if empty
        """
        if text is None:
            return None
        
        try:
            normalized = clean_text_field(text)
            return normalized
        except Exception as e:
            if self.diagnostics:
                self.diagnostics.track_normalization_issue(
                    source="normalizer",
                    field=field_name,
                    original_value=text,
                    error=f"Text normalization error: {str(e)}"
                )
            logger.warning(f"Error normalizing text field '{field_name}': {e}")
            # Return cleaned text even if there was an error
            return clean_text(str(text)) if text else None
    
    def normalize_url(self, url: Optional[str], base_url: Optional[str] = None, 
                     field_name: str = "url") -> Optional[str]:
        """
        Normalize URL format and resolve relative URLs.
        
        Args:
            url: URL to normalize
            base_url: Optional base URL for resolving relative URLs
            field_name: Name of the field (for error logging)
        
        Returns:
            Normalized URL string or None if invalid/empty
        """
        if not url:
            return None
        
        url_str = str(url).strip()
        
        # Remove whitespace
        url_str = re.sub(r'\s+', '', url_str)
        
        # If relative URL and base_url provided, resolve it
        if base_url and not url_str.startswith(('http://', 'https://')):
            try:
                url_str = urljoin(base_url, url_str)
            except Exception as e:
                if self.diagnostics:
                    self.diagnostics.track_normalization_issue(
                        source="normalizer",
                        field=field_name,
                        original_value=url,
                        error=f"URL resolution error: {str(e)}"
                    )
                logger.warning(f"Error resolving relative URL '{url}' with base '{base_url}': {e}")
        
        # Basic URL validation
        parsed = urlparse(url_str)
        if not parsed.scheme or not parsed.netloc:
            if self.diagnostics:
                self.diagnostics.track_normalization_issue(
                    source="normalizer",
                    field=field_name,
                    original_value=url,
                    error="Invalid URL format (missing scheme or netloc)"
                )
            logger.warning(f"Invalid URL format: '{url_str}'")
            return None
        
        return url_str
    
    def normalize_job_listing(self, job_data: Dict[str, Any], source_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Normalize all fields in a job listing dictionary.
        
        This method normalizes dates, text fields, and URLs in the job listing.
        Other normalization (location, job types, etc.) will be added in Phase 2B.
        
        Args:
            job_data: Dictionary containing job listing data
            source_url: Optional source URL for resolving relative URLs
        
        Returns:
            Dictionary with normalized fields
        """
        normalized = job_data.copy()
        
        # Normalize date fields
        if "deadline" in normalized:
            deadline_norm, deadline_display = self.normalize_date(normalized["deadline"], "deadline")
            if deadline_norm:
                normalized["deadline"] = deadline_norm
                normalized["deadline_display"] = deadline_display
        
        if "start_date" in normalized and normalized["start_date"]:
            start_norm, _ = self.normalize_date(normalized["start_date"], "start_date")
            if start_norm:
                normalized["start_date"] = start_norm
        
        # Normalize text fields
        text_fields = ["title", "institution", "department", "description", "requirements"]
        for field in text_fields:
            if field in normalized:
                normalized[field] = self.normalize_text(normalized[field], field)
        
        # Normalize URL fields
        if "application_link" in normalized:
            normalized["application_link"] = self.normalize_url(
                normalized["application_link"], 
                source_url, 
                "application_link"
            )
        
        if "source_url" in normalized:
            normalized["source_url"] = self.normalize_url(
                normalized["source_url"],
                None,
                "source_url"
            )
        
        # Normalize contact_email (basic validation, full validation in Phase 2B)
        if "contact_email" in normalized and normalized["contact_email"]:
            email = str(normalized["contact_email"]).strip().lower()
            # Basic email format check
            if "@" in email and "." in email.split("@")[1]:
                normalized["contact_email"] = email
            else:
                logger.warning(f"Invalid email format: '{normalized['contact_email']}'")
                if self.diagnostics:
                    self.diagnostics.track_normalization_issue(
                        source="normalizer",
                        field="contact_email",
                        original_value=normalized["contact_email"],
                        error="Invalid email format"
                    )
                normalized["contact_email"] = None
        
        return normalized

