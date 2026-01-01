"""
Tests for text extraction utilities.
"""

import unittest
from pathlib import Path
import sys
from bs4 import BeautifulSoup

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from parsers.text_extractor import (
    extract_text,
    clean_text,
    remove_script_and_style,
    extract_main_content,
    find_links_by_keywords,
    find_text_by_keywords
)


class TestTextExtractor(unittest.TestCase):
    """Test text extraction utilities."""
    
    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        dirty_text = "  Hello   world  \n\n  with   spaces  "
        cleaned = clean_text(dirty_text)
        self.assertEqual(cleaned, "Hello world with spaces")
    
    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text("   "), "")
    
    def test_clean_text_no_whitespace(self):
        """Test cleaning text with no extra whitespace."""
        text = "Hello world"
        self.assertEqual(clean_text(text), "Hello world")
    
    def test_clean_text_tabs_and_newlines(self):
        """Test cleaning text with tabs and newlines."""
        text = "Hello\t\tworld\n\nwith\n\tspaces"
        cleaned = clean_text(text)
        self.assertEqual(cleaned, "Hello world with spaces")
    
    def test_extract_text_from_element(self):
        """Test extracting text from BeautifulSoup element."""
        html = "<div>Hello <span>world</span></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        
        text = extract_text(element)
        self.assertIn("Hello", text)
        self.assertIn("world", text)
    
    def test_extract_text_from_none(self):
        """Test extracting text from None element."""
        self.assertEqual(extract_text(None), "")
    
    def test_extract_text_strip_false(self):
        """Test extracting text without stripping."""
        html = "<div>  Hello  </div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        
        text = extract_text(element, strip=False)
        # Should still clean whitespace but not strip
        self.assertIn("Hello", text)
    
    def test_remove_script_and_style(self):
        """Test removing script and style elements."""
        html = """
        <html>
            <head>
                <script>alert('test');</script>
                <style>body { color: red; }</style>
            </head>
            <body>
                <p>Content</p>
                <noscript>No script</noscript>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        remove_script_and_style(soup)
        
        # Script and style should be removed
        self.assertIsNone(soup.find("script"))
        self.assertIsNone(soup.find("style"))
        self.assertIsNone(soup.find("noscript"))
        
        # Content should remain
        self.assertIsNotNone(soup.find("p"))
    
    def test_extract_main_content_with_selector(self):
        """Test extracting main content with specific selector."""
        html = """
        <html>
            <body>
                <nav>Navigation</nav>
                <main>Main content here</main>
                <footer>Footer</footer>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        content = extract_main_content(soup, selectors=["main"])
        
        self.assertIsNotNone(content)
        self.assertEqual(content.name, "main")
        self.assertIn("Main content here", content.get_text())
    
    def test_extract_main_content_fallback(self):
        """Test extracting main content with fallback selectors."""
        html = """
        <html>
            <body>
                <nav>Navigation</nav>
                <article>Article content</article>
                <footer>Footer</footer>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        content = extract_main_content(soup)
        
        # Should find article or body
        self.assertIsNotNone(content)
        self.assertIn(content.name, ["article", "body"])
    
    def test_extract_main_content_no_selectors(self):
        """Test extracting main content without selectors."""
        html = """
        <html>
            <body>
                <p>Content</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        content = extract_main_content(soup)
        
        # Should return body as fallback
        self.assertIsNotNone(content)
        self.assertEqual(content.name, "body")
    
    def test_find_links_by_keywords(self):
        """Test finding links by keywords."""
        html = """
        <html>
            <body>
                <a href="/job1">Job Position</a>
                <a href="/other">Other Link</a>
                <a href="/job2">Faculty Opening</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        links = find_links_by_keywords(soup, ["job", "faculty"])
        
        self.assertEqual(len(links), 2)
        self.assertTrue(any("job" in link["text"].lower() or "job" in link["url"].lower() for link in links))
        self.assertTrue(any("faculty" in link["text"].lower() for link in links))
    
    def test_find_links_by_keywords_no_matches(self):
        """Test finding links with no matches."""
        html = """
        <html>
            <body>
                <a href="/other1">Other Link 1</a>
                <a href="/other2">Other Link 2</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        links = find_links_by_keywords(soup, ["job", "faculty"])
        
        self.assertEqual(len(links), 0)
    
    def test_find_text_by_keywords(self):
        """Test finding text by keywords."""
        html = """
        <html>
            <body>
                <p>Application deadline: January 15, 2025</p>
                <p>Other content here</p>
                <p>Closing date: February 20, 2025</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        results = find_text_by_keywords(soup, ["deadline", "closing date"])
        
        self.assertGreater(len(results), 0)
        # Should find both keywords
        keywords_found = [r["keyword"] for r in results]
        self.assertTrue(any("deadline" in kw.lower() for kw in keywords_found))
    
    def test_find_text_by_keywords_context(self):
        """Test finding text by keywords with context."""
        html = """
        <html>
            <body>
                <p>Some text before. Application deadline: January 15, 2025. Some text after.</p>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        results = find_text_by_keywords(soup, ["deadline"], context_length=20)
        
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn("deadline", result["text"].lower())
            self.assertIn("keyword", result)


if __name__ == "__main__":
    unittest.main()

