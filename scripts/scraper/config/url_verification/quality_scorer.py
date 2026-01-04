"""Quality Scorer - Calculate quality scores for URL verification.

This module provides data structures and functions for calculating
and managing quality scores for verified URLs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """Quality score breakdown for a verified URL.
    
    Total score: 0-100 points
    - Job Titles Found: 30 points
    - Position Details: 25 points
    - Application Links: 20 points
    - Job Descriptions: 15 points
    - Freshness: 10 points
    """
    
    # Overall score
    total_score: int = 0
    max_score: int = 100
    
    # Individual component scores
    job_titles_score: int = 0
    job_titles_max: int = 30
    job_titles_count: int = 0
    
    position_details_score: int = 0
    position_details_max: int = 25
    avg_fields_per_job: float = 0.0
    
    application_links_score: int = 0
    application_links_max: int = 20
    apply_links_count: int = 0
    emails_count: int = 0
    
    descriptions_score: int = 0
    descriptions_max: int = 15
    avg_description_length: int = 0
    
    freshness_score: int = 0
    freshness_max: int = 10
    recent_count: int = 0
    
    # Quality assessment
    recommendation: str = "unknown"  # excellent, good, marginal, poor
    action: str = "review"  # keep, review, move_to_non_accessible
    
    # Additional metadata
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate total score after initialization."""
        self.total_score = (
            self.job_titles_score
            + self.position_details_score
            + self.application_links_score
            + self.descriptions_score
            + self.freshness_score
        )
        
        # Determine recommendation if not set
        if self.recommendation == "unknown":
            if self.total_score >= 80:
                self.recommendation = "excellent"
                self.action = "keep"
            elif self.total_score >= 60:
                self.recommendation = "good"
                self.action = "keep"
            elif self.total_score >= 40:
                self.recommendation = "marginal"
                self.action = "review"
            else:
                self.recommendation = "poor"
                self.action = "move_to_non_accessible"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "total_score": self.total_score,
            "max_score": self.max_score,
            "recommendation": self.recommendation,
            "action": self.action,
            "breakdown": {
                "job_titles": {
                    "score": self.job_titles_score,
                    "max": self.job_titles_max,
                    "count": self.job_titles_count,
                },
                "position_details": {
                    "score": self.position_details_score,
                    "max": self.position_details_max,
                    "avg_fields": round(self.avg_fields_per_job, 2),
                },
                "application_links": {
                    "score": self.application_links_score,
                    "max": self.application_links_max,
                    "apply_links": self.apply_links_count,
                    "emails": self.emails_count,
                },
                "descriptions": {
                    "score": self.descriptions_score,
                    "max": self.descriptions_max,
                    "avg_length": self.avg_description_length,
                },
                "freshness": {
                    "score": self.freshness_score,
                    "max": self.freshness_max,
                    "recent_count": self.recent_count,
                },
            },
            "issues": self.issues,
            "warnings": self.warnings,
        }
    
    @classmethod
    def from_breakdown(cls, breakdown: Dict) -> "QualityScore":
        """Create QualityScore from breakdown dictionary.
        
        Args:
            breakdown: Dictionary with score breakdown (from calculate_content_quality_score)
            
        Returns:
            QualityScore instance
        """
        job_titles = breakdown.get("job_titles", {})
        position_details = breakdown.get("position_details", {})
        application_links = breakdown.get("application_links", {})
        descriptions = breakdown.get("job_descriptions", {})
        freshness = breakdown.get("freshness", {})
        
        return cls(
            job_titles_score=job_titles.get("score", 0),
            job_titles_count=job_titles.get("count", 0),
            position_details_score=position_details.get("score", 0),
            avg_fields_per_job=position_details.get("avg_fields", 0.0),
            application_links_score=application_links.get("score", 0),
            apply_links_count=application_links.get("apply_links", 0),
            emails_count=application_links.get("emails", 0),
            descriptions_score=descriptions.get("score", 0),
            avg_description_length=descriptions.get("avg_length", 0),
            freshness_score=freshness.get("score", 0),
            recent_count=freshness.get("recent_count", 0),
        )
    
    def get_summary(self) -> str:
        """Get human-readable summary of the quality score."""
        lines = [
            f"Quality Score: {self.total_score}/{self.max_score} ({self.recommendation})",
            f"Action: {self.action}",
            "",
            "Breakdown:",
            f"  • Job Titles: {self.job_titles_score}/{self.job_titles_max} ({self.job_titles_count} found)",
            f"  • Position Details: {self.position_details_score}/{self.position_details_max} (avg {self.avg_fields_per_job:.1f} fields)",
            f"  • Application Links: {self.application_links_score}/{self.application_links_max} ({self.apply_links_count} links, {self.emails_count} emails)",
            f"  • Descriptions: {self.descriptions_score}/{self.descriptions_max} (avg {self.avg_description_length} chars)",
            f"  • Freshness: {self.freshness_score}/{self.freshness_max} ({self.recent_count} recent)",
        ]
        
        if self.issues:
            lines.append("")
            lines.append("Issues:")
            for issue in self.issues:
                lines.append(f"  ⚠ {issue}")
        
        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  ℹ {warning}")
        
        return "\n".join(lines)


def calculate_quality_breakdown(
    num_listings: int,
    avg_fields: float,
    apply_links: int,
    emails: int,
    avg_description_length: int,
    recent_count: int,
) -> QualityScore:
    """Calculate quality score from individual metrics.
    
    Args:
        num_listings: Number of job listings found
        avg_fields: Average number of fields per listing
        apply_links: Number of application links found
        emails: Number of email contacts found
        avg_description_length: Average length of job descriptions
        recent_count: Number of recent postings
        
    Returns:
        QualityScore instance
    """
    # Calculate job titles score (30 pts)
    if num_listings >= 5:
        job_titles_score = 30
    elif num_listings >= 3:
        job_titles_score = 20
    elif num_listings >= 1:
        job_titles_score = 10
    else:
        job_titles_score = 0
    
    # Calculate position details score (25 pts)
    if avg_fields >= 2.5:
        position_details_score = 25
    elif avg_fields >= 1.5:
        position_details_score = 18
    elif avg_fields >= 0.5:
        position_details_score = 10
    else:
        position_details_score = 0
    
    # Calculate application links score (20 pts)
    if num_listings > 0:
        if apply_links >= num_listings * 0.5:
            application_links_score = 20
        elif emails >= num_listings * 0.5:
            application_links_score = 10
        elif apply_links > 0 or emails > 0:
            application_links_score = 5
        else:
            application_links_score = 0
    else:
        application_links_score = 0
    
    # Calculate descriptions score (15 pts)
    if avg_description_length >= 200:
        descriptions_score = 15
    elif avg_description_length >= 50:
        descriptions_score = 8
    else:
        descriptions_score = 0
    
    # Calculate freshness score (10 pts)
    if num_listings > 0:
        if recent_count >= num_listings * 0.5:
            freshness_score = 10
        elif recent_count >= num_listings * 0.25:
            freshness_score = 5
        else:
            freshness_score = 0
    else:
        freshness_score = 0
    
    return QualityScore(
        job_titles_score=job_titles_score,
        job_titles_count=num_listings,
        position_details_score=position_details_score,
        avg_fields_per_job=avg_fields,
        application_links_score=application_links_score,
        apply_links_count=apply_links,
        emails_count=emails,
        descriptions_score=descriptions_score,
        avg_description_length=avg_description_length,
        freshness_score=freshness_score,
        recent_count=recent_count,
    )
