"""
Verify URLs in scraping_sources.json and validate they contain job listings.

IMPORTANT RULE: Only URLs containing relevant job information should be in the accessible section.
URLs that are inaccessible or don't contain job listings will be moved to non_accessible section.

This script:
1. Checks URLs in the accessible section to ensure they still work and contain job listings
2. Checks URLs in the non_accessible section and moves them to accessible when verified
3. Verifies that URLs contain actual job listings (following links, checking PDFs)
4. Moves invalid URLs from accessible to non_accessible if they don't contain job content
"""

import json
import requests
import time
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse, urlunparse, quote, unquote, urljoin
from bs4 import BeautifulSoup
import sys

# Add parent directories to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

from utils.config_loader import load_master_config, CONFIG_DIR, save_config

# Configuration
CONFIG_FILE = CONFIG_DIR / "scraping_sources.json"
TIMEOUT = 30
DELAY_BETWEEN_REQUESTS = 2  # Rate limiting
MAX_RETRIES = 3
RETRY_DELAY_BASE = 1  # Base delay for exponential backoff
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8,application/pdf",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Keywords to check if page might contain job postings (English)
JOB_KEYWORDS_EN = [
    "job", "position", "employment", "career", "faculty", "recruit",
    "opening", "vacancy", "hire", "application", "apply", "posting",
    "professor", "lecturer", "researcher", "assistant professor", "associate professor"
]

# Chinese keywords for job postings (Simplified Chinese)
JOB_KEYWORDS_CN = [
    "招聘",      # recruitment
    "职位",      # position/job
    "岗位",      # position/post
    "人才",      # talent
    "应聘",      # application
    "申请",      # application
    "工作",      # work/job
    "就业",      # employment
    "职位信息",   # job information
    "招聘信息",   # recruitment information
    "人才招聘",   # talent recruitment
    "教师招聘",   # faculty recruitment
    "教学岗位",   # teaching position
    "科研岗位",   # research position
    "人事",      # human resources
    "人事处",     # human resources office
    "人才引进",   # talent introduction/recruitment
    "师资",      # faculty/staff
    "师资招聘",   # faculty recruitment
]

# Combined keywords for checking
JOB_KEYWORDS = JOB_KEYWORDS_EN + JOB_KEYWORDS_CN

# PDF-related keywords
PDF_KEYWORDS = [".pdf", "pdf", "download", "职位描述", "job description", "position description"]


def extract_urls_from_accessible(config: Dict) -> List[Tuple[str, str, str, Dict]]:
    """
    Extract all URLs from accessible section with their location info.
    
    Returns list of tuples: (url, source_type, description, location_info)
    """
    urls = []
    accessible = config.get("accessible", {})
    
    # Job portals
    if "job_portals" in accessible:
        for portal_id, portal_data in accessible["job_portals"].items():
            if "url" in portal_data:
                urls.append((
                    portal_data["url"],
                    "job_portal",
                    f"{portal_data.get('name', portal_id)}",
                    {
                        "category": "accessible",
                        "type": "job_portal",
                        "key": portal_id,
                        "item": portal_data.copy()
                    }
                ))
    
    # Regions
    if "regions" in accessible:
        regions = accessible["regions"]
        
        # Process all regions (united_states, mainland_china, other_countries)
        for region_key, region_data in regions.items():
            if region_key == "other_countries" and "countries" in region_data:
                # Other countries structure
                for country_id, country_data in region_data["countries"].items():
                    # Universities
                    for uni_idx, uni in enumerate(country_data.get("universities", [])):
                        for dept_idx, dept in enumerate(uni.get("departments", [])):
                            if "url" in dept:
                                urls.append((
                                    dept["url"],
                                    "university_department",
                                    f"{uni.get('name', 'Unknown')} ({country_id}) - {dept.get('name', 'Unknown')}",
                                    {
                                        "category": "accessible",
                                        "type": "university_department",
                                        "region": region_key,
                                        "country_id": country_id,
                                        "uni_idx": uni_idx,
                                        "dept_idx": dept_idx,
                                        "item": dept.copy(),
                                        "uni_data": uni.copy()
                                    }
                                ))
                    
                    # Research institutes
                    for inst_idx, inst in enumerate(country_data.get("research_institutes", [])):
                        if "url" in inst:
                            urls.append((
                                inst["url"],
                                "research_institute",
                                f"{inst.get('name', 'Unknown')} ({country_id})",
                                {
                                    "category": "accessible",
                                    "type": "research_institute",
                                    "region": region_key,
                                    "country_id": country_id,
                                    "inst_idx": inst_idx,
                                    "item": inst.copy()
                                }
                            ))
            else:
                # Standard region structure (united_states, mainland_china)
                # Universities
                for uni_idx, uni in enumerate(region_data.get("universities", [])):
                    for dept_idx, dept in enumerate(uni.get("departments", [])):
                        if "url" in dept:
                            urls.append((
                                dept["url"],
                                "university_department",
                                f"{uni.get('name', 'Unknown')} - {dept.get('name', 'Unknown')}",
                                {
                                    "category": "accessible",
                                    "type": "university_department",
                                    "region": region_key,
                                    "uni_idx": uni_idx,
                                    "dept_idx": dept_idx,
                                    "item": dept.copy(),
                                    "uni_data": uni.copy()
                                }
                            ))
                
                # Research institutes
                for inst_idx, inst in enumerate(region_data.get("research_institutes", [])):
                    if "url" in inst:
                        urls.append((
                            inst["url"],
                            "research_institute",
                            inst.get("name", "Unknown"),
                            {
                                "category": "accessible",
                                "type": "research_institute",
                                "region": region_key,
                                "inst_idx": inst_idx,
                                "item": inst.copy()
                            }
                        ))
    
    return urls


