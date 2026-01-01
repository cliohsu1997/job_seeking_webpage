"""
Basic tests for scraper modules.
"""

import unittest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "scraper"))

from utils.rate_limiter import RateLimiter
from utils.retry_handler import RetryHandler
from utils.user_agent import UserAgentRotator
from parsers.html_parser import HTMLParser
from parsers.date_parser import parse_date, extract_deadline
from parsers.text_extractor import clean_text


class TestRateLimiter(unittest.TestCase):
    """Test rate limiter functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(delay_seconds=2.0)
        self.assertEqual(limiter.delay_seconds, 2.0)
        self.assertIsNone(limiter.last_request_time)
    
    def test_rate_limiter_reset(self):
        """Test rate limiter reset."""
        limiter = RateLimiter()
        limiter.wait_if_needed()
        limiter.reset()
        self.assertIsNone(limiter.last_request_time)


class TestUserAgentRotator(unittest.TestCase):
    """Test user agent rotator."""
    
    def test_user_agent_rotator(self):
        """Test user agent rotator returns valid user agents."""
        rotator = UserAgentRotator()
        user_agent = rotator.get_random()
        self.assertIsInstance(user_agent, str)
        self.assertGreater(len(user_agent), 0)
        
        default = rotator.get_default()
        self.assertIsInstance(default, str)
        self.assertGreater(len(default), 0)


class TestTextExtractor(unittest.TestCase):
    """Test text extraction utilities."""
    
    def test_clean_text(self):
        """Test text cleaning."""
        dirty_text = "  Hello   world  \n\n  with   spaces  "
        cleaned = clean_text(dirty_text)
        self.assertEqual(cleaned, "Hello world with spaces")
        
        empty = clean_text("")
        self.assertEqual(empty, "")


class TestDateParser(unittest.TestCase):
    """Test date parsing utilities."""
    
    def test_parse_date(self):
        """Test date parsing."""
        # Test various date formats
        self.assertEqual(parse_date("2025-01-15"), "2025-01-15")
        self.assertEqual(parse_date("01/15/2025"), "2025-01-15")
        self.assertIsNotNone(parse_date("January 15, 2025"))
        
        # Test invalid dates
        self.assertIsNone(parse_date(""))
        self.assertIsNone(parse_date("invalid date"))
    
    def test_extract_deadline(self):
        """Test deadline extraction."""
        text = "Application deadline: January 15, 2025. Please submit by this date."
        deadline = extract_deadline(text)
        self.assertIsNotNone(deadline)


class TestHTMLParser(unittest.TestCase):
    """Test HTML parser."""
    
    def test_html_parser_initialization(self):
        """Test HTML parser initialization."""
        html = "<html><body><h1>Test</h1></body></html>"
        parser = HTMLParser(html)
        self.assertIsNotNone(parser.soup)
    
    def test_html_parser_select_one(self):
        """Test CSS selector functionality."""
        html = "<html><body><div class='test'>Content</div></body></html>"
        parser = HTMLParser(html)
        content = parser.select_one(".test")
        self.assertEqual(content, "Content")
    
    def test_html_parser_get_full_text(self):
        """Test full text extraction."""
        html = "<html><body><p>Hello</p><p>World</p></body></html>"
        parser = HTMLParser(html)
        text = parser.get_full_text()
        self.assertIn("Hello", text)
        self.assertIn("World", text)


if __name__ == "__main__":
    unittest.main()

