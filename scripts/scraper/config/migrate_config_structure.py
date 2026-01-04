"""Script to restructure scraping_sources.json into three categories."""

import json
from pathlib import Path

config_path = Path("data/config/scraping_sources.json")

# Read current config
with open(config_path) as f:
    config = json.load(f)

# Restructure: currently "accessible" becomes "accessible_verified"
# "non_accessible" becomes "non_verified" (not yet verified for accessibility)
# Create empty "potential_links" for future exploration

new_config = {
    "accessible_verified": config.get("accessible", []),  # Currently accessible and working
    "accessible_unverified": config.get("non_accessible", []),  # Accessible but content not yet verified
    "potential_links": [],  # New URLs to check for accessibility
}

# Write new config
with open(config_path, "w") as f:
    json.dump(new_config, f, indent=2, ensure_ascii=False)

print("✅ Config restructured successfully!")
print(f"  • accessible_verified: {len(new_config['accessible_verified'])} URLs")
print(f"  • accessible_unverified: {len(new_config['accessible_unverified'])} URLs")
print(f"  • potential_links: {len(new_config['potential_links'])} URLs")
