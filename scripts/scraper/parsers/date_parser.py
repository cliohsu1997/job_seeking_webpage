"""
Date parsing utilities with support for multiple formats.
"""

import re
from datetime import datetime
from typing import Optional
from dateutil import parser as date_parser


def parse_date(date_string: str, formats: Optional[list] = None) -> Optional[str]:
    """
    Parse a date string to YYYY-MM-DD format.
    
    Args:
        date_string: Date string to parse
        formats: Optional list of format strings to try (not currently used, dateutil handles this)
    
    Returns:
        Date in YYYY-MM-DD format or None if parsing fails
    """
    if not date_string:
        return None
    
    # Clean the date string
    date_string = date_string.strip()
    
    # Try to extract date using regex first (common patterns)
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
        r'\d{2}/\d{2}/\d{2}',  # MM/DD/YY
        r'\d{1,2}/\d{1,2}/\d{4}',  # M/D/YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_string)
        if match:
            date_string = match.group(0)
            break
    
    try:
        # Use dateutil for flexible parsing
        parsed_date = date_parser.parse(date_string, fuzzy=True, default=datetime.now())
        return parsed_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def extract_deadline(text: str, keywords: Optional[list] = None) -> Optional[str]:
    """
    Extract deadline date from text using keywords.
    
    Args:
        text: Text to search for deadline
        keywords: Keywords to look for (default: common deadline keywords)
    
    Returns:
        Parsed date in YYYY-MM-DD format or None
    """
    if keywords is None:
        keywords = ["deadline", "closing date", "due date", "application deadline", "closes"]
    
    text_lower = text.lower()
    
    for keyword in keywords:
        # Find keyword and extract surrounding text
        pattern = re.compile(
            rf'{re.escape(keyword)}[:\s]+([^.\n]+)',
            re.IGNORECASE
        )
        matches = pattern.findall(text)
        
        for match in matches:
            # Try to parse the matched text as a date
            date_str = parse_date(match)
            if date_str:
                return date_str
    
    return None

