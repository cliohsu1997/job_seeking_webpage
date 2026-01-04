"""Validate the 30 predefined replacement URLs and generate replacement report.

This script validates only the predefined URLs to avoid network issues with discovery.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Setup paths
sys.path.insert(0, str(Path.cwd()))

import scripts.scraper.config.url_replacement.replacement_engine as engine
from scripts.scraper.config.url_verification.decision_engine import validate_url

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Validate predefined URLs and create replacement jobs."""
    print("=" * 70)
    print("VALIDATING PREDEFINED REPLACEMENT URLs")
    print("=" * 70)
    print()
    
    # Load the predefined test results
    results_path = Path("data/config/url_replacement/predefined_test_results.json")
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    print(f"Total problematic URLs: {data['summary']['total']}")
    print(f"Total replacement URLs to validate: {data['summary']['total_replacements']}")
    print()
    
    # Create replacement jobs manually
    jobs = []
    
    for i, prob_url_data in enumerate(data['problematic_urls'], 1):
        url = prob_url_data['url']
        reason = prob_url_data['reason']
        
        # Find predefined results
        pred_result = next((r for r in data['predefined_results'] if r['original'] == url), None)
        if not pred_result or not pred_result['has_predefined']:
            continue
        
        print(f"[{i}/{data['summary']['total']}] Processing: {url}")
        institution = engine.extract_institution_name(url)
        
        # Create job
        job = engine.ReplacementJob(
            original_url=url,
            original_reason=reason,
            original_quality_score=0,
            institution_name=institution,
            candidates=[],
            timestamp=datetime.now().isoformat(),
        )
        
        # Add predefined URLs as candidates
        print(f"  Validating {len(pred_result['urls'])} predefined URLs...")
        for j, pred_url in enumerate(pred_result['urls'], 1):
            candidate = engine.ReplacementCandidate(
                original_url=url,
                original_reason=reason,
                candidate_url=pred_url,
                discovery_method="predefined",
            )
            
            print(f"    [{j}/{len(pred_result['urls'])}] {pred_url}")
            
            # Validate
            try:
                validated = engine.validate_replacement(candidate, min_quality_score=60, timeout=10)
                job.candidates.append(validated)
            except Exception as e:
                logger.error(f"      Error validating {pred_url}: {e}")
                candidate.is_valid = False
                candidate.validation_result = {"error": str(e)}
                job.candidates.append(candidate)
        
        # Select best candidate
        valid_candidates = [c for c in job.candidates if c.is_valid]
        if valid_candidates:
            best = max(valid_candidates, key=lambda c: c.quality_score)
            best.selected = True
            job.best_candidate = best
            job.status = "completed"
            print(f"  ✓ Best: {best.candidate_url} (score: {best.quality_score})")
        else:
            job.status = "failed"
            print(f"  ✗ No valid replacements found")
        
        jobs.append(job)
        print()
    
    # Summary
    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    
    completed = sum(1 for j in jobs if j.status == "completed")
    failed = sum(1 for j in jobs if j.status == "failed")
    
    print(f"\nResults:")
    print(f"  Completed: {completed}/{len(jobs)} ({completed/len(jobs)*100:.1f}%)")
    print(f"  Failed: {failed}/{len(jobs)}")
    
    if completed > 0:
        avg_quality = sum(j.best_candidate.quality_score for j in jobs if j.best_candidate) / completed
        print(f"  Average Quality Score: {avg_quality:.1f}/100")
    
    # Save results
    print("\nSaving results...")
    engine.save_candidates(jobs)
    engine.generate_replacement_report(jobs)
    
    print("\nFiles created:")
    print("  - data/config/url_replacement/candidates.json")
    print("  - data/config/url_replacement/replacement_report.md")
    
    # Ask about updating config
    if completed > 0:
        print("\n" + "=" * 70)
        print(f"✓ Found {completed} valid replacements!")
        print("=" * 70)
        print("\nDo you want to update scraping_sources.json with these replacements?")
        print("(This will create a backup first)")
        response = input("\nType 'yes' to proceed: ")
        
        if response.lower() == 'yes':
            print("\nUpdating configuration...")
            engine.validate_and_finalize(jobs, backup=True)
            print("\n✓ Configuration updated!")
            print("  Backup saved in data/config/")
        else:
            print("\n⊘ Configuration not updated.")
            print("  Review the reports and update manually if needed.")
    
    print("\n✓ Validation complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user.")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise
