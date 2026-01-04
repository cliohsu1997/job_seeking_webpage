"""Tests for URL verification content validation."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from scripts.scraper.config.url_verification.content_validator import (
    extract_job_listings,
    validate_critical_fields,
    calculate_content_quality_score,
)


class TestExtractJobListings:
    """Test job listing extraction from HTML."""
    
    def test_extract_from_job_containers(self):
        """Test extraction from div containers with job class."""
        html = """
        <html>
            <div class="job-listing">
                <h3>Assistant Professor of Economics</h3>
                <p>Tenure-track position in Economics Department</p>
                <p>Deadline: December 15, 2025</p>
                <a href="/apply/123">Apply Now</a>
            </div>
            <div class="job-listing">
                <h3>Postdoctoral Fellow</h3>
                <p>Research position in Finance</p>
                <a href="mailto:hr@university.edu">Contact</a>
            </div>
        </html>
        """
        
        listings = extract_job_listings(html, "https://university.edu")
        
        assert len(listings) >= 2
        assert any("professor" in l.get("title", "").lower() for l in listings)
        assert any("postdoc" in l.get("title", "").lower() for l in listings)
    
    def test_extract_from_links(self):
        """Test extraction from job-related links."""
        html = """
        <html>
            <ul>
                <li><a href="/jobs/1">Assistant Professor of Economics</a></li>
                <li><a href="/jobs/2">Associate Professor in Finance</a></li>
                <li><a href="/jobs/3">Lecturer Position</a></li>
            </ul>
        </html>
        """
        
        listings = extract_job_listings(html, "https://university.edu")
        
        assert len(listings) >= 3
        titles = [l.get("title", "").lower() for l in listings]
        assert any("professor" in t for t in titles)
        assert any("lecturer" in t for t in titles)
    
    def test_extract_position_details(self):
        """Test extraction of position details."""
        html = """
        <div class="job">
            <h3>Assistant Professor</h3>
            <p>Tenure-track position in Economics Department</p>
            <p>Application deadline: January 15, 2026</p>
            <a href="/apply">Apply Here</a>
        </div>
        """
        
        listings = extract_job_listings(html, "https://university.edu")
        
        assert len(listings) > 0
        listing = listings[0]
        assert listing.get("title")
        # Should extract at least some details
        assert listing.get("position_type") or listing.get("department") or listing.get("deadline")
    
    def test_resolve_relative_urls(self):
        """Test URL resolution for relative links."""
        html = """
        <div class="job">
            <h3>Professor Position</h3>
            <a href="/apply/123">Apply</a>
        </div>
        """
        
        listings = extract_job_listings(html, "https://university.edu")
        
        assert len(listings) > 0
        listing = listings[0]
        url = listing.get("url", "")
        assert url.startswith("https://") or url.startswith("http://")
    
    def test_no_listings_found(self):
        """Test handling when no job listings are found."""
        html = """
        <html>
            <h1>About Our Department</h1>
            <p>We are a leading economics department...</p>
        </html>
        """
        
        listings = extract_job_listings(html, "https://university.edu")
        
        assert isinstance(listings, list)
        # May be empty or contain very few items
        assert len(listings) < 3


class TestValidateCriticalFields:
    """Test critical field validation."""
    
    def test_valid_listing_with_all_fields(self):
        """Test validation with complete listing."""
        listing = {
            "title": "Assistant Professor of Economics",
            "position_type": "tenure-track",
            "department": "economics",
            "deadline": "January 15, 2026",
            "application_link": "https://university.edu/apply",
        }
        
        is_valid, issues = validate_critical_fields(listing)
        
        assert is_valid
        assert len(issues) == 0
    
    def test_valid_listing_with_minimum_fields(self):
        """Test validation with minimum required fields."""
        listing = {
            "title": "Postdoctoral Research Fellow",
            "department": "economics",
        }
        
        is_valid, issues = validate_critical_fields(listing)
        
        assert is_valid
        assert len(issues) == 0
    
    def test_invalid_missing_title(self):
        """Test validation fails without title."""
        listing = {
            "position_type": "tenure-track",
            "department": "economics",
        }
        
        is_valid, issues = validate_critical_fields(listing)
        
        assert not is_valid
        assert any("title" in issue.lower() for issue in issues)
    
    def test_invalid_title_too_short(self):
        """Test validation fails with too-short title."""
        listing = {
            "title": "Job",
            "department": "economics",
        }
        
        is_valid, issues = validate_critical_fields(listing)
        
        assert not is_valid
        assert any("short" in issue.lower() for issue in issues)
    
    def test_invalid_generic_title(self):
        """Test validation fails with generic title."""
        listing = {
            "title": "Faculty",
            "department": "economics",
        }
        
        is_valid, issues = validate_critical_fields(listing)
        
        assert not is_valid
        assert any("generic" in issue.lower() for issue in issues)
    
    def test_invalid_no_details(self):
        """Test validation fails without any position details."""
        listing = {
            "title": "Economics Professor Position",
        }
        
        is_valid, issues = validate_critical_fields(listing)
        
        assert not is_valid
        assert any("detail" in issue.lower() for issue in issues)


class TestCalculateContentQualityScore:
    """Test content quality scoring."""
    
    def test_excellent_quality_multiple_listings(self):
        """Test scoring for high-quality page with many listings."""
        listings = [
            {
                "title": f"Assistant Professor Position {i}",
                "position_type": "tenure-track",
                "department": "economics",
                "deadline": "January 2026",
                "application_link": f"https://university.edu/apply/{i}",
                "full_text": "Full job description with requirements and qualifications. " * 10,
            }
            for i in range(1, 6)
        ]
        
        result = calculate_content_quality_score(listings)
        
        assert result["score"] >= 80
        assert result["recommendation"] == "excellent"
        assert result["action"] == "keep"
        assert result["num_listings"] == 5
    
    def test_good_quality_moderate_listings(self):
        """Test scoring for good quality page."""
        listings = [
            {
                "title": "Economics Faculty Position",
                "department": "economics",
                "deadline": "December 2025",
                "full_text": "Brief job description.",
            }
            for i in range(3)
        ]
        
        result = calculate_content_quality_score(listings)
        
        assert 40 <= result["score"] < 80
        assert result["recommendation"] in ["good", "marginal"]
    
    def test_poor_quality_few_listings(self):
        """Test scoring for poor quality page."""
        listings = [
            {
                "title": "Job Opening",
                "full_text": "",
            }
        ]
        
        result = calculate_content_quality_score(listings)
        
        assert result["score"] < 40
        assert result["recommendation"] == "poor"
        assert result["action"] == "move_to_non_accessible"
    
    def test_no_listings_zero_score(self):
        """Test scoring when no listings found."""
        listings = []
        
        result = calculate_content_quality_score(listings)
        
        assert result["score"] == 0
        assert result["recommendation"] == "poor"
        assert result["num_listings"] == 0
    
    def test_breakdown_structure(self):
        """Test that breakdown contains all expected components."""
        listings = [
            {
                "title": "Professor Position",
                "department": "economics",
                "full_text": "Job description",
            }
        ]
        
        result = calculate_content_quality_score(listings)
        
        assert "breakdown" in result
        breakdown = result["breakdown"]
        assert "job_titles" in breakdown
        assert "position_details" in breakdown
        assert "application_links" in breakdown
        assert "job_descriptions" in breakdown
        assert "freshness" in breakdown
        
        # Each component should have score and max
        for component in breakdown.values():
            assert "score" in component
            assert "max" in component


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
