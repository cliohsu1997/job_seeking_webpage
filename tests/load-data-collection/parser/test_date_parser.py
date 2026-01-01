"""
Tests for date parsing utilities.
"""

import unittest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from parsers.date_parser import parse_date, extract_deadline


class TestDateParser(unittest.TestCase):
    """Test date parsing utilities."""
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO format dates."""
        self.assertEqual(parse_date("2025-01-15"), "2025-01-15")
        self.assertEqual(parse_date("2024-12-31"), "2024-12-31")
    
    def test_parse_date_us_format(self):
        """Test parsing US format dates."""
        self.assertEqual(parse_date("01/15/2025"), "2025-01-15")
        self.assertEqual(parse_date("12/31/2024"), "2024-12-31")
    
    def test_parse_date_short_year(self):
        """Test parsing dates with short year."""
        result = parse_date("01/15/25")
        self.assertIsNotNone(result)
        # Should parse to full year (may be 2025 or 1925 depending on dateutil)
    
    def test_parse_date_text_format(self):
        """Test parsing text format dates."""
        result = parse_date("January 15, 2025")
        self.assertIsNotNone(result)
        self.assertEqual(result, "2025-01-15")
    
    def test_parse_date_text_format_abbreviated(self):
        """Test parsing abbreviated text format dates."""
        result = parse_date("Jan 15, 2025")
        self.assertIsNotNone(result)
        self.assertEqual(result, "2025-01-15")
    
    def test_parse_date_with_extra_text(self):
        """Test parsing dates with extra text."""
        result = parse_date("The deadline is January 15, 2025 for applications")
        self.assertIsNotNone(result)
        self.assertEqual(result, "2025-01-15")
    
    def test_parse_date_empty_string(self):
        """Test parsing empty string."""
        self.assertIsNone(parse_date(""))
        self.assertIsNone(parse_date("   "))
    
    def test_parse_date_invalid(self):
        """Test parsing invalid date strings."""
        self.assertIsNone(parse_date("invalid date"))
        self.assertIsNone(parse_date("not a date"))
        self.assertIsNone(parse_date("abc123"))
    
    def test_parse_date_none(self):
        """Test parsing None."""
        # Should handle None gracefully
        try:
            result = parse_date(None)
            # Either returns None or raises TypeError
            if result is not None:
                self.fail("parse_date(None) should return None or raise TypeError")
        except (TypeError, AttributeError):
            pass  # Expected behavior
    
    def test_extract_deadline_basic(self):
        """Test extracting deadline from text."""
        text = "Application deadline: January 15, 2025. Please submit by this date."
        deadline = extract_deadline(text)
        self.assertIsNotNone(deadline)
        self.assertEqual(deadline, "2025-01-15")
    
    def test_extract_deadline_different_keywords(self):
        """Test extracting deadline with different keywords."""
        text1 = "Closing date: February 20, 2025"
        deadline1 = extract_deadline(text1)
        self.assertIsNotNone(deadline1)
        
        text2 = "Due date: March 10, 2025"
        deadline2 = extract_deadline(text2)
        self.assertIsNotNone(deadline2)
        
        text3 = "Application deadline: April 5, 2025"
        deadline3 = extract_deadline(text3)
        self.assertIsNotNone(deadline3)
        self.assertEqual(deadline3, "2025-04-05")
    
    def test_extract_deadline_custom_keywords(self):
        """Test extracting deadline with custom keywords."""
        text = "Submit by: May 1, 2025"
        deadline = extract_deadline(text, keywords=["submit by"])
        self.assertIsNotNone(deadline)
        self.assertEqual(deadline, "2025-05-01")
    
    def test_extract_deadline_no_deadline(self):
        """Test extracting deadline when none exists."""
        text = "This is just regular text with no deadline information."
        deadline = extract_deadline(text)
        self.assertIsNone(deadline)
    
    def test_extract_deadline_multiple_dates(self):
        """Test extracting deadline when multiple dates exist."""
        text = "Posted on January 1, 2025. Application deadline: January 15, 2025."
        deadline = extract_deadline(text)
        # Should extract the deadline, not the posted date
        self.assertIsNotNone(deadline)
        self.assertEqual(deadline, "2025-01-15")
    
    def test_extract_deadline_various_formats(self):
        """Test extracting deadline in various date formats."""
        test_cases = [
            ("Deadline: 2025-01-15", "2025-01-15"),
            ("Deadline: 01/15/2025", "2025-01-15"),
            ("Deadline: January 15, 2025", "2025-01-15"),
            ("Deadline: Jan 15, 2025", "2025-01-15"),
        ]
        
        for text, expected in test_cases:
            deadline = extract_deadline(text)
            self.assertIsNotNone(deadline, f"Failed to parse: {text}")
            self.assertEqual(deadline, expected, f"Wrong date for: {text}")
    
    def test_extract_deadline_case_insensitive(self):
        """Test that deadline extraction is case insensitive."""
        text1 = "DEADLINE: January 15, 2025"
        text2 = "Deadline: January 15, 2025"
        text3 = "deadline: January 15, 2025"
        
        deadline1 = extract_deadline(text1)
        deadline2 = extract_deadline(text2)
        deadline3 = extract_deadline(text3)
        
        self.assertEqual(deadline1, "2025-01-15")
        self.assertEqual(deadline2, "2025-01-15")
        self.assertEqual(deadline3, "2025-01-15")


if __name__ == "__main__":
    unittest.main()

