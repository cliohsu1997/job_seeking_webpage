"""
Comprehensive script to find and fix problematic URLs from non_accessible section.

This script combines URL pattern testing with config file integration:
1. Reads problematic URLs from scraping_sources.json non_accessible section
2. Tests common URL patterns to find working replacements
3. Verifies job content on replacement URLs
4. Downloads any business school PDFs found during testing
5. Saves results for manual review and config updates

Usage:
    poetry run python scripts/scraper/check_config/find_url_replacements.py
    
    # Or test specific universities manually:
    poetry run python scripts/scraper/check_config/find_url_replacements.py --manual
"""

import json
import requests
import time
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import sys

# Add parent directories to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

try:
    from utils.config_loader import load_master_config, CONFIG_DIR, save_config
except ImportError:
    # Fallback if config_loader not available
    CONFIG_DIR = Path(__file__).parent.parent.parent.parent / "data" / "config"
    def load_master_config():
        with open(CONFIG_DIR / "scraping_sources.json", 'r', encoding='utf-8') as f:
            return json.load(f)

# Configuration
CONFIG_FILE = CONFIG_DIR / "scraping_sources.json"
TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 1
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8,application/pdf",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}

# Common URL patterns to try
COMMON_PATTERNS = [
    "https://jobs.{base_domain}",
    "https://careers.{base_domain}",
    "https://facultyjobs.{base_domain}",
    "https://hiring.{base_domain}",
    "https://hr.{base_domain}",
    "https://employment.{base_domain}",
    "https://www.{base_domain}/jobs",
    "https://www.{base_domain}/careers",
    "https://www.{base_domain}/employment",
    "https://www.{base_domain}/faculty/jobs",
    "https://www.{base_domain}/human-resources",
    "https://www.{base_domain}/academic-jobs",
    "https://www.{base_domain}/faculty-positions",
    "https://www.{base_domain}/faculty/openings",
    "https://www.{base_domain}/academics/jobs",
]

# Job-related keywords for content verification
JOB_KEYWORDS_EN = [
    'job', 'position', 'opening', 'vacancy', 'hire', 'recruit',
    'faculty', 'professor', 'assistant professor', 'associate professor',
    'lecturer', 'researcher', 'postdoc', 'post-doctoral',
    'economics', 'business', 'management', 'academic',
    'application', 'apply', 'deadline', 'qualification'
]

JOB_KEYWORDS_CN = [
    "招聘", "职位", "岗位", "人才", "应聘", "申请", "工作", "就业",
    "职位信息", "招聘信息", "人才招聘", "教师招聘", "教学岗位", "科研岗位",
    "人事", "人事处", "人才引进", "师资", "师资招聘"
]

JOB_KEYWORDS = JOB_KEYWORDS_EN + JOB_KEYWORDS_CN


def get_base_domain(url: str) -> str:
    """Extract base domain from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc
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


def test_url_accessibility(url: str) -> Tuple[bool, int, str]:
    """Test if URL is accessible."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return True, response.status_code, response.url
    except requests.exceptions.RequestException as e:
        return False, 0, str(e)


def check_job_content(html_content: str, url: str) -> Tuple[bool, float, List[str]]:
    """
    Check if page contains job-related content.
    Returns: (has_job_content, score, found_pdfs)
    """
    if not html_content:
        return False, 0.0, []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text().lower()
    
    # Count keyword matches
    score = sum(1 for keyword in JOB_KEYWORDS if keyword.lower() in text)
    has_job_content = score >= 3  # At least 3 keywords
    
    # Find PDF links
    pdfs = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.lower().endswith('.pdf'):
            full_url = urljoin(url, href)
            pdfs.append(full_url)
        # Also check for PDF in link text
        link_text = link.get_text().lower()
        if 'pdf' in link_text or 'download' in link_text:
            href_full = urljoin(url, href)
            if href_full not in pdfs:
                pdfs.append(href_full)
    
    return has_job_content, score, pdfs


