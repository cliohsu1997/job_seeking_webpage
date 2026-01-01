"""
Data Schema Definition for Processed Job Listings

This module defines the schema structure for processed job listings,
including required fields, optional fields, data types, and validation rules.

Schema Structure:
    - Core Identification: id, title, institution, institution_type, department, department_category
    - Location: location object with city, state/province, country, region
    - Job Details: job_type, deadline, deadline_display, start_date, description, requirements, specializations
    - Application Information: application_link, application_portal, contact_email, contact_person, materials_required
    - Metadata: source, source_url, sources, scraped_date, processed_date, last_updated, is_active, is_new

Example:
    {
        "id": "abc123def456...",
        "title": "Assistant Professor of Economics",
        "institution": "Harvard University",
        "institution_type": "university",
        "department": "Department of Economics",
        "department_category": "Economics",
        "location": {
            "city": "Cambridge",
            "state": "MA",
            "country": "United States",
            "region": "united_states"
        },
        "job_type": "tenure-track",
        "deadline": "2025-01-15",
        "deadline_display": "January 15, 2025",
        "start_date": "2025-09-01",
        "application_link": "https://academicpositions.harvard.edu/...",
        "application_portal": "Harvard Academic Positions",
        "contact_email": "econ-jobs@harvard.edu",
        "contact_person": "Dr. Jane Smith",
        "materials_required": {
            "cv": true,
            "cover_letter": true,
            "research_statement": true,
            "teaching_statement": true,
            "research_papers": "Job Market Paper + 2 additional papers",
            "letters_of_recommendation": 3,
            "other": ["Transcripts", "Diversity Statement"]
        },
        "description": "Full job description text...",
        "requirements": "PhD in Economics or related field required...",
        "specializations": ["Macroeconomics", "Monetary Economics"],
        "salary_range": "Not disclosed",
        "source": "university_website",
        "source_url": "https://economics.harvard.edu/faculty/positions",
        "sources": ["university_website"],
        "scraped_date": "2025-12-31",
        "processed_date": "2026-01-01",
        "last_updated": "2025-12-20",
        "is_active": true,
        "is_new": true
    }
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import re


# Schema Definition: Field types and constraints
SCHEMA = {
    # Core Identification (Required)
    "id": {
        "type": str,
        "required": True,
        "description": "Unique identifier (hash-based on institution + title + deadline)"
    },
    "title": {
        "type": str,
        "required": True,
        "description": "Job title"
    },
    "institution": {
        "type": str,
        "required": True,
        "description": "Institution name"
    },
    "institution_type": {
        "type": str,
        "required": True,
        "allowed_values": ["university", "research_institute", "think_tank", "job_portal"],
        "description": "Type of institution"
    },
    "department": {
        "type": str,
        "required": True,
        "description": "Department name"
    },
    "department_category": {
        "type": str,
        "required": True,
        "allowed_values": ["Economics", "Management", "Marketing", "Other"],
        "description": "Department category classification"
    },
    
    # Location (Required)
    "location": {
        "type": dict,
        "required": True,
        "description": "Location object with city, state/province, country, region",
        "schema": {
            "city": {"type": str, "required": False},
            "state": {"type": str, "required": False},
            "province": {"type": str, "required": False},
            "country": {"type": str, "required": True},
            "region": {
                "type": str,
                "required": True,
                "allowed_values": ["united_states", "mainland_china", "united_kingdom", 
                                  "canada", "australia", "other_countries"]
            }
        }
    },
    
    # Job Details (Required)
    "job_type": {
        "type": str,
        "required": True,
        "allowed_values": ["tenure-track", "visiting", "postdoc", "lecturer", "other"],
        "description": "Job type classification"
    },
    "deadline": {
        "type": str,
        "required": True,
        "format": "date",  # YYYY-MM-DD format
        "description": "Application deadline in ISO date format (YYYY-MM-DD)"
    },
    "deadline_display": {
        "type": str,
        "required": True,
        "description": "Human-readable deadline format"
    },
    "description": {
        "type": str,
        "required": True,
        "description": "Full job description text"
    },
    "requirements": {
        "type": str,
        "required": True,
        "description": "Qualifications and requirements"
    },
    "specializations": {
        "type": list,
        "required": True,
        "item_type": str,
        "description": "Array of research fields/areas"
    },
    
    # Job Details (Optional)
    "start_date": {
        "type": str,
        "required": False,
        "format": "date",  # YYYY-MM-DD format
        "description": "When position begins (if specified)"
    },
    "salary_range": {
        "type": str,
        "required": False,
        "description": "Salary range if disclosed"
    },
    
    # Application Information (Required)
    "application_link": {
        "type": str,
        "required": True,
        "format": "url",
        "description": "Direct URL to apply"
    },
    "materials_required": {
        "type": dict,
        "required": True,
        "description": "Object with required materials details",
        "schema": {
            "cv": {"type": bool, "required": False},
            "cover_letter": {"type": bool, "required": False},
            "research_statement": {"type": bool, "required": False},
            "teaching_statement": {"type": bool, "required": False},
            "teaching_portfolio": {"type": bool, "required": False},
            "research_papers": {"type": (str, bool), "required": False},  # Can be bool or string description
            "letters_of_recommendation": {"type": int, "required": False},
            "transcripts": {"type": bool, "required": False},
            "diversity_statement": {"type": bool, "required": False},
            "other": {"type": list, "required": False, "item_type": str}
        }
    },
    
    # Application Information (Optional)
    "application_portal": {
        "type": str,
        "required": False,
        "description": "Portal name if different (e.g., 'Interfolio', 'AcademicJobsOnline')"
    },
    "contact_email": {
        "type": str,
        "required": False,
        "format": "email",
        "description": "Contact email address"
    },
    "contact_person": {
        "type": str,
        "required": False,
        "description": "Contact name (if available)"
    },
    
    # Metadata (Required)
    "source": {
        "type": str,
        "required": True,
        "allowed_values": ["aea", "university_website", "institute_website", "job_portal"],
        "description": "Source identifier"
    },
    "source_url": {
        "type": str,
        "required": True,
        "format": "url",
        "description": "Original URL where listing was found"
    },
    "sources": {
        "type": list,
        "required": True,
        "item_type": str,
        "description": "Array of sources (for deduplicated entries, contains all sources)"
    },
    "scraped_date": {
        "type": str,
        "required": True,
        "format": "date",  # YYYY-MM-DD format
        "description": "Date when data was collected"
    },
    "processed_date": {
        "type": str,
        "required": True,
        "format": "date",  # YYYY-MM-DD format
        "description": "Date when data was processed"
    },
    "is_active": {
        "type": bool,
        "required": True,
        "description": "Whether listing is still open"
    },
    "is_new": {
        "type": bool,
        "required": True,
        "description": "Whether this is a new listing (compared to previous run)"
    },
    
    # Metadata (Optional)
    "last_updated": {
        "type": str,
        "required": False,
        "format": "date",  # YYYY-MM-DD format
        "description": "Date when posting was last modified (if available)"
    },
    "campus": {
        "type": str,
        "required": False,
        "description": "Campus information for multi-campus universities"
    }
}


# Required fields list
REQUIRED_FIELDS = [
    "id", "title", "institution", "institution_type", "department", "department_category",
    "location", "job_type", "deadline", "deadline_display", "description", "requirements",
    "specializations", "application_link", "materials_required", "source", "source_url",
    "sources", "scraped_date", "processed_date", "is_active", "is_new"
]


# Optional fields with default values
OPTIONAL_FIELDS_DEFAULTS = {
    "start_date": None,
    "salary_range": None,
    "application_portal": None,
    "contact_email": None,
    "contact_person": None,
    "last_updated": None,
    "campus": None
}


def validate_date_format(date_str: str) -> bool:
    """
    Validate that a date string is in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not isinstance(date_str, str):
        return False
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not date_pattern.match(date_str):
        return False
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_url(url: str) -> bool:
    """
    Basic URL format validation.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid URL format, False otherwise
    """
    if not isinstance(url, str):
        return False
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def validate_email(email: str) -> bool:
    """
    Basic email format validation.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    if not isinstance(email, str):
        return False
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))


def validate_field_type(value: Any, field_def: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate that a field value matches the expected type and constraints.
    
    Args:
        value: Value to validate
        field_def: Field definition from SCHEMA
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    expected_type = field_def.get("type")
    
    # Handle special case: materials_required["research_papers"] can be str or bool
    if expected_type == (str, bool):
        if not isinstance(value, (str, bool)):
            return False, f"Expected str or bool, got {type(value).__name__}"
    # Handle list types with item_type
    elif expected_type == list:
        if not isinstance(value, list):
            return False, f"Expected list, got {type(value).__name__}"
        item_type = field_def.get("item_type")
        if item_type:
            for item in value:
                if not isinstance(item, item_type):
                    return False, f"List items must be {item_type.__name__}, found {type(item).__name__}"
    # Handle dict types with nested schema
    elif expected_type == dict:
        if not isinstance(value, dict):
            return False, f"Expected dict, got {type(value).__name__}"
        # Nested schema validation would go here if needed
    else:
        if not isinstance(value, expected_type):
            return False, f"Expected {expected_type.__name__}, got {type(value).__name__}"
    
    # Validate format constraints
    if "format" in field_def:
        format_type = field_def["format"]
        if format_type == "date":
            if not validate_date_format(value):
                return False, f"Invalid date format. Expected YYYY-MM-DD, got '{value}'"
        elif format_type == "url":
            if not validate_url(value):
                return False, f"Invalid URL format: '{value}'"
        elif format_type == "email":
            if not validate_email(value):
                return False, f"Invalid email format: '{value}'"
    
    # Validate allowed values
    if "allowed_values" in field_def:
        if value not in field_def["allowed_values"]:
            return False, f"Value '{value}' not in allowed values: {field_def['allowed_values']}"
    
    return True, None


def validate_schema(job_listing: Dict[str, Any], strict: bool = True) -> Tuple[bool, List[str]]:
    """
    Validate a job listing against the schema definition.
    
    Args:
        job_listing: Dictionary containing job listing data
        strict: If True, all required fields must be present. If False, missing optional fields are allowed.
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check for required fields
    for field in REQUIRED_FIELDS:
        if field not in job_listing:
            errors.append(f"Missing required field: '{field}'")
            continue
        
        # Validate field type and constraints
        if field in SCHEMA:
            is_valid, error_msg = validate_field_type(job_listing[field], SCHEMA[field])
            if not is_valid:
                errors.append(f"Field '{field}': {error_msg}")
        
        # Additional validation for location object
        if field == "location":
            location = job_listing[field]
            if not isinstance(location, dict):
                errors.append("Field 'location': Must be a dictionary object")
            else:
                if "country" not in location:
                    errors.append("Field 'location.country': Required field missing")
                if "region" not in location:
                    errors.append("Field 'location.region': Required field missing")
                elif location.get("region") not in ["united_states", "mainland_china", "united_kingdom", 
                                                    "canada", "australia", "other_countries"]:
                    errors.append(f"Field 'location.region': Invalid value '{location.get('region')}'")
    
    # Validate optional fields if present
    for field, field_def in SCHEMA.items():
        if field not in REQUIRED_FIELDS and field in job_listing:
            is_valid, error_msg = validate_field_type(job_listing[field], field_def)
            if not is_valid:
                errors.append(f"Field '{field}': {error_msg}")
    
    # Check for unknown fields (optional - could be useful for debugging)
    if strict:
        known_fields = set(SCHEMA.keys())
        provided_fields = set(job_listing.keys())
        unknown_fields = provided_fields - known_fields
        if unknown_fields:
            errors.append(f"Unknown fields found: {', '.join(unknown_fields)}")
    
    return len(errors) == 0, errors


def get_empty_schema() -> Dict[str, Any]:
    """
    Get an empty job listing dictionary with all required fields set to None or default values.
    Useful for creating new job listings.
    
    Returns:
        Dictionary with all schema fields initialized to None/default values
    """
    empty = {}
    
    # Set required fields to None
    for field in REQUIRED_FIELDS:
        if field == "location":
            empty[field] = {
                "city": None,
                "state": None,
                "country": None,
                "region": None
            }
        elif field == "materials_required":
            empty[field] = {}
        elif field == "specializations":
            empty[field] = []
        elif field == "sources":
            empty[field] = []
        elif field in ["is_active", "is_new"]:
            empty[field] = False
        else:
            empty[field] = None
    
    # Set optional fields to None
    for field in OPTIONAL_FIELDS_DEFAULTS:
        empty[field] = OPTIONAL_FIELDS_DEFAULTS[field]
    
    return empty


def get_schema_description() -> str:
    """
    Get a human-readable description of the schema structure.
    
    Returns:
        String description of the schema
    """
    return __doc__

