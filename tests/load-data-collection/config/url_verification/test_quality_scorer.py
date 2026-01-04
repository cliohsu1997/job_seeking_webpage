"""Tests for quality scoring system."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from scripts.scraper.config.url_verification.quality_scorer import (
    QualityScore,
    calculate_quality_breakdown,
)


class TestQualityScore:
    """Test QualityScore data class."""
    
    def test_quality_score_initialization(self):
        """Test basic initialization and total score calculation."""
        score = QualityScore(
            job_titles_score=30,
            position_details_score=25,
            application_links_score=20,
            descriptions_score=15,
            freshness_score=10,
        )
        
        assert score.total_score == 100
        assert score.max_score == 100
        assert score.recommendation == "excellent"
        assert score.action == "keep"
    
    def test_quality_score_recommendation_excellent(self):
        """Test recommendation for excellent scores."""
        score = QualityScore(
            job_titles_score=28,
            position_details_score=23,
            application_links_score=18,
            descriptions_score=13,
            freshness_score=8,
        )
        
        assert score.total_score == 90
        assert score.recommendation == "excellent"
        assert score.action == "keep"
    
    def test_quality_score_recommendation_good(self):
        """Test recommendation for good scores."""
        score = QualityScore(
            job_titles_score=20,
            position_details_score=18,
            application_links_score=10,
            descriptions_score=8,
            freshness_score=5,
        )
        
        assert score.total_score == 61
        assert score.recommendation == "good"
        assert score.action == "keep"
    
    def test_quality_score_recommendation_marginal(self):
        """Test recommendation for marginal scores."""
        score = QualityScore(
            job_titles_score=10,
            position_details_score=10,
            application_links_score=10,
            descriptions_score=8,
            freshness_score=5,
        )
        
        assert score.total_score == 43
        assert score.recommendation == "marginal"
        assert score.action == "review"
    
    def test_quality_score_recommendation_poor(self):
        """Test recommendation for poor scores."""
        score = QualityScore(
            job_titles_score=10,
            position_details_score=10,
            application_links_score=0,
            descriptions_score=0,
            freshness_score=0,
        )
        
        assert score.total_score == 20
        assert score.recommendation == "poor"
        assert score.action == "move_to_non_accessible"
    
    def test_quality_score_to_dict(self):
        """Test conversion to dictionary."""
        score = QualityScore(
            job_titles_score=30,
            job_titles_count=5,
            position_details_score=25,
            avg_fields_per_job=2.5,
            application_links_score=20,
            apply_links_count=4,
            emails_count=3,
        )
        
        result = score.to_dict()
        
        assert result["total_score"] == 75
        assert result["recommendation"] == "good"
        assert "breakdown" in result
        assert result["breakdown"]["job_titles"]["count"] == 5
        assert result["breakdown"]["position_details"]["avg_fields"] == 2.5
    
    def test_quality_score_from_breakdown(self):
        """Test creation from breakdown dictionary."""
        breakdown = {
            "job_titles": {"score": 30, "count": 6},
            "position_details": {"score": 25, "avg_fields": 2.8},
            "application_links": {"score": 20, "apply_links": 5, "emails": 2},
            "job_descriptions": {"score": 15, "avg_length": 250},
            "freshness": {"score": 10, "recent_count": 4},
        }
        
        score = QualityScore.from_breakdown(breakdown)
        
        assert score.total_score == 100
        assert score.job_titles_count == 6
        assert score.avg_fields_per_job == 2.8
        assert score.apply_links_count == 5
        assert score.recommendation == "excellent"
    
    def test_quality_score_get_summary(self):
        """Test human-readable summary generation."""
        score = QualityScore(
            job_titles_score=20,
            job_titles_count=3,
            position_details_score=18,
            avg_fields_per_job=1.7,
            issues=["Low freshness score"],
            warnings=["Missing some application links"],
        )
        
        summary = score.get_summary()
        
        assert "Quality Score:" in summary
        assert "3 found" in summary
        assert "Issues:" in summary
        assert "Warnings:" in summary


class TestCalculateQualityBreakdown:
    """Test quality breakdown calculation."""
    
    def test_calculate_excellent_quality(self):
        """Test calculation for excellent quality metrics."""
        score = calculate_quality_breakdown(
            num_listings=6,
            avg_fields=2.8,
            apply_links=5,
            emails=3,
            avg_description_length=250,
            recent_count=4,
        )
        
        assert score.total_score >= 80
        assert score.job_titles_score == 30  # 5+ listings
        assert score.position_details_score == 25  # avg_fields >= 2.5
        assert score.application_links_score == 20  # apply_links >= 50%
        assert score.descriptions_score == 15  # avg_length >= 200
        assert score.freshness_score == 10  # recent_count >= 50%
    
    def test_calculate_good_quality(self):
        """Test calculation for good quality metrics."""
        score = calculate_quality_breakdown(
            num_listings=4,
            avg_fields=1.8,
            apply_links=2,
            emails=1,
            avg_description_length=100,
            recent_count=1,
        )
        
        assert 40 <= score.total_score < 80
        assert score.job_titles_score == 20  # 3-4 listings
        assert score.position_details_score == 18  # 1.5 <= avg_fields < 2.5
        assert score.application_links_score == 20  # apply_links >= 50%
        assert score.descriptions_score == 8  # 50 <= avg_length < 200
    
    def test_calculate_marginal_quality(self):
        """Test calculation for marginal quality metrics."""
        score = calculate_quality_breakdown(
            num_listings=2,
            avg_fields=0.8,
            apply_links=0,
            emails=1,
            avg_description_length=60,
            recent_count=0,
        )
        
        assert score.total_score < 60
        assert score.job_titles_score == 10  # 1-2 listings
        assert score.position_details_score == 10  # 0.5 <= avg_fields < 1.5
        assert score.application_links_score == 10  # emails >= 50%
    
    def test_calculate_poor_quality(self):
        """Test calculation for poor quality metrics."""
        score = calculate_quality_breakdown(
            num_listings=0,
            avg_fields=0.0,
            apply_links=0,
            emails=0,
            avg_description_length=0,
            recent_count=0,
        )
        
        assert score.total_score == 0
        assert score.recommendation == "poor"
        assert score.action == "move_to_non_accessible"
    
    def test_calculate_with_emails_only(self):
        """Test calculation when only emails available (no apply links)."""
        score = calculate_quality_breakdown(
            num_listings=3,
            avg_fields=1.5,
            apply_links=0,
            emails=2,
            avg_description_length=100,
            recent_count=1,
        )
        
        # Should get 10 points for emails (not full 20 for apply links)
        assert score.application_links_score == 10
        assert score.emails_count == 2
        assert score.apply_links_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
