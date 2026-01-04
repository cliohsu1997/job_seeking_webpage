"""Test connectivity report generation."""

import json
import pytest
from pathlib import Path
from scripts.scraper.check_config.url_access import generate_accessibility_report


@pytest.fixture
def scraping_sources_path():
    """Get path to scraping sources config."""
    return Path(__file__).parent.parent.parent.parent.parent / "data" / "config" / "scraping_sources.json"


@pytest.fixture
def temp_report_dir(tmp_path):
    """Create temporary directory for reports."""
    return tmp_path / "reports"


class TestReportGeneration:
    """Test accessibility report generation."""
    
    def test_report_structure(self, scraping_sources_path, temp_report_dir):
        """Test that report has proper structure."""
        if not scraping_sources_path.exists():
            pytest.skip("Scraping sources config not found")
        
        # Generate a small report (limiting to first few URLs)
        report = generate_accessibility_report(
            str(scraping_sources_path),
            str(temp_report_dir),
            output_formats=["json"],
        )
        
        assert "summary" in report
        assert "detailed_results" in report
        assert "by_region" in report
        assert "by_category" in report
    
    def test_report_summary_fields(self, scraping_sources_path, temp_report_dir):
        """Test that summary has expected fields."""
        report = generate_accessibility_report(
            str(scraping_sources_path),
            str(temp_report_dir),
            output_formats=["json"],
        )
        
        summary = report["summary"]
        expected_fields = [
            "total_urls",
            "accessible",
            "timeout",
            "not_found",
            "forbidden",
        ]
        
        for field in expected_fields:
            assert field in summary
            assert isinstance(summary[field], int)
    
    def test_detailed_results_completeness(self, scraping_sources_path, temp_report_dir):
        """Test that each detailed result is complete."""
        report = generate_accessibility_report(
            str(scraping_sources_path),
            str(temp_report_dir),
            output_formats=["json"],
        )
        
        for result in report["detailed_results"]:
            assert "url" in result
            assert "accessible" in result
            assert "status_code" in result
            assert "error_type" in result
