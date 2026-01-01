"""
Parser Manager for routing raw HTML/XML files to appropriate parsers.

This module scans the data/raw/ directory, identifies source types,
and routes files to appropriate extraction methods (reusing Phase 1 parsers).
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from datetime import datetime

from .diagnostics import DiagnosticTracker

logger = logging.getLogger(__name__)


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
    
    def parse_file(self, file_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse a single file and extract job listings.
        
        This is a placeholder that will be expanded to integrate with Phase 1 parsers.
        For Phase 2A, this returns an empty list as a basic structure.
        
        Args:
            file_metadata: File metadata dictionary from scan_raw_files()
        
        Returns:
            List of extracted job listing dictionaries (empty for now)
        """
        file_path = file_metadata["file_path"]
        source_type = file_metadata["source_type"]
        
        try:
            # TODO: Integrate with Phase 1 parsers
            # For Phase 2A, this is a placeholder structure
            # Phase 2A focuses on pipeline structure, full parsing integration comes later
            
            logger.debug(f"Parsing {source_type} file: {file_path.name}")
            
            # Track parsing attempt
            if self.diagnostics:
                # For now, just log that we attempted to parse
                # Actual parsing logic will be added when integrating Phase 1 parsers
                pass
            
            # Return empty list for now - actual extraction will be implemented
            # when integrating with Phase 1 scraper parsers
            return []
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
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

