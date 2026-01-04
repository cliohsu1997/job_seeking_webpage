"""
Download sample HTML files from various sources for parsing approach analysis.

This script reads from scraping_sources.json and downloads HTML samples from all
accessible URLs to compare class-based vs pattern-based extraction.

Config is flat: each entry already contains URL and metadata (type, region, etc.).
"""

import re
import requests
import time
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_loader import get_accessible_config

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


def extract_sources_from_config(entries):
    """Extract all accessible URLs from flat configuration entries."""
    sources = []

    for entry in entries:
        url = entry.get("url")
        if not url:
            continue

        entry_id = entry.get("id") or entry.get("name", "unknown")
        entry_type = entry.get("type", "unknown")

        # Create deterministic filenames for saved samples
        filename_prefix = "portal" if entry_type == "job_portal" else entry_type
        filename = f"{filename_prefix}_{sanitize_filename(entry_id)}.html"

        sources.append(
            {
                "name": entry.get("name", entry_id),
                "url": url,
                "filename": filename,
                "type": entry_type,
            }
        )

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
    config_data = get_accessible_config()
    
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

