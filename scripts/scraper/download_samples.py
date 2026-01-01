"""
Download sample HTML files from various sources for parsing approach analysis.

This script reads from scraping_sources.json and downloads HTML samples from all
accessible URLs to compare class-based vs pattern-based extraction.
"""

import re
import requests
import time
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_loader import get_config

# Base directory for samples
SAMPLES_DIR = Path("data/raw/samples")
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# User agent to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def sanitize_filename(name):
    """Convert a name to a safe filename."""
    # Remove special characters and replace spaces with underscores
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name.lower()


def extract_sources_from_config(config_data):
    """Extract all accessible URLs from configuration (assumes config already filtered to accessible only)."""
    sources = []
    
    # Extract from job portals
    if "job_portals" in config_data:
        for portal_key, portal_data in config_data["job_portals"].items():
            if "url" in portal_data:
                name = sanitize_filename(portal_data.get("name", portal_key))
                filename = f"portal_{name}.html"
                sources.append({
                    "name": portal_data.get("name", portal_key),
                    "url": portal_data["url"],
                    "filename": filename,
                    "type": "portal"
                })
    
    # Extract from regions
    if "regions" in config_data:
        regions = config_data["regions"]
        
        # United States universities
        if "united_states" in regions and "universities" in regions["united_states"]:
            for uni in regions["united_states"]["universities"]:
                uni_name = sanitize_filename(uni["name"])
                if "departments" in uni:
                    for dept in uni["departments"]:
                        if "url" in dept:
                            dept_name = sanitize_filename(dept["name"])
                            filename = f"us_{uni_name}_{dept_name}.html"
                            sources.append({
                                "name": f"{uni['name']} - {dept['name']}",
                                "url": dept["url"],
                                "filename": filename,
                                "type": "university"
                            })
        
        # United States research institutes
        if "united_states" in regions and "research_institutes" in regions["united_states"]:
            for inst in regions["united_states"]["research_institutes"]:
                if "url" in inst:
                    name = sanitize_filename(inst["name"])
                    filename = f"us_institute_{name}.html"
                    sources.append({
                        "name": inst["name"],
                        "url": inst["url"],
                        "filename": filename,
                        "type": "institute"
                    })
        
        # Mainland China (added support)
        if "mainland_china" in regions and "universities" in regions["mainland_china"]:
            for uni in regions["mainland_china"]["universities"]:
                uni_name = sanitize_filename(uni["name"])
                if "departments" in uni:
                    for dept in uni["departments"]:
                        if "url" in dept:
                            dept_name = sanitize_filename(dept["name"])
                            filename = f"cn_{uni_name}_{dept_name}.html"
                            sources.append({
                                "name": f"{uni['name']} - {dept['name']}",
                                "url": dept["url"],
                                "filename": filename,
                                "type": "university"
                            })
        
        # Other countries
        if "other_countries" in regions and "countries" in regions["other_countries"]:
            for country_key, country_data in regions["other_countries"]["countries"].items():
                # Universities
                if "universities" in country_data:
                    for uni in country_data["universities"]:
                        uni_name = sanitize_filename(uni["name"])
                        if "departments" in uni:
                            for dept in uni["departments"]:
                                if "url" in dept:
                                    dept_name = sanitize_filename(dept["name"])
                                    filename = f"{country_key}_{uni_name}_{dept_name}.html"
                                    sources.append({
                                        "name": f"{uni['name']} - {dept['name']}",
                                        "url": dept["url"],
                                        "filename": filename,
                                        "type": "university"
                                    })
                
                # Research institutes
                if "research_institutes" in country_data:
                    for inst in country_data["research_institutes"]:
                        if "url" in inst:
                            name = sanitize_filename(inst["name"])
                            filename = f"{country_key}_institute_{name}.html"
                            sources.append({
                                "name": inst["name"],
                                "url": inst["url"],
                                "filename": filename,
                                "type": "institute"
                            })
    
    return sources


def download_html(url, filename, name):
    """Download HTML from URL and save to file."""
    try:
        print(f"Downloading {name}...")
        print(f"  URL: {url}")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        filepath = SAMPLES_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        size_kb = len(response.text) / 1024
        print(f"  ✓ Saved {filename} ({size_kb:.1f} KB)")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed: {e}")
        return False


def main():
    """Download all sample HTML files from scraping_sources.json."""
    print("=" * 70)
    print("Downloading sample HTML files for parsing approach analysis")
    print("=" * 70)
    print()
    
    # Load configuration (accessible URLs only for efficiency)
    config_data = get_config(accessible_only=True)
    
    # Extract all accessible sources
    sources = extract_sources_from_config(config_data)
    
    if not sources:
        print("✗ No accessible sources found in configuration file.")
        return
    
    print(f"Found {len(sources)} accessible sources to download")
    print()
    
    # Download all sources
    success_count = 0
    failed_sources = []
    
    for i, source in enumerate(sources, 1):
        print(f"[{i}/{len(sources)}] {source['type'].upper()}: {source['name']}")
        if download_html(source["url"], source["filename"], source["name"]):
            success_count += 1
        else:
            failed_sources.append(source)
        time.sleep(2)  # Rate limiting
        print()
    
    # Summary
    print("=" * 70)
    print(f"Download Summary:")
    print(f"  ✓ Success: {success_count}/{len(sources)} files downloaded")
    if failed_sources:
        print(f"  ✗ Failed: {len(failed_sources)} files")
        print("\nFailed sources:")
        for source in failed_sources:
            print(f"  - {source['name']}: {source['url']}")
    print(f"\nSample files saved to: {SAMPLES_DIR.absolute()}")
    print("=" * 70)


if __name__ == "__main__":
    main()

