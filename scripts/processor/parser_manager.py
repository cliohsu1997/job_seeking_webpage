"""
Parser Manager for routing raw HTML/XML files to appropriate parsers.

This module scans the data/raw/ directory, identifies source types,
and routes files to appropriate extraction methods (reusing Phase 1 parsers).
"""

import logging
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from datetime import datetime
from urllib.parse import urlparse

from .diagnostics import DiagnosticTracker

# Import Phase 1 parsers and scrapers
import sys
from pathlib import Path as PathLib

# Add project root to path for imports (allows importing from scripts.scraper)
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import scrapers and parsers
try:
    from scripts.scraper.aea_scraper import AEAScraper
    from scripts.scraper.university_scraper import UniversityScraper
    from scripts.scraper.institute_scraper import InstituteScraper
    from scripts.scraper.parsers.rss_parser import parse_feed, detect_feed_type
except ImportError:
    # Fallback: try adding scraper directory to path
    scraper_dir = Path(__file__).parent.parent / "scraper"
    if str(scraper_dir) not in sys.path:
        sys.path.insert(0, str(scraper_dir))
    from aea_scraper import AEAScraper
    from university_scraper import UniversityScraper
    from institute_scraper import InstituteScraper
    from parsers.rss_parser import parse_feed, detect_feed_type

logger = logging.getLogger(__name__)

# Path to scraping sources config
CONFIG_FILE = project_root / "data/config/scraping_sources.json"


