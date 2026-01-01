"""
Diagnostic tracking system for the data processing pipeline.

This module tracks issues throughout the pipeline stages to help identify
root causes of data extraction and processing failures.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class DiagnosticTracker:
    """
    Tracks diagnostic information throughout the processing pipeline.
    
    Stores issues by category (URL, scraping, parsing, extraction, normalization, enrichment)
    and provides methods to retrieve and analyze diagnostic data.
    """
    
    def __init__(self):
        """Initialize an empty diagnostic tracker."""
        self._data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._start_time = datetime.now()
        self._statistics: Dict[str, int] = defaultdict(int)
    
    def track_url_issue(self, url: str, error: str, source: Optional[str] = None):
        """
        Track a URL accessibility or validation issue.
        
        Args:
            url: The problematic URL
            error: Error message or description
            source: Optional source identifier
        """
        self._data["url_issues"].append({
            "url": url,
            "error": error,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["url_issues"] += 1
    
    def track_scraping_issue(self, source: str, url: str, error: str, error_type: Optional[str] = None):
        """
        Track a scraping failure.
        
        Args:
            source: Source identifier (e.g., "aea", "university_website")
            url: URL that failed to scrape
            error: Error message or description
            error_type: Optional error type (e.g., "HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE")
        """
        self._data["scraping_issues"].append({
            "source": source,
            "url": url,
            "error": error,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["scraping_issues"] += 1
    
    def track_parsing_issue(self, source: str, file_path: Optional[str] = None, 
                           error: str = "", error_type: Optional[str] = None):
        """
        Track a parsing failure (HTML/XML parsing issues).
        
        Args:
            source: Source identifier
            file_path: Optional path to the file that failed to parse
            error: Error message or description
            error_type: Optional error type (e.g., "PARSE_ERROR", "MISSING_ELEMENTS")
        """
        self._data["parsing_issues"].append({
            "source": source,
            "file_path": file_path,
            "error": error,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["parsing_issues"] += 1
    
    def track_extraction_issue(self, source: str, field: Optional[str] = None,
                              error: str = "", extracted_data: Optional[Dict] = None):
        """
        Track an extraction failure (data extraction from parsed HTML).
        
        Args:
            source: Source identifier
            field: Optional field name that failed to extract
            error: Error message or description
            extracted_data: Optional partial extracted data for debugging
        """
        self._data["extraction_issues"].append({
            "source": source,
            "field": field,
            "error": error,
            "extracted_data": extracted_data,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["extraction_issues"] += 1
    
    def track_normalization_issue(self, source: str, field: str, original_value: Any,
                                  error: str = "", normalized_value: Optional[Any] = None):
        """
        Track a normalization failure (format conversion, standardization issues).
        
        Args:
            source: Source identifier
            field: Field name that failed normalization
            original_value: Original value that couldn't be normalized
            error: Error message or description
            normalized_value: Optional normalized value (if partial success)
        """
        self._data["normalization_issues"].append({
            "source": source,
            "field": field,
            "original_value": str(original_value) if original_value is not None else None,
            "normalized_value": str(normalized_value) if normalized_value is not None else None,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["normalization_issues"] += 1
    
    def track_enrichment_issue(self, source: str, field: str, error: str = "",
                              available_data: Optional[Dict] = None):
        """
        Track an enrichment failure (computed field generation issues).
        
        Args:
            source: Source identifier
            field: Field name that failed enrichment (e.g., "region", "job_type")
            error: Error message or description
            available_data: Optional available data that was used for enrichment attempt
        """
        self._data["enrichment_issues"].append({
            "source": source,
            "field": field,
            "error": error,
            "available_data": available_data,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["enrichment_issues"] += 1
    
    def track_validation_issue(self, source: str, field: Optional[str] = None,
                              error: str = "", validation_type: Optional[str] = None):
        """
        Track a validation failure (schema validation, data quality issues).
        
        Args:
            source: Source identifier
            field: Optional field name that failed validation
            error: Error message or description
            validation_type: Optional validation type (e.g., "SCHEMA", "DATE_FORMAT", "URL_FORMAT")
        """
        self._data["validation_issues"].append({
            "source": source,
            "field": field,
            "error": error,
            "validation_type": validation_type,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["validation_issues"] += 1
    
    def get_issues_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all issues for a specific category.
        
        Args:
            category: Category name (e.g., "url_issues", "parsing_issues", "normalization_issues")
        
        Returns:
            List of issue dictionaries for the category
        """
        return self._data.get(category, []).copy()
    
    def get_all_issues(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all tracked issues organized by category.
        
        Returns:
            Dictionary mapping category names to lists of issues
        """
        return dict(self._data)
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get summary statistics of tracked issues.
        
        Returns:
            Dictionary mapping category names to issue counts
        """
        return dict(self._statistics)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all diagnostic data.
        
        Returns:
            Dictionary containing summary statistics and issue counts
        """
        end_time = datetime.now()
        duration = (end_time - self._start_time).total_seconds()
        
        return {
            "start_time": self._start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "statistics": self.get_statistics(),
            "total_issues": sum(self._statistics.values()),
            "categories": list(self._data.keys())
        }
    
    def clear(self):
        """Clear all tracked diagnostic data."""
        self._data.clear()
        self._statistics.clear()
        self._start_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert diagnostic data to a dictionary for serialization (JSON).
        
        Returns:
            Dictionary representation of all diagnostic data
        """
        return {
            "summary": self.get_summary(),
            "issues": self.get_all_issues()
        }

