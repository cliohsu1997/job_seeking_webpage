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


def update_scraping_sources(
    validation_results: Dict[str, URLValidationResult],
    config_path: str = "data/config/scraping_sources.json",
    backup: bool = True,
) -> Dict[str, int]:
    """Update scraping_sources.json based on validation results.
    
    This function reorganizes URLs based on validation decisions:
    - KEEP: Remains in accessible_verified
    - MOVE: Moves to accessible_unverified
    - REPLACE/REVIEW: Marked for review in accessible_unverified
    
    Args:
        validation_results: Dictionary of URL -> URLValidationResult
        config_path: Path to scraping_sources.json
        backup: Whether to create a backup before updating
        
    Returns:
        Dictionary with update statistics
    """
    import json
    import shutil
    from pathlib import Path
    from datetime import datetime
    
    config_path_obj = Path(config_path)
    
    # Create backup
    if backup:
        backup_path = config_path_obj.with_stem(f"{config_path_obj.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy(config_path_obj, backup_path)
        logger.info(f"Backup created: {backup_path}")
    
    # Load current config
    with open(config_path_obj, 'r') as f:
        config = json.load(f)
    
    # Initialize result tracking
    stats = {
        "total_validated": len(validation_results),
        "kept_in_verified": 0,
        "moved_to_unverified": 0,
        "moved_to_potential": 0,
        "errors": 0,
    }
    
    # Process each validation result
    verified_list = config.get("accessible_verified", [])
    unverified_list = config.get("accessible_unverified", [])
    
    # Create URL to entry mapping for easy lookup
    verified_map = {entry["url"]: entry for entry in verified_list}
    unverified_map = {entry["url"]: entry for entry in unverified_list}
    
    for url, result in validation_results.items():
        # Find the entry in current config
        entry = verified_map.get(url) or unverified_map.get(url)
        
        if not entry:
            logger.warning(f"URL {url} not found in current config")
            stats["errors"] += 1
            continue
        
        # Add validation metadata to entry
        entry["validation"] = {
            "decision": result.decision.value,
            "page_type": result.page_type,
            "page_confidence": round(result.page_confidence, 3),
            "num_listings": result.num_listings,
            "quality_score": result.quality_score.total_score,
            "suggestions": result.suggestions[:2],  # Top 2 suggestions
            "timestamp": datetime.now().isoformat(),
        }
        
        # Remove from old location
        if url in verified_map:
            verified_list = [e for e in verified_list if e["url"] != url]
        if url in unverified_map:
            unverified_list = [e for e in unverified_list if e["url"] != url]
        
        # Place in new location based on decision
        if result.decision == ValidationDecision.KEEP:
            verified_list.append(entry)
            stats["kept_in_verified"] += 1
        elif result.decision == ValidationDecision.MOVE:
            unverified_list.append(entry)
            stats["moved_to_unverified"] += 1
        elif result.decision in [ValidationDecision.REVIEW, ValidationDecision.REPLACE]:
            # Add to unverified with review flag
            entry["needs_review"] = True
            entry["alternative_urls"] = result.alternative_urls
            unverified_list.append(entry)
            stats["moved_to_unverified"] += 1
    
    # Update config
    config["accessible_verified"] = verified_list
    config["accessible_unverified"] = unverified_list
    
    # Save updated config
    with open(config_path_obj, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Config updated: {stats['kept_in_verified']} kept, {stats['moved_to_unverified']} moved")
    return stats


def generate_validation_report(
    validation_results: Dict[str, URLValidationResult],
    output_dir: str = "data/config/url_verification",
) -> None:
    """Generate comprehensive validation report in multiple formats.
    
    Args:
        validation_results: Dictionary of URL -> URLValidationResult
        output_dir: Directory to save report files
    """
    import json
    from pathlib import Path
    from datetime import datetime
    from collections import defaultdict
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Organize results by decision
    by_decision = defaultdict(list)
    by_page_type = defaultdict(list)
    quality_stats = {
        "excellent": [],  # >= 80
        "good": [],       # 60-79
        "marginal": [],   # 40-59
        "poor": [],       # < 40
    }
    
    json_results = []
    
    for url, result in validation_results.items():
        by_decision[result.decision.value].append(result)
        by_page_type[result.page_type].append(result)
        
        # Quality categorization
        score = result.quality_score.total_score
        if score >= 80:
            quality_stats["excellent"].append(result)
        elif score >= 60:
            quality_stats["good"].append(result)
        elif score >= 40:
            quality_stats["marginal"].append(result)
        else:
            quality_stats["poor"].append(result)
        
        json_results.append(result.to_dict())
    
    # Save JSON report
    json_report_path = output_path / f"verification_results_latest.json"
    with open(json_report_path, 'w') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    logger.info(f"JSON report saved: {json_report_path}")
    
    # Generate markdown report
    md_lines = [
        "# URL Validation Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary Statistics",
        f"- Total URLs Validated: {len(validation_results)}",
        f"- KEEP: {len(by_decision.get('keep', []))} URLs",
        f"- MOVE: {len(by_decision.get('move', []))} URLs",
        f"- REPLACE: {len(by_decision.get('replace', []))} URLs",
        f"- REVIEW: {len(by_decision.get('review', []))} URLs",
        "",
        "## Quality Distribution",
        f"- Excellent (80+): {len(quality_stats['excellent'])} URLs",
        f"- Good (60-79): {len(quality_stats['good'])} URLs",
        f"- Marginal (40-59): {len(quality_stats['marginal'])} URLs",
        f"- Poor (<40): {len(quality_stats['poor'])} URLs",
        "",
        "## By Page Type",
    ]
    
    for page_type, results in sorted(by_page_type.items()):
        md_lines.append(f"- {page_type}: {len(results)} URLs")
    
    md_lines.extend([
        "",
        "## URLs to KEEP (in accessible_verified)",
        "High quality sources - maintained in accessible section",
        "",
    ])
    
    for result in by_decision.get("keep", []):
        md_lines.append(f"- {result.url}")
        md_lines.append(f"  - Quality: {result.quality_score.total_score}/100")
        md_lines.append(f"  - Listings: {result.num_listings}")
        md_lines.append("")
    
    md_lines.extend([
        "",
        "## URLs to MOVE (to accessible_unverified)",
        "Lower quality or needs review - moved out of verified section",
        "",
    ])
    
    for result in by_decision.get("move", []):
        md_lines.append(f"- {result.url}")
        md_lines.append(f"  - Reason: {result.suggestions[0] if result.suggestions else 'Low quality'}")
        md_lines.append(f"  - Quality: {result.quality_score.total_score}/100")
        md_lines.append("")
    
    # Save markdown report
    md_report_path = output_path / f"verification_report_latest.md"
    with open(md_report_path, 'w') as f:
        f.write("\n".join(md_lines))
    logger.info(f"Markdown report saved: {md_report_path}")
    
    # Print summary
    logger.info("=" * 60)
    logger.info("VALIDATION REPORT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total URLs Validated: {len(validation_results)}")
    logger.info(f"KEEP: {len(by_decision.get('keep', []))} | MOVE: {len(by_decision.get('move', []))} | REPLACE: {len(by_decision.get('replace', []))} | REVIEW: {len(by_decision.get('review', []))}")
    logger.info(f"Quality: Excellent {len(quality_stats['excellent'])} | Good {len(quality_stats['good'])} | Marginal {len(quality_stats['marginal'])} | Poor {len(quality_stats['poor'])}")
    logger.info("=" * 60)
