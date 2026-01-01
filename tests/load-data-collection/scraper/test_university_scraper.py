"""
Tests for university scraper.
"""

import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from university_scraper import UniversityScraper, scrape_all_universities


class TestUniversityScraper(unittest.TestCase):
    """Test university scraper functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "output"
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_university_scraper_initialization(self):
        """Test university scraper initialization."""
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com/jobs",
            department="Economics",
            output_dir=self.output_dir
        )
        self.assertEqual(scraper.university_name, "Test University")
        self.assertEqual(scraper.url, "https://example.com/jobs")
        self.assertEqual(scraper.department, "Economics")
        self.assertEqual(scraper.source_name, "university_website")
    
    def test_university_scraper_default_output_dir(self):
        """Test university scraper with default output directory."""
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com/jobs"
        )
        self.assertEqual(scraper.output_dir, Path("data/raw/universities"))
    
    def test_university_scraper_parse_with_containers(self):
        """Test parsing HTML with job containers."""
        html = """
        <html>
            <body>
                <div class="job-listing">
                    <h2><a href="/job1">Faculty Position</a></h2>
                    <p>Description here</p>
                    <p>Application deadline: January 15, 2025</p>
                </div>
                <div class="job-listing">
                    <h2><a href="/job2">Assistant Professor</a></h2>
                    <p>Another description</p>
                </div>
            </body>
        </html>
        """
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com",
            department="Economics"
        )
        listings = scraper.parse(html)
        
        # Should find job listings
        self.assertGreater(len(listings), 0)
        for listing in listings:
            self.assertEqual(listing["source"], "university_website")
            self.assertEqual(listing["institution"], "Test University")
            self.assertEqual(listing["department"], "Economics")
    
    def test_university_scraper_parse_with_links(self):
        """Test parsing HTML with job links."""
        html = """
        <html>
            <body>
                <a href="/job1">Faculty Position in Economics</a>
                <a href="/job2">Job Opening</a>
                <a href="/other">Other Link</a>
            </body>
        </html>
        """
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com",
            department="Economics"
        )
        listings = scraper.parse(html)
        
        # Should find job-related links
        self.assertGreater(len(listings), 0)
        for listing in listings:
            self.assertIn("source_url", listing)
            self.assertIn("title", listing)
    
    def test_university_scraper_parse_deduplication(self):
        """Test that parser deduplicates by URL."""
        html = """
        <html>
            <body>
                <div class="job-listing">
                    <h2><a href="/job1">Faculty Position</a></h2>
                </div>
                <div class="job-listing">
                    <h2><a href="/job1">Same Position</a></h2>
                </div>
            </body>
        </html>
        """
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com",
            department="Economics"
        )
        listings = scraper.parse(html)
        
        # Should deduplicate
        urls = [listing.get("source_url", "") for listing in listings]
        unique_urls = set(urls)
        self.assertEqual(len(urls), len(unique_urls))
    
    def test_university_scraper_extract_listing_from_element(self):
        """Test extracting listing from element."""
        from bs4 import BeautifulSoup
        
        html = """
        <div class="job-listing">
            <h2><a href="/job1">Faculty Position</a></h2>
            <p>Description text</p>
            <p>Deadline: January 15, 2025</p>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")
        
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com",
            department="Economics"
        )
        from parsers.html_parser import HTMLParser
        parser = HTMLParser(html)
        
        listing = scraper._extract_listing_from_element(element, parser)
        
        self.assertIsNotNone(listing)
        self.assertIn("title", listing)
        self.assertIn("source_url", listing)
        self.assertEqual(listing["institution"], "Test University")
        self.assertEqual(listing["department"], "Economics")
    
    def test_university_scraper_sanitize_filename(self):
        """Test filename sanitization."""
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com"
        )
        
        filename1 = scraper._sanitize_filename("Test University_Economics.html")
        self.assertNotIn(" ", filename1)
        self.assertNotIn(".", filename1)
        
        filename2 = scraper._sanitize_filename("Test@University#123.html")
        self.assertNotIn("@", filename2)
        self.assertNotIn("#", filename2)
    
    @patch('university_scraper.UniversityScraper.fetch')
    def test_university_scraper_scrape(self, mock_fetch):
        """Test main scraping method."""
        html = """
        <html>
            <body>
                <div class="job-listing">
                    <h2><a href="/job1">Faculty Position</a></h2>
                </div>
            </body>
        </html>
        """
        mock_fetch.return_value = html
        
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com/jobs",
            department="Economics",
            output_dir=self.output_dir
        )
        listings = scraper.scrape()
        
        self.assertGreater(len(listings), 0)
        mock_fetch.assert_called_once_with("https://example.com/jobs")
        # Check that HTML was saved
        self.assertTrue(any(f.name.endswith(".html") for f in self.output_dir.iterdir()))
    
    @patch('university_scraper.UniversityScraper.fetch')
    def test_university_scraper_scrape_fetch_failure(self, mock_fetch):
        """Test scraping when fetch fails."""
        mock_fetch.return_value = None
        
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com/jobs",
            department="Economics"
        )
        listings = scraper.scrape()
        
        self.assertEqual(len(listings), 0)
    
    def test_university_scraper_get_current_date(self):
        """Test getting current date."""
        scraper = UniversityScraper(
            university_name="Test University",
            url="https://example.com"
        )
        date = scraper._get_current_date()
        
        # Should be in YYYY-MM-DD format
        self.assertRegex(date, r'^\d{4}-\d{2}-\d{2}$')
    
    @patch('university_scraper.get_accessible_config')
    @patch('university_scraper.UniversityScraper.scrape')
    def test_scrape_all_universities(self, mock_scrape, mock_get_config):
        """Test scraping all universities from config."""
        mock_get_config.return_value = {
            "regions": {
                "united_states": {
                    "universities": [
                        {
                            "name": "Test University",
                            "departments": [
                                {"name": "Economics", "url": "https://example.com/econ"}
                            ]
                        }
                    ]
                }
            }
        }
        mock_scrape.return_value = [
            {"title": "Job 1", "source": "university_website"}
        ]
        
        listings = scrape_all_universities(output_dir=self.output_dir)
        
        self.assertGreater(len(listings), 0)
        mock_scrape.assert_called()


if __name__ == "__main__":
    unittest.main()

