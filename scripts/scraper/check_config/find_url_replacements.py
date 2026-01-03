"""
Helper script to find and test common URL patterns for university job pages.
This script tests common patterns and reports which ones work.
"""

import requests
import json
from pathlib import Path
from typing import List, Tuple, Optional
import time

# Common URL patterns to try
COMMON_PATTERNS = [
    "jobs.{domain}",
    "careers.{domain}",
    "facultyjobs.{domain}",
    "hiring.{domain}",
    "hr.{domain}",
    "employment.{domain}",
    "jobs.{base_domain}",
    "careers.{base_domain}",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TIMEOUT = 10


def get_base_domain(url: str) -> str:
    """Extract base domain from URL."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc
    # Remove www. if present
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def get_domain_parts(domain: str) -> Tuple[str, str]:
    """Split domain into base and full domain."""
    parts = domain.split(".")
    if len(parts) >= 2:
        base = ".".join(parts[-2:])  # e.g., "princeton.edu"
        return base, domain
    return domain, domain


def test_url(url: str) -> Tuple[bool, int, str]:
    """Test if URL is accessible."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return True, response.status_code, response.url
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)


def find_working_urls(original_url: str, university_name: str) -> List[Tuple[str, int, str]]:
    """Try common URL patterns and return working ones."""
    print(f"[CHECKPOINT] Extracting domain from: {original_url}")
    domain = get_base_domain(original_url)
    base_domain, full_domain = get_domain_parts(domain)
    print(f"[CHECKPOINT] Base domain: {base_domain}")
    
    working_urls = []
    patterns_to_try = [
        f"https://jobs.{base_domain}",
        f"https://careers.{base_domain}",
        f"https://facultyjobs.{base_domain}",
        f"https://hiring.{base_domain}",
        f"https://hr.{base_domain}",
        f"https://employment.{base_domain}",
        f"https://www.{base_domain}/jobs",
        f"https://www.{base_domain}/careers",
        f"https://www.{base_domain}/employment",
        f"https://www.{base_domain}/faculty/jobs",
        f"https://www.{base_domain}/human-resources",
    ]
    
    print(f"[CHECKPOINT] Testing {len(patterns_to_try)} URL patterns for {university_name} ({domain}):")
    for idx, pattern_url in enumerate(patterns_to_try, 1):
        print(f"  [Testing {idx}/{len(patterns_to_try)}] {pattern_url}...", end=" ", flush=True)
        is_accessible, status_code, info = test_url(pattern_url)
        if is_accessible and status_code == 200:
            print(f"✓ (Status: {status_code})")
            working_urls.append((pattern_url, status_code, info))
        elif is_accessible and status_code in [301, 302, 303, 307, 308]:
            print(f"→ Redirects to: {info}")
            working_urls.append((pattern_url, status_code, info))
        else:
            print(f"✗")
        time.sleep(0.5)  # Rate limiting
    
    print(f"[CHECKPOINT] Found {len(working_urls)} working URLs for {university_name}")
    return working_urls


def main():
    """Test URL patterns for problematic universities."""
    print("[CHECKPOINT] Starting URL replacement finder script...")
    
    # List of problematic universities from verification output
    problematic = [
        ("Princeton University", "https://puwebp.princeton.edu/AcadHire/"),
        ("University of Pennsylvania", "https://wd1.myworkday.com/upenn/d/inst/1$9925/9925$315.htm"),
        ("Columbia University", "https://opportunities.columbia.edu/"),
        ("NYU", "https://apply.interfolio.com/"),
        ("University of Michigan", "https://careers.umich.edu/"),
        ("University of Wisconsin-Madison", "https://jobs.wisc.edu/"),
        ("Penn State", "https://psu.wd1.myworkdayjobs.com/PSU_Academic"),
        ("Ohio State University", "https://osujoblinks.com/"),
        ("University of Virginia", "https://uva.wd1.myworkdayjobs.com/UVAJobs"),
        ("Rice University", "https://jobs.rice.edu/"),
    ]
    
    print(f"[CHECKPOINT] Found {len(problematic)} universities to test")
    print("=" * 80)
    print("Testing Common URL Patterns for Problematic Universities")
    print("=" * 80)
    
    results = {}
    for idx, (uni_name, original_url) in enumerate(problematic, 1):
        print(f"\n[CHECKPOINT] Processing {idx}/{len(problematic)}: {uni_name}")
        working = find_working_urls(original_url, uni_name)
        if working:
            results[uni_name] = working[0][0]  # Take first working URL
            print(f"[CHECKPOINT] Found working URL for {uni_name}: {working[0][0]}")
        else:
            print(f"[CHECKPOINT] No working URL found for {uni_name}")
        time.sleep(1)
    
    print("\n[CHECKPOINT] Generating summary...")
    print("\n" + "=" * 80)
    print("SUMMARY - Suggested Replacement URLs:")
    print("=" * 80)
    for uni_name, new_url in results.items():
        print(f"{uni_name}: {new_url}")
    print(f"\n[CHECKPOINT] Script completed. Found {len(results)} replacement URLs.")


if __name__ == "__main__":
    main()

