"""
Verify URLs in scraping_sources.json before scraping.

This script checks if all URLs are accessible and optionally validates
that they contain job posting content.
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse

# Configuration - paths relative to script location (scripts/scraper/check_config/)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "data/config/scraping_sources.json"
TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 2  # Rate limiting
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Keywords to check if page might contain job postings
JOB_KEYWORDS = [
    "job", "position", "employment", "career", "faculty", "recruit",
    "opening", "vacancy", "hire", "application", "apply", "posting"
]


def load_config() -> Dict:
    """Load scraping_sources.json configuration."""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_urls(config: Dict) -> List[Tuple[str, str, str]]:
    """
    Extract all URLs from configuration.
    
    Returns list of tuples: (url, source_type, description)
    """
    urls = []
    
    # Job portals
    if "job_portals" in config:
        for portal_id, portal_data in config["job_portals"].items():
            if "url" in portal_data:
                urls.append((
                    portal_data["url"],
                    "job_portal",
                    f"{portal_data.get('name', portal_id)}"
                ))
    
    # Regions
    if "regions" in config:
        regions = config["regions"]
        
        # United States
        if "united_states" in regions:
            us_region = regions["united_states"]
            
            # Universities
            for uni in us_region.get("universities", []):
                for dept in uni.get("departments", []):
                    if "url" in dept:
                        urls.append((
                            dept["url"],
                            "university_department",
                            f"{uni.get('name', 'Unknown')} - {dept.get('name', 'Unknown')}"
                        ))
            
            # Research institutes
            for inst in us_region.get("research_institutes", []):
                if "url" in inst:
                    urls.append((
                        inst["url"],
                        "research_institute",
                        inst.get("name", "Unknown")
                    ))
            
            # Think tanks
            for tank in us_region.get("think_tanks", []):
                if "url" in tank:
                    urls.append((
                        tank["url"],
                        "think_tank",
                        tank.get("name", "Unknown")
                    ))
        
        # Other countries
        if "other_countries" in regions:
            oc_region = regions["other_countries"]
            
            if "countries" in oc_region:
                for country_id, country_data in oc_region["countries"].items():
                    # Universities
                    for uni in country_data.get("universities", []):
                        for dept in uni.get("departments", []):
                            if "url" in dept:
                                urls.append((
                                    dept["url"],
                                    "university_department",
                                    f"{uni.get('name', 'Unknown')} ({country_id}) - {dept.get('name', 'Unknown')}"
                                ))
                    
                    # Research institutes
                    for inst in country_data.get("research_institutes", []):
                        if "url" in inst:
                            urls.append((
                                inst["url"],
                                "research_institute",
                                f"{inst.get('name', 'Unknown')} ({country_id})"
                            ))
                    
                    # Think tanks
                    for tank in country_data.get("think_tanks", []):
                        if "url" in tank:
                            urls.append((
                                tank["url"],
                                "think_tank",
                                f"{tank.get('name', 'Unknown')} ({country_id})"
                            ))
    
    return urls


def check_url(url: str, description: str) -> Dict:
    """
    Check if URL is accessible.
    
    Returns dict with status, status_code, error, and content_check results.
    """
    result = {
        "url": url,
        "description": description,
        "status": "unknown",
        "status_code": None,
        "error": None,
        "content_check": None,
        "content_length": None
    }
    
    try:
        print(f"Checking: {description}")
        print(f"  URL: {url}")
        
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True
        )
        
        result["status_code"] = response.status_code
        result["content_length"] = len(response.text)
        
        if response.status_code == 200:
            result["status"] = "accessible"
            
            # Quick content check - look for job-related keywords in text
            text_lower = response.text.lower()
            found_keywords = [kw for kw in JOB_KEYWORDS if kw in text_lower]
            
            if found_keywords:
                result["content_check"] = "likely_contains_jobs"
            else:
                result["content_check"] = "no_job_keywords_found"
            
            print(f"  ✓ Accessible (Status: {response.status_code}, Size: {len(response.text)} chars)")
            if result["content_check"] == "likely_contains_jobs":
                print(f"  ✓ Found job-related keywords: {', '.join(found_keywords[:5])}")
            else:
                print(f"  ⚠ No job-related keywords found (may still be a job page)")
        
        elif response.status_code in [301, 302, 303, 307, 308]:
            result["status"] = "redirect"
            result["error"] = f"Redirected to: {response.url}"
            print(f"  ⚠ Redirected (Status: {response.status_code})")
            print(f"  Final URL: {response.url}")
        
        elif response.status_code == 404:
            result["status"] = "not_found"
            result["error"] = "Page not found (404)"
            print(f"  ✗ Not found (404)")
        
        elif response.status_code == 403:
            result["status"] = "forbidden"
            result["error"] = "Access forbidden (403)"
            print(f"  ✗ Forbidden (403)")
        
        else:
            result["status"] = "error"
            result["error"] = f"HTTP {response.status_code}"
            print(f"  ✗ Error (Status: {response.status_code})")
    
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "Request timed out"
        print(f"  ✗ Timeout")
    
    except requests.exceptions.ConnectionError as e:
        result["status"] = "connection_error"
        result["error"] = f"Connection error: {str(e)}"
        print(f"  ✗ Connection error")
    
    except requests.exceptions.RequestException as e:
        result["status"] = "error"
        result["error"] = f"Request error: {str(e)}"
        print(f"  ✗ Error: {str(e)}")
    
    print()
    return result


def verify_all_urls(config: Dict) -> List[Dict]:
    """Verify all URLs in configuration."""
    urls = extract_urls(config)
    
    print("=" * 80)
    print(f"URL Verification - Checking {len(urls)} URLs")
    print("=" * 80)
    print()
    
    results = []
    for i, (url, source_type, description) in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {source_type.upper()}")
        result = check_url(url, description)
        result["source_type"] = source_type
        results.append(result)
        
        # Rate limiting
        if i < len(urls):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    return results


def print_summary(results: List[Dict]):
    """Print verification summary."""
    print()
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    total = len(results)
    accessible = sum(1 for r in results if r["status"] == "accessible")
    not_found = sum(1 for r in results if r["status"] == "not_found")
    forbidden = sum(1 for r in results if r["status"] == "forbidden")
    errors = sum(1 for r in results if r["status"] not in ["accessible", "redirect"])
    
    print(f"Total URLs checked: {total}")
    print(f"✓ Accessible: {accessible}")
    print(f"✗ Not Found (404): {not_found}")
    print(f"✗ Forbidden (403): {forbidden}")
    print(f"✗ Other Errors: {errors - not_found - forbidden}")
    print()
    
    # List accessible URLs
    if accessible > 0:
        print("ACCESSIBLE URLs:")
        print("-" * 80)
        for r in results:
            if r["status"] == "accessible":
                content_status = "✓" if r["content_check"] == "likely_contains_jobs" else "⚠"
                print(f"{content_status} {r['description']}")
                print(f"    {r['url']}")
        print()
    
    # List problematic URLs
    if errors > 0:
        print("PROBLEMATIC URLs (need attention):")
        print("-" * 80)
        for r in results:
            if r["status"] != "accessible":
                print(f"✗ {r['description']}")
                print(f"    {r['url']}")
                print(f"    Status: {r['status']} - {r['error']}")
        print()
    
    # Redirects
    redirects = [r for r in results if r["status"] == "redirect"]
    if redirects:
        print("REDIRECTS (may need URL update):")
        print("-" * 80)
        for r in redirects:
            print(f"⚠ {r['description']}")
            print(f"    Original: {r['url']}")
            print(f"    Redirected to: {r['error']}")
        print()


def save_results(results: List[Dict], output_file: str = None):
    """Save verification results to JSON file."""
    if output_file is None:
        output_path = PROJECT_ROOT / "data/config/url_verification_results.json"
    else:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {output_path}")
    print()


def main():
    """Main verification function."""
    print("Loading configuration...")
    config = load_config()
    print(f"Configuration loaded from: {CONFIG_FILE}")
    print()
    
    results = verify_all_urls(config)
    print_summary(results)
    
    # Save results
    save_results(results)
    
    # Exit with error code if there are issues
    errors = sum(1 for r in results if r["status"] not in ["accessible", "redirect"])
    if errors > 0:
        print(f"⚠ Warning: {errors} URLs have issues and may need to be updated")
        return 1
    else:
        print("✓ All URLs are accessible!")
        return 0


if __name__ == "__main__":
    exit(main())

