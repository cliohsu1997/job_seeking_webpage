"""Content Validator - Extract and validate job listings from HTML pages.

This module provides functions to extract job listings from HTML pages and validate
whether they contain the critical fields needed for the job aggregator.
"""

import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# Job-related keywords for content detection
JOB_KEYWORDS = [
    "professor",
    "assistant professor",
    "associate professor",
    "tenure",
    "postdoc",
    "postdoctoral",
    "lecturer",
    "faculty",
    "position",
    "opening",
    "vacancy",
    "hiring",
    "recruitment",
    "academic",
    "research",
    "economist",
]

# Position type keywords
POSITION_TYPES = [
    "tenure-track",
    "tenured",
    "visiting",
    "postdoc",
    "lecturer",
    "instructor",
    "research",
    "teaching",
    "clinical",
    "adjunct",
]

# Department/field keywords
DEPARTMENT_KEYWORDS = [
    "economics",
    "business",
    "finance",
    "management",
    "marketing",
    "accounting",
]

# Deadline keywords
DEADLINE_KEYWORDS = [
    "deadline",
    "apply by",
    "closing date",
    "application deadline",
    "review date",
    "priority deadline",
]


def extract_job_listings(
    html_content: str,
    base_url: str = "",
) -> List[Dict[str, any]]:
    """Extract potential job listings from HTML content.
    
    Args:
        html_content: The HTML content to parse
        base_url: Base URL for resolving relative links
        
    Returns:
        List of dictionaries containing extracted job information
    """
    soup = BeautifulSoup(html_content, "html.parser")
    listings = []
    
    # Strategy 1: Look for common job listing containers
    job_containers = []
    
    # Try various common container patterns
    patterns = [
        {"class_": re.compile(r"job", re.I)},
        {"class_": re.compile(r"position", re.I)},
        {"class_": re.compile(r"vacancy", re.I)},
        {"class_": re.compile(r"opening", re.I)},
        {"class_": re.compile(r"posting", re.I)},
    ]
    
    for pattern in patterns:
        job_containers.extend(soup.find_all(["div", "article", "li", "section"], **pattern))
    
    # Strategy 2: Look for links with job-related keywords
    job_links = soup.find_all("a", href=True)
    
    # Process containers
    for container in job_containers:
        listing = _extract_from_container(container, base_url)
        if listing and listing.get("title"):
            listings.append(listing)
    
    # Process standalone links if no containers found
    if not listings:
        for link in job_links:
            text = link.get_text(strip=True).lower()
            if any(keyword in text for keyword in JOB_KEYWORDS):
                listing = {
                    "title": link.get_text(strip=True),
                    "url": _resolve_url(link.get("href"), base_url),
                }
                # Try to extract additional info from nearby text
                parent = link.parent
                if parent:
                    parent_text = parent.get_text()
                    listing["context"] = parent_text[:200]
                listings.append(listing)
    
    # Deduplicate by title
    seen_titles = set()
    unique_listings = []
    for listing in listings:
        title = listing.get("title", "").strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_listings.append(listing)
    
    return unique_listings


def _extract_from_container(
    container: BeautifulSoup,
    base_url: str,
) -> Optional[Dict[str, any]]:
    """Extract job information from a container element."""
    listing = {}
    
    # Extract title
    title_elem = container.find(["h1", "h2", "h3", "h4", "h5", "a"])
    if title_elem:
        listing["title"] = title_elem.get_text(strip=True)
    
    # Extract link
    link_elem = container.find("a", href=True)
    if link_elem:
        listing["url"] = _resolve_url(link_elem.get("href"), base_url)
    
    # Extract full text for analysis
    full_text = container.get_text()
    listing["full_text"] = full_text[:500]  # First 500 chars
    
    # Try to detect position type
    text_lower = full_text.lower()
    for pos_type in POSITION_TYPES:
        if pos_type in text_lower:
            listing["position_type"] = pos_type
            break
    
    # Try to detect department
    for dept in DEPARTMENT_KEYWORDS:
        if dept in text_lower:
            listing["department"] = dept
            break
    
    # Try to detect deadline
    for deadline_kw in DEADLINE_KEYWORDS:
        if deadline_kw in text_lower:
            # Extract date after keyword
            match = re.search(
                rf"{deadline_kw}[:\s]+([A-Za-z]+\s+\d{{1,2}},?\s+\d{{4}}|\d{{1,2}}/\d{{1,2}}/\d{{2,4}})",
                full_text,
                re.IGNORECASE,
            )
            if match:
                listing["deadline"] = match.group(1)
                break
    
    # Look for application link/email
    apply_link = container.find("a", href=re.compile(r"apply", re.I))
    if apply_link:
        listing["application_link"] = _resolve_url(apply_link.get("href"), base_url)
    
    email = container.find("a", href=re.compile(r"mailto:", re.I))
    if email:
        listing["contact_email"] = email.get("href").replace("mailto:", "")
    
    return listing if listing else None


def _resolve_url(url: str, base_url: str) -> str:
    """Resolve relative URL to absolute URL."""
    if not url:
        return ""
    
    # Already absolute
    if url.startswith(("http://", "https://")):
        return url
    
    # Ignore non-http protocols
    if url.startswith(("mailto:", "javascript:", "tel:", "#")):
        return url
    
    if not base_url:
        return url
    
    # Remove trailing slash from base
    base_url = base_url.rstrip("/")
    
    # Handle relative URLs
    if url.startswith("/"):
        # Root-relative
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}{url}"
    else:
        # Path-relative
        return f"{base_url}/{url}"


