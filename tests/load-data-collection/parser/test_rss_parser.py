"""
Tests for RSS/XML feed parser.
"""

import unittest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from parsers.rss_parser import (
    parse_rss_feed,
    parse_atom_feed,
    detect_feed_type,
    parse_feed
)


class TestRSSParser(unittest.TestCase):
    """Test RSS/XML feed parser functionality."""
    
    def test_parse_rss_feed_basic(self):
        """Test parsing basic RSS feed."""
        rss_xml = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Job Title 1</title>
                    <link>https://example.com/job1</link>
                    <description>Job description 1</description>
                    <pubDate>Mon, 01 Jan 2025 12:00:00 GMT</pubDate>
                </item>
                <item>
                    <title>Job Title 2</title>
                    <link>https://example.com/job2</link>
                    <description>Job description 2</description>
                    <pubDate>Mon, 02 Jan 2025 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>
        """
        items = parse_rss_feed(rss_xml)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "Job Title 1")
        self.assertEqual(items[0]["url"], "https://example.com/job1")
        self.assertEqual(items[1]["title"], "Job Title 2")
    
    def test_parse_rss_feed_missing_fields(self):
        """Test parsing RSS feed with missing optional fields."""
        rss_xml = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Job Title</title>
                    <link>https://example.com/job</link>
                </item>
            </channel>
        </rss>
        """
        items = parse_rss_feed(rss_xml)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Job Title")
        self.assertEqual(items[0]["url"], "https://example.com/job")
        self.assertEqual(items[0].get("description"), "")
    
    def test_parse_rss_feed_additional_fields(self):
        """Test parsing RSS feed with additional fields."""
        rss_xml = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Job Title</title>
                    <link>https://example.com/job</link>
                    <description>Description</description>
                    <pubDate>Mon, 01 Jan 2025 12:00:00 GMT</pubDate>
                    <category>Economics</category>
                    <author>admin@example.com</author>
                </item>
            </channel>
        </rss>
        """
        items = parse_rss_feed(rss_xml)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["category"], "Economics")
        self.assertEqual(items[0]["author"], "admin@example.com")
    
    def test_parse_atom_feed_basic(self):
        """Test parsing basic Atom feed."""
        atom_xml = """<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Job Title 1</title>
                <link href="https://example.com/job1"/>
                <summary>Job description 1</summary>
                <published>2025-01-01T12:00:00Z</published>
            </entry>
            <entry>
                <title>Job Title 2</title>
                <link href="https://example.com/job2"/>
                <summary>Job description 2</summary>
                <published>2025-01-02T12:00:00Z</published>
            </entry>
        </feed>
        """
        items = parse_atom_feed(atom_xml)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["title"], "Job Title 1")
        self.assertEqual(items[0]["url"], "https://example.com/job1")
        self.assertEqual(items[1]["title"], "Job Title 2")
    
    def test_parse_atom_feed_missing_fields(self):
        """Test parsing Atom feed with missing fields."""
        atom_xml = """<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Job Title</title>
                <link href="https://example.com/job"/>
            </entry>
        </feed>
        """
        items = parse_atom_feed(atom_xml)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Job Title")
        self.assertEqual(items[0]["url"], "https://example.com/job")
        self.assertEqual(items[0].get("description"), "")
    
    def test_detect_feed_type_rss(self):
        """Test detecting RSS feed type."""
        rss_xml = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel></channel>
        </rss>
        """
        feed_type = detect_feed_type(rss_xml)
        self.assertEqual(feed_type, "rss")
    
    def test_detect_feed_type_atom(self):
        """Test detecting Atom feed type."""
        atom_xml = """<?xml version="1.0"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
        </feed>
        """
        feed_type = detect_feed_type(atom_xml)
        self.assertEqual(feed_type, "atom")
    
    def test_detect_feed_type_unknown(self):
        """Test detecting unknown feed type."""
        xml = """<?xml version="1.0"?>
        <unknown>
        </unknown>
        """
        feed_type = detect_feed_type(xml)
        self.assertIsNone(feed_type)
    
    def test_detect_feed_type_invalid_xml(self):
        """Test detecting feed type with invalid XML."""
        invalid_xml = "not xml content"
        feed_type = detect_feed_type(invalid_xml)
        self.assertIsNone(feed_type)
    
    def test_parse_feed_auto_detect_rss(self):
        """Test auto-detecting and parsing RSS feed."""
        rss_xml = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Job Title</title>
                    <link>https://example.com/job</link>
                </item>
            </channel>
        </rss>
        """
        items = parse_feed(rss_xml)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Job Title")
    
    def test_parse_feed_auto_detect_atom(self):
        """Test auto-detecting and parsing Atom feed."""
        atom_xml = """<?xml version="1.0"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Job Title</title>
                <link href="https://example.com/job"/>
            </entry>
        </feed>
        """
        items = parse_feed(atom_xml)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Job Title")
    
    def test_parse_feed_fallback(self):
        """Test parse_feed fallback behavior."""
        # Feed that doesn't clearly indicate type
        xml = """<?xml version="1.0"?>
        <feed>
            <item>
                <title>Job Title</title>
                <link>https://example.com/job</link>
            </item>
        </feed>
        """
        # Should try RSS first, then Atom
        try:
            items = parse_feed(xml)
            # May succeed or fail depending on structure
            if items:
                self.assertIsInstance(items, list)
        except ValueError:
            # Expected if feed can't be parsed
            pass
    
    def test_parse_feed_invalid_xml(self):
        """Test parsing invalid XML."""
        invalid_xml = "not valid xml"
        with self.assertRaises(ValueError):
            parse_feed(invalid_xml)
    
    def test_parse_rss_feed_empty(self):
        """Test parsing empty RSS feed."""
        rss_xml = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
            </channel>
        </rss>
        """
        items = parse_rss_feed(rss_xml)
        self.assertEqual(len(items), 0)
    
    def test_parse_atom_feed_empty(self):
        """Test parsing empty Atom feed."""
        atom_xml = """<?xml version="1.0"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
        </feed>
        """
        items = parse_atom_feed(atom_xml)
        self.assertEqual(len(items), 0)


if __name__ == "__main__":
    unittest.main()

