"""
Data normalization module for standardizing formats and values.

This module normalizes dates, text fields, URLs, and other data formats
to ensure consistency across all job listings.
"""

import re
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path

# Import Phase 1 date parser
import sys

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
from .utils.location_parser import parse_location, normalize_location
from .diagnostics import DiagnosticTracker

logger = logging.getLogger(__name__)

# Path to processing rules config
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "data/config/processing_rules.json"

# Compiled regex patterns (cached for performance)
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
EMAIL_PREFIX_PATTERN = re.compile(r'^(mailto:|email:)\s*', re.IGNORECASE)
CONTACT_PREFIX_PATTERN = re.compile(r'^(contact:|dr\.|prof\.|professor)\s+', re.IGNORECASE)
LETTERS_NUMBER_PATTERNS = [
    re.compile(r'(\d+)\s*(?:letters?|references?)', re.IGNORECASE),
    re.compile(r'(?:letters?|references?)\s*(?:of\s*)?(?:recommendation\s*)?[:\-]?\s*(\d+)', re.IGNORECASE),
    re.compile(r'(\d+)\s*(?:letters?|references?)\s*(?:of\s*)?(?:recommendation)?', re.IGNORECASE)
]
RESEARCH_PAPER_PATTERNS = [
    re.compile(r'job\s*market\s*paper(?:\s*\+\s*(\d+))?\s*(?:additional\s*)?(?:papers?|publications?)?', re.IGNORECASE),
    re.compile(r'(\d+)\s*(?:papers?|publications?|writing\s*samples?)', re.IGNORECASE),
    re.compile(r'writing\s*sample(?:s)?', re.IGNORECASE)
]


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
        self._load_processing_rules()
    
    def _load_processing_rules(self) -> None:
        """Load processing rules from configuration file."""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.processing_rules = json.load(f)
            # Cache frequently accessed rule sections
            self._job_type_keywords = self.processing_rules.get("job_type_keywords", {})
            self._department_mapping = self.processing_rules.get("department_category_mapping", {})
            self._materials_keywords = self.processing_rules.get("materials_keywords", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load processing rules from {CONFIG_FILE}: {e}")
            self.processing_rules = {}
            self._job_type_keywords = {}
            self._department_mapping = {}
            self._materials_keywords = {}
    
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
                     field_name: str = "url", fallback_base_urls: Optional[List[str]] = None) -> Optional[str]:
        """
        Normalize URL format and resolve relative URLs.
        
        Args:
            url: URL to normalize
            base_url: Optional base URL for resolving relative URLs
            field_name: Name of the field (for error logging)
            fallback_base_urls: Optional list of fallback base URLs to try if base_url doesn't work
        
        Returns:
            Normalized URL string or None if invalid/empty
        """
        if not url:
            return None
        
        url_str = str(url).strip()
        
        # Remove whitespace
        url_str = re.sub(r'\s+', '', url_str)
        
        # Skip non-URL protocols (mailto, javascript, tel, etc.)
        if url_str.startswith(('mailto:', 'javascript:', 'tel:', '#')):
            return None
        
        # If relative URL, try to resolve it
        if not url_str.startswith(('http://', 'https://')):
            resolved = False
            
            # Try primary base_url first
            if base_url:
                try:
                    url_str = urljoin(base_url, url_str)
                    resolved = True
                except Exception as e:
                    logger.debug(f"Failed to resolve URL with base_url '{base_url}': {e}")
            
            # Try fallback base URLs if primary didn't work
            if not resolved and fallback_base_urls:
                for fallback_base in fallback_base_urls:
                    if not fallback_base:
                        continue
                    try:
                        test_url = urljoin(fallback_base, url_str)
                        # Validate the result
                        parsed_test = urlparse(test_url)
                        if parsed_test.scheme and parsed_test.netloc:
                            url_str = test_url
                            resolved = True
                            break
                    except Exception:
                        continue
            
            # If still not resolved, log the issue
            if not resolved:
                if self.diagnostics:
                    self.diagnostics.track_normalization_issue(
                        source="normalizer",
                        field=field_name,
                        original_value=url,
                        error="Could not resolve relative URL (no valid base URL available)"
                    )
                logger.warning(f"Could not resolve relative URL '{url}' for field '{field_name}' (no base URL)")
        
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
            source_url: Optional source URL for resolving relative URLs (deprecated - extracted from job_data)
        
        Returns:
            Dictionary with normalized fields
        """
        normalized = job_data.copy()
        
        # Extract base URLs from the listing for resolving relative URLs
        # Try to get an absolute source_url first, then try application_link as fallback
        base_urls = []
        if normalized.get("source_url"):
            source_url_val = str(normalized["source_url"]).strip()
            if source_url_val.startswith(('http://', 'https://')):
                # Extract base URL from absolute source_url (scheme + netloc)
                parsed = urlparse(source_url_val)
                if parsed.scheme and parsed.netloc:
                    base_urls.append(f"{parsed.scheme}://{parsed.netloc}")
        
        if normalized.get("application_link"):
            app_link = str(normalized["application_link"]).strip()
            if app_link.startswith(('http://', 'https://')):
                parsed = urlparse(app_link)
                if parsed.scheme and parsed.netloc:
                    app_base = f"{parsed.scheme}://{parsed.netloc}"
                    if app_base not in base_urls:
                        base_urls.append(app_base)
        
        # Use the first base_url as primary, rest as fallbacks
        primary_base_url = base_urls[0] if base_urls else source_url
        fallback_base_urls = base_urls[1:] if len(base_urls) > 1 else None
        
        # Normalize date fields
        if "deadline" in normalized and normalized["deadline"]:
            deadline_norm, deadline_display = self.normalize_date(normalized["deadline"], "deadline")
            if deadline_norm:
                normalized["deadline"] = deadline_norm
                normalized["deadline_display"] = deadline_display
            else:
                # Clear invalid deadline
                normalized.pop("deadline", None)
                normalized.pop("deadline_display", None)
        
        if "start_date" in normalized and normalized["start_date"]:
            start_norm, _ = self.normalize_date(normalized["start_date"], "start_date")
            if start_norm:
                normalized["start_date"] = start_norm
        
        # Normalize text fields
        text_fields = ["title", "institution", "department", "description", "requirements"]
        for field in text_fields:
            if field in normalized:
                normalized[field] = self.normalize_text(normalized[field], field)
        
        # Normalize source_url first (before application_link, as it can be used as base)
        # For source_url, try to use the original source_url parameter or extract from other fields
        if "source_url" in normalized:
            # If source_url is already absolute, we can use it as-is after validation
            # If relative, try to resolve using any available absolute URLs
            normalized["source_url"] = self.normalize_url(
                normalized["source_url"],
                primary_base_url,
                "source_url",
                fallback_base_urls=fallback_base_urls
            )
            # Update base_urls after source_url normalization (might now be absolute)
            if normalized.get("source_url") and normalized["source_url"].startswith(('http://', 'https://')):
                parsed = urlparse(normalized["source_url"])
                if parsed.scheme and parsed.netloc:
                    new_base = f"{parsed.scheme}://{parsed.netloc}"
                    if new_base not in base_urls:
                        primary_base_url = new_base
        
        # Normalize application_link using source_url as base if available
        if "application_link" in normalized:
            # Use normalized source_url as base if available
            base_for_app = normalized.get("source_url") or primary_base_url
            normalized["application_link"] = self.normalize_url(
                normalized["application_link"], 
                base_for_app,
                "application_link",
                fallback_base_urls=fallback_base_urls
            )
        
        # Normalize contact_email
        if "contact_email" in normalized and normalized["contact_email"]:
            normalized["contact_email"] = self.normalize_contact_email(normalized["contact_email"])
        
        # Normalize contact_person
        if "contact_person" in normalized and normalized["contact_person"]:
            normalized["contact_person"] = self.normalize_contact_person(normalized["contact_person"])
        
        # Normalize location
        if "location" in normalized:
            normalized["location"] = self.normalize_location_field(normalized["location"])
        
        # Normalize job_type
        if "job_type" in normalized and normalized["job_type"]:
            normalized["job_type"] = self.normalize_job_type(normalized["job_type"], normalized.get("title", ""))
        
        # Normalize department_category
        if "department" in normalized and normalized["department"]:
            normalized["department_category"] = self.normalize_department_category(normalized["department"])
        
        # Normalize materials_required (always call to parse from description/requirements)
        normalized["materials_required"] = self.normalize_materials_required(
            normalized.get("description", ""),
            normalized.get("requirements", ""),
            normalized.get("materials_required")
        )
        
        return normalized
    
    def normalize_location_field(self, location: Any) -> Dict[str, Optional[str]]:
        """
        Normalize location field using location parser.
        
        Args:
            location: Location data (string or dict)
        
        Returns:
            Normalized location dictionary
        """
        try:
            if isinstance(location, str):
                # Parse location string
                parsed = parse_location(location)
            elif isinstance(location, dict):
                # Normalize existing location dict
                parsed = normalize_location(location)
            else:
                parsed = {
                    "city": None,
                    "state": None,
                    "province": None,
                    "country": "Unknown",
                    "region": "other_countries"
                }
            
            return parsed
        except Exception as e:
            if self.diagnostics:
                self.diagnostics.track_normalization_issue(
                    source="normalizer",
                    field="location",
                    original_value=str(location),
                    error=f"Location normalization error: {str(e)}"
                )
            logger.warning(f"Error normalizing location '{location}': {e}")
            return {
                "city": None,
                "state": None,
                "province": None,
                "country": "Unknown",
                "region": "other_countries"
            }
    
    def normalize_job_type(self, job_type: str, title: str = "") -> str:
        """
        Normalize job type using processing rules.
        
        Args:
            job_type: Job type string to normalize
            title: Job title (for additional context)
        
        Returns:
            Normalized job type (tenure-track, visiting, postdoc, lecturer, other)
        """
        if not job_type:
            return "other"
        
        job_type_lower = job_type.lower().strip()
        title_lower = title.lower() if title else ""
        combined_text = f"{job_type_lower} {title_lower}".strip()
        
        # Check each job type category (use cached keywords)
        for normalized_type, keywords in self._job_type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    return normalized_type
        
        # If no match found, return original (will be handled by enricher)
        return job_type_lower
    
    def normalize_department_category(self, department: str) -> str:
        """
        Map department name to category (Economics, Management, Marketing, Other).
        
        Args:
            department: Department name
        
        Returns:
            Department category string
        """
        if not department:
            return "Other"
        
        department_lower = department.lower()
        
        # Check each category (use cached mapping)
        for category, keywords in self._department_mapping.items():
            for keyword in keywords:
                if keyword.lower() in department_lower:
                    return category
        
        # Default to Other if no match
        return "Other"
    
    def normalize_contact_email(self, email: str) -> Optional[str]:
        """
        Normalize contact email format.
        
        Args:
            email: Email string to normalize
        
        Returns:
            Normalized email or None if invalid
        """
        if not email:
            return None
        
        # Clean and normalize email
        email = str(email).strip().lower()
        
        # Remove common prefixes like "mailto:" or "Email:"
        email = EMAIL_PREFIX_PATTERN.sub('', email)
        
        # Basic email format validation
        if EMAIL_PATTERN.match(email):
            return email
        else:
            if self.diagnostics:
                self.diagnostics.track_normalization_issue(
                    source="normalizer",
                    field="contact_email",
                    original_value=email,
                    error="Invalid email format"
                )
            logger.warning(f"Invalid email format: '{email}'")
            return None
    
    def normalize_contact_person(self, contact_person: str) -> Optional[str]:
        """
        Normalize contact person name.
        
        Args:
            contact_person: Contact person string to normalize
        
        Returns:
            Normalized contact person name
        """
        if not contact_person:
            return None
        
        # Clean text
        normalized = clean_text_field(contact_person)
        
        # Remove common prefixes like "Contact:", "Dr.", "Prof."
        normalized = CONTACT_PREFIX_PATTERN.sub('', normalized)
        
        # Capitalize properly (Title Case)
        normalized = normalized.title()
        
        return normalized if normalized else None
    
    def normalize_materials_required(self, description: str = "", requirements: str = "", 
                                   existing_materials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse and normalize materials required from description/requirements text.
        
        Args:
            description: Job description text
            requirements: Requirements text
            existing_materials: Existing materials_required dict (if any)
        
        Returns:
            Normalized materials_required dictionary
        """
        materials = existing_materials.copy() if existing_materials else {}
        
        # Combine description and requirements for parsing (only if needed)
        if not description and not requirements:
            return materials if materials else {}
        
        combined_text = f"{description} {requirements}".lower()
        
        # Check for each material type (use cached keywords)
        for material_type, keywords in self._materials_keywords.items():
            if material_type not in materials:
                # Check if any keyword appears in text
                for keyword in keywords:
                    if keyword.lower() in combined_text:
                        # For letters of recommendation, try to extract number
                        if material_type == "letters_of_recommendation":
                            # Use pre-compiled patterns
                            for pattern in LETTERS_NUMBER_PATTERNS:
                                match = pattern.search(combined_text)
                                if match:
                                    try:
                                        materials[material_type] = int(match.group(1))
                                        break
                                    except (ValueError, IndexError):
                                        pass
                            # If no number found, set to True
                            if material_type not in materials:
                                materials[material_type] = True
                        # For research_papers, try to extract description
                        elif material_type == "research_papers":
                            # Use pre-compiled patterns
                            found_description = None
                            for pattern in RESEARCH_PAPER_PATTERNS:
                                match = pattern.search(combined_text)
                                if match:
                                    # Extract the full match as description
                                    found_description = match.group(0)
                                    break
                            if found_description:
                                materials[material_type] = found_description
                            else:
                                materials[material_type] = True
                        else:
                            # For boolean materials, set to True
                            materials[material_type] = True
                        break
        
        # Ensure "other" field is a list
        if "other" in materials and not isinstance(materials["other"], list):
            if materials["other"]:
                materials["other"] = [str(materials["other"])]
            else:
                materials["other"] = []
        
        return materials

