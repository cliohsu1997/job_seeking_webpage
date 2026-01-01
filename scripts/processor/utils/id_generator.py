"""
ID generation utilities for creating unique identifiers for job listings.

This module provides functions for generating hash-based unique IDs
from job listing data (institution + title + deadline).
"""

import hashlib
from typing import Optional, Dict, Any


def generate_job_id(institution: str, title: str, deadline: str) -> str:
    """
    Generate a unique hash-based ID for a job listing.
    
    Uses SHA256 hash of institution + title + deadline to create a deterministic
    unique identifier. This ensures the same job posting gets the same ID even
    if processed multiple times.
    
    Args:
        institution: Institution name
        title: Job title
        deadline: Deadline date (YYYY-MM-DD format preferred)
        
    Returns:
        Unique ID string (SHA256 hex digest, truncated to 32 characters for readability)
    """
    # Handle None values by converting to empty string
    institution = institution or ""
    title = title or ""
    deadline = deadline or ""
    
    # Convert to strings if not already
    institution = str(institution).strip().lower()
    title = str(title).strip().lower()
    deadline = str(deadline).strip().lower()
    
    # Combine fields with a delimiter
    combined = f"{institution}|{title}|{deadline}"
    
    # Generate SHA256 hash
    hash_object = hashlib.sha256(combined.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    
    # Use first 32 characters for readability (collision probability is still extremely low)
    return hash_hex[:32]


def generate_id_from_dict(job_data: Dict[str, Any]) -> Optional[str]:
    """
    Generate ID from a job listing dictionary.
    
    Extracts institution, title, and deadline from the dictionary and generates
    an ID. Handles missing fields gracefully.
    
    Args:
        job_data: Dictionary containing job listing data with keys:
                  - institution (required)
                  - title (required)
                  - deadline (required)
        
    Returns:
        Generated ID string, or None if required fields are missing
    """
    # Extract required fields
    institution = job_data.get("institution") or job_data.get("institution_name")
    title = job_data.get("title") or job_data.get("job_title")
    deadline = job_data.get("deadline") or job_data.get("deadline_date")
    
    # Check if we have minimum required fields
    if not institution or not title:
        return None
    
    # If deadline is missing, use empty string (ID will still be generated)
    deadline = deadline or ""
    
    return generate_job_id(institution, title, deadline)


def is_valid_id(job_id: str) -> bool:
    """
    Check if a job ID is valid.
    
    Valid IDs are:
    - Non-empty strings
    - Hexadecimal strings (for SHA256 hashes)
    - Reasonable length (16-64 characters)
    
    Args:
        job_id: ID string to validate
        
    Returns:
        True if ID appears valid, False otherwise
    """
    if not job_id:
        return False
    
    if not isinstance(job_id, str):
        return False
    
    # Check length (SHA256 hex is 64 chars, we use 32)
    if len(job_id) < 16 or len(job_id) > 64:
        return False
    
    # Check if it's hexadecimal (for hash-based IDs)
    try:
        int(job_id, 16)
        return True
    except ValueError:
        # Not hexadecimal, but could still be valid if using different ID scheme
        # Allow alphanumeric strings
        return job_id.isalnum() or all(c.isalnum() or c in '-_' for c in job_id)

