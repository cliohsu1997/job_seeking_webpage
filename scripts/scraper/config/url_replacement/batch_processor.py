"""Batch processor for URL validation and configuration updates.

This module provides CLI tools to:
1. Validate multiple URLs with progress tracking
2. Update scraping_sources.json with validation results
3. Generate comprehensive reports
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
import sys

from url_verification.decision_engine import (
    batch_validate_urls,
    generate_validation_report,
    update_scraping_sources,
    URLValidationResult,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_urls_from_config(
    config_path: str = "data/config/scraping_sources.json",
    section: str = "accessible_verified",
) -> List[str]:
    """Load URLs from scraping_sources.json.
    
    Args:
        config_path: Path to config file
        section: Section to load from (accessible_verified, accessible_unverified, etc.)
        
    Returns:
        List of URLs
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    urls = [entry["url"] for entry in config.get(section, [])]
    logger.info(f"Loaded {len(urls)} URLs from {section}")
    return urls


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a text file (one URL per line).
    
    Args:
        file_path: Path to text file with URLs
        
    Returns:
        List of URLs
    """
    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    logger.info(f"Loaded {len(urls)} URLs from {file_path}")
    return urls


def validate_urls_batch(
    urls: List[str],
    timeout: int = 10,
    delay: float = 1.0,
) -> dict:
    """Validate a batch of URLs.
    
    Args:
        urls: List of URLs to validate
        timeout: Request timeout in seconds
        delay: Delay between requests in seconds
        
    Returns:
        Dictionary of validation results
    """
    logger.info(f"Starting validation of {len(urls)} URLs...")
    logger.info(f"Timeout: {timeout}s, Delay: {delay}s between requests")
    
    results = batch_validate_urls(urls, timeout=timeout, delay=delay)
    
    logger.info(f"Validation complete: {len(results)} results")
    return results


def process_and_update(
    validation_results: dict,
    config_path: str = "data/config/scraping_sources.json",
    report_dir: str = "data/config/url_verification",
    update_config: bool = False,
) -> None:
    """Process validation results, generate reports, optionally update config.
    
    Args:
        validation_results: Dictionary of URL -> URLValidationResult
        config_path: Path to scraping_sources.json
        report_dir: Directory for reports
        update_config: Whether to update the config file
    """
    # Generate report
    logger.info("Generating validation reports...")
    generate_validation_report(validation_results, report_dir)
    
    # Count by decision
    decisions = {}
    for result in validation_results.values():
        decision = result.decision.value
        decisions[decision] = decisions.get(decision, 0) + 1
    
    logger.info("Decision Summary:")
    for decision, count in sorted(decisions.items()):
        logger.info(f"  {decision.upper()}: {count}")
    
    # Optionally update config
    if update_config:
        logger.info("Updating scraping_sources.json...")
        stats = update_scraping_sources(validation_results, config_path=config_path)
        logger.info("Update Statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")


def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch URL validation processor")
    parser.add_argument(
        "--validate",
        type=str,
        help="Validate URLs from file (one per line) or 'config:section' to load from scraping_sources.json",
        required=True,
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--update-config",
        action="store_true",
        help="Update scraping_sources.json with results"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="data/config/scraping_sources.json",
        help="Path to scraping_sources.json"
    )
    parser.add_argument(
        "--report-dir",
        type=str,
        default="data/config/url_verification",
        help="Directory for validation reports"
    )
    
    args = parser.parse_args()
    
    # Load URLs
    if args.validate.startswith("config:"):
        section = args.validate.split(":", 1)[1]
        urls = load_urls_from_config(args.config, section)
    else:
        urls = load_urls_from_file(args.validate)
    
    if not urls:
        logger.error("No URLs to validate")
        sys.exit(1)
    
    # Validate
    results = validate_urls_batch(urls, timeout=args.timeout, delay=args.delay)
    
    # Process and report
    process_and_update(
        results,
        config_path=args.config,
        report_dir=args.report_dir,
        update_config=args.update_config,
    )
    
    logger.info("Done!")


if __name__ == "__main__":
    main()