def extract_urls_from_non_accessible(config: Dict) -> List[Tuple[str, str, str, Dict]]:
    """
    Extract all URLs from non_accessible section with their location info.
    
    Returns list of tuples: (url, source_type, description, location_info)
    location_info contains: category ("non_accessible"), path to item, and item data
    """
    urls = []
    non_accessible = config.get("non_accessible", {})
    
    # Job portals
    if "job_portals" in non_accessible:
        for portal_id, portal_data in non_accessible["job_portals"].items():
            if "url" in portal_data:
                urls.append((
                    portal_data["url"],
                    "job_portal",
                    f"{portal_data.get('name', portal_id)}",
                    {
                        "category": "non_accessible",
                        "type": "job_portal",
                        "key": portal_id,
                        "item": portal_data.copy()
                    }
                ))
    
    # Regions
    if "regions" in non_accessible:
        regions = non_accessible["regions"]
        
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
                            {
                                "category": "non_accessible",
                                "type": "university_department",
                                "region": "united_states",
                                "uni_idx": uni_idx,
                                "dept_idx": dept_idx,
                                "item": dept.copy(),
                                "uni_data": uni.copy()
                            }
                        ))
            
            # Research institutes
            for inst_idx, inst in enumerate(us_region.get("research_institutes", [])):
                if "url" in inst:
                    urls.append((
                        inst["url"],
                        "research_institute",
                        inst.get("name", "Unknown"),
                        {
                            "category": "non_accessible",
                            "type": "research_institute",
                            "region": "united_states",
                            "inst_idx": inst_idx,
                            "item": inst.copy()
                        }
                    ))
            
            # Think tanks
            for tank_idx, tank in enumerate(us_region.get("think_tanks", [])):
                if "url" in tank:
                    urls.append((
                        tank["url"],
                        "think_tank",
                        tank.get("name", "Unknown"),
                        {
                            "category": "non_accessible",
                            "type": "think_tank",
                            "region": "united_states",
                            "tank_idx": tank_idx,
                            "item": tank.copy()
                        }
                    ))
        
        # Mainland China
        if "mainland_china" in regions:
            china_region = regions["mainland_china"]
            
            # Universities
            for uni_idx, uni in enumerate(china_region.get("universities", [])):
                for dept_idx, dept in enumerate(uni.get("departments", [])):
                    if "url" in dept:
                        urls.append((
                            dept["url"],
                            "university_department",
                            f"{uni.get('name', 'Unknown')} (China) - {dept.get('name', 'Unknown')}",
                            {
                                "category": "non_accessible",
                                "type": "university_department",
                                "region": "mainland_china",
                                "uni_idx": uni_idx,
                                "dept_idx": dept_idx,
                                "item": dept.copy(),
                                "uni_data": uni.copy()
                            }
                        ))
            
            # Research institutes
            for inst_idx, inst in enumerate(china_region.get("research_institutes", [])):
                if "url" in inst:
                    urls.append((
                        inst["url"],
                        "research_institute",
                        f"{inst.get('name', 'Unknown')} (China)",
                        {
                            "category": "non_accessible",
                            "type": "research_institute",
                            "region": "mainland_china",
                            "inst_idx": inst_idx,
                            "item": inst.copy()
                        }
                    ))
            
            # Think tanks
            for tank_idx, tank in enumerate(china_region.get("think_tanks", [])):
                if "url" in tank:
                    urls.append((
                        tank["url"],
                        "think_tank",
                        f"{tank.get('name', 'Unknown')} (China)",
                        {
                            "category": "non_accessible",
                            "type": "think_tank",
                            "region": "mainland_china",
                            "tank_idx": tank_idx,
                            "item": tank.copy()
                        }
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
                                    {
                                        "category": "non_accessible",
                                        "type": "university_department",
                                        "region": "other_countries",
                                        "country_id": country_id,
                                        "uni_idx": uni_idx,
                                        "dept_idx": dept_idx,
                                        "item": dept.copy(),
                                        "uni_data": uni.copy()
                                    }
                                ))
                    
                    # Research institutes
                    for inst_idx, inst in enumerate(country_data.get("research_institutes", [])):
                        if "url" in inst:
                            urls.append((
                                inst["url"],
                                "research_institute",
                                f"{inst.get('name', 'Unknown')} ({country_id})",
                                {
                                    "category": "non_accessible",
                                    "type": "research_institute",
                                    "region": "other_countries",
                                    "country_id": country_id,
                                    "inst_idx": inst_idx,
                                    "item": inst.copy()
                                }
                            ))
                    
                    # Think tanks
                    for tank_idx, tank in enumerate(country_data.get("think_tanks", [])):
                        if "url" in tank:
                            urls.append((
                                tank["url"],
                                "think_tank",
                                f"{tank.get('name', 'Unknown')} ({country_id})",
                                {
                                    "category": "non_accessible",
                                    "type": "think_tank",
                                    "region": "other_countries",
                                    "country_id": country_id,
                                    "tank_idx": tank_idx,
                                    "item": tank.copy()
                                }
                            ))
    
    return urls