def test_url_with_content(url: str, require_job_content: bool = False) -> Tuple[bool, Optional[str], List[str], float]:
    """
    Test URL for accessibility and job content.
    Returns: (is_valid, final_url, pdfs_found, content_score)
    """
    is_accessible, status_code, final_url = test_url_accessibility(url)
    
    if not is_accessible or status_code not in [200, 301, 302, 303, 307, 308]:
        return False, None, [], 0.0
    
    # Get content for job content check
    try:
        response = requests.get(final_url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if response.status_code == 200:
            has_job_content, score, pdfs = check_job_content(response.text, final_url)
            if require_job_content and not has_job_content:
                return False, final_url, pdfs, score
            return True, final_url, pdfs, score
    except Exception as e:
        pass
    
    # Even if job content check fails, return True if accessible (might be a listing page)
    return True, final_url, [], 0.0


def find_replacement_urls(original_url: str, university_name: str = "", require_job_content: bool = False, verbose: bool = True) -> List[Tuple[str, str, List[str], float]]:
    """
    Try common URL patterns and return working ones.
    Returns: List of (url, status, pdfs_found, content_score)
    """
    domain = get_base_domain(original_url)
    base_domain, full_domain = get_domain_parts(domain)
    
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
        f"https://www.{base_domain}/academic-jobs",
        f"https://www.{base_domain}/faculty-positions",
        f"https://www.{base_domain}/faculty/openings",
        f"https://www.{base_domain}/academics/jobs",
    ]
    
    if verbose:
        print(f"  Testing {len(patterns_to_try)} URL patterns for {university_name or domain}...")
    
    for pattern_url in patterns_to_try:
        is_valid, final_url, pdfs, score = test_url_with_content(pattern_url, require_job_content)
        if is_valid:
            status = "working"
            if score >= 5:
                status = "working (high job content)"
            working_urls.append((final_url or pattern_url, status, pdfs, score))
            if verbose:
                print(f"    ✓ {pattern_url} (score: {score:.1f})")
        elif verbose:
            print(f"    ✗ {pattern_url}")
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    if verbose:
        print(f"  Found {len(working_urls)} working URLs for {university_name or domain}")
    
    return working_urls


