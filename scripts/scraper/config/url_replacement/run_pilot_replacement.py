"""Run pilot URL replacement workflow for 10 test universities.

This script:
1. Loads problematic URLs from validation results
2. Executes replacement workflow
3. Generates reports
4. Updates configuration (optional)
"""

import json
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from replacement_engine import (
    execute_replacements,
    save_candidates,
    generate_replacement_report,
    validate_and_finalize,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_problematic_urls(
    results_path: str = "data/config/url_verification/verification_results_latest.json",
    max_urls: int = 10,
) -> list:
    """Load problematic URLs from validation results.
    
    Args:
        results_path: Path to verification results JSON
        max_urls: Maximum number of URLs to process (for pilot)
        
    Returns:
        List of dicts with 'url' and 'reason' keys
    """
    results_path = Path(results_path)
    
    if not results_path.exists():
        logger.error(f"Verification results not found: {results_path}")
        return []
    
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Filter for URLs with decision='move'
    problematic = []
    for result in results:
        if result.get('decision') == 'move':
            url = result['url']
            
            # Extract reason from suggestions or quality
            reason = "unknown"
            if result.get('suggestions'):
                reason = result['suggestions'][0] if isinstance(result['suggestions'], list) else str(result['suggestions'])
            elif result.get('quality', {}).get('recommendation'):
                reason = result['quality']['recommendation']
            
            problematic.append({
                'url': url,
                'reason': reason[:100],  # Truncate long reasons
            })
    
    logger.info(f"Found {len(problematic)} problematic URLs")
    
    # Limit to max_urls for pilot
    if max_urls:
        problematic = problematic[:max_urls]
        logger.info(f"Limited to {len(problematic)} URLs for pilot test")
    
    return problematic


def main():
    """Run pilot URL replacement workflow."""
    print("=" * 70)
    print("PILOT URL REPLACEMENT WORKFLOW")
    print("=" * 70)
    print()
    
    # Step 1: Load problematic URLs
    logger.info("Step 1: Loading problematic URLs...")
    problematic_urls = load_problematic_urls(max_urls=10)
    
    if not problematic_urls:
        logger.error("No problematic URLs found. Exiting.")
        return
    
    print(f"\nProblematic URLs to replace ({len(problematic_urls)}):")
    for i, url_info in enumerate(problematic_urls, 1):
        print(f"  {i}. {url_info['url']}")
        print(f"     Reason: {url_info['reason']}")
    
    print()
    input("Press Enter to start replacement workflow (Ctrl+C to cancel)...")
    print()
    
    # Step 2: Execute replacement workflow
    logger.info("\nStep 2: Executing replacement workflow...")
    jobs = execute_replacements(
        problematic_urls,
        min_quality_score=60,
        timeout=10,
    )
    
    # Step 3: Save candidates
    logger.info("\nStep 3: Saving candidates...")
    save_candidates(jobs)
    
    # Step 4: Generate report
    logger.info("\nStep 4: Generating report...")
    generate_replacement_report(jobs)
    
    # Step 5: Optionally update config
    print("\n" + "=" * 70)
    print("PILOT REPLACEMENT COMPLETE")
    print("=" * 70)
    
    completed = sum(1 for j in jobs if j.status == "completed")
    print(f"\nSuccessfully found replacements for {completed}/{len(jobs)} URLs")
    print("\nReports saved:")
    print("  - data/config/url_replacement/candidates.json")
    print("  - data/config/url_replacement/replacement_report.md")
    
    if completed > 0:
        print("\nDo you want to update scraping_sources.json with these replacements?")
        response = input("Type 'yes' to proceed, anything else to skip: ")
        
        if response.lower() == 'yes':
            logger.info("\nStep 5: Updating configuration...")
            validate_and_finalize(jobs, backup=True)
            print("\n✓ Configuration updated!")
            print("  Backup created in data/config/")
        else:
            print("\n⊘ Configuration not updated.")
            print("  You can manually review the results and apply them later.")
    
    print("\nPilot replacement workflow complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
