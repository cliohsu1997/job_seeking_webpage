"""Replacement Engine - Orchestrate URL replacement workflow.

This module provides the core logic for finding, validating, and executing
URL replacements for problematic sources in scraping_sources.json.

Workflow:
1. Find problematic URLs (from validation results)
2. Discover replacement candidates (using url_discovery)
3. Validate each candidate (using decision_engine)
4. Select best replacement (highest quality score)
5. Update configuration
6. Generate reports
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

# Add parent directories to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraper.config.url_replacement.url_discovery import (
    discover_urls,
    suggest_replacement_urls,
    get_predefined_urls,
)
from scripts.scraper.config.url_verification.decision_engine import (
    validate_url,
    URLValidationResult,
    ValidationDecision,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ReplacementCandidate:
    """A candidate replacement URL with validation results."""
    original_url: str
    original_reason: str
    candidate_url: str
    discovery_method: str  # "predefined", "common_path", "subdomain"
    validation_result: Optional[Dict] = None
    quality_score: int = 0
    is_valid: bool = False
    selected: bool = False


@dataclass
class ReplacementJob:
    """A complete replacement job for one problematic URL."""
    original_url: str
    original_reason: str
    original_quality_score: int
    institution_name: str
    candidates: List[ReplacementCandidate]
    best_candidate: Optional[ReplacementCandidate] = None
    status: str = "pending"  # pending, completed, failed
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


def extract_institution_name(url: str) -> str:
    """Extract institution name from URL.
    
    Args:
        url: URL to extract from
        
    Returns:
        Institution name (best guess)
    """
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Remove common prefixes
    domain = domain.replace('www.', '').replace('economics.', '').replace('business.', '')
    
    # Take first part before .edu or .com
    name = domain.split('.')[0]
    
    # Capitalize
    return name.capitalize()


def find_replacements_for_url(
    url: str,
    reason: str,
    institution_name: Optional[str] = None,
    timeout: int = 10,
) -> ReplacementJob:
    """Find replacement candidates for a single problematic URL.
    
    Args:
        url: Problematic URL to replace
        reason: Reason why URL needs replacement
        institution_name: Name of institution (optional, will be inferred if not provided)
        timeout: Request timeout for discovery
        
    Returns:
        ReplacementJob with all candidates
    """
    if not institution_name:
        institution_name = extract_institution_name(url)
    
    logger.info(f"Finding replacements for {institution_name}: {url}")
    logger.info(f"Reason: {reason}")
    
    candidates = []
    
    # Method 1: Check predefined URLs
    predefined = get_predefined_urls(url)
    if predefined:
        logger.info(f"  Found {len(predefined)} predefined URLs")
        for pred_url in predefined:
            candidates.append(ReplacementCandidate(
                original_url=url,
                original_reason=reason,
                candidate_url=pred_url,
                discovery_method="predefined",
            ))
    
    # Method 2: Use discover_urls to find alternatives
    suggested = discover_urls(url, test_paths=True, test_subdomains=True, timeout=timeout)
    logger.info(f"  Discovered {len(suggested)} alternatives")
    
    for sugg_url in suggested:
        # Avoid duplicates
        if not any(c.candidate_url == sugg_url for c in candidates):
            candidates.append(ReplacementCandidate(
                original_url=url,
                original_reason=reason,
                candidate_url=sugg_url,
                discovery_method="discovered",
            ))
    
    job = ReplacementJob(
        original_url=url,
        original_reason=reason,
        original_quality_score=0,
        institution_name=institution_name,
        candidates=candidates,
    )
    
    logger.info(f"  Total candidates found: {len(candidates)}")
    return job


def validate_replacement(
    candidate: ReplacementCandidate,
    min_quality_score: int = 60,
    timeout: int = 10,
) -> ReplacementCandidate:
    """Validate a replacement candidate URL.
    
    Args:
        candidate: Replacement candidate to validate
        min_quality_score: Minimum quality score to be considered valid
        timeout: Request timeout
        
    Returns:
        Updated candidate with validation results
    """
    logger.info(f"  Validating: {candidate.candidate_url}")
    
    try:
        result = validate_url(candidate.candidate_url, timeout=timeout)
        
        # Convert result to dict
        result_dict = {
            "url": result.url,
            "decision": result.decision.value,
            "page_classification": {
                "type": result.page_type,
                "confidence": result.page_confidence,
            },
            "content": {
                "num_listings": result.num_listings,
            },
            "quality": {
                "total_score": result.quality_score.total_score,
                "recommendation": result.quality_score.recommendation,
            },
            "suggestions": result.suggestions,
        }
        
        candidate.validation_result = result_dict
        candidate.quality_score = result.quality_score.total_score
        candidate.is_valid = (
            result.decision == ValidationDecision.KEEP and
            result.quality_score.total_score >= min_quality_score
        )
        
        if candidate.is_valid:
            logger.info(f"    ✓ Valid (score: {candidate.quality_score})")
        else:
            logger.info(f"    ✗ Invalid (score: {candidate.quality_score}, decision: {result.decision})")
        
    except Exception as e:
        logger.error(f"    ✗ Validation error: {e}")
        candidate.validation_result = {"error": str(e)}
        candidate.is_valid = False
    
    return candidate


def create_replacement_job(
    url: str,
    reason: str,
    institution_name: Optional[str] = None,
    min_quality_score: int = 60,
    timeout: int = 10,
) -> ReplacementJob:
    """Complete workflow to create a replacement job with validated candidates.
    
    Args:
        url: Problematic URL to replace
        reason: Reason for replacement
        institution_name: Institution name (optional)
        min_quality_score: Minimum quality score for valid replacement
        timeout: Request timeout
        
    Returns:
        Complete ReplacementJob with validated candidates
    """
    # Step 1: Find candidates
    job = find_replacements_for_url(url, reason, institution_name, timeout)
    
    if not job.candidates:
        logger.warning(f"No candidates found for {url}")
        job.status = "failed"
        return job
    
    # Step 2: Validate all candidates
    logger.info(f"Validating {len(job.candidates)} candidates...")
    for i, candidate in enumerate(job.candidates, 1):
        logger.info(f"  [{i}/{len(job.candidates)}] {candidate.candidate_url}")
        job.candidates[i-1] = validate_replacement(candidate, min_quality_score, timeout)
    
    # Step 3: Select best candidate
    valid_candidates = [c for c in job.candidates if c.is_valid]
    
    if valid_candidates:
        # Sort by quality score (descending)
        best = max(valid_candidates, key=lambda c: c.quality_score)
        best.selected = True
        job.best_candidate = best
        job.status = "completed"
        logger.info(f"✓ Best replacement found: {best.candidate_url} (score: {best.quality_score})")
    else:
        job.status = "failed"
        logger.warning(f"✗ No valid replacements found for {url}")
    
    return job


def execute_replacements(
    problematic_urls: List[Dict[str, str]],
    min_quality_score: int = 60,
    timeout: int = 10,
    max_urls: Optional[int] = None,
) -> List[ReplacementJob]:
    """Execute replacement workflow for multiple problematic URLs.
    
    Args:
        problematic_urls: List of dicts with 'url' and 'reason' keys
        min_quality_score: Minimum quality score for valid replacement
        timeout: Request timeout
        max_urls: Maximum number of URLs to process (for testing)
        
    Returns:
        List of ReplacementJobs
    """
    if max_urls:
        problematic_urls = problematic_urls[:max_urls]
    
    logger.info(f"Starting replacement workflow for {len(problematic_urls)} URLs")
    logger.info("=" * 70)
    
    jobs = []
    for i, url_info in enumerate(problematic_urls, 1):
        url = url_info['url']
        reason = url_info.get('reason', 'unknown')
        
        logger.info(f"\n[{i}/{len(problematic_urls)}] Processing: {url}")
        
        try:
            job = create_replacement_job(url, reason, None, min_quality_score, timeout)
            jobs.append(job)
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            # Create failed job
            job = ReplacementJob(
                original_url=url,
                original_reason=reason,
                original_quality_score=0,
                institution_name=extract_institution_name(url),
                candidates=[],
                status="error",
            )
            jobs.append(job)
    
    logger.info("\n" + "=" * 70)
    logger.info("REPLACEMENT WORKFLOW COMPLETE")
    logger.info("=" * 70)
    
    # Summary
    completed = sum(1 for j in jobs if j.status == "completed")
    failed = sum(1 for j in jobs if j.status == "failed")
    error = sum(1 for j in jobs if j.status == "error")
    
    logger.info(f"Total URLs processed: {len(jobs)}")
    logger.info(f"  Completed: {completed} ({completed/len(jobs)*100:.1f}%)")
    logger.info(f"  Failed: {failed} ({failed/len(jobs)*100:.1f}%)")
    logger.info(f"  Error: {error} ({error/len(jobs)*100:.1f}%)")
    
    return jobs


def save_candidates(
    jobs: List[ReplacementJob],
    output_path: str = "data/config/url_replacement/candidates.json",
) -> None:
    """Save replacement candidates to JSON file.
    
    Args:
        jobs: List of ReplacementJobs
        output_path: Path to save candidates
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to serializable format
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_jobs": len(jobs),
        "completed": sum(1 for j in jobs if j.status == "completed"),
        "failed": sum(1 for j in jobs if j.status == "failed"),
        "jobs": [
            {
                "original_url": job.original_url,
                "original_reason": job.original_reason,
                "institution": job.institution_name,
                "status": job.status,
                "candidates": [
                    {
                        "url": c.candidate_url,
                        "method": c.discovery_method,
                        "quality_score": c.quality_score,
                        "is_valid": c.is_valid,
                        "selected": c.selected,
                        "validation": c.validation_result,
                    }
                    for c in job.candidates
                ],
                "best_candidate": {
                    "url": job.best_candidate.candidate_url,
                    "method": job.best_candidate.discovery_method,
                    "quality_score": job.best_candidate.quality_score,
                } if job.best_candidate else None,
            }
            for job in jobs
        ]
    }
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"\nCandidates saved to: {output_path}")


