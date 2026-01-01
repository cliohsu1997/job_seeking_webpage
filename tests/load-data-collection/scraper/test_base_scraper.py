"""
Tests for base scraper class.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from base_scraper import BaseScraper
from utils.rate_limiter import RateLimiter
from utils.retry_handler import RetryHandler
from utils.user_agent import UserAgentRotator


class ConcreteScraper(BaseScraper):
    """Concrete implementation of BaseScraper for testing."""
    
    def parse(self, html: str):
        """Parse HTML and return job listings."""
        return [{"title": "Test Job", "url": "https://example.com/job"}]
    
    def scrape(self):
        """Main scraping method."""
        html = self.fetch("https://example.com")
        if html:
            return self.parse(html)
        return []


class TestBaseScraper(unittest.TestCase):
    """Test base scraper functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_base_scraper_initialization(self):
        """Test base scraper initialization."""
        scraper = ConcreteScraper(output_dir=self.output_dir)
        self.assertIsInstance(scraper.rate_limiter, RateLimiter)
        self.assertIsInstance(scraper.retry_handler, RetryHandler)
        self.assertIsInstance(scraper.user_agent_rotator, UserAgentRotator)
        self.assertEqual(scraper.timeout, 30)
        self.assertEqual(scraper.output_dir, self.output_dir)
    
    def test_base_scraper_default_output_dir(self):
        """Test base scraper with default output directory."""
        scraper = ConcreteScraper()
        self.assertEqual(scraper.output_dir, Path("data/raw"))
    
    def test_base_scraper_custom_parameters(self):
        """Test base scraper with custom parameters."""
        scraper = ConcreteScraper(
            rate_limit_delay=5.0,
            max_retries=5,
            timeout=60,
            output_dir=self.output_dir
        )
        self.assertEqual(scraper.rate_limiter.delay_seconds, 5.0)
        self.assertEqual(scraper.retry_handler.max_retries, 5)
        self.assertEqual(scraper.timeout, 60)
    
    @patch('base_scraper.requests.Session')
    def test_base_scraper_fetch_success(self, mock_session_class):
        """Test successful fetch."""
        mock_response = Mock()
        mock_response.text = "<html>Test content</html>"
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        scraper = ConcreteScraper(output_dir=self.output_dir)
        scraper.session = mock_session
        
        html = scraper.fetch("https://example.com")
        self.assertEqual(html, "<html>Test content</html>")
        mock_session.get.assert_called_once()
    
    @patch('base_scraper.requests.Session')
    def test_base_scraper_fetch_failure(self, mock_session_class):
        """Test fetch failure."""
        import requests
        
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.RequestException("Connection error")
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        scraper = ConcreteScraper(output_dir=self.output_dir, max_retries=1)
        scraper.session = mock_session
        
        html = scraper.fetch("https://example.com")
        self.assertIsNone(html)
    
    def test_base_scraper_save_raw_html(self):
        """Test saving raw HTML to file."""
        scraper = ConcreteScraper(output_dir=self.output_dir)
        content = "<html>Test content</html>"
        filename = "test.html"
        
        filepath = scraper.save_raw_html(content, filename)
        
        self.assertTrue(filepath.exists())
        self.assertEqual(filepath, self.output_dir / filename)
        with open(filepath, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), content)
    
    def test_base_scraper_save_raw_html_nested_path(self):
        """Test saving raw HTML to nested path."""
        scraper = ConcreteScraper(output_dir=self.output_dir)
        content = "<html>Test</html>"
        filename = "subdir/test.html"
        
        filepath = scraper.save_raw_html(content, filename)
        
        self.assertTrue(filepath.exists())
        self.assertEqual(filepath, self.output_dir / "subdir" / "test.html")
    
    @patch('base_scraper.requests.Session')
    def test_base_scraper_extract(self, mock_session_class):
        """Test extract method (fetch + parse)."""
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        scraper = ConcreteScraper(output_dir=self.output_dir)
        scraper.session = mock_session
        
        listings = scraper.extract("https://example.com", save_raw=False)
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0]["title"], "Test Job")
    
    @patch('base_scraper.requests.Session')
    def test_base_scraper_extract_with_save(self, mock_session_class):
        """Test extract method with saving raw HTML."""
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        scraper = ConcreteScraper(output_dir=self.output_dir)
        scraper.session = mock_session
        
        listings = scraper.extract("https://example.com", save_raw=True, filename="test.html")
        self.assertEqual(len(listings), 1)
        # Check that file was saved
        self.assertTrue((self.output_dir / "test.html").exists())
    
    @patch('base_scraper.requests.Session')
    def test_base_scraper_extract_fetch_failure(self, mock_session_class):
        """Test extract method when fetch fails."""
        import requests
        
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.RequestException("Error")
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        scraper = ConcreteScraper(output_dir=self.output_dir, max_retries=1)
        scraper.session = mock_session
        
        listings = scraper.extract("https://example.com")
        self.assertEqual(len(listings), 0)
    
    @patch('base_scraper.requests.Session')
    def test_base_scraper_extract_parse_failure(self, mock_session_class):
        """Test extract method when parse fails."""
        class FailingScraper(ConcreteScraper):
            def parse(self, html: str):
                raise Exception("Parse error")
        
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.raise_for_status = Mock()
        
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session.headers = {}
        mock_session_class.return_value = mock_session
        
        scraper = FailingScraper(output_dir=self.output_dir)
        scraper.session = mock_session
        
        listings = scraper.extract("https://example.com")
        self.assertEqual(len(listings), 0)
    
    def test_base_scraper_abstract_methods(self):
        """Test that abstract methods must be implemented."""
        # BaseScraper should not be instantiable directly
        with self.assertRaises(TypeError):
            BaseScraper()


if __name__ == "__main__":
    unittest.main()

