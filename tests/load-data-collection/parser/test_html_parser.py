"""
Tests for HTML parser.
"""

import unittest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from parsers.html_parser import HTMLParser


class TestHTMLParser(unittest.TestCase):
    """Test HTML parser functionality."""
    
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
    
    def test_html_parser_select_one_not_found(self):
        """Test CSS selector when element not found."""
        html = "<html><body><div>Content</div></body></html>"
        parser = HTMLParser(html)
        content = parser.select_one(".nonexistent")
        self.assertIsNone(content)
    
    def test_html_parser_select_all(self):
        """Test selecting all elements by CSS selector."""
        html = """
        <html>
            <body>
                <div class='item'>Item 1</div>
                <div class='item'>Item 2</div>
                <div class='item'>Item 3</div>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        items = parser.select_all(".item")
        self.assertEqual(len(items), 3)
        self.assertIn("Item 1", items)
        self.assertIn("Item 2", items)
        self.assertIn("Item 3", items)
    
    def test_html_parser_find_by_class(self):
        """Test finding elements by class name."""
        html = """
        <html>
            <body>
                <div class='test'>Content 1</div>
                <p class='test'>Content 2</p>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        elements = parser.find_by_class("test")
        self.assertEqual(len(elements), 2)
        self.assertIn("Content 1", elements)
        self.assertIn("Content 2", elements)
    
    def test_html_parser_find_by_class_with_tag(self):
        """Test finding elements by class name with specific tag."""
        html = """
        <html>
            <body>
                <div class='test'>Content 1</div>
                <p class='test'>Content 2</p>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        elements = parser.find_by_class("test", tag="div")
        self.assertEqual(len(elements), 1)
        self.assertIn("Content 1", elements)
    
    def test_html_parser_extract_links(self):
        """Test extracting links from HTML."""
        html = """
        <html>
            <body>
                <a href="/page1">Link 1</a>
                <a href="/page2">Link 2</a>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        links = parser.extract_links()
        self.assertEqual(len(links), 2)
        self.assertTrue(any(link["url"] == "/page1" for link in links))
        self.assertTrue(any(link["url"] == "/page2" for link in links))
    
    def test_html_parser_extract_links_with_keywords(self):
        """Test extracting links filtered by keywords."""
        html = """
        <html>
            <body>
                <a href="/job1">Job Position</a>
                <a href="/other">Other Link</a>
                <a href="/job2">Faculty Opening</a>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        links = parser.extract_links(keywords=["job", "faculty"])
        self.assertEqual(len(links), 2)
        self.assertTrue(any("job" in link["text"].lower() or "job" in link["url"].lower() for link in links))
    
    def test_html_parser_extract_deadline(self):
        """Test extracting deadline from HTML."""
        html = """
        <html>
            <body>
                <p>Application deadline: January 15, 2025</p>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        deadline = parser.extract_deadline()
        self.assertIsNotNone(deadline)
        self.assertEqual(deadline, "2025-01-15")
    
    def test_html_parser_extract_deadline_from_text(self):
        """Test extracting deadline from specific text."""
        text = "Application deadline: February 20, 2025"
        parser = HTMLParser("<html><body></body></html>")
        deadline = parser.extract_deadline(text=text)
        self.assertIsNotNone(deadline)
        self.assertEqual(deadline, "2025-02-20")
    
    def test_html_parser_get_main_content(self):
        """Test extracting main content area."""
        html = """
        <html>
            <body>
                <nav>Navigation</nav>
                <main>Main content here</main>
                <footer>Footer</footer>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        content = parser.get_main_content(selectors=["main"])
        self.assertIsNotNone(content)
        self.assertIn("Main content here", content)
    
    def test_html_parser_get_main_content_fallback(self):
        """Test extracting main content with fallback."""
        html = """
        <html>
            <body>
                <p>Content in body</p>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        content = parser.get_main_content()
        self.assertIsNotNone(content)
        self.assertIn("Content in body", content)
    
    def test_html_parser_get_full_text(self):
        """Test getting full text content."""
        html = """
        <html>
            <body>
                <p>Hello</p>
                <p>World</p>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        text = parser.get_full_text()
        self.assertIn("Hello", text)
        self.assertIn("World", text)
    
    def test_html_parser_get_soup(self):
        """Test getting the underlying BeautifulSoup object."""
        html = "<html><body><div>Test</div></body></html>"
        parser = HTMLParser(html)
        soup = parser.get_soup()
        self.assertIsNotNone(soup)
        # Should be able to use BeautifulSoup methods
        div = soup.find("div")
        self.assertIsNotNone(div)
        self.assertEqual(div.get_text(), "Test")
    
    def test_html_parser_removes_script_and_style(self):
        """Test that parser removes script and style elements."""
        html = """
        <html>
            <head>
                <script>alert('test');</script>
                <style>body { color: red; }</style>
            </head>
            <body>
                <p>Content</p>
            </body>
        </html>
        """
        parser = HTMLParser(html)
        # Script and style should be removed
        self.assertIsNone(parser.soup.find("script"))
        self.assertIsNone(parser.soup.find("style"))
        # Content should remain
        self.assertIsNotNone(parser.soup.find("p"))


if __name__ == "__main__":
    unittest.main()