def check_for_job_links_and_pdfs(html_content: str, base_url: str, session: requests.Session) -> Dict:
    """
    Check if page contains job listing links or PDFs with job descriptions.
    
    Returns dict with:
    - has_job_links: bool
    - job_link_count: int
    - has_pdf_links: bool
    - pdf_link_count: int
    - sample_links: List[str]
    """
    result = {
        "has_job_links": False,
        "job_link_count": 0,
        "has_pdf_links": False,
        "pdf_link_count": 0,
        "sample_links": []
    }
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        
        job_links = []
        pdf_links = []
        
        for link in all_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True).lower()
            
            # Resolve relative URLs
            if href.startswith('/') or not href.startswith('http'):
                full_url = urljoin(base_url, href)
            else:
                full_url = href
            
            # Check if it's a PDF link
            if href.lower().endswith('.pdf') or 'pdf' in link_text or any(kw in link_text for kw in PDF_KEYWORDS):
                pdf_links.append(full_url)
            
            # Check if link text or URL suggests job listing
            text_lower = link_text
            url_lower = href.lower()
            
            job_indicators = [
                any(kw in text_lower for kw in JOB_KEYWORDS_EN),
                any(kw in url_lower for kw in ['job', 'position', 'career', 'recruit', 'vacancy', 'opening']),
                any(kw in text_lower for kw in ['apply', 'application', 'view', 'details', 'more']),
            ]
            
            # Also check for Chinese keywords
            if any(kw in link_text for kw in JOB_KEYWORDS_CN):
                job_indicators.append(True)
            
            if any(job_indicators) and href:
                job_links.append(full_url)
        
        result["job_link_count"] = len(job_links)
        result["has_job_links"] = len(job_links) > 0
        result["pdf_link_count"] = len(pdf_links)
        result["has_pdf_links"] = len(pdf_links) > 0
        
        # Store sample links (first 5)
        result["sample_links"] = job_links[:5] + pdf_links[:5]
        
        return result
        
    except Exception as e:
        print(f"    ⚠ Error checking for links: {e}")
        return result


def verify_job_content(html_content: str, url: str, session: requests.Session) -> Dict:
    """
    Verify that the page actually contains job listings by checking content and following links.
    
    Returns dict with verification results.
    """
    result = {
        "has_job_content": False,
        "has_job_keywords": False,
        "has_job_links": False,
        "has_pdfs": False,
        "verification_score": 0,
        "details": ""
    }
    
    try:
        # Check for job keywords in content
        content_lower = html_content.lower()
        found_keywords = [kw for kw in JOB_KEYWORDS_EN if kw in content_lower]
        result["has_job_keywords"] = len(found_keywords) > 0
        
        # Check for links to job listings or PDFs
        link_check = check_for_job_links_and_pdfs(html_content, url, session)
        result["has_job_links"] = link_check["has_job_links"]
        result["has_pdfs"] = link_check["has_pdf_links"]
        
        # Calculate verification score
        score = 0
        if result["has_job_keywords"]:
            score += 2
        if result["has_job_links"]:
            score += 3
            if link_check["job_link_count"] >= 3:
                score += 1  # Bonus for multiple job links
        if result["has_pdfs"]:
            score += 2
        
        result["verification_score"] = score
        result["has_job_content"] = score >= 3  # Require at least 3 points
        
        # Build details string
        details_parts = []
        if result["has_job_keywords"]:
            details_parts.append(f"{len(found_keywords)} job keywords")
        if result["has_job_links"]:
            details_parts.append(f"{link_check['job_link_count']} job links")
        if result["has_pdfs"]:
            details_parts.append(f"{link_check['pdf_link_count']} PDF links")
        
        result["details"] = ", ".join(details_parts) if details_parts else "No job content indicators"
        
        return result
        
    except Exception as e:
        result["details"] = f"Error: {str(e)}"
        return result


def add_to_non_accessible(config: Dict, location_info: Dict):
    """Add item to non_accessible section."""
    non_accessible = config.get("non_accessible", {})
    item_type = location_info["type"]
    item = location_info["item"]
    
    if item_type == "job_portal":
        portal_id = location_info["key"]
        if "job_portals" not in non_accessible:
            non_accessible["job_portals"] = {}
        non_accessible["job_portals"][portal_id] = item
    
    elif item_type == "university_department":
        region = location_info["region"]
        uni_data = location_info.get("uni_data", {})
        
        if "regions" not in non_accessible:
            non_accessible["regions"] = {}
        if region not in non_accessible["regions"]:
            non_accessible["regions"][region] = {}
            # Copy metadata if exists
            if region in config.get("accessible", {}).get("regions", {}):
                source_region = config["accessible"]["regions"][region]
                for meta_key in ["ranking_source", "coverage"]:
                    if meta_key in source_region:
                        non_accessible["regions"][region][meta_key] = source_region[meta_key]
        
        if region in ["united_states", "mainland_china"]:
            if "universities" not in non_accessible["regions"][region]:
                non_accessible["regions"][region]["universities"] = []
            
            # Find or create university
            uni_name = uni_data.get("name", "Unknown")
            uni_found = False
            for existing_uni in non_accessible["regions"][region]["universities"]:
                if existing_uni.get("name") == uni_name:
                    if "departments" not in existing_uni:
                        existing_uni["departments"] = []
                    existing_uni["departments"].append(item)
                    uni_found = True
                    break
            
            if not uni_found:
                new_uni = uni_data.copy()
                new_uni["departments"] = [item]
                non_accessible["regions"][region]["universities"].append(new_uni)
        
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "other_countries" not in non_accessible["regions"]:
                non_accessible["regions"]["other_countries"] = {}
            if "countries" not in non_accessible["regions"]["other_countries"]:
                non_accessible["regions"]["other_countries"]["countries"] = {}
            if country_id not in non_accessible["regions"]["other_countries"]["countries"]:
                non_accessible["regions"]["other_countries"]["countries"][country_id] = {}
            
            country_data = non_accessible["regions"]["other_countries"]["countries"][country_id]
            if "universities" not in country_data:
                country_data["universities"] = []
            
            # Find or create university
            uni_name = uni_data.get("name", "Unknown")
            uni_found = False
            for existing_uni in country_data["universities"]:
                if existing_uni.get("name") == uni_name:
                    if "departments" not in existing_uni:
                        existing_uni["departments"] = []
                    existing_uni["departments"].append(item)
                    uni_found = True
                    break
            
            if not uni_found:
                new_uni = uni_data.copy()
                new_uni["departments"] = [item]
                country_data["universities"].append(new_uni)
    
    elif item_type == "research_institute":
        region = location_info["region"]
        
        if "regions" not in non_accessible:
            non_accessible["regions"] = {}
        if region not in non_accessible["regions"]:
            non_accessible["regions"][region] = {}
        
        if region in ["united_states", "mainland_china"]:
            if "research_institutes" not in non_accessible["regions"][region]:
                non_accessible["regions"][region]["research_institutes"] = []
            non_accessible["regions"][region]["research_institutes"].append(item)
        
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "other_countries" not in non_accessible["regions"]:
                non_accessible["regions"]["other_countries"] = {}
            if "countries" not in non_accessible["regions"]["other_countries"]:
                non_accessible["regions"]["other_countries"]["countries"] = {}
            if country_id not in non_accessible["regions"]["other_countries"]["countries"]:
                non_accessible["regions"]["other_countries"]["countries"][country_id] = {}
            
            country_data = non_accessible["regions"]["other_countries"]["countries"][country_id]
            if "research_institutes" not in country_data:
                country_data["research_institutes"] = []
            country_data["research_institutes"].append(item)
    
    elif item_type == "think_tank":
        region = location_info["region"]
        
        if "regions" not in non_accessible:
            non_accessible["regions"] = {}
        if region not in non_accessible["regions"]:
            non_accessible["regions"][region] = {}
        
        if region in ["united_states", "mainland_china"]:
            if "think_tanks" not in non_accessible["regions"][region]:
                non_accessible["regions"][region]["think_tanks"] = []
            non_accessible["regions"][region]["think_tanks"].append(item)
        
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "other_countries" not in non_accessible["regions"]:
                non_accessible["regions"]["other_countries"] = {}
            if "countries" not in non_accessible["regions"]["other_countries"]:
                non_accessible["regions"]["other_countries"]["countries"] = {}
            if country_id not in non_accessible["regions"]["other_countries"]["countries"]:
                non_accessible["regions"]["other_countries"]["countries"][country_id] = {}
            
            country_data = non_accessible["regions"]["other_countries"]["countries"][country_id]
            if "think_tanks" not in country_data:
                country_data["think_tanks"] = []
            country_data["think_tanks"].append(item)