def generate_replacement_report(
    jobs: List[ReplacementJob],
    output_path: str = "data/config/url_replacement/replacement_report.md",
) -> None:
    """Generate comprehensive replacement report in Markdown format.
    
    Args:
        jobs: List of ReplacementJobs
        output_path: Path to save report
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    completed_jobs = [j for j in jobs if j.status == "completed"]
    failed_jobs = [j for j in jobs if j.status in ["failed", "error"]]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# URL Replacement Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Total URLs Processed**: {len(jobs)}\n")
        f.write(f"- **Successfully Replaced**: {len(completed_jobs)} ({len(completed_jobs)/len(jobs)*100:.1f}%)\n")
        f.write(f"- **Failed to Replace**: {len(failed_jobs)} ({len(failed_jobs)/len(jobs)*100:.1f}%)\n")
        
        if completed_jobs:
            avg_quality = sum(j.best_candidate.quality_score for j in completed_jobs) / len(completed_jobs)
            f.write(f"- **Average Quality Score**: {avg_quality:.1f}/100\n")
        
        f.write("\n")
        
        # Completed Replacements
        if completed_jobs:
            f.write("## ✓ Successful Replacements\n\n")
            f.write("| Institution | Old URL | Reason | New URL | Quality Score | Method |\n")
            f.write("|-------------|---------|--------|---------|---------------|--------|\n")
            
            for job in completed_jobs:
                best = job.best_candidate
                f.write(f"| {job.institution_name} | {job.original_url} | {job.original_reason} | ")
                f.write(f"{best.candidate_url} | {best.quality_score}/100 | {best.discovery_method} |\n")
            
            f.write("\n")
        
        # Failed Replacements
        if failed_jobs:
            f.write("## ✗ Failed Replacements\n\n")
            f.write("| Institution | URL | Reason | Status | Candidates Tested |\n")
            f.write("|-------------|-----|--------|--------|-------------------|\n")
            
            for job in failed_jobs:
                f.write(f"| {job.institution_name} | {job.original_url} | {job.original_reason} | ")
                f.write(f"{job.status} | {len(job.candidates)} |\n")
            
            f.write("\n")
        
        # Detailed Results
        f.write("## Detailed Results\n\n")
        
        for i, job in enumerate(jobs, 1):
            f.write(f"### {i}. {job.institution_name}\n\n")
            f.write(f"**Original URL**: {job.original_url}  \n")
            f.write(f"**Reason**: {job.original_reason}  \n")
            f.write(f"**Status**: {job.status}  \n")
            f.write(f"**Candidates Found**: {len(job.candidates)}  \n")
            
            if job.best_candidate:
                f.write(f"**Selected Replacement**: {job.best_candidate.candidate_url}  \n")
                f.write(f"**Quality Score**: {job.best_candidate.quality_score}/100  \n")
                f.write(f"**Discovery Method**: {job.best_candidate.discovery_method}  \n")
            
            if job.candidates:
                f.write("\n**All Candidates**:\n\n")
                for j, candidate in enumerate(job.candidates, 1):
                    status = "✓ SELECTED" if candidate.selected else ("✓ Valid" if candidate.is_valid else "✗ Invalid")
                    f.write(f"{j}. {candidate.candidate_url}\n")
                    f.write(f"   - Method: {candidate.discovery_method}\n")
                    f.write(f"   - Quality: {candidate.quality_score}/100\n")
                    f.write(f"   - Status: {status}\n")
            
            f.write("\n---\n\n")
    
    logger.info(f"Report saved to: {output_path}")


def validate_and_finalize(
    jobs: List[ReplacementJob],
    config_path: str = "data/config/scraping_sources.json",
    backup: bool = True,
) -> None:
    """Finalize replacements by updating scraping_sources.json.
    
    Args:
        jobs: List of ReplacementJobs (only completed ones will be applied)
        config_path: Path to scraping_sources.json
        backup: Whether to create backup before updating
    """
    config_path = Path(config_path)
    
    # Create backup
    if backup:
        backup_path = config_path.parent / f"scraping_sources_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import shutil
        shutil.copy(config_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Apply replacements
    completed_jobs = [j for j in jobs if j.status == "completed" and j.best_candidate]
    
    logger.info(f"\nApplying {len(completed_jobs)} replacements to config...")
    
    for job in completed_jobs:
        old_url = job.original_url
        new_url = job.best_candidate.candidate_url
        
        # Find and replace in accessible_verified
        for section in ["accessible_verified", "accessible_unverified"]:
            for i, entry in enumerate(config.get(section, [])):
                if entry["url"] == old_url:
                    # Update URL and add metadata
                    config[section][i]["url"] = new_url
                    config[section][i]["replaced_from"] = old_url
                    config[section][i]["replacement_reason"] = job.original_reason
                    config[section][i]["replacement_date"] = datetime.now().isoformat()
                    config[section][i]["quality_score"] = job.best_candidate.quality_score
                    
                    logger.info(f"  ✓ Replaced {job.institution_name}: {old_url} → {new_url}")
                    break
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"\n✓ Config updated: {config_path}")
    logger.info(f"  {len(completed_jobs)} URLs replaced")


if __name__ == "__main__":
    # Example usage
    print("Replacement Engine - URL Replacement Workflow")
    print("=" * 70)
    print("\nThis module provides functions to:")
    print("  1. Find replacement candidates for problematic URLs")
    print("  2. Validate each candidate")
    print("  3. Select best replacement")
    print("  4. Update configuration")
    print("  5. Generate reports")
    print("\nUse execute_replacements() to run the full workflow.")
