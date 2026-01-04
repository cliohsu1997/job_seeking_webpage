"""Test redirect handling with real sources."""

import json
import pytest
from pathlib import Path
from scripts.scraper.config.url_access import follow_redirects


@pytest.fixture
def job_portal_urls():
    """Get job portal URLs from config."""
    config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "config" / "scraping_sources.json"
    with open(config_path) as f:
        sources = json.load(f)
    
    urls = []
    if "accessible" in sources and "job_portals" in sources["accessible"]:
        for key, config in sources["accessible"]["job_portals"].items():
            urls.append(config["url"])
    
    return urls


class TestRedirectChains:
    """Test redirect chain tracking."""
    
    def test_redirect_chain_structure(self, job_portal_urls):
        """Test that redirect results have proper structure."""
        if not job_portal_urls:
            pytest.skip("No job portals configured")
        
        url = job_portal_urls[0]
        result = follow_redirects(url, timeout=5)
        
        assert "original_url" in result
        assert "final_url" in result
        assert "redirect_chain" in result
        assert "status_codes" in result
        assert "loop_detected" in result
        assert "external_system" in result
    
    def test_external_system_detection(self):
        """Test detection of external HR systems."""
        # ICIMS example
        result = follow_redirects("https://example.icims.com/jobs")
        assert result.get("external_system") is not None
    
    def test_no_redirect_chain_single_url(self):
        """Test URL with no redirects returns single-item chain."""
        url = "https://www.aeaweb.org/joe/"
        result = follow_redirects(url)
        
        if not result.get("error"):
            # If successful, should have at least original URL
            assert len(result["redirect_chain"]) >= 1
            assert result["redirect_chain"][0] == url