def download_pdf(pdf_url: str, output_dir: Path, filename: str = None) -> Optional[Path]:
    """Download a PDF file if it's business/economics related."""
    try:
        response = requests.get(pdf_url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        if response.status_code == 200 and 'pdf' in response.headers.get('content-type', '').lower():
            if filename is None:
                filename = pdf_url.split('/')[-1]
            output_path = output_dir / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return output_path
    except Exception as e:
        pass
    return None


def extract_problematic_urls(config: Dict) -> List[Dict]:
    """Extract all problematic URLs from non_accessible section."""
    problematic = []
    non_accessible = config.get("non_accessible", {})
    
    # Job portals
    if "job_portals" in non_accessible:
        for portal_id, portal_data in non_accessible["job_portals"].items():
            if "url" in portal_data:
                problematic.append({
                    "type": "job_portal",
                    "name": portal_data.get("name", portal_id),
                    "url": portal_data["url"],
                    "location": {"key": portal_id, "data": portal_data}
                })
    
    # Regions
    if "regions" in non_accessible:
        for region_key, region_data in non_accessible["regions"].items():
            # Universities
            if "universities" in region_data:
                for uni_idx, uni in enumerate(region_data["universities"]):
                    uni_name = uni.get("name", "Unknown")
                    for dept_idx, dept in enumerate(uni.get("departments", [])):
                        if "url" in dept:
                            problematic.append({
                                "type": "university_department",
                                "name": f"{uni_name} - {dept.get('name', 'Unknown')}",
                                "url": dept["url"],
                                "location": {
                                    "region": region_key,
                                    "uni_idx": uni_idx,
                                    "dept_idx": dept_idx,
                                    "uni_data": uni,
                                    "dept_data": dept
                                }
                            })
            
            # Research institutes
            if "research_institutes" in region_data:
                for inst_idx, inst in enumerate(region_data["research_institutes"]):
                    if "url" in inst:
                        problematic.append({
                            "type": "research_institute",
                            "name": inst.get("name", "Unknown"),
                            "url": inst["url"],
                            "location": {
                                "region": region_key,
                                "inst_idx": inst_idx,
                                "inst_data": inst
                            }
                        })
    
    return problematic


def main():
    """Main function to find and fix problematic URLs."""
    parser = argparse.ArgumentParser(description="Find replacement URLs for problematic sources")
    parser.add_argument("--manual", action="store_true", help="Test manual list of universities")
    parser.add_argument("--limit", type=int, default=20, help="Limit number of URLs to process")
    parser.add_argument("--require-job-content", action="store_true", help="Require job content verification")
    parser.add_argument("--download-pdfs", action="store_true", help="Download business school PDFs found")
    args = parser.parse_args()
    
    print("=" * 80)
    print("URL Replacement Finder - Finding fixes for problematic URLs")
    print("=" * 80)
    
    results = {}
    
    if args.manual:
        # Manual list mode (original functionality)
        print("\n[Mode: Manual List]")
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
        
        print(f"Testing {len(problematic)} universities from manual list...")
        for idx, (uni_name, original_url) in enumerate(problematic, 1):
            print(f"\n[{idx}/{len(problematic)}] Processing: {uni_name}")
            print(f"  Original URL: {original_url}")
            
            replacements = find_replacement_urls(original_url, uni_name, args.require_job_content)
            
            if replacements:
                # Sort by content score (highest first)
                replacements.sort(key=lambda x: x[3], reverse=True)
                best_replacement = replacements[0]
                results[uni_name] = {
                    "original": original_url,
                    "replacement": best_replacement[0],
                    "status": best_replacement[1],
                    "content_score": best_replacement[3],
                    "pdfs": best_replacement[2],
                    "all_working": [r[0] for r in replacements]
                }
                print(f"  ✓ Found replacement: {best_replacement[0]} (score: {best_replacement[3]:.1f})")
            else:
                print(f"  ✗ No replacement found")
                results[uni_name] = {
                    "original": original_url,
                    "replacement": None
                }
            time.sleep(DELAY_BETWEEN_REQUESTS)
    else:
        # Config file mode
        print("\n[Mode: Config File]")
        print("[1/5] Loading configuration...")
        try:
            config = load_master_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return
        
        print("[2/5] Extracting problematic URLs from non_accessible section...")
        problematic = extract_problematic_urls(config)
        print(f"Found {len(problematic)} problematic URLs")
        
        # Prioritize: US universities, job portals, research institutes first
        priority_order = ["job_portal", "research_institute", "university_department"]
        problematic_sorted = sorted(
            problematic,
            key=lambda x: (
                priority_order.index(x["type"]) if x["type"] in priority_order else 999,
                x["name"]
            )
        )
        
        # Process limited number
        limit = min(args.limit, len(problematic_sorted))
        print(f"\n[3/5] Processing first {limit} URLs...")
        
        for idx, item in enumerate(problematic_sorted[:limit], 1):
            print(f"\n[{idx}/{limit}] Processing: {item['name']}")
            print(f"  Original URL: {item['url']}")
            
            replacements = find_replacement_urls(item['url'], item['name'], args.require_job_content)
            
            if replacements:
                # Sort by content score (highest first)
                replacements.sort(key=lambda x: x[3], reverse=True)
                best_replacement = replacements[0]
                results[item['name']] = {
                    "original": item['url'],
                    "replacement": best_replacement[0],
                    "status": best_replacement[1],
                    "content_score": best_replacement[3],
                    "pdfs": best_replacement[2],
                    "location": item['location'],
                    "all_working": [r[0] for r in replacements]
                }
                print(f"  ✓ Found replacement: {best_replacement[0]} (score: {best_replacement[3]:.1f})")
                
                # Download PDFs if requested
                if args.download_pdfs and best_replacement[2]:
                    print(f"  Downloading {len(best_replacement[2])} PDF(s)...")
                    pdf_dir = Path(__file__).parent.parent.parent.parent / "data" / "raw" / "documents"
                    for pdf_url in best_replacement[2]:
                        downloaded = download_pdf(pdf_url, pdf_dir)
                        if downloaded:
                            print(f"    ✓ Downloaded: {downloaded.name}")
            else:
                print(f"  ✗ No replacement found")
                results[item['name']] = {
                    "original": item['url'],
                    "replacement": None,
                    "location": item['location']
                }
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Save results
    print(f"\n[4/5] Saving results...")
    results_file = CONFIG_DIR / "url_replacements.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {results_file}")
    
    # Summary
    print(f"\n[5/5] Summary:")
    print("=" * 80)
    found = sum(1 for r in results.values() if r.get("replacement"))
    print(f"Found replacements: {found}/{len(results)}")
    
    if found > 0:
        print(f"\nWorking replacements:")
        for name, result in results.items():
            if result.get("replacement"):
                score = result.get("content_score", 0)
                print(f"  ✓ {name}: {result['replacement']} (score: {score:.1f})")
    
    not_found = [name for name, result in results.items() if not result.get("replacement")]
    if not_found:
        print(f"\nNo replacement found ({len(not_found)}):")
        for name in not_found[:10]:  # Show first 10
            print(f"  ✗ {name}")
        if len(not_found) > 10:
            print(f"  ... and {len(not_found) - 10} more")
    
    print(f"\nNext steps:")
    print("1. Review url_replacements.json")
    print("2. Manually verify replacements")
    print("3. Update scraping_sources.json with verified replacements")
    print("4. Re-run verification script: poetry run python scripts/scraper/check_config/verify_urls.py")


if __name__ == "__main__":
    main()
