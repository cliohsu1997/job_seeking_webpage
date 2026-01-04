"""Decision Engine - Make validation decisions for URLs based on multiple criteria.

This module combines page classification, content validation, and quality scoring
to make final decisions about URL validity.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time
import requests
import logging

from .page_classifier import classify_page_type, PageType, is_useful_for_jobs
from .content_validator import (
    extract_job_listings,
    validate_critical_fields,
    calculate_content_quality_score,
)
from .quality_scorer import QualityScore

logger = logging.getLogger(__name__)


class ValidationDecision(Enum):
    """Final decision for URL validation."""
    
    KEEP = "keep"  # Keep in accessible section
    MOVE = "move"  # Move to non_accessible section
    REPLACE = "replace"  # Suggest replacement URL
    REVIEW = "review"  # Manual review needed


@dataclass
class URLValidationResult:
    """Complete validation result for a URL."""
    
    url: str
    decision: ValidationDecision
    
    # Page classification
    page_type: str
    page_confidence: float
    
    # Content extraction
    num_listings: int
    listings_sample: List[Dict]
    
    # Quality scoring
    quality_score: QualityScore
    
    # Suggestions
    suggestions: List[str]
    alternative_urls: List[str]
    
    # Metadata
    title: str = ""
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "url": self.url,
            "decision": self.decision.value,
            "page_classification": {
                "type": self.page_type,
                "confidence": round(self.page_confidence, 3),
            },
            "content": {
                "num_listings": self.num_listings,
                "sample_listings": self.listings_sample[:3],  # First 3 only
            },
            "quality": self.quality_score.to_dict(),
            "suggestions": self.suggestions,
            "alternative_urls": self.alternative_urls,
            "metadata": {
                "title": self.title,
                "error": self.error,
            },
        }
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        lines = [
            f"URL: {self.url}",
            f"Decision: {self.decision.value.upper()}",
            f"Page Type: {self.page_type} (confidence: {self.page_confidence:.2f})",
            f"Listings Found: {self.num_listings}",
            "",
            self.quality_score.get_summary(),
        ]
        
        if self.suggestions:
            lines.append("")
            lines.append("Suggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")
        
        if self.alternative_urls:
            lines.append("")
            lines.append("Alternative URLs:")
            for alt_url in self.alternative_urls:
                lines.append(f"  → {alt_url}")
        
        if self.error:
            lines.append("")
            lines.append(f"Error: {self.error}")
        
        return "\n".join(lines)


def validate_url(
    url: str,
    timeout: int = 10,
    user_agent: str = "Mozilla/5.0",
) -> URLValidationResult:
    """Validate a URL and make a decision.
    
    This is the main entry point for URL verification. It:
    1. Fetches the URL content
    2. Classifies the page type
    3. Extracts job listings
    4. Calculates quality score
    5. Makes a final decision
    
    Args:
        url: The URL to validate
        timeout: Request timeout in seconds
        user_agent: User agent string
        
    Returns:
        URLValidationResult with complete analysis
    """
    logger.info(f"Validating URL: {url}")
    
    # Step 1: Fetch content
    try:
        headers = {"User-Agent": user_agent}
        response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
        response.raise_for_status()
        html_content = response.text
        title = response.url  # Final URL after redirects
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return URLValidationResult(
            url=url,
            decision=ValidationDecision.MOVE,
            page_type="error",
            page_confidence=1.0,
            num_listings=0,
            listings_sample=[],
            quality_score=QualityScore(recommendation="poor", action="move_to_non_accessible"),
            suggestions=[f"URL not accessible: {str(e)}"],
            alternative_urls=[],
            error=str(e),
        )
    
    # Step 2: Classify page type
    page_type, confidence, classification_details = classify_page_type(
        html_content=html_content,
        url=url,
    )
    
    title = classification_details.get("title", "")
    
    # Early return for non-job pages
    if page_type in [PageType.ERROR_PAGE, PageType.FACULTY_DIRECTORY, PageType.DEPARTMENT_PAGE]:
        return URLValidationResult(
            url=url,
            decision=ValidationDecision.MOVE,
            page_type=page_type.value,
            page_confidence=confidence,
            num_listings=0,
            listings_sample=[],
            quality_score=QualityScore(recommendation="poor", action="move_to_non_accessible"),
            suggestions=[f"Page is classified as {page_type.value}, not a job portal"],
            alternative_urls=_suggest_alternative_urls(url, page_type),
            title=title,
        )
    
    # Step 3: Extract job listings
    listings = extract_job_listings(html_content, base_url=url)
    
    # Step 4: Calculate quality score
    quality_result = calculate_content_quality_score(listings, html_content)
    quality_score = QualityScore.from_breakdown(quality_result["breakdown"])
    quality_score.issues = []
    quality_score.warnings = []
    
    # Validate each listing
    valid_count = 0
    for listing in listings:
        is_valid, issues = validate_critical_fields(listing)
        if is_valid:
            valid_count += 1
        else:
            quality_score.warnings.extend(issues)
    
    if valid_count < len(listings) * 0.5:
        quality_score.issues.append(f"Only {valid_count}/{len(listings)} listings have complete data")
    
    # Step 5: Make decision
    decision, suggestions = _make_decision(
        page_type=page_type,
        page_confidence=confidence,
        quality_score=quality_score,
        num_listings=len(listings),
        valid_count=valid_count,
    )
    
    # Generate alternative URLs if needed
    alternative_urls = []
    if decision in [ValidationDecision.MOVE, ValidationDecision.REPLACE]:
        alternative_urls = _suggest_alternative_urls(url, page_type)
    
    return URLValidationResult(
        url=url,
        decision=decision,
        page_type=page_type.value,
        page_confidence=confidence,
        num_listings=len(listings),
        listings_sample=listings[:5],  # First 5 listings
        quality_score=quality_score,
        suggestions=suggestions,
        alternative_urls=alternative_urls,
        title=title,
    )


def _make_decision(
    page_type: PageType,
    page_confidence: float,
    quality_score: QualityScore,
    num_listings: int,
    valid_count: int,
) -> Tuple[ValidationDecision, List[str]]:
    """Make final decision based on all criteria.
    
    Decision tree:
    1. If page is not useful for jobs → MOVE
    2. If quality score >= 60 and valid_count >= 50% → KEEP
    3. If quality score >= 40 → REVIEW
    4. Otherwise → MOVE or REPLACE
    
    Args:
        page_type: Classified page type
        page_confidence: Classification confidence
        quality_score: Quality score object
        num_listings: Total number of listings found
        valid_count: Number of valid listings
        
    Returns:
        Tuple of (decision, list of suggestions)
    """
    suggestions = []
    
    # Rule 1: Page type must be useful
    if not is_useful_for_jobs(page_type, page_confidence):
        return ValidationDecision.MOVE, [
            f"Page is classified as {page_type.value}, not suitable for job scraping",
            "Consider finding the careers/jobs page for this institution",
        ]
    
    # Rule 2: High quality score → KEEP
    if quality_score.total_score >= 60 and valid_count >= num_listings * 0.5:
        suggestions.append("High quality source - keep in accessible section")
        return ValidationDecision.KEEP, suggestions
    
    # Rule 3: Good quality but needs attention → REVIEW
    if quality_score.total_score >= 40:
        suggestions.append("Marginal quality - manual review recommended")
        
        if num_listings < 3:
            suggestions.append("Consider if this URL is a listing page or a detail page")
        
        if valid_count < num_listings * 0.5:
            suggestions.append(f"Only {valid_count}/{num_listings} listings have complete data")
        
        return ValidationDecision.REVIEW, suggestions
    
    # Rule 4: Low quality → MOVE or REPLACE
    suggestions.append("Low quality source - move to non_accessible section")
    
    if num_listings == 0:
        suggestions.append("No job listings found on this page")
        return ValidationDecision.REPLACE, suggestions
    elif num_listings == 1 and page_type == PageType.SINGLE_JOB_POSTING:
        suggestions.append("This appears to be a single job detail page, not a listing page")
        suggestions.append("Try to find the main jobs/careers page instead")
        return ValidationDecision.REPLACE, suggestions
    else:
        suggestions.append("Quality score too low - insufficient extractable data")
        return ValidationDecision.MOVE, suggestions


def _suggest_alternative_urls(url: str, page_type: PageType) -> List[str]:
    """Suggest alternative URLs based on the current URL and page type.
    
    Args:
        url: The current URL
        page_type: The classified page type
        
    Returns:
        List of suggested alternative URLs to try
    """
    from urllib.parse import urlparse, urljoin
    
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    alternatives = []
    
    # Common career page paths
    career_paths = [
        "/careers",
        "/careers/faculty",
        "/jobs",
        "/employment",
        "/opportunities",
        "/about/careers",
        "/about/employment",
        "/faculty-positions",
        "/open-positions",
    ]
    
    # If it's a department or faculty page, suggest career paths
    if page_type in [PageType.DEPARTMENT_PAGE, PageType.FACULTY_DIRECTORY]:
        for path in career_paths:
            alt_url = urljoin(base_url, path)
            if alt_url != url:
                alternatives.append(alt_url)
    
    # If it's a single job posting, try to go up a level
    if page_type == PageType.SINGLE_JOB_POSTING:
        # Remove the last path segment
        parts = parsed.path.rstrip("/").split("/")
        if len(parts) > 1:
            parent_path = "/".join(parts[:-1])
            alternatives.append(urljoin(base_url, parent_path))
    
    return alternatives[:5]  # Return max 5 suggestions


def batch_validate_urls(
    urls: List[str],
    timeout: int = 10,
    delay: float = 1.0,
) -> Dict[str, URLValidationResult]:
    """Validate multiple URLs with rate limiting.
    
    Args:
        urls: List of URLs to validate
        timeout: Request timeout in seconds
        delay: Delay between requests in seconds
        
    Returns:
        Dictionary mapping URLs to validation results
    """
    results = {}
    
    for i, url in enumerate(urls):
        logger.info(f"Validating {i+1}/{len(urls)}: {url}")
        
        result = validate_url(url, timeout=timeout)
        results[url] = result
        
        # Rate limiting
        if i < len(urls) - 1:
            time.sleep(delay)
    
    return results
