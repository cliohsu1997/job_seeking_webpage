"""Configuration tests for load-data-collection phase."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def scraping_sources():
    """Load scraping sources configuration."""
    config_path = Path(__file__).parent.parent.parent.parent / "data" / "config" / "scraping_sources.json"
    with open(config_path) as f:
        return json.load(f)


class TestScrapingSourcesStructure:
    """Test scraping sources configuration structure."""
    
    def test_has_accessible_section(self, scraping_sources):
        """Test that config has accessible section."""
        assert "accessible" in scraping_sources
    
    def test_has_non_accessible_section(self, scraping_sources):
        """Test that config has non_accessible section."""
        assert "non_accessible" in scraping_sources
    
    def test_all_entries_have_url(self, scraping_sources):
        """Test that all entries have URL field."""
        for section in ["accessible", "non_accessible"]:
            entries = scraping_sources.get(section, [])
            for entry in entries:
                assert "url" in entry, f"Missing URL in {section} entry {entry.get('id') or entry.get('name')}"
    
    def test_url_format_validity(self, scraping_sources):
        """Test that all URLs have valid format."""
        for section in ["accessible", "non_accessible"]:
            entries = scraping_sources.get(section, [])
            for entry in entries:
                url = entry.get("url", "")
                assert url.startswith(("http://", "https://")), f"Invalid URL format: {url}"
    
    def test_url_count(self, scraping_sources):
        """Test total URL count."""
        total = 0
        for section in ["accessible", "non_accessible"]:
            entries = scraping_sources.get(section, [])
            total += len(entries)

        assert total > 0, "No URLs configured"
        print(f"\nTotal URLs in config: {total}")