def validate_critical_fields(listing: Dict[str, any]) -> Tuple[bool, List[str]]:
    """Validate that a listing contains critical fields.
    
    Critical fields:
    1. Job title (must be present and specific)
    2. At least one position detail (type, department, deadline, or application link)
    
    Args:
        listing: Dictionary containing extracted job information
        
    Returns:
        Tuple of (is_valid, list of missing/invalid fields)
    """
    issues = []
    
    # Check title
    title = listing.get("title", "").strip()
    if not title:
        issues.append("Missing job title")
    elif len(title) < 5:
        issues.append(f"Title too short: '{title}'")
    elif title.lower() in ["faculty", "research", "position", "opening"]:
        issues.append(f"Title too generic: '{title}'")
    
    # Check for at least one position detail
    has_detail = any([
        listing.get("position_type"),
        listing.get("department"),
        listing.get("deadline"),
        listing.get("application_link"),
        listing.get("contact_email"),
    ])
    
    if not has_detail:
        issues.append("No position details found (type/department/deadline/contact)")
    
    is_valid = len(issues) == 0
    return is_valid, issues


def calculate_content_quality_score(
    listings: List[Dict[str, any]],
    page_html: str = "",
) -> Dict[str, any]:
    """Calculate content quality score (0-100) for extracted listings.
    
    Scoring breakdown:
    - Job Titles Found (30 pts): 5+ titles = 30, 3-4 = 20, 1-2 = 10
    - Position Details (25 pts): All fields = 25, type+dept = 18, dept only = 10
    - Application Links (20 pts): Apply links = 20, Email only = 10, None = 0
    - Job Descriptions (15 pts): Full text = 15, Brief = 8, Titles only = 0
    - Freshness (10 pts): <1 week = 10, <1 month = 5, Old/none = 0
    
    Args:
        listings: List of extracted job listings
        page_html: Full page HTML for additional analysis
        
    Returns:
        Dictionary with score, breakdown, and recommendation
    """
    score = 0
    breakdown = {}
    
    # 1. Job Titles Found (30 pts)
    num_listings = len(listings)
    if num_listings >= 5:
        title_score = 30
    elif num_listings >= 3:
        title_score = 20
    elif num_listings >= 1:
        title_score = 10
    else:
        title_score = 0
    
    score += title_score
    breakdown["job_titles"] = {
        "score": title_score,
        "max": 30,
        "count": num_listings,
    }
    
    # 2. Position Details (25 pts)
    if not listings:
        details_score = 0
        avg_fields = 0
    else:
        total_fields = 0
        for listing in listings:
            fields = sum([
                bool(listing.get("position_type")),
                bool(listing.get("department")),
                bool(listing.get("deadline")),
            ])
            total_fields += fields
        
        avg_fields = total_fields / len(listings)
        if avg_fields >= 2.5:
            details_score = 25
        elif avg_fields >= 1.5:
            details_score = 18
        elif avg_fields >= 0.5:
            details_score = 10
        else:
            details_score = 0
    
    score += details_score
    breakdown["position_details"] = {
        "score": details_score,
        "max": 25,
        "avg_fields": round(avg_fields, 2),
    }
    
    # 3. Application Links (20 pts)
    apply_links = sum(1 for l in listings if l.get("application_link"))
    emails = sum(1 for l in listings if l.get("contact_email"))
    
    if num_listings > 0:
        if apply_links >= num_listings * 0.5:
            link_score = 20
        elif emails >= num_listings * 0.5:
            link_score = 10
        elif apply_links > 0 or emails > 0:
            link_score = 5
        else:
            link_score = 0
    else:
        link_score = 0
    
    score += link_score
    breakdown["application_links"] = {
        "score": link_score,
        "max": 20,
        "apply_links": apply_links,
        "emails": emails,
    }
    
    # 4. Job Descriptions (15 pts)
    if not listings:
        desc_score = 0
        avg_length = 0
    else:
        total_length = sum(len(l.get("full_text", "")) for l in listings)
        avg_length = total_length / len(listings)
        
        if avg_length >= 200:
            desc_score = 15
        elif avg_length >= 50:
            desc_score = 8
        else:
            desc_score = 0
    
    score += desc_score
    breakdown["job_descriptions"] = {
        "score": desc_score,
        "max": 15,
        "avg_length": int(avg_length),
    }
    
    # 5. Freshness (10 pts)
    # Check for recent dates in listings
    recent_count = 0
    if num_listings > 0:
        for listing in listings:
            deadline = listing.get("deadline", "")
            if deadline:
                # Simple heuristic: if has deadline text, likely recent
                recent_count += 1
        
        if recent_count >= num_listings * 0.5:
            fresh_score = 10
        elif recent_count >= num_listings * 0.25:
            fresh_score = 5
        else:
            fresh_score = 0
    else:
        fresh_score = 0
    
    score += fresh_score
    breakdown["freshness"] = {
        "score": fresh_score,
        "max": 10,
        "recent_count": recent_count,
    }
    
    # Determine recommendation
    if score >= 80:
        recommendation = "excellent"
        action = "keep"
    elif score >= 60:
        recommendation = "good"
        action = "keep"
    elif score >= 40:
        recommendation = "marginal"
        action = "review"
    else:
        recommendation = "poor"
        action = "move_to_non_accessible"
    
    return {
        "score": score,
        "max_score": 100,
        "recommendation": recommendation,
        "action": action,
        "breakdown": breakdown,
        "num_listings": num_listings,
    }
