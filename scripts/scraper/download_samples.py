"""
Download sample HTML files from various sources for parsing approach analysis.

This script downloads HTML samples to compare class-based vs pattern-based extraction.
"""

import os
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup

# Base directory for samples
SAMPLES_DIR = Path("data/raw/samples")
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# User agent to avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Sample sources to download
SAMPLE_SOURCES = [
    {
        "name": "AEA_JOE",
        "url": "https://www.aeaweb.org/joe/",
        "filename": "aea_joe.html"
    },
    {
        "name": "Harvard_Economics",
        "url": "https://economics.harvard.edu/faculty/positions",
        "filename": "harvard_economics.html"
    },
    {
        "name": "MIT_Economics",
        "url": "https://economics.mit.edu/faculty/positions",
        "filename": "mit_economics.html"
    },
    {
        "name": "Stanford_Economics",
        "url": "https://economics.stanford.edu/faculty/positions",
        "filename": "stanford_economics.html"
    },
    {
        "name": "LSE_Economics",
        "url": "https://www.lse.ac.uk/economics/jobs",
        "filename": "lse_economics.html"
    }
]


def download_html(url, filename):
    """Download HTML from URL and save to file."""
    try:
        print(f"Downloading {filename} from {url}...")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        filepath = SAMPLES_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"✓ Saved {filename} ({len(response.text)} characters)")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False


def main():
    """Download all sample HTML files."""
    print("=" * 60)
    print("Downloading sample HTML files for parsing approach analysis")
    print("=" * 60)
    print()
    
    success_count = 0
    for source in SAMPLE_SOURCES:
        if download_html(source["url"], source["filename"]):
            success_count += 1
        time.sleep(2)  # Rate limiting
    
    print()
    print("=" * 60)
    print(f"Download complete: {success_count}/{len(SAMPLE_SOURCES)} files downloaded")
    print(f"Sample files saved to: {SAMPLES_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

