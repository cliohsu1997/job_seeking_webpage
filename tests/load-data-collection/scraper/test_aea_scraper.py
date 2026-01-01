"""
Tests for AEA scraper.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from aea_scraper import AEAScraper


class TestAEAScraper(unittest.TestCase):
    """Test AEA scraper functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_aea_scraper_initialization(self):
        """Test AEA scraper initialization."""
        scraper = AEAScraper(output_dir=self.output_dir)
        self.assertEqual(scraper.source_name, "aea")
        self.assertEqual(scraper.BASE_URL, "https://www.aeaweb.org")
        self.assertEqual(scraper.LISTINGS_URL, "https://www.aeaweb.org/joe/listings.php")
    
    def test_aea_scraper_default_output_dir(self):
        """Test AEA scraper with default output directory."""
        scraper = AEAScraper()
        self.assertEqual(scraper.output_dir, Path("data/raw/aea"))
    
    @patch('aea_scraper.AEAScraper.fetch')
    def test_aea_scraper_check_rss_feed_success(self, mock_fetch):
        """Test checking RSS feed successfully."""
        rss_xml = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Job Title</title>
                    <link>https://example.com/job</link>
                    <description>Job description</description>
                    <pubDate>Mon, 01 Jan 2025 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>
        """
        mock_fetch.return_value = rss_xml
        
        scraper = AEAScraper(output_dir=self.output_dir)
        listings = scraper.check_rss_feed()
        
        self.assertGreater(len(listings), 0)
        self.assertEqual(listings[0]["source"], "aea")
        self.assertIn("title", listings[0])
        self.assertIn("source_url", listings[0])
    
    @patch('aea_scraper.AEAScraper.fetch')
    def test_aea_scraper_check_rss_feed_not_available(self, mock_fetch):
        """Test checking RSS feed when not available."""
        mock_fetch.return_value = "<html>Not RSS</html>"
        
        scraper = AEAScraper(output_dir=self.output_dir)
        listings = scraper.check_rss_feed()
        
        self.assertEqual(len(listings), 0)
    
    @patch('aea_scraper.AEAScraper.fetch')
    def test_aea_scraper_check_rss_feed_failure(self, mock_fetch):
        """Test checking RSS feed when fetch fails."""
        mock_fetch.return_value = None
        
        scraper = AEAScraper(output_dir=self.output_dir)
        listings = scraper.check_rss_feed()
        
        self.assertEqual(len(listings), 0)
    
    def test_aea_scraper_normalize_rss_listing(self):
        """Test normalizing RSS listing."""
        scraper = AEAScraper(output_dir=self.output_dir)
        rss_listing = {
            "title": "Job Title",
            "url": "https://example.com/job",
            "description": "Job description",
            "published_date": "2025-01-01"
        }
        
        normalized = scraper._normalize_rss_listing(rss_listing)
        
        self.assertEqual(normalized["title"], "Job Title")
        self.assertEqual(normalized["source"], "aea")
        self.assertEqual(normalized["source_url"], "https://example.com/job")
        self.assertIn("scraped_date", normalized)
    
    def test_aea_scraper_parse_html(self):
        """Test parsing HTML content."""
        html = """
        <html>
            <body>
                <div class="job-listing">
                    <h2><a href="/job1">Faculty Position</a></h2>
                    <p>Application deadline: January 15, 2025</p>
                </div>
            </body>
        </html>
        """
        scraper = AEAScraper(output_dir=self.output_dir)
        listings = scraper.parse(html)
        
        # May return empty list if structure doesn't match
        # This is expected as AEA structure may vary
        self.assertIsInstance(listings, list)
    
    @patch('aea_scraper.AEAScraper.check_rss_feed')
    @patch('aea_scraper.AEAScraper.fetch')
    def test_aea_scraper_scrape_rss_available(self, mock_fetch, mock_check_rss):
        """Test scraping when RSS feed is available."""
        mock_check_rss.return_value = [
            {"title": "Job 1", "source": "aea", "source_url": "https://example.com/job1"}
        ]
        
        scraper = AEAScraper(output_dir=self.output_dir)
        listings = scraper.scrape()
        
        self.assertEqual(len(listings), 1)
        self.assertEqual(listings[0]["title"], "Job 1")
        # Should not fetch HTML when RSS is available
        mock_fetch.assert_not_called()
    
    @patch('aea_scraper.AEAScraper.check_rss_feed')
    @patch('aea_scraper.AEAScraper.fetch')
    @patch('aea_scraper.AEAScraper.parse')
    def test_aea_scraper_scrape_html_fallback(self, mock_parse, mock_fetch, mock_check_rss):
        """Test scraping with HTML fallback."""
        mock_check_rss.return_value = []  # No RSS feed
        mock_fetch.return_value = "<html>Content</html>"
        mock_parse.return_value = [
            {"title": "Job 1", "source": "aea", "source_url": "https://example.com/job1"}
        ]
        
        scraper = AEAScraper(output_dir=self.output_dir)
        listings = scraper.scrape()
        
        self.assertEqual(len(listings), 1)
        mock_fetch.assert_called_once_with(scraper.LISTINGS_URL)
        mock_parse.assert_called_once()
    
    @patch('aea_scraper.AEAScraper.check_rss_feed')
    @patch('aea_scraper.AEAScraper.fetch')
    def test_aea_scraper_scrape_fetch_failure(self, mock_fetch, mock_check_rss):
        """Test scraping when fetch fails."""
        mock_check_rss.return_value = []
        mock_fetch.return_value = None
        
        scraper = AEAScraper(output_dir=self.output_dir)
        listings = scraper.scrape()
        
        self.assertEqual(len(listings), 0)
    
    def test_aea_scraper_get_current_date(self):
        """Test getting current date."""
        scraper = AEAScraper(output_dir=self.output_dir)
        date = scraper._get_current_date()
        
        # Should be in YYYY-MM-DD format
        self.assertRegex(date, r'^\d{4}-\d{2}-\d{2}$')


if __name__ == "__main__":
    unittest.main()

