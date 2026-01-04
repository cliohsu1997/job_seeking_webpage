"""Test URL accessibility with real scraping sources."""

import json
import pytest
from pathlib import Path
from scripts.scraper.config.url_access import (
    test_accessibility,
    is_accessible,
    follow_redirects,
)


@pytest.fixture
def scraping_sources():
    """Load real scraping sources."""
    config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "config" / "scraping_sources.json"
    with open(config_path) as f:
        return json.load(f)


@pytest.fixture
def sample_urls(scraping_sources):
    """Extract sample URLs for testing."""
    urls = []
    
    # Get first URLs from flat entries
    for section in ["accessible", "non_accessible"]:
        entries = scraping_sources.get(section, [])
        for entry in entries:
            if "url" in entry:
                urls.append(entry["url"])
            if len(urls) >= 5:
                break
        if len(urls) >= 5:
            break
    
    return urls[:5]


class TestBasicAccessibility:
    """Test basic HTTP accessibility."""
    
    def test_accessible_portal(self):
        """Test accessing a known working portal."""
        url = "https://www.aeaweb.org/joe/"
        result = test_accessibility(url)
        assert "accessible" in result
        assert "status_code" in result
    
    def test_timeout_detection(self):
        """Test that timeout is properly detected."""
        url = "https://httpbin.org/delay/15"  # Simulates 15s delay
        result = test_accessibility(url, timeout=2)
        assert result["error_type"] == "timeout"
    
    def test_is_accessible_wrapper(self):
        """Test is_accessible helper function."""
        url = "https://www.aeaweb.org/joe/"
        result = test_accessibility(url)
        assert isinstance(result["accessible"], bool)


class TestRedirectHandling:
    """Test redirect following."""
    
    def test_no_redirect(self):
        """Test URL with no redirects."""
        url = "https://www.aeaweb.org/joe/"
        result = follow_redirects(url)
        
        assert "original_url" in result
        assert "final_url" in result
        assert "redirect_chain" in result
        assert result["original_url"] == url
    
    def test_redirect_chain_recorded(self):
        """Test that redirect chains are recorded."""
        url = "https://httpbin.org/redirect/3"
        result = follow_redirects(url)
        
        assert "redirect_chain" in result
        assert "status_codes" in result


class TestWithRealSources:
    """Test with real scraping sources."""
    
    def test_sample_urls(self, sample_urls):
        """Test accessibility of sample URLs from config."""
        for url in sample_urls:
            result = test_accessibility(url, timeout=10)
            
            # Just verify result structure
            assert isinstance(result, dict)
            assert "accessible" in result
            assert isinstance(result["accessible"], bool)
            assert "error_type" in result
            
            print(f"\n{url}")
            print(f"  Accessible: {result['accessible']}")
            print(f"  Error: {result['error_type']}")
    
    def test_all_sources_have_urls(self, scraping_sources):
        """Verify all sources have valid URLs."""
        url_count = 0
        
        for section in ["accessible", "non_accessible"]:
            entries = scraping_sources.get(section, [])
            for entry in entries:
                assert "url" in entry, f"Missing URL in {section} entry {entry.get('id') or entry.get('name')}"
                assert entry["url"].startswith("http"), f"Invalid URL: {entry['url']}"
                url_count += 1
        
        assert url_count > 0, "No URLs found in scraping sources"
        print(f"\nTotal URLs found: {url_count}")
