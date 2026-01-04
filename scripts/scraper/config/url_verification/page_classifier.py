"""Page Classifier - Classify web page types for URL verification.

This module classifies web pages to determine if they are job portals,
faculty directories, department pages, or other types.
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class PageType(Enum):
    """Types of pages that can be classified."""
    
    JOB_PORTAL = "job_portal"  # Career/jobs page with listings
    FACULTY_DIRECTORY = "faculty_directory"  # List of current faculty
    DEPARTMENT_PAGE = "department_page"  # General department info
    NEWS_ANNOUNCEMENTS = "news_announcements"  # News or blog posts
    SINGLE_JOB_POSTING = "single_job_posting"  # Single job detail page
    EXTERNAL_SYSTEM = "external_system"  # External HR system (ICIMS, Workday)
    ERROR_PAGE = "error_page"  # 404, 403, or other error
    UNKNOWN = "unknown"  # Cannot determine type


# Keywords for each page type
JOB_PORTAL_KEYWORDS = [
    "career",
    "careers",
    "jobs",
    "employment",
    "opportunities",
    "openings",
    "vacancies",
    "positions",
    "recruitment",
    "hiring",
    "academic positions",
    "faculty positions",
]

FACULTY_DIRECTORY_KEYWORDS = [
    "faculty directory",
    "faculty members",
    "our faculty",
    "our team",
    "staff directory",
    "people",
    "directory",
    "faculty profiles",
]

DEPARTMENT_PAGE_KEYWORDS = [
    "about us",
    "about the department",
    "our department",
    "mission",
    "research areas",
    "programs",
    "courses",
    "undergraduate",
    "graduate",
]

NEWS_KEYWORDS = [
    "news",
    "announcements",
    "blog",
    "events",
    "seminars",
    "colloquia",
]

ERROR_KEYWORDS = [
    "404",
    "not found",
    "page not found",
    "403",
    "forbidden",
    "access denied",
    "error",
]


def classify_page_type(
    html_content: str,
    url: str = "",
    title: str = "",
) -> Tuple[PageType, float, Dict[str, any]]:
    """Classify the type of web page.
    
    Args:
        html_content: The HTML content to analyze
        url: The URL of the page (optional)
        title: The page title (optional)
        
    Returns:
        Tuple of (PageType, confidence_score, details_dict)
        confidence_score is 0.0-1.0
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract title if not provided
    if not title:
        title_elem = soup.find("title")
        title = title_elem.get_text() if title_elem else ""
    
    # Extract meta description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc.get("content") if meta_desc else ""
    
    # Get all text content
    page_text = soup.get_text().lower()
    title_lower = title.lower()
    desc_lower = description.lower()
    url_lower = url.lower()
    
    # Combine for analysis
    combined_text = f"{title_lower} {desc_lower} {page_text[:2000]}"
    
    # Initialize scores for each type
    scores = {
        PageType.ERROR_PAGE: 0.0,
        PageType.EXTERNAL_SYSTEM: 0.0,
        PageType.JOB_PORTAL: 0.0,
        PageType.SINGLE_JOB_POSTING: 0.0,
        PageType.FACULTY_DIRECTORY: 0.0,
        PageType.DEPARTMENT_PAGE: 0.0,
        PageType.NEWS_ANNOUNCEMENTS: 0.0,
    }
    
    details = {
        "title": title,
        "url": url,
        "keyword_matches": {},
    }
    
    # 1. Check for error page
    error_matches = sum(1 for kw in ERROR_KEYWORDS if kw in combined_text)
    if error_matches > 0 or "404" in title_lower or "403" in title_lower:
        scores[PageType.ERROR_PAGE] = min(1.0, 0.5 + error_matches * 0.2)
        details["keyword_matches"]["error"] = error_matches
    
    # 2. Check for external system
    external_systems = [
        "icims.com",
        "workday.com",
        "myworkdayjobs.com",
        "peoplesoft",
        "successfactors",
        "taleo",
        "lever.co",
        "greenhouse.io",
    ]
    for system in external_systems:
        if system in url_lower:
            scores[PageType.EXTERNAL_SYSTEM] = 1.0
            details["external_system"] = system
            break
    
    # 3. Check for job portal
    job_matches = sum(1 for kw in JOB_PORTAL_KEYWORDS if kw in combined_text)
    url_job_matches = sum(1 for kw in ["career", "job", "employment", "position"] if kw in url_lower)
    
    # Count job-like links
    job_links = len(soup.find_all("a", href=True, string=re.compile(r"(professor|postdoc|faculty|position)", re.I)))
    
    job_score = 0.0
    if job_matches >= 3:
        job_score += 0.4
    if url_job_matches >= 1:
        job_score += 0.3
    if job_links >= 3:
        job_score += 0.3
    
    scores[PageType.JOB_PORTAL] = min(1.0, job_score)
    details["keyword_matches"]["job_portal"] = job_matches
    details["job_links_count"] = job_links
    
    # 4. Check for single job posting
    # Indicators: specific position title in h1, detailed job description, single application link
    h1 = soup.find("h1")
    has_position_title = False
    if h1:
        h1_text = h1.get_text().lower()
        position_keywords = ["professor", "postdoc", "lecturer", "faculty position", "research"]
        has_position_title = any(kw in h1_text for kw in position_keywords)
    
    apply_buttons = len(soup.find_all(["a", "button"], string=re.compile(r"apply", re.I)))
    long_description = len(page_text) > 1000
    
    if has_position_title and (apply_buttons >= 1 or long_description):
        scores[PageType.SINGLE_JOB_POSTING] = 0.7 if apply_buttons >= 1 else 0.5
        details["has_position_title"] = True
        details["apply_buttons"] = apply_buttons
    
    # 5. Check for faculty directory
    faculty_matches = sum(1 for kw in FACULTY_DIRECTORY_KEYWORDS if kw in combined_text)
    
    # Count email addresses (faculty listings usually have many)
    emails = len(soup.find_all("a", href=re.compile(r"mailto:", re.I)))
    
    # Count profile-like structures
    profiles = len(soup.find_all(["div", "li"], class_=re.compile(r"(faculty|profile|person|member)", re.I)))
    
    faculty_score = 0.0
    if faculty_matches >= 2:
        faculty_score += 0.4
    if emails >= 5:
        faculty_score += 0.3
    if profiles >= 3:
        faculty_score += 0.3
    
    scores[PageType.FACULTY_DIRECTORY] = min(1.0, faculty_score)
    details["keyword_matches"]["faculty_directory"] = faculty_matches
    details["email_count"] = emails
    details["profile_count"] = profiles
    
    # 6. Check for department page
    dept_matches = sum(1 for kw in DEPARTMENT_PAGE_KEYWORDS if kw in combined_text)
    scores[PageType.DEPARTMENT_PAGE] = min(1.0, dept_matches * 0.15)
    details["keyword_matches"]["department"] = dept_matches
    
    # 7. Check for news/announcements
    news_matches = sum(1 for kw in NEWS_KEYWORDS if kw in combined_text)
    scores[PageType.NEWS_ANNOUNCEMENTS] = min(1.0, news_matches * 0.2)
    details["keyword_matches"]["news"] = news_matches
    
    # Determine final classification
    max_score = max(scores.values())
    
    if max_score < 0.3:
        return PageType.UNKNOWN, max_score, details
    
    # Get type with highest score
    page_type = max(scores, key=scores.get)
    confidence = scores[page_type]
    
    details["all_scores"] = {pt.value: score for pt, score in scores.items()}
    
    return page_type, confidence, details


def is_job_portal(page_type: PageType, confidence: float) -> bool:
    """Check if page is classified as a job portal with sufficient confidence.
    
    Args:
        page_type: The classified page type
        confidence: The confidence score (0.0-1.0)
        
    Returns:
        True if page is a job portal with confidence >= 0.5
    """
    return page_type == PageType.JOB_PORTAL and confidence >= 0.5


def is_useful_for_jobs(page_type: PageType, confidence: float) -> bool:
    """Check if page is useful for finding jobs.
    
    Args:
        page_type: The classified page type
        confidence: The confidence score (0.0-1.0)
        
    Returns:
        True if page is job portal or single posting with sufficient confidence
    """
    useful_types = [PageType.JOB_PORTAL, PageType.SINGLE_JOB_POSTING]
    return page_type in useful_types and confidence >= 0.4
