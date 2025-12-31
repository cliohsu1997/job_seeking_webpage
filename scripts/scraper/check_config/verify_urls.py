"""
Verify URLs in scraping_sources.json before scraping.

This script checks if all URLs are accessible and updates url_status
directly in scraping_sources.json. Only URLs without url_status="accessible"
will be checked.
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

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


def save_config(config: Dict):
    """Save scraping_sources.json configuration."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def extract_urls_with_path(config: Dict) -> List[Tuple[str, str, str, List[str]]]:
    """
    Extract all URLs from configuration with their path for updating.
    
    Returns list of tuples: (url, source_type, description, path_to_update)
    path_to_update is a list of keys to navigate to the URL field in the config
    """
    urls = []
    
    # Job portals
    if "job_portals" in config:
        for portal_id, portal_data in config["job_portals"].items():
            if "url" in portal_data:
                urls.append((
                    portal_data["url"],
                    "job_portal",
                    f"{portal_data.get('name', portal_id)}",
                    ["job_portals", portal_id, "url"]
                ))
    
    # Regions
    if "regions" in config:
        regions = config["regions"]
        
        # United States
        if "united_states" in regions:
            us_region = regions["united_states"]
            
            # Universities
            for uni_idx, uni in enumerate(us_region.get("universities", [])):
                for dept_idx, dept in enumerate(uni.get("departments", [])):
                    if "url" in dept:
                        urls.append((
                            dept["url"],
                            "university_department",
                            f"{uni.get('name', 'Unknown')} - {dept.get('name', 'Unknown')}",
                            ["regions", "united_states", "universities", uni_idx, "departments", dept_idx, "url"]
                        ))
            
            # Research institutes
            for inst_idx, inst in enumerate(us_region.get("research_institutes", [])):
                if "url" in inst:
                    urls.append((
                        inst["url"],
                        "research_institute",
                        inst.get("name", "Unknown"),
                        ["regions", "united_states", "research_institutes", inst_idx, "url"]
                    ))
            
            # Think tanks
            for tank_idx, tank in enumerate(us_region.get("think_tanks", [])):
                if "url" in tank:
                    urls.append((
                        tank["url"],
                        "think_tank",
                        tank.get("name", "Unknown"),
                        ["regions", "united_states", "think_tanks", tank_idx, "url"]
                    ))
        
        # Other countries
        if "other_countries" in regions:
            oc_region = regions["other_countries"]
            
            if "countries" in oc_region:
                for country_id, country_data in oc_region["countries"].items():
                    # Universities
                    for uni_idx, uni in enumerate(country_data.get("universities", [])):
                        for dept_idx, dept in enumerate(uni.get("departments", [])):
                            if "url" in dept:
                                urls.append((
                                    dept["url"],
                                    "university_department",
                                    f"{uni.get('name', 'Unknown')} ({country_id}) - {dept.get('name', 'Unknown')}",
                                    ["regions", "other_countries", "countries", country_id, "universities", uni_idx, "departments", dept_idx, "url"]
                                ))
                    
                    # Research institutes
                    for inst_idx, inst in enumerate(country_data.get("research_institutes", [])):
                        if "url" in inst:
                            urls.append((
                                inst["url"],
                                "research_institute",
                                f"{inst.get('name', 'Unknown')} ({country_id})",
                                ["regions", "other_countries", "countries", country_id, "research_institutes", inst_idx, "url"]
                            ))
                    
                    # Think tanks
                    for tank_idx, tank in enumerate(country_data.get("think_tanks", [])):
                        if "url" in tank:
                            urls.append((
                                tank["url"],
                                "think_tank",
                                f"{tank.get('name', 'Unknown')} ({country_id})",
                                ["regions", "other_countries", "countries", country_id, "think_tanks", tank_idx, "url"]
                            ))
    
    return urls


def get_url_status(config: Dict, path: List) -> Optional[str]:
    """Get url_status from config using path (path should point to url field, we check for url_status at same level)."""
    # Navigate to parent of URL field
    obj = config
    for key in path[:-1]:
        if isinstance(key, int):
            obj = obj[key]
        else:
            obj = obj.get(key, {})
    
    # Check for url_status at same level as url
    return obj.get("url_status")