def remove_from_accessible(config: Dict, location_info: Dict):
    """Remove item from accessible section."""
    accessible = config.get("accessible", {})
    item_type = location_info["type"]
    
    if item_type == "job_portal":
        portal_id = location_info["key"]
        if "job_portals" in accessible and portal_id in accessible["job_portals"]:
            del accessible["job_portals"][portal_id]
    
    elif item_type == "university_department":
        region = location_info["region"]
        
        if region == "other_countries":
            country_id = location_info["country_id"]
            uni_idx = location_info["uni_idx"]
            dept_idx = location_info["dept_idx"]
            
            if "regions" in accessible and "other_countries" in accessible["regions"]:
                oc_region = accessible["regions"]["other_countries"]
                if "countries" in oc_region and country_id in oc_region["countries"]:
                    country_data = oc_region["countries"][country_id]
                    if "universities" in country_data and uni_idx < len(country_data["universities"]):
                        uni = country_data["universities"][uni_idx]
                        if "departments" in uni and dept_idx < len(uni["departments"]):
                            del uni["departments"][dept_idx]
                            if not uni["departments"]:
                                del country_data["universities"][uni_idx]
        else:
            uni_idx = location_info["uni_idx"]
            dept_idx = location_info["dept_idx"]
            
            if "regions" in accessible and region in accessible["regions"]:
                region_data = accessible["regions"][region]
                if "universities" in region_data and uni_idx < len(region_data["universities"]):
                    uni = region_data["universities"][uni_idx]
                    if "departments" in uni and dept_idx < len(uni["departments"]):
                        del uni["departments"][dept_idx]
                        if not uni["departments"]:
                            del region_data["universities"][uni_idx]
    
    elif item_type == "research_institute":
        region = location_info["region"]
        inst_idx = location_info["inst_idx"]
        
        if region == "other_countries":
            country_id = location_info["country_id"]
            if "regions" in accessible and "other_countries" in accessible["regions"]:
                oc_region = accessible["regions"]["other_countries"]
                if "countries" in oc_region and country_id in oc_region["countries"]:
                    country_data = oc_region["countries"][country_id]
                    if "research_institutes" in country_data and inst_idx < len(country_data["research_institutes"]):
                        del country_data["research_institutes"][inst_idx]
        else:
            if "regions" in accessible and region in accessible["regions"]:
                region_data = accessible["regions"][region]
                if "research_institutes" in region_data and inst_idx < len(region_data["research_institutes"]):
                    del region_data["research_institutes"][inst_idx]


