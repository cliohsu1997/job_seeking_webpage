"""
Data validation module for schema and quality validation.

This module validates job listings against:
- Schema definition (required fields, types, formats)
- Data quality (completeness, suspicious values, inconsistencies)
- Date validation
- URL validation
- Completeness checks

Separates critical validation issues from warnings.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

from .schema import (
    SCHEMA,
    REQUIRED_FIELDS,
    validate_schema,
    validate_date_format,
    validate_url,
    validate_email
)

# Create set of required fields for fast lookup
_REQUIRED_FIELDS_SET = set(REQUIRED_FIELDS)
from .diagnostics import DiagnosticTracker

logger = logging.getLogger(__name__)

# Compiled regex patterns (cached for performance)
FIELD_ERROR_PATTERN = re.compile(r"(?:field|Field)\s+['\"]([^'\"]+)['\"]")

# Date fields list (cached)
DATE_FIELDS = ["deadline", "start_date", "scraped_date", "processed_date", "last_updated"]

# URL fields list (cached)
URL_FIELDS = ["application_link", "source_url"]

# Common materials list (cached)
COMMON_MATERIALS = ["cv", "cover_letter", "research_statement"]

# US country keywords (cached)
US_KEYWORDS = {"united states", "usa", "us", "u.s.", "america"}

# China country keywords (cached)
CHINA_KEYWORDS = {"china", "prc", "people's republic of china"}


class DataValidator:
    """
    Validates job listing data against schema and quality checks.
    
    Separates critical validation errors from warnings.
    """
    
    def __init__(self, diagnostics: Optional[DiagnosticTracker] = None):
        """
        Initialize the validator.
        
        Args:
            diagnostics: Optional DiagnosticTracker instance for tracking validation issues
        """
        self.diagnostics = diagnostics
        
        # Critical fields that must be present and valid for a listing to be useful (set for O(1) lookup)
        self.critical_fields = {
            "id", "title", "institution", "deadline", "application_link",
            "location", "source", "source_url"
        }
        
        # Fields that should ideally be present but aren't critical (set for O(1) lookup)
        self.important_fields = {
            "description", "requirements", "job_type", "department"
        }
    
    def validate_job_listing(
        self,
        job_listing: Dict[str, Any],
        source: Optional[str] = None,
        strict: bool = True
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a job listing against schema and quality checks.
        
        Args:
            job_listing: Dictionary containing job listing data
            source: Optional source identifier for diagnostic tracking
            strict: If True, all required fields must be present. If False, missing optional fields are allowed.
        
        Returns:
            Tuple of (is_valid, critical_errors, warnings)
            - is_valid: True if no critical errors
            - critical_errors: List of critical validation errors
            - warnings: List of warning-level issues
        """
        critical_errors = []
        warnings = []
        
        # Get source identifier for diagnostics
        source_id = source or job_listing.get("source", "unknown")
        
        # Schema validation
        is_schema_valid, schema_errors = validate_schema(job_listing, strict=strict)
        
        # Categorize schema errors as critical or warnings
        for error in schema_errors:
            field_name = self._extract_field_from_error(error)
            is_critical = False
            
            # All required field errors are critical (missing fields or validation errors)
            if field_name and field_name in _REQUIRED_FIELDS_SET:
                is_critical = True
            # Also check error message directly for missing required fields
            elif any(f"Missing required field: '{field}'" in error for field in _REQUIRED_FIELDS_SET):
                is_critical = True
                # Extract field name from error message
                for field in _REQUIRED_FIELDS_SET:
                    if f"Missing required field: '{field}'" in error:
                        field_name = field
                        break
            # Format/validation errors for required fields
            elif any(f"Field '{field}':" in error for field in _REQUIRED_FIELDS_SET):
                is_critical = True
                # Extract field name from error message
                for field in _REQUIRED_FIELDS_SET:
                    if f"Field '{field}':" in error:
                        field_name = field
                        break
            
            if is_critical:
                critical_errors.append(f"Schema: {error}")
                if self.diagnostics:
                    self.diagnostics.track_validation_issue(
                        source=source_id,
                        field=field_name,
                        error=error,
                        validation_type="SCHEMA"
                    )
            else:
                warnings.append(f"Schema: {error}")
        
        # Additional validation checks
        self._validate_dates(job_listing, source_id, critical_errors, warnings)
        self._validate_urls(job_listing, source_id, critical_errors, warnings)
        self._validate_completeness(job_listing, source_id, warnings)
        self._validate_quality(job_listing, source_id, warnings)
        self._validate_consistency(job_listing, source_id, warnings)
        
        # Listing is valid if no critical errors
        is_valid = len(critical_errors) == 0
        
        return is_valid, critical_errors, warnings
    
    def _validate_dates(
        self,
        job_listing: Dict[str, Any],
        source: str,
        critical_errors: List[str],
        warnings: List[str]
    ) -> None:
        """Validate date fields."""
        for field in DATE_FIELDS:
            if field not in job_listing:
                continue
            
            value = job_listing[field]
            if value is None:
                continue
            
            # Validate format
            if not validate_date_format(value):
                error_msg = f"Invalid date format for '{field}': '{value}' (expected YYYY-MM-DD)"
                if field in self.critical_fields:
                    critical_errors.append(error_msg)
                    if self.diagnostics:
                        self.diagnostics.track_validation_issue(
                            source=source,
                            field=field,
                            error=error_msg,
                            validation_type="DATE_FORMAT"
                        )
                else:
                    warnings.append(error_msg)
            else:
                # Validate date logic (deadline shouldn't be in the past too far, etc.)
                try:
                    date_obj = datetime.strptime(value, '%Y-%m-%d').date()
                    today = datetime.now().date()
                    
                    # Check if deadline is suspiciously old (more than 2 years)
                    if field == "deadline" and (today - date_obj).days > 730:
                        warnings.append(
                            f"Deadline '{value}' is more than 2 years old (may be stale)"
                        )
                    
                    # Check if processed_date is before scraped_date (illogical)
                    if field == "processed_date" and "scraped_date" in job_listing:
                        scraped = job_listing.get("scraped_date")
                        if scraped and validate_date_format(scraped):
                            scraped_date = datetime.strptime(scraped, '%Y-%m-%d').date()
                            if date_obj < scraped_date:
                                warnings.append(
                                    f"processed_date '{value}' is before scraped_date '{scraped}'"
                                )
                except ValueError:
                    pass  # Already caught by format validation
    
    def _validate_urls(
        self,
        job_listing: Dict[str, Any],
        source: str,
        critical_errors: List[str],
        warnings: List[str]
    ) -> None:
        """Validate URL fields."""
        for field in URL_FIELDS:
            if field not in job_listing:
                continue
            
            value = job_listing[field]
            if value is None:
                if field in self.critical_fields:
                    critical_errors.append(f"Missing required URL field: '{field}'")
                continue
            
            # Validate URL format
            if not validate_url(value):
                error_msg = f"Invalid URL format for '{field}': '{value}'"
                critical_errors.append(error_msg)
                if self.diagnostics:
                    self.diagnostics.track_validation_issue(
                        source=source,
                        field=field,
                        error=error_msg,
                        validation_type="URL_FORMAT"
                    )
            
            # Check for suspicious URLs
            if value and ("example.com" in value.lower() or "test.com" in value.lower()):
                warnings.append(f"Suspicious URL in '{field}': '{value}' (may be placeholder)")
        
        # Validate contact_email if present
        if "contact_email" in job_listing and job_listing["contact_email"]:
            email = job_listing["contact_email"]
            if not validate_email(email):
                warnings.append(f"Invalid email format: '{email}'")
    
    def _validate_completeness(
        self,
        job_listing: Dict[str, Any],
        source: str,
        warnings: List[str]
    ) -> None:
        """Check data completeness (warnings for missing important fields)."""
        # Check for empty strings in important fields
        for field in self.important_fields:
            if field not in job_listing:
                warnings.append(f"Missing important field: '{field}'")
            elif isinstance(job_listing[field], str) and not job_listing[field].strip():
                warnings.append(f"Empty value in important field: '{field}'")
        
        # Check location completeness
        if "location" in job_listing and isinstance(job_listing["location"], dict):
            location = job_listing["location"]
            if not location.get("country"):
                warnings.append("Location missing country")
            if not location.get("city") and not location.get("state"):
                warnings.append("Location missing both city and state/province")
        
        # Check materials_required
        if "materials_required" in job_listing:
            materials = job_listing["materials_required"]
            if isinstance(materials, dict) and len(materials) == 0:
                warnings.append("materials_required is empty (unusual for academic positions)")
            elif isinstance(materials, dict):
                # Check if at least some common materials are specified
                if not any(materials.get(mat) for mat in COMMON_MATERIALS):
                    warnings.append("materials_required missing common materials (cv, cover_letter, research_statement)")
        
        # Check specializations
        if "specializations" in job_listing:
            specs = job_listing["specializations"]
            if isinstance(specs, list) and len(specs) == 0:
                warnings.append("specializations is empty (may indicate incomplete extraction)")
    
    def _validate_quality(
        self,
        job_listing: Dict[str, Any],
        source: str,
        warnings: List[str]
    ) -> None:
        """Check data quality (suspicious values, inconsistencies)."""
        # Check for suspiciously short titles
        if "title" in job_listing and isinstance(job_listing["title"], str):
            title = job_listing["title"].strip()
            if len(title) < 5:
                warnings.append(f"Suspiciously short title: '{title}'")
            if len(title) > 200:
                warnings.append(f"Unusually long title ({len(title)} chars): '{title[:50]}...'")
        
        # Check for suspiciously short descriptions
        if "description" in job_listing and isinstance(job_listing["description"], str):
            desc = job_listing["description"].strip()
            if len(desc) < 50:
                warnings.append(f"Description is very short ({len(desc)} chars)")
        
        # Check institution name
        if "institution" in job_listing and isinstance(job_listing["institution"], str):
            inst = job_listing["institution"].strip()
            if len(inst) < 2:
                warnings.append(f"Suspiciously short institution name: '{inst}'")
            if "test" in inst.lower() or "example" in inst.lower():
                warnings.append(f"Suspicious institution name: '{inst}'")
        
        # Check job_type consistency
        if "job_type" in job_listing and "title" in job_listing:
            job_type = job_listing["job_type"]
            title = (job_listing.get("title") or "").lower()
            
            # Check if title matches job_type
            if job_type == "tenure-track" and "visiting" in title:
                warnings.append(f"Job type 'tenure-track' but title contains 'visiting': '{job_listing.get('title')}'")
            elif job_type == "visiting" and "tenure" in title and "non-tenure" not in title:
                warnings.append(f"Job type 'visiting' but title contains 'tenure': '{job_listing.get('title')}'")
    
    def _validate_consistency(
        self,
        job_listing: Dict[str, Any],
        source: str,
        warnings: List[str]
    ) -> None:
        """Check data consistency across fields."""
        # Check location.region consistency with location.country
        if "location" in job_listing and isinstance(job_listing["location"], dict):
            location = job_listing["location"]
            country = location.get("country", "").lower()
            region = location.get("region", "")
            
            if country and region:
                # Basic consistency checks
                if region == "united_states" and not any(kw in country for kw in US_KEYWORDS):
                    warnings.append(
                        f"Region 'united_states' but country is '{location.get('country')}'"
                    )
                elif region == "mainland_china" and not any(kw in country for kw in CHINA_KEYWORDS):
                    warnings.append(
                        f"Region 'mainland_china' but country is '{location.get('country')}'"
                    )
        
        # Check source consistency
        if "source" in job_listing and "sources" in job_listing:
            source_val = job_listing["source"]
            sources_list = job_listing["sources"]
            
            if isinstance(sources_list, list) and source_val not in sources_list:
                warnings.append(
                    f"Source '{source_val}' not in sources list: {sources_list}"
                )
    
    def _extract_field_from_error(self, error: str) -> Optional[str]:
        """Extract field name from validation error message."""
        # Patterns: "Missing required field: 'field'", "Field 'field': error"
        match = FIELD_ERROR_PATTERN.search(error)
        if match:
            return match.group(1)
        return None
    
    def validate_batch(
        self,
        job_listings: List[Dict[str, Any]],
        strict: bool = True
    ) -> Dict[str, Any]:
        """
        Validate a batch of job listings and generate summary report.
        
        Args:
            job_listings: List of job listing dictionaries
            strict: If True, all required fields must be present
        
        Returns:
            Dictionary containing validation results:
            {
                "total": total_count,
                "valid": valid_count,
                "invalid": invalid_count,
                "total_critical_errors": count,
                "total_warnings": count,
                "results": [
                    {
                        "index": index,
                        "id": listing_id,
                        "is_valid": bool,
                        "critical_errors": [...],
                        "warnings": [...]
                    },
                    ...
                ]
            }
        """
        results = []
        total_critical_errors = 0
        total_warnings = 0
        valid_count = 0
        
        for idx, listing in enumerate(job_listings):
            listing_id = listing.get("id", f"listing_{idx}")
            source = listing.get("source", "unknown")
            
            is_valid, critical_errors, warnings = self.validate_job_listing(
                listing,
                source=source,
                strict=strict
            )
            
            if is_valid:
                valid_count += 1
            
            total_critical_errors += len(critical_errors)
            total_warnings += len(warnings)
            
            results.append({
                "index": idx,
                "id": listing_id,
                "is_valid": is_valid,
                "critical_errors": critical_errors,
                "warnings": warnings
            })
        
        return {
            "total": len(job_listings),
            "valid": valid_count,
            "invalid": len(job_listings) - valid_count,
            "total_critical_errors": total_critical_errors,
            "total_warnings": total_warnings,
            "results": results
        }

