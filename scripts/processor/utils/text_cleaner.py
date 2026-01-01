"""
Text cleaning utilities for normalizing and cleaning text fields.

This module provides functions for cleaning text extracted from HTML/XML,
including whitespace normalization, encoding handling, HTML tag removal,
and special character handling.
"""

import re
import html
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace, normalizing encoding, and handling special characters.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Convert to string if not already
    if not isinstance(text, str):
        text = str(text)
    
    # Decode HTML entities (e.g., &amp; -> &, &lt; -> <)
    text = html.unescape(text)
    
    # Remove HTML tags if any remain (simple regex-based removal)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Replace multiple whitespace (spaces, tabs, newlines) with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def clean_whitespace(text: str) -> str:
    """
    Clean only whitespace without handling HTML entities or tags.
    Useful when text is already clean but has whitespace issues.
    
    Args:
        text: Text to clean
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def remove_special_characters(text: str, keep_unicode: bool = True) -> str:
    """
    Remove or normalize special characters.
    
    Args:
        text: Text to clean
        keep_unicode: If True, keep Unicode characters. If False, remove non-ASCII characters.
        
    Returns:
        Text with special characters handled
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    if keep_unicode:
        # Remove control characters but keep printable Unicode
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    else:
        # Keep only ASCII printable characters
        text = re.sub(r'[^\x20-\x7e]', '', text)
    
    return text


def normalize_encoding(text: str) -> str:
    """
    Normalize text encoding issues.
    
    Args:
        text: Text with potential encoding issues
        
    Returns:
        Text with normalized encoding
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Normalize common encoding issues
    # Replace common problematic characters
    replacements = {
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u201C': '"',  # Left double quotation mark
        '\u201D': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '--',  # Em dash
        '\u2026': '...',  # Horizontal ellipsis
        '\u00A0': ' ',   # Non-breaking space
    }
    
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)
    
    return text


def clean_text_field(text: Optional[str]) -> Optional[str]:
    """
    Comprehensive text cleaning function that applies all cleaning steps.
    Returns None if input is None or empty after cleaning.
    
    Args:
        text: Text field to clean (can be None)
        
    Returns:
        Cleaned text or None if empty
    """
    if text is None:
        return None
    
    # Apply all cleaning steps
    cleaned = clean_text(text)
    cleaned = normalize_encoding(cleaned)
    cleaned = remove_special_characters(cleaned, keep_unicode=True)
    
    # Return None if empty after cleaning
    if not cleaned:
        return None
    
    return cleaned