def remove_from_non_accessible(config: Dict, location_info: Dict):
    """Remove item from non_accessible section."""
    non_accessible = config.get("non_accessible", {})
    item_type = location_info["type"]
    
    if item_type == "job_portal":
        portal_id = location_info["key"]
        if "job_portals" in non_accessible and portal_id in non_accessible["job_portals"]:
            del non_accessible["job_portals"][portal_id]
    
    elif item_type == "university_department":
        region = location_info["region"]
        uni_idx = location_info["uni_idx"]
        dept_idx = location_info["dept_idx"]
        
        if region in ["united_states", "mainland_china"]:
            if "regions" in non_accessible and region in non_accessible["regions"]:
                region_data = non_accessible["regions"][region]
                if "universities" in region_data and uni_idx < len(region_data["universities"]):
                    uni = region_data["universities"][uni_idx]
                    if "departments" in uni and dept_idx < len(uni["departments"]):
                        del uni["departments"][dept_idx]
                        # If no departments left, remove university
                        if not uni["departments"]:
                            del region_data["universities"][uni_idx]
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "regions" in non_accessible and "other_countries" in non_accessible["regions"]:
                oc_region = non_accessible["regions"]["other_countries"]
                if "countries" in oc_region and country_id in oc_region["countries"]:
                    country_data = oc_region["countries"][country_id]
                    if "universities" in country_data and uni_idx < len(country_data["universities"]):
                        uni = country_data["universities"][uni_idx]
                        if "departments" in uni and dept_idx < len(uni["departments"]):
                            del uni["departments"][dept_idx]
                            if not uni["departments"]:
                                del country_data["universities"][uni_idx]
    
    elif item_type == "research_institute":
        region = location_info["region"]
        inst_idx = location_info["inst_idx"]
        
        if region in ["united_states", "mainland_china"]:
            if "regions" in non_accessible and region in non_accessible["regions"]:
                region_data = non_accessible["regions"][region]
                if "research_institutes" in region_data and inst_idx < len(region_data["research_institutes"]):
                    del region_data["research_institutes"][inst_idx]
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "regions" in non_accessible and "other_countries" in non_accessible["regions"]:
                oc_region = non_accessible["regions"]["other_countries"]
                if "countries" in oc_region and country_id in oc_region["countries"]:
                    country_data = oc_region["countries"][country_id]
                    if "research_institutes" in country_data and inst_idx < len(country_data["research_institutes"]):
                        del country_data["research_institutes"][inst_idx]
    
    elif item_type == "think_tank":
        region = location_info["region"]
        tank_idx = location_info["tank_idx"]
        
        if region in ["united_states", "mainland_china"]:
            if "regions" in non_accessible and region in non_accessible["regions"]:
                region_data = non_accessible["regions"][region]
                if "think_tanks" in region_data and tank_idx < len(region_data["think_tanks"]):
                    del region_data["think_tanks"][tank_idx]
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "regions" in non_accessible and "other_countries" in non_accessible["regions"]:
                oc_region = non_accessible["regions"]["other_countries"]
                if "countries" in oc_region and country_id in oc_region["countries"]:
                    country_data = oc_region["countries"][country_id]
                    if "think_tanks" in country_data and tank_idx < len(country_data["think_tanks"]):
                        del country_data["think_tanks"][tank_idx]


def add_to_accessible(config: Dict, location_info: Dict):
    """Add item to accessible section."""
    accessible = config.get("accessible", {})
    item_type = location_info["type"]
    item = location_info["item"]
    
    if item_type == "job_portal":
        portal_id = location_info["key"]
        if "job_portals" not in accessible:
            accessible["job_portals"] = {}
        accessible["job_portals"][portal_id] = item
    
    elif item_type == "university_department":
        region = location_info["region"]
        uni_data = location_info.get("uni_data", {})
        
        if "regions" not in accessible:
            accessible["regions"] = {}
        if region not in accessible["regions"]:
            accessible["regions"][region] = {}
            # Copy metadata if exists
            if region in config.get("non_accessible", {}).get("regions", {}):
                source_region = config["non_accessible"]["regions"][region]
                for meta_key in ["ranking_source", "coverage"]:
                    if meta_key in source_region:
                        accessible["regions"][region][meta_key] = source_region[meta_key]
        
        if region in ["united_states", "mainland_china"]:
            if "universities" not in accessible["regions"][region]:
                accessible["regions"][region]["universities"] = []
            
            # Find or create university
            uni_name = uni_data.get("name", "Unknown")
            uni_found = False
            for existing_uni in accessible["regions"][region]["universities"]:
                if existing_uni.get("name") == uni_name:
                    if "departments" not in existing_uni:
                        existing_uni["departments"] = []
                    existing_uni["departments"].append(item)
                    uni_found = True
                    break
            
            if not uni_found:
                new_uni = uni_data.copy()
                new_uni["departments"] = [item]
                accessible["regions"][region]["universities"].append(new_uni)
        
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "other_countries" not in accessible["regions"]:
                accessible["regions"]["other_countries"] = {}
            if "countries" not in accessible["regions"]["other_countries"]:
                accessible["regions"]["other_countries"]["countries"] = {}
            if country_id not in accessible["regions"]["other_countries"]["countries"]:
                accessible["regions"]["other_countries"]["countries"][country_id] = {}
            
            country_data = accessible["regions"]["other_countries"]["countries"][country_id]
            if "universities" not in country_data:
                country_data["universities"] = []
            
            # Find or create university
            uni_name = uni_data.get("name", "Unknown")
            uni_found = False
            for existing_uni in country_data["universities"]:
                if existing_uni.get("name") == uni_name:
                    if "departments" not in existing_uni:
                        existing_uni["departments"] = []
                    existing_uni["departments"].append(item)
                    uni_found = True
                    break
            
            if not uni_found:
                new_uni = uni_data.copy()
                new_uni["departments"] = [item]
                country_data["universities"].append(new_uni)
    
    elif item_type == "research_institute":
        region = location_info["region"]
        
        if "regions" not in accessible:
            accessible["regions"] = {}
        if region not in accessible["regions"]:
            accessible["regions"][region] = {}
        
        if region in ["united_states", "mainland_china"]:
            if "research_institutes" not in accessible["regions"][region]:
                accessible["regions"][region]["research_institutes"] = []
            accessible["regions"][region]["research_institutes"].append(item)
        
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "other_countries" not in accessible["regions"]:
                accessible["regions"]["other_countries"] = {}
            if "countries" not in accessible["regions"]["other_countries"]:
                accessible["regions"]["other_countries"]["countries"] = {}
            if country_id not in accessible["regions"]["other_countries"]["countries"]:
                accessible["regions"]["other_countries"]["countries"][country_id] = {}
            
            country_data = accessible["regions"]["other_countries"]["countries"][country_id]
            if "research_institutes" not in country_data:
                country_data["research_institutes"] = []
            country_data["research_institutes"].append(item)
    
    elif item_type == "think_tank":
        region = location_info["region"]
        
        if "regions" not in accessible:
            accessible["regions"] = {}
        if region not in accessible["regions"]:
            accessible["regions"][region] = {}
        
        if region in ["united_states", "mainland_china"]:
            if "think_tanks" not in accessible["regions"][region]:
                accessible["regions"][region]["think_tanks"] = []
            accessible["regions"][region]["think_tanks"].append(item)
        
        elif region == "other_countries":
            country_id = location_info["country_id"]
            if "other_countries" not in accessible["regions"]:
                accessible["regions"]["other_countries"] = {}
            if "countries" not in accessible["regions"]["other_countries"]:
                accessible["regions"]["other_countries"]["countries"] = {}
            if country_id not in accessible["regions"]["other_countries"]["countries"]:
                accessible["regions"]["other_countries"]["countries"][country_id] = {}
            
            country_data = accessible["regions"]["other_countries"]["countries"][country_id]
            if "think_tanks" not in country_data:
                country_data["think_tanks"] = []
            country_data["think_tanks"].append(item)


