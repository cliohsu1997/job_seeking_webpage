"""Test pilot replacement workflow with limited network calls.

This version focuses on the predefined URLs first to verify the workflow works.
"""

import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test the workflow with predefined URLs only."""
    print("=" * 70)
    print("TEST: PREDEFINED URLs for Pilot Universities")
    print("=" * 70)
    print()
    
    # Load verification results
    results_path = Path("data/config/url_verification/verification_results_latest.json")
    
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Get first 10 problematic URLs
    problematic = []
    for result in results:
        if result.get('decision') == 'move':
            url = result['url']
            reason = result.get('suggestions', ['unknown'])[0] if result.get('suggestions') else 'unknown'
            problematic.append({
                'url': url,
                'reason': str(reason)[:100],
            })
            if len(problematic) >= 10:
                break
    
    print(f"Found {len(problematic)} problematic URLs:\n")
    for i, p in enumerate(problematic, 1):
        print(f"{i}. {p['url']}")
        print(f"   Reason: {p['reason']}")
    
    print("\n" + "=" * 70)
    print("Checking predefined replacement URLs...")
    print("=" * 70)
    print()
    
    # Import after printing to avoid network calls during import
    import sys
    sys.path.insert(0, str(Path.cwd()))
    
    from scripts.scraper.config.url_replacement.url_discovery import get_predefined_urls
    
    results_summary = []
    
    for p in problematic:
        url = p['url']
        print(f"\n{url}")
        
        predefined = get_predefined_urls(url)
        if predefined:
            print(f"  ✓ Found {len(predefined)} predefined URLs:")
            for pred_url in predefined:
                print(f"    - {pred_url}")
            results_summary.append({
                'original': url,
                'has_predefined': True,
                'count': len(predefined),
                'urls': predefined
            })
        else:
            print(f"  ✗ No predefined URLs found")
            results_summary.append({
                'original': url,
                'has_predefined': False,
                'count': 0,
                'urls': []
            })
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    with_predefined = sum(1 for r in results_summary if r['has_predefined'])
    total_replacements = sum(r['count'] for r in results_summary)
    
    print(f"\nTotal problematic URLs: {len(problematic)}")
    print(f"With predefined replacements: {with_predefined} ({with_predefined/len(problematic)*100:.1f}%)")
    print(f"Total replacement URLs found: {total_replacements}")
    
    # Save results
    output = {
        'timestamp': '2026-01-04T15:50:00',
        'problematic_urls': problematic,
        'predefined_results': results_summary,
        'summary': {
            'total': len(problematic),
            'with_predefined': with_predefined,
            'total_replacements': total_replacements
        }
    }
    
    output_path = Path("data/config/url_replacement/predefined_test_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    print("\n✓ Test complete!")
    print("\nNext step: Run full validation on these predefined URLs")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