def set_url_status(config: Dict, path: List, status: str):
    """Set url_status in config using path (path should point to url field, we set url_status at same level)."""
    # Navigate to parent of URL field
    obj = config
    for key in path[:-1]:
        if isinstance(key, int):
            obj = obj[key]
        else:
            if key not in obj:
                obj[key] = {}
            obj = obj[key]
    
    # Set url_status at same level as url
    obj["url_status"] = status


def check_url(url: str, description: str) -> Dict:
    """
    Check if URL is accessible.
    
    Returns dict with status and other details.
    """
    result = {
        "status": "unknown",
        "status_code": None,
        "error": None,
        "content_check": None
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


def verify_urls(config: Dict) -> Tuple[Dict, List[Dict]]:
    """
    Verify URLs in configuration and update url_status in config.
    
    Returns (updated_config, list of results)
    """
    urls_with_path = extract_urls_with_path(config)
    
    # Separate URLs that need verification from those already verified
    urls_to_check = []
    verified_count = 0
    
    for url, source_type, description, path in urls_with_path:
        current_status = get_url_status(config, path)
        if current_status == "accessible":
            verified_count += 1
        else:
            urls_to_check.append((url, source_type, description, path))
    
    total_urls = len(urls_with_path)
    check_count = len(urls_to_check)
    
    print("=" * 80)
    print(f"URL Verification - Total URLs: {total_urls}")
    print(f"  ✓ Previously verified (skipped): {verified_count}")
    print(f"  🔍 Checking now: {check_count}")
    print("=" * 80)
    print()
    
    results = []
    
    if check_count == 0:
        print("All URLs have been previously verified as accessible. No checks needed.")
        print()
        return config, results
    
    # Verify URLs that need checking
    for i, (url, source_type, description, path) in enumerate(urls_to_check, 1):
        print(f"[{i}/{check_count}] {source_type.upper()}")
        result = check_url(url, description)
        result["url"] = url
        result["description"] = description
        result["source_type"] = source_type
        results.append(result)
        
        # Update status in config
        set_url_status(config, path, result["status"])
        
        # Rate limiting
        if i < len(urls_to_check):
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    return config, results


def print_summary(results: List[Dict], total_urls: int, verified_count: int):
    """Print verification summary."""
    print()
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    newly_checked = len(results)
    newly_accessible = sum(1 for r in results if r["status"] == "accessible")
    not_found = sum(1 for r in results if r["status"] == "not_found")
    forbidden = sum(1 for r in results if r["status"] == "forbidden")
    errors = sum(1 for r in results if r["status"] not in ["accessible", "redirect"])
    
    total_accessible = verified_count + newly_accessible
    
    print(f"Total URLs in config: {total_urls}")
    print(f"✓ Accessible: {total_accessible} ({verified_count} previously + {newly_accessible} newly verified)")
    print(f"✗ Not Found (404): {not_found}")
    print(f"✗ Forbidden (403): {forbidden}")
    print(f"✗ Other Errors: {errors - not_found - forbidden}")
    print()
    
    # List newly accessible URLs
    if newly_accessible > 0:
        print("NEWLY VERIFIED ACCESSIBLE URLs:")
        print("-" * 80)
        for r in results:
            if r["status"] == "accessible":
                content_status = "✓" if r.get("content_check") == "likely_contains_jobs" else "⚠"
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
                print(f"    Status: {r['status']} - {r.get('error', '')}")
        print()
    
    # Redirects
    redirects = [r for r in results if r["status"] == "redirect"]
    if redirects:
        print("REDIRECTS (may need URL update):")
        print("-" * 80)
        for r in redirects:
            print(f"⚠ {r['description']}")
            print(f"    Original: {r['url']}")
            print(f"    Redirected to: {r.get('error', '')}")
        print()


def main():
    """Main verification function."""
    print("Loading configuration...")
    config = load_config()
    print(f"Configuration loaded from: {CONFIG_FILE}")
    print()
    
    # Verify URLs and update config
    updated_config, results = verify_urls(config)
    
    # Count total accessible
    urls_with_path = extract_urls_with_path(updated_config)
    verified_count = sum(1 for _, _, _, path in urls_with_path if get_url_status(updated_config, path) == "accessible")
    total_urls = len(urls_with_path)
    
    print_summary(results, total_urls, verified_count - len([r for r in results if r["status"] == "accessible"]))
    
    # Save updated config
    save_config(updated_config)
    print(f"Configuration updated and saved to: {CONFIG_FILE}")
    print()
    
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