def is_chinese_url(url: str, description: str) -> bool:
    """Check if URL is for a Chinese university/institution."""
    return "(China)" in description or ".edu.cn" in url or ".cn" in url


def encode_url(url: str) -> str:
    """
    Properly encode URL, handling Chinese characters and other special characters.
    
    Only encodes the path and query parts, preserves scheme, netloc, etc.
    """
    try:
        parsed = urlparse(url)
        # Encode path and query parts
        encoded_path = quote(parsed.path, safe='/')
        encoded_query = quote(parsed.query, safe='=&') if parsed.query else ''
        encoded_fragment = quote(parsed.fragment, safe='') if parsed.fragment else ''
        
        # Reconstruct URL
        encoded = urlunparse((
            parsed.scheme,
            parsed.netloc,
            encoded_path,
            parsed.params,
            encoded_query if encoded_query else parsed.query,
            encoded_fragment if encoded_fragment else parsed.fragment
        ))
        return encoded
    except Exception as e:
        # If encoding fails, return original URL
        print(f"  ⚠ URL encoding warning: {e}")
        return url


def get_alternative_urls(base_url: str) -> List[str]:
    """
    Generate alternative URL patterns to try if the original fails.
    Common patterns for Chinese university HR portals.
    """
    alternatives = []
    parsed = urlparse(base_url)
    base_path = parsed.path.rstrip('/')
    
    # Common alternative paths for Chinese universities
    alternative_paths = [
        f"{base_path}/index.html",
        f"{base_path}/index.php",
        f"{base_path}/recruit",
        f"{base_path}/recruitment",
        f"{base_path}/jobs",
        f"{base_path}/positions",
        f"{base_path}/zhaopin",  # 招聘 (recruitment in Chinese)
        f"{base_path}/zhaopin/index.html",
        f"{base_path}/zhaopin/index.php",
    ]
    
    for alt_path in alternative_paths:
        alt_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            alt_path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        alternatives.append(alt_url)
    
    return alternatives


def check_url_with_retry(url: str, description: str, session: requests.Session, max_retries: int = MAX_RETRIES, verify_content: bool = True) -> Dict:
    """
    Check URL with retry logic and exponential backoff.
    
    Returns dict with status and other details.
    """
    result = {
        "status": "unknown",
        "status_code": None,
        "error": None,
        "content_check": None,
        "job_content_verified": False,
        "verification_score": 0,
        "final_url": None
    }
    
    is_chinese = is_chinese_url(url, description)
    
    # Encode URL if it contains non-ASCII characters
    encoded_url = encode_url(url)
    if encoded_url != url:
        print(f"  [URL encoded for special characters]")
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                print(f"  [Retry {attempt}/{max_retries - 1} after {delay}s...]")
                time.sleep(delay)
            
            response = session.get(
                encoded_url,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=True
            )
            
            # Set encoding for Chinese content
            if is_chinese:
                response.encoding = response.apparent_encoding or 'utf-8'
            
            result["status_code"] = response.status_code
            result["final_url"] = response.url
            
            if response.status_code == 200:
                result["status"] = "accessible"
                
                # Quick content check - look for job-related keywords in text
                text_content = response.text
                
                if is_chinese:
                    # Check both English and Chinese keywords for Chinese URLs
                    found_keywords_en = [kw for kw in JOB_KEYWORDS_EN if kw.lower() in text_content.lower()]
                    found_keywords_cn = [kw for kw in JOB_KEYWORDS_CN if kw in text_content]
                    found_keywords = found_keywords_en + found_keywords_cn
                else:
                    # For non-Chinese URLs, check English keywords
                    text_lower = text_content.lower()
                    found_keywords = [kw for kw in JOB_KEYWORDS_EN if kw in text_lower]
                
                if found_keywords:
                    result["content_check"] = "likely_contains_jobs"
                else:
                    result["content_check"] = "no_job_keywords_found"
                
                # Enhanced verification: check for job links and PDFs
                if verify_content:
                    job_verification = verify_job_content(text_content, response.url, session)
                    result["job_content_verified"] = job_verification["has_job_content"]
                    result["verification_score"] = job_verification["verification_score"]
                    result["verification_details"] = job_verification["details"]
                
                print(f"  ✓ Accessible (Status: {response.status_code}, Size: {len(response.text)} chars)")
                if result["content_check"] == "likely_contains_jobs":
                    # Show keywords found (limit display)
                    keywords_display = found_keywords[:5]
                    if len(found_keywords) > 5:
                        keywords_display.append(f"... and {len(found_keywords) - 5} more")
                    print(f"  ✓ Found job-related keywords: {', '.join(keywords_display)}")
                    if verify_content and result.get("job_content_verified"):
                        print(f"  ✓ Job content verified (score: {result['verification_score']}, {result.get('verification_details', '')})")
                    elif verify_content:
                        print(f"  ⚠ Job content verification failed (score: {result['verification_score']}, {result.get('verification_details', '')})")
                else:
                    print(f"  ⚠ No job-related keywords found (may still be a job page)")
                return result
            
            elif response.status_code in [301, 302, 303, 307, 308]:
                result["status"] = "redirect"
                result["error"] = f"Redirected to: {response.url}"
                print(f"  ⚠ Redirected (Status: {response.status_code})")
                print(f"  Final URL: {response.url}")
                return result
            
            elif response.status_code == 404:
                # Don't retry on 404
                result["status"] = "not_found"
                result["error"] = "Page not found (404)"
                print(f"  ✗ Not found (404)")
                return result
            
            elif response.status_code == 403:
                # Don't retry on 403
                result["status"] = "forbidden"
                result["error"] = "Access forbidden (403)"
                print(f"  ✗ Forbidden (403)")
                return result
            
            else:
                # Retry on other HTTP errors
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"
                if attempt == max_retries - 1:
                    print(f"  ✗ Error (Status: {response.status_code})")
                    return result
        
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                result["status"] = "timeout"
                result["error"] = "Request timed out"
                print(f"  ✗ Timeout")
                return result
        
        except requests.exceptions.ConnectionError as e:
            if attempt == max_retries - 1:
                result["status"] = "connection_error"
                result["error"] = f"Connection error: {str(e)}"
                print(f"  ✗ Connection error")
                return result
        
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                result["status"] = "error"
                result["error"] = f"Request error: {str(e)}"
                print(f"  ✗ Error: {str(e)}")
                return result
    
    return result