class ParserManager:
    """
    Manages parsing of raw HTML/XML files from different sources.
    
    Routes files to appropriate parsers based on source type (AEA, university, institute).
    """
    
    def __init__(self, raw_data_dir: Path = None, diagnostics: Optional[DiagnosticTracker] = None):
        """
        Initialize the parser manager.
        
        Args:
            raw_data_dir: Directory containing raw HTML/XML files (default: data/raw/)
            diagnostics: Optional DiagnosticTracker instance for tracking parsing issues
        """
        self.raw_data_dir = raw_data_dir or Path("data/raw")
        self.diagnostics = diagnostics
        self._source_types = {
            "aea": "aea",
            "universities": "university",
            "institutes": "institute"
        }
        self._config_cache = None  # Cache for scraping sources config
    
    def scan_raw_files(self) -> List[Dict[str, Any]]:
        """
        Scan data/raw/ directory for HTML/XML files.
        
        Returns:
            List of file metadata dictionaries with keys:
            - file_path: Path to the file
            - source_type: "aea", "university", or "institute"
            - filename: Name of the file
            - directory: Directory name (aea, universities, institutes)
        """
        files = []
        
        if not self.raw_data_dir.exists():
            logger.warning(f"Raw data directory does not exist: {self.raw_data_dir}")
            return files
        
        # Scan each source type directory
        for dir_name, source_type in self._source_types.items():
            source_dir = self.raw_data_dir / dir_name
            
            if not source_dir.exists():
                logger.debug(f"Source directory does not exist: {source_dir}")
                continue
            
            # Find HTML and XML files
            for file_path in source_dir.glob("*.html"):
                files.append({
                    "file_path": file_path,
                    "source_type": source_type,
                    "filename": file_path.name,
                    "directory": dir_name
                })
            
            for file_path in source_dir.glob("*.xml"):
                files.append({
                    "file_path": file_path,
                    "source_type": source_type,
                    "filename": file_path.name,
                    "directory": dir_name
                })
        
        logger.info(f"Scanned {len(files)} raw files from {self.raw_data_dir}")
        return files
    
    def identify_source_type(self, file_path: Path) -> Optional[str]:
        """
        Identify source type based on file location.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Source type ("aea", "university", "institute") or None if unknown
        """
        # Get relative path from raw_data_dir
        try:
            relative_path = file_path.relative_to(self.raw_data_dir)
            directory = relative_path.parts[0]
            
            return self._source_types.get(directory)
        except ValueError:
            # File is not within raw_data_dir
            logger.warning(f"File {file_path} is not within raw_data_dir {self.raw_data_dir}")
            return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load scraping sources config (with caching)."""
        if self._config_cache is None:
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self._config_cache = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to load scraping sources config: {e}")
                self._config_cache = {"accessible": [], "non_accessible": []}
        return self._config_cache
    
    def _lookup_base_url(self, filename: str, source_type: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Look up base URL from scraping sources config based on filename and metadata.
        
        Args:
            filename: Name of the file
            source_type: Source type ("aea", "university", "institute")
            metadata: Extracted metadata from filename
        
        Returns:
            Base URL string or None if not found
        """
        config = self._load_config()
        accessible_entries = config.get("accessible", [])

        try:
            if source_type == "aea":
                for entry in accessible_entries:
                    if entry.get("type") == "job_portal" and entry.get("id") == "aea":
                        return entry.get("url")

            elif source_type == "university":
                university_name = metadata.get("university_name", "").lower()
                department = metadata.get("department", "").lower()

                for entry in accessible_entries:
                    if entry.get("type") != "university_department":
                        continue
                    entry_uni = entry.get("university", "").lower()
                    entry_dept = entry.get("department", "").lower()

                    name_match = university_name and (entry_uni == university_name or university_name in entry_uni or entry_uni in university_name)
                    dept_match = not department or entry_dept == department or department in entry_dept or entry_dept in department

                    if name_match and dept_match:
                        return entry.get("url")

            elif source_type == "institute":
                institute_name = metadata.get("institute_name", "").lower()

                for entry in accessible_entries:
                    if entry.get("type") != "research_institute":
                        continue
                    entry_name = entry.get("institute", entry.get("name", "")).lower()

                    if institute_name and (entry_name == institute_name or institute_name in entry_name or entry_name in institute_name):
                        return entry.get("url")

        except Exception as e:
            logger.debug(f"Error looking up base URL for {filename}: {e}")

        return None
    
    def _extract_base_url_from_url(self, url: str) -> Optional[str]:
        """
        Extract base URL (scheme + netloc) from a full URL.
        
        Args:
            url: Full URL
        
        Returns:
            Base URL string or None if invalid
        """
        if not url:
            return None
        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            pass
        return None
    
    def _parse_filename(self, filename: str, source_type: str) -> Dict[str, Any]:
        """
        Parse filename to extract metadata (university name, department, institute name).
        
        Args:
            filename: Name of the file (without extension)
            source_type: Source type ("aea", "university", "institute")
        
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        filename_no_ext = filename.replace(".html", "").replace(".xml", "")
        
        if source_type == "university":
            # Pattern: {country}_{university_name}_{department}.html
            # Examples: us_harvard_university_economics.html, cn_peking_university_economics.html
            parts = filename_no_ext.split("_")
            if len(parts) >= 3:
                metadata["country"] = parts[0]
                # University name is everything between country and last part (department)
                university_parts = parts[1:-1]
                metadata["university_name"] = " ".join(university_parts).replace("_", " ").title()
                metadata["department"] = parts[-1].title()
        
        elif source_type == "institute":
            # Pattern: {country}_institute_{institute_name}.html
            # Examples: us_institute_brookings_institution.html
            parts = filename_no_ext.split("_")
            if len(parts) >= 3 and parts[1] == "institute":
                metadata["country"] = parts[0]
                # Institute name is everything after "institute"
                institute_parts = parts[2:]
                metadata["institute_name"] = " ".join(institute_parts).replace("_", " ").title()
        
        elif source_type == "aea":
            # AEA files: portal_american_economic_association_joe.html
            metadata["source_name"] = "AEA JOE"
        
        return metadata
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read file content from disk with multiple encoding attempts.
        
        Args:
            file_path: Path to the file
        
        Returns:
            File content as string or None if failed
        """
        # Try multiple encodings in order of likelihood
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1", "gb2312", "gbk", "utf-16", "utf-16-le", "utf-16-be"]
        
        # First, try to detect encoding using chardet if available
        try:
            import chardet
            with open(file_path, "rb") as f:
                raw_data = f.read()
                if raw_data:
                    detected = chardet.detect(raw_data)
                    if detected and detected.get("encoding"):
                        detected_encoding = detected["encoding"].lower()
                        # Add detected encoding to the front of the list
                        if detected_encoding not in encodings:
                            encodings.insert(0, detected_encoding)
                        else:
                            # Move to front
                            encodings.remove(detected_encoding)
                            encodings.insert(0, detected_encoding)
        except ImportError:
            # chardet not available, continue with default encodings
            pass
        except Exception as e:
            logger.debug(f"Encoding detection failed for {file_path}: {e}")
        
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding, errors="replace") as f:
                    content = f.read()
                    # Basic validation: check if we got meaningful content
                    if len(content.strip()) > 0:
                        return content
            except (UnicodeDecodeError, LookupError):
                # Try next encoding
                continue
            except Exception as e:
                # Other errors (file not found, permission, etc.)
                logger.error(f"Failed to read file {file_path} with encoding {encoding}: {e}")
                # Try next encoding for encoding-related errors
                if "encoding" in str(e).lower() or "decode" in str(e).lower():
                    continue
                # For other errors, return None
                return None
        
        # If all encodings failed, try with errors="ignore" as last resort
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if len(content.strip()) > 0:
                    logger.warning(f"Read file {file_path} with utf-8 and errors='ignore' (some data may be lost)")
                    return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path} after all encoding attempts: {e}")
        
        return None
    
    def _is_xml_feed(self, content: str) -> bool:
        """
        Check if content is an XML/RSS feed.
        
        Args:
            content: File content
        
        Returns:
            True if content appears to be XML/RSS
        """
        content_lower = content.strip().lower()
        return (
            content_lower.startswith("<?xml") or
            content_lower.startswith("<rss") or
            content_lower.startswith("<feed") or
            "<rss" in content_lower[:500] or
            "<feed" in content_lower[:500]
        )
    
    def _parse_aea_file(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse AEA file (can be RSS/XML or HTML).
        
        Args:
            content: File content
            file_path: Path to the file
        
        Returns:
            List of job listing dictionaries
        """
        listings = []
        
        # Check if it's an RSS/XML feed
        if self._is_xml_feed(content):
            try:
                rss_listings = parse_feed(content)
                # Normalize RSS listings to our format
                for listing in rss_listings:
                    normalized = {
                        "title": listing.get("title", ""),
                        "source": "aea",
                        "source_url": listing.get("url", "") or "",  # Ensure it's always a string
                        "description": listing.get("description", ""),
                        "published_date": listing.get("published_date", ""),
                        "scraped_date": datetime.now().strftime("%Y-%m-%d"),
                    }
                    listings.append(normalized)
            except Exception as e:
                logger.warning(f"Failed to parse AEA file as RSS/XML: {e}, trying HTML parser")
                # Fall through to HTML parsing
        
        # Try HTML parsing (either as fallback or primary method)
        try:
            # Create a minimal AEA scraper instance for parsing
            scraper = AEAScraper(output_dir=self.raw_data_dir / "aea")
            html_listings = scraper.parse(content)
            listings.extend(html_listings)
        except Exception as e:
            logger.error(f"Failed to parse AEA file as HTML: {e}")
        
        return listings
    
    def _parse_university_file(
        self,
        content: str,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse university file.
        
        Args:
            content: File content
            file_path: Path to the file
            metadata: Extracted metadata from filename
        
        Returns:
            List of job listing dictionaries
        """
        university_name = metadata.get("university_name", "Unknown University")
        department = metadata.get("department", "")
        
        try:
            # Create a minimal university scraper instance for parsing
            # We don't need the URL since we're parsing from file
            scraper = UniversityScraper(
                university_name=university_name,
                url="",  # Not needed for parsing from file
                department=department,
                output_dir=self.raw_data_dir / "universities"
            )
            listings = scraper.parse(content)
            
            # Enhance listings with metadata from filename
            for listing in listings:
                if "institution" not in listing or not listing["institution"]:
                    listing["institution"] = university_name
                if "department" not in listing or not listing["department"]:
                    listing["department"] = department
                if "institution_type" not in listing:
                    listing["institution_type"] = "university"
            
            return listings
        except Exception as e:
            logger.error(f"Failed to parse university file {file_path}: {e}")
            return []
    
    def _parse_institute_file(
        self,
        content: str,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse institute file.
        
        Args:
            content: File content
            file_path: Path to the file
            metadata: Extracted metadata from filename
        
        Returns:
            List of job listing dictionaries
        """
        institute_name = metadata.get("institute_name", "Unknown Institute")
        
        try:
            # Create a minimal institute scraper instance for parsing
            scraper = InstituteScraper(
                institute_name=institute_name,
                url="",  # Not needed for parsing from file
                output_dir=self.raw_data_dir / "institutes"
            )
            listings = scraper.parse(content)
            
            # Enhance listings with metadata from filename
            for listing in listings:
                if "institution" not in listing or not listing["institution"]:
                    listing["institution"] = institute_name
                if "institution_type" not in listing:
                    listing["institution_type"] = "research_institute"
            
            return listings
        except Exception as e:
            logger.error(f"Failed to parse institute file {file_path}: {e}")
            return []
    
    def parse_file(self, file_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse a single file and extract job listings.
        
        Integrates with Phase 1 parsers to extract structured data from raw HTML/XML files.
        
        Args:
            file_metadata: File metadata dictionary from scan_raw_files()
        
        Returns:
            List of extracted job listing dictionaries
        """
        file_path = file_metadata["file_path"]
        source_type = file_metadata["source_type"]
        filename = file_metadata["filename"]
        
        try:
            logger.debug(f"Parsing {source_type} file: {filename}")
            
            # Read file content
            content = self._read_file_content(file_path)
            if not content:
                logger.warning(f"Could not read file content: {file_path}")
                if self.diagnostics:
                    self.diagnostics.track_parsing_issue(
                        source=source_type,
                        file_path=str(file_path),
                        error="Could not read file content",
                        error_type="READ_ERROR"
                    )
                return []
            
            # Parse filename to extract metadata
            metadata = self._parse_filename(filename, source_type)
            
            # Route to appropriate parser based on source type
            listings = []
            
            if source_type == "aea":
                listings = self._parse_aea_file(content, file_path)
            elif source_type == "university":
                listings = self._parse_university_file(content, file_path, metadata)
            elif source_type == "institute":
                listings = self._parse_institute_file(content, file_path, metadata)
            else:
                logger.warning(f"Unknown source type: {source_type}")
                if self.diagnostics:
                    self.diagnostics.track_parsing_issue(
                        source=source_type,
                        file_path=str(file_path),
                        error=f"Unknown source type: {source_type}",
                        error_type="UNKNOWN_SOURCE"
                    )
                return []
            
            # Look up base URL from config for URL resolution
            base_url = self._lookup_base_url(filename, source_type, metadata)
            
            # Add source file information to each listing and ensure required fields
            for listing in listings:
                listing["source_file"] = str(file_path.relative_to(self.raw_data_dir))
                if "scraped_date" not in listing:
                    listing["scraped_date"] = datetime.now().strftime("%Y-%m-%d")
                
                # Ensure source field is set (map scrapers' source_name to schema values)
                if "source" not in listing or not listing.get("source"):
                    # Map source_type to schema-compatible source values
                    source_mapping = {
                        "aea": "aea",
                        "university": "university_website",
                        "institute": "institute_website"
                    }
                    listing["source"] = source_mapping.get(source_type, "job_portal")
                else:
                    # Fix source name mappings to match schema
                    source_name_mapping = {
                        "research_institute": "institute_website",
                        "aea": "aea",
                        "university_website": "university_website"
                    }
                    current_source = listing.get("source", "")
                    listing["source"] = source_name_mapping.get(current_source, current_source)
                
                # Ensure source_url field is ALWAYS set
                # Priority: 1) existing source_url from listing, 2) base_url from config, 3) empty string
                current_source_url = listing.get("source_url", "")
                if not current_source_url:
                    # If source_url is missing or empty, use base_url from config
                    if base_url:
                        listing["source_url"] = base_url
                    else:
                        listing["source_url"] = ""
                
                # Store base URL for URL resolution in normalizer
                # Priority: 1) extract from absolute source_url, 2) use base_url from config
                base_url_for_resolution = None
                
                # First, try to extract from current source_url if it's absolute
                if listing.get("source_url"):
                    extracted_base = self._extract_base_url_from_url(listing["source_url"])
                    if extracted_base:
                        base_url_for_resolution = extracted_base
                
                # If source_url is relative and we have base_url from config, use it
                if not base_url_for_resolution:
                    if base_url:
                        # Extract base from config base_url
                        base_url_for_resolution = self._extract_base_url_from_url(base_url)
                        # If source_url is relative, we can still use base_url to resolve it
                        if base_url_for_resolution and not listing.get("source_url", "").startswith(('http://', 'https://')):
                            # Keep the relative URL but set base_url for resolution
                            pass
                
                # Always set _base_url if we have one (for normalizer to use)
                # This is critical for resolving relative URLs
                if base_url_for_resolution:
                    listing["_base_url"] = base_url_for_resolution
                elif base_url:
                    # Even if we couldn't extract base, try to use base_url directly
                    base_url_for_resolution = self._extract_base_url_from_url(base_url)
                    if base_url_for_resolution:
                        listing["_base_url"] = base_url_for_resolution
            
            logger.debug(f"Extracted {len(listings)} listings from {filename}")
            return listings
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}", exc_info=True)
            if self.diagnostics:
                self.diagnostics.track_parsing_issue(
                    source=source_type,
                    file_path=str(file_path),
                    error=str(e),
                    error_type="PARSE_ERROR"
                )
            return []
    
    def parse_all_files(self) -> List[Dict[str, Any]]:
        """
        Parse all files in the raw data directory.
        
        Returns:
            List of all extracted job listings
        """
        files = self.scan_raw_files()
        all_listings = []
        
        success_count = 0
        failure_count = 0
        
        for file_metadata in files:
            listings = self.parse_file(file_metadata)
            if listings:
                all_listings.extend(listings)
                success_count += 1
            else:
                failure_count += 1
        
        logger.info(f"Parsed {len(files)} files: {success_count} successful, {failure_count} failed")
        logger.info(f"Extracted {len(all_listings)} total job listings")
        
        return all_listings
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about parsing process.
        
        Returns:
            Dictionary with parsing statistics
        """
        files = self.scan_raw_files()
        
        stats = {
            "total_files": len(files),
            "by_source_type": {},
            "by_directory": {}
        }
        
        for file_metadata in files:
            source_type = file_metadata["source_type"]
            directory = file_metadata["directory"]
            
            stats["by_source_type"][source_type] = stats["by_source_type"].get(source_type, 0) + 1
            stats["by_directory"][directory] = stats["by_directory"].get(directory, 0) + 1
        
        return stats

