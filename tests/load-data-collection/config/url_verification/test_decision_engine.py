"""Tests for decision engine and URL validation."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, patch
from scripts.scraper.config.url_verification.decision_engine import (
    ValidationDecision,
    URLValidationResult,
    validate_url,
    _make_decision,
    _suggest_alternative_urls,
    batch_validate_urls,
)
from scripts.scraper.config.url_verification.page_classifier import PageType
from scripts.scraper.config.url_verification.quality_scorer import QualityScore


class TestMakeDecision:
    """Test decision making logic."""
    
    def test_decision_keep_high_quality(self):
        """Test KEEP decision for high quality pages."""
        quality_score = QualityScore(
            job_titles_score=30,
            position_details_score=25,
            application_links_score=20,
            descriptions_score=15,
            freshness_score=10,
        )
        
        decision, suggestions = _make_decision(
            page_type=PageType.JOB_PORTAL,
            page_confidence=0.8,
            quality_score=quality_score,
            num_listings=5,
            valid_count=4,
        )
        
        assert decision == ValidationDecision.KEEP
        assert any("keep" in s.lower() for s in suggestions)
    
    def test_decision_move_not_useful_page(self):
        """Test MOVE decision for non-job pages."""
        quality_score = QualityScore()
        
        decision, suggestions = _make_decision(
            page_type=PageType.FACULTY_DIRECTORY,
            page_confidence=0.8,
            quality_score=quality_score,
            num_listings=0,
            valid_count=0,
        )
        
        assert decision == ValidationDecision.MOVE
        assert any("faculty_directory" in s.lower() for s in suggestions)
    
    def test_decision_review_marginal_quality(self):
        """Test REVIEW decision for marginal quality."""
        quality_score = QualityScore(
            job_titles_score=10,
            position_details_score=10,
            application_links_score=10,
            descriptions_score=8,
            freshness_score=5,
        )
        
        decision, suggestions = _make_decision(
            page_type=PageType.JOB_PORTAL,
            page_confidence=0.6,
            quality_score=quality_score,
            num_listings=3,
            valid_count=1,
        )
        
        assert decision == ValidationDecision.REVIEW
        assert any("review" in s.lower() for s in suggestions)
    
    def test_decision_replace_single_posting(self):
        """Test REPLACE decision for single job posting."""
        quality_score = QualityScore(
            job_titles_score=10,
            position_details_score=10,
        )
        
        decision, suggestions = _make_decision(
            page_type=PageType.SINGLE_JOB_POSTING,
            page_confidence=0.7,
            quality_score=quality_score,
            num_listings=1,
            valid_count=1,
        )
        
        assert decision == ValidationDecision.REPLACE
        assert any("single job" in s.lower() or "detail page" in s.lower() for s in suggestions)
    
    def test_decision_move_no_listings(self):
        """Test MOVE decision when no listings found."""
        quality_score = QualityScore()
        
        decision, suggestions = _make_decision(
            page_type=PageType.JOB_PORTAL,
            page_confidence=0.5,
            quality_score=quality_score,
            num_listings=0,
            valid_count=0,
        )
        
        assert decision in [ValidationDecision.MOVE, ValidationDecision.REPLACE]
        assert any("no job listings" in s.lower() for s in suggestions)


class TestSuggestAlternativeUrls:
    """Test alternative URL suggestions."""
    
    def test_suggest_for_department_page(self):
        """Test suggestions for department pages."""
        alternatives = _suggest_alternative_urls(
            "https://university.edu/economics",
            PageType.DEPARTMENT_PAGE,
        )
        
        assert len(alternatives) > 0
        assert any("career" in alt.lower() or "job" in alt.lower() for alt in alternatives)
    
    def test_suggest_for_faculty_directory(self):
        """Test suggestions for faculty directories."""
        alternatives = _suggest_alternative_urls(
            "https://university.edu/economics/faculty",
            PageType.FACULTY_DIRECTORY,
        )
        
        assert len(alternatives) > 0
        assert any("/careers" in alt or "/jobs" in alt for alt in alternatives)
    
    def test_suggest_for_single_posting(self):
        """Test suggestions for single job postings."""
        alternatives = _suggest_alternative_urls(
            "https://university.edu/careers/job-123",
            PageType.SINGLE_JOB_POSTING,
        )
        
        assert len(alternatives) > 0
        # Should suggest parent directory
        assert any("job-123" not in alt for alt in alternatives)
    
    def test_no_duplicates_in_suggestions(self):
        """Test that suggested URLs don't include original."""
        url = "https://university.edu/careers"
        alternatives = _suggest_alternative_urls(url, PageType.DEPARTMENT_PAGE)
        
        assert url not in alternatives
    
    def test_max_five_suggestions(self):
        """Test that maximum 5 suggestions are returned."""
        alternatives = _suggest_alternative_urls(
            "https://university.edu/dept",
            PageType.DEPARTMENT_PAGE,
        )
        
        assert len(alternatives) <= 5