def check_url(url: str, description: str, session: Optional[requests.Session] = None, verify_content: bool = True) -> Dict:
    """
    Check if URL is accessible, trying original and alternative patterns.
    
    Returns dict with status and other details.
    """
    is_chinese = is_chinese_url(url, description)
    
    print(f"Checking: {description}")
    print(f"  URL: {url}")
    if is_chinese:
        print(f"  [Chinese URL - checking for Chinese keywords]")
    
    # Use provided session or create a new one
    if session is None:
        session = requests.Session()
        use_session = False
    else:
        use_session = True
    
    # Try original URL first
    result = check_url_with_retry(url, description, session, verify_content=verify_content)
    
    # If original URL failed and it's a Chinese URL, try alternative patterns
    if result["status"] != "accessible" and is_chinese:
        alternative_urls = get_alternative_urls(url)
        print(f"  [Trying {len(alternative_urls)} alternative URL patterns...]")
        
        for alt_url in alternative_urls[:5]:  # Limit to 5 alternatives to avoid too many requests
            print(f"  Trying alternative: {alt_url}")
            alt_result = check_url_with_retry(alt_url, description, session, max_retries=1, verify_content=False)
            
            if alt_result["status"] == "accessible":
                # Verify content for the working alternative
                if verify_content:
                    try:
                        response = session.get(alt_url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
                        if response.status_code == 200:
                            job_verification = verify_job_content(response.text, response.url, session)
                            alt_result["job_content_verified"] = job_verification["has_job_content"]
                            alt_result["verification_score"] = job_verification["verification_score"]
                            alt_result["verification_details"] = job_verification["details"]
                    except:
                        pass
                
                result = alt_result
                result["original_url"] = url
                result["working_url"] = alt_url
                print(f"  ✓ Found working alternative URL!")
                break
            time.sleep(0.5)  # Small delay between alternative attempts
    
    # Close session if we created it
    if not use_session:
        session.close()
    
    print()
    return result


def verify_urls(config: Dict, check_accessible: bool = True, verify_content: bool = True, remove_invalid: bool = True) -> Tuple[Dict, List[Dict]]:
    """
    Verify URLs in accessible and/or non_accessible sections.
    
    Rule: Only URLs containing relevant job information should be in the accessible section.
    URLs that don't contain job listings will be moved to non_accessible.
    
    Args:
        config: Configuration dictionary
        check_accessible: If True, verify URLs in accessible section
        verify_content: If True, verify URLs contain job listings
        remove_invalid: If True, move invalid URLs from accessible to non_accessible
    
    Returns (updated_config, list of results)
    """
    all_urls = []
    
    # Extract URLs from accessible section
    if check_accessible:
        accessible_urls = extract_urls_from_accessible(config)
        all_urls.extend(accessible_urls)
        print(f"  Found {len(accessible_urls)} URLs in accessible section")
    
    # Extract URLs from non_accessible section
    non_accessible_urls = extract_urls_from_non_accessible(config)
    all_urls.extend(non_accessible_urls)
    print(f"  Found {len(non_accessible_urls)} URLs in non_accessible section")
    
    total_urls = len(all_urls)
    
    print("=" * 80)
    print(f"URL Verification")
    print(f"  🔍 URLs to check: {total_urls}")
    print(f"  ⚙️  Options: check_accessible={check_accessible}, verify_content={verify_content}, remove_invalid={remove_invalid}")
    print("=" * 80)
    print()
    
    results = []
    
    if total_urls == 0:
        print("No URLs to verify.")
        print()
        return config, results
    
    # Create a session for better performance (connection reuse)
    session = requests.Session()
    session.headers.update(HEADERS)
    
    try:
        # Verify URLs
        moved_count = 0
        removed_count = 0
        
        for i, (url, source_type, description, location_info) in enumerate(all_urls, 1):
            category = location_info["category"]
            print(f"[{i}/{total_urls}] {category.upper()} - {source_type.upper()}")
            
            result = check_url(url, description, session=session, verify_content=verify_content)
            result["url"] = url
            result["description"] = description
            result["source_type"] = source_type
            result["location_info"] = location_info
            result["category"] = category
            results.append(result)
            
            # Handle results based on category
            if category == "non_accessible":
                # If accessible, move from non_accessible to accessible
                if result["status"] == "accessible":
                    # Only move if content is verified (if verification enabled)
                    if not verify_content or result.get("job_content_verified", True):
                        remove_from_non_accessible(config, location_info)
                        add_to_accessible(config, location_info)
                        moved_count += 1
                        print(f"  → Moved to accessible section")
                        
                        # Update URL if we found a working alternative
                        if "working_url" in result:
                            location_info["item"]["url"] = result["working_url"]
                            print(f"  → Updated URL to working alternative")
                    else:
                        print(f"  ⚠ Accessible but no job content - keeping in non_accessible")
            
            elif category == "accessible":
                # If not accessible or no job content, move from accessible to non_accessible
                should_move = False
                reason = ""
                
                if result["status"] != "accessible":
                    should_move = True
                    reason = f"Status: {result['status']}"
                elif verify_content and remove_invalid and not result.get("job_content_verified", False):
                    should_move = True
                    reason = f"No job content verified (score: {result.get('verification_score', 0)})"
                
                if should_move and remove_invalid:
                    remove_from_accessible(config, location_info)
                    add_to_non_accessible(config, location_info)
                    removed_count += 1
                    print(f"  → Moved to non_accessible section ({reason})")
            
            # Rate limiting
            if i < len(all_urls):
                time.sleep(DELAY_BETWEEN_REQUESTS)
        
        if moved_count > 0:
            print()
            print(f"✓ Moved {moved_count} URLs from non_accessible to accessible")
        if removed_count > 0:
            print()
            print(f"✗ Moved {removed_count} invalid URLs from accessible to non_accessible")
        print()
    finally:
        session.close()
    
    return config, results


def print_summary(results: List[Dict], total_urls: int):
    """Print verification summary."""
    print()
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    accessible_results = [r for r in results if r["category"] == "accessible"]
    non_accessible_results = [r for r in results if r["category"] == "non_accessible"]
    
    newly_accessible = sum(1 for r in non_accessible_results if r["status"] == "accessible" and r.get("job_content_verified", True))
    removed_from_accessible = sum(1 for r in accessible_results if r["status"] != "accessible" or not r.get("job_content_verified", True))
    not_found = sum(1 for r in results if r["status"] == "not_found")
    forbidden = sum(1 for r in results if r["status"] == "forbidden")
    errors = sum(1 for r in results if r["status"] not in ["accessible", "redirect"])
    
    print(f"Total URLs checked: {total_urls}")
    print(f"  From accessible section: {len(accessible_results)}")
    print(f"  From non_accessible section: {len(non_accessible_results)}")
    print()
    print(f"✓ Moved to accessible: {newly_accessible}")
    print(f"✗ Moved to non_accessible: {removed_from_accessible}")
    print(f"✗ Not Found (404): {not_found}")
    print(f"✗ Forbidden (403): {forbidden}")
    print(f"✗ Other Errors: {errors - not_found - forbidden}")
    print()
    
    # List newly accessible URLs
    if newly_accessible > 0:
        print("NEWLY VERIFIED ACCESSIBLE URLs (moved to accessible section):")
        print("-" * 80)
        for r in non_accessible_results:
            if r["status"] == "accessible" and r.get("job_content_verified", True):
                content_status = "✓" if r.get("content_check") == "likely_contains_jobs" else "⚠"
                print(f"{content_status} {r['description']}")
                print(f"    {r['url']}")
                if r.get("verification_details"):
                    print(f"    Details: {r['verification_details']}")
        print()
    
    # List moved URLs (from accessible to non_accessible)
    if removed_from_accessible > 0:
        print("MOVED FROM ACCESSIBLE TO NON_ACCESSIBLE:")
        print("-" * 80)
        for r in accessible_results:
            if r["status"] != "accessible" or not r.get("job_content_verified", True):
                print(f"✗ {r['description']}")
                print(f"    {r['url']}")
                if r["status"] != "accessible":
                    print(f"    Status: {r['status']} - {r.get('error', '')}")
                else:
                    print(f"    Reason: No job content verified (score: {r.get('verification_score', 0)})")
        print()
    
    # List problematic URLs in non_accessible
    problematic_non_accessible = [r for r in non_accessible_results if r["status"] != "accessible"]
    if problematic_non_accessible:
        print("PROBLEMATIC URLs (still in non_accessible):")
        print("-" * 80)
        for r in problematic_non_accessible:
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify URLs in scraping_sources.json")
    parser.add_argument("--check-accessible", action="store_true", default=True,
                        help="Check URLs in accessible section (default: True)")
    parser.add_argument("--no-check-accessible", dest="check_accessible", action="store_false",
                        help="Don't check URLs in accessible section")
    parser.add_argument("--verify-content", action="store_true", default=True,
                        help="Verify URLs contain job listings (default: True)")
    parser.add_argument("--no-verify-content", dest="verify_content", action="store_false",
                        help="Don't verify job content")
    parser.add_argument("--remove-invalid", action="store_true", default=True,
                        help="Remove invalid URLs from accessible section (default: True)")
    parser.add_argument("--no-remove-invalid", dest="remove_invalid", action="store_false",
                        help="Don't remove invalid URLs")
    
    args = parser.parse_args()
    
    print("Loading configuration...")
    config = load_master_config()
    print(f"Configuration loaded from: {CONFIG_FILE}")
    print()
    
    # Verify URLs and update config
    updated_config, results = verify_urls(
        config,
        check_accessible=args.check_accessible,
        verify_content=args.verify_content,
        remove_invalid=args.remove_invalid
    )
    
    total_urls = len(results)
    
    print_summary(results, total_urls)
    
    # Save updated config
    save_config(updated_config)
    print(f"Configuration updated and saved to: {CONFIG_FILE}")
    print()
    
    # Exit with error code if there are issues
    errors = sum(1 for r in results if r["status"] not in ["accessible", "redirect"])
    if errors > 0:
        print(f"⚠ Warning: {errors} URLs have issues")
        return 1
    else:
        print("✓ All checked URLs are accessible!")
        return 0


if __name__ == "__main__":
    exit(main())
