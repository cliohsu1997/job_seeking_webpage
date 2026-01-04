"""Find replacement URLs for problematic universities."""

import sys
import logging
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from config.url_discovery import suggest_replacement_urls, get_predefined_urls, discover_urls

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Map problematic URLs to institution names
PROBLEMATIC_URLS = [
    ('Princeton', 'https://economics.princeton.edu/', 'https://www.princeton.edu/'),
    ('UPenn', 'https://economics.upenn.edu/', 'https://www.upenn.edu/'),
    ('Columbia', 'https://economics.columbia.edu/', 'https://www.columbia.edu/'),
    ('NYU', 'https://economics.nyu.edu/', 'https://www.nyu.edu/'),
    ('Wisconsin-Madison', 'https://economics.wisc.edu/', 'https://www.wisc.edu/'),
    ('Michigan', 'https://economics.umich.edu/', 'https://www.umich.edu/'),
]

print("=" * 70)
print("URL REPLACEMENT DISCOVERY FOR PROBLEMATIC UNIVERSITIES")
print("=" * 70)
print()

all_alternatives = {}

for institution, bad_url, main_url in PROBLEMATIC_URLS:
    print(f"\n{institution}:")
    print(f"  ✗ Bad URL: {bad_url}")
    print(f"  Main domain: {main_url}")
    print(f"  Discovering alternatives...")
    
    # Discover URLs from main domain
    alternatives = discover_urls(main_url, test_paths=True, test_subdomains=False, timeout=3)
    
    if alternatives:
        print(f"  ✓ Found {len(alternatives)} accessible alternatives:")
        for alt in alternatives[:5]:
            print(f"    - {alt}")
        all_alternatives[institution] = alternatives
    else:
        print(f"  ✗ No accessible alternatives found")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total institutions: {len(PROBLEMATIC_URLS)}")
print(f"With alternatives: {len(all_alternatives)}")

# Save alternatives to JSON
import json
from datetime import datetime

output = {
    "timestamp": datetime.now().isoformat(),
    "results": {
        institution: {
            "alternatives": alternatives,
            "status": "has_alternatives" if alternatives else "no_alternatives"
        }
        for institution, alternatives in all_alternatives.items()
    }
}

output_path = Path("data/config/url_verification/discovery_results.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")