class TestURLValidationResult:
    """Test URLValidationResult data class."""
    
    def test_validation_result_to_dict(self):
        """Test conversion to dictionary."""
        quality_score = QualityScore(
            job_titles_score=20,
            job_titles_count=3,
        )
        
        result = URLValidationResult(
            url="https://university.edu/jobs",
            decision=ValidationDecision.KEEP,
            page_type="job_portal",
            page_confidence=0.8,
            num_listings=3,
            listings_sample=[{"title": "Professor"}],
            quality_score=quality_score,
            suggestions=["Good quality source"],
            alternative_urls=[],
            title="Careers - University",
        )
        
        data = result.to_dict()
        
        assert data["url"] == "https://university.edu/jobs"
        assert data["decision"] == "keep"
        assert data["page_classification"]["type"] == "job_portal"
        assert data["content"]["num_listings"] == 3
        assert "quality" in data
        assert "metadata" in data
    
    def test_validation_result_get_summary(self):
        """Test human-readable summary."""
        quality_score = QualityScore(
            job_titles_score=30,
            job_titles_count=5,
        )
        
        result = URLValidationResult(
            url="https://university.edu/jobs",
            decision=ValidationDecision.KEEP,
            page_type="job_portal",
            page_confidence=0.9,
            num_listings=5,
            listings_sample=[],
            quality_score=quality_score,
            suggestions=["Excellent source"],
            alternative_urls=[],
        )
        
        summary = result.get_summary()
        
        assert "https://university.edu/jobs" in summary
        assert "KEEP" in summary
        assert "job_portal" in summary
        assert "Listings Found: 5" in summary


class TestValidateUrl:
    """Test full URL validation with mocked requests."""
    
    @patch("scripts.scraper.config.url_verification.decision_engine.requests.get")
    def test_validate_url_success(self, mock_get):
        """Test successful URL validation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.text = """
        <html>
            <title>Careers - University</title>
            <div class="job">
                <h3>Assistant Professor</h3>
                <p>Economics Department</p>
                <a href="/apply">Apply</a>
            </div>
        </html>
        """
        mock_response.url = "https://university.edu/careers"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = validate_url("https://university.edu/careers")
        
        assert isinstance(result, URLValidationResult)
        assert result.url == "https://university.edu/careers"
        assert result.decision in [ValidationDecision.KEEP, ValidationDecision.REVIEW, ValidationDecision.MOVE]
        assert result.num_listings >= 0
    
    @patch("scripts.scraper.config.url_verification.decision_engine.requests.get")
    def test_validate_url_request_error(self, mock_get):
        """Test URL validation with request error."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        result = validate_url("https://university.edu/invalid")
        
        assert result.decision == ValidationDecision.MOVE
        assert result.error is not None
        assert "timeout" in result.error.lower()
        assert len(result.suggestions) > 0


class TestBatchValidateUrls:
    """Test batch URL validation."""
    
    @patch("scripts.scraper.config.url_verification.decision_engine.validate_url")
    @patch("scripts.scraper.config.url_verification.decision_engine.time.sleep")
    def test_batch_validate_multiple_urls(self, mock_sleep, mock_validate):
        """Test batch validation of multiple URLs."""
        # Mock validation results
        def side_effect(url, **kwargs):
            return URLValidationResult(
                url=url,
                decision=ValidationDecision.KEEP,
                page_type="job_portal",
                page_confidence=0.8,
                num_listings=3,
                listings_sample=[],
                quality_score=QualityScore(),
                suggestions=[],
                alternative_urls=[],
            )
        
        mock_validate.side_effect = side_effect
        
        urls = [
            "https://university1.edu/jobs",
            "https://university2.edu/careers",
            "https://university3.edu/positions",
        ]
        
        results = batch_validate_urls(urls, delay=0.1)
        
        assert len(results) == 3
        assert all(url in results for url in urls)
        assert mock_validate.call_count == 3
        # Should have called sleep (n-1) times for rate limiting
        assert mock_sleep.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
