"""URL Discovery Tool - Find alternative career/jobs URLs for universities.

This module helps discover correct URLs for finding job listings at universities
by trying common career page paths and searching for job portals.
"""

import requests
import logging
from typing import List, Tuple
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


# Common paths where universities host job listings
COMMON_PATHS = [
    # Direct paths
    "/careers",
    "/jobs",
    "/employment",
    "/opportunities",
    "/career-opportunities",
    "/job-opportunities",
    "/hiring",
    "/apply",
    "/positions",
    "/openings",
    "/vacancies",
    "/faculty-positions",
    "/faculty-opportunities",
    "/open-positions",
    "/faculty-search",
    "/faculty-recruitment",
    "/join",
    "/work-with-us",
    "/join-us",
    "/recruiting",
    "/recruitment",
    "/hr/careers",
    "/about/careers",
    "/about/employment",
    "/humanresources/careers",
]

# Common subdomains for career portals
COMMON_SUBDOMAINS = [
    "careers",
    "jobs",
    "recruit",
    "hr",
    "employment",
    "apply",
]


def extract_domain(url: str) -> str:
    """Extract base domain from URL.
    
    Args:
        url: Full URL
        
    Returns:
        Base domain (scheme + netloc)
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def test_url_accessibility(url: str, timeout: int = 5) -> Tuple[bool, int, str]:
    """Test if a URL is accessible.
    
    Args:
        url: URL to test
        timeout: Request timeout
        
    Returns:
        Tuple of (is_accessible, status_code, error_message)
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return True, response.status_code, ""
    except Exception as e:
        return False, 0, str(e)


def discover_urls(
    institution_url: str,
    test_paths: bool = True,
    test_subdomains: bool = True,
    timeout: int = 5,
) -> List[str]:
    """Discover potential career/jobs URLs for an institution.
    
    Args:
        institution_url: The institution's main URL or department URL
        test_paths: Whether to test common paths
        test_subdomains: Whether to test common subdomains
        timeout: Request timeout in seconds
        
    Returns:
        List of discovered accessible URLs
    """
    base_domain = extract_domain(institution_url)
    parsed = urlparse(institution_url)
    
    candidates = []
    discovered = []
    
    # Test common paths
    if test_paths:
        for path in COMMON_PATHS:
            candidates.append(urljoin(base_domain, path))
    
    # Test common subdomains
    if test_subdomains:
        for subdomain in COMMON_SUBDOMAINS:
            # Replace existing subdomain or add new one
            host_parts = parsed.netloc.split(".")
            
            # Try prepending subdomain
            alt_domain = f"{subdomain}.{parsed.netloc}"
            candidates.append(f"{parsed.scheme}://{alt_domain}/")
            
            # Try replacing first subdomain
            if len(host_parts) > 2:
                host_parts[0] = subdomain
                alt_domain = ".".join(host_parts)
                candidates.append(f"{parsed.scheme}://{alt_domain}/")
    
    # Test all candidates
    for candidate in set(candidates):  # Remove duplicates
        try:
            is_accessible, status, error = test_url_accessibility(candidate, timeout)
            if is_accessible and status < 400:
                discovered.append(candidate)
                logger.info(f"✓ Found: {candidate}")
            else:
                logger.debug(f"✗ Not accessible: {candidate} (status: {status})")
        except Exception as e:
            logger.debug(f"✗ Error testing {candidate}: {e}")
    
    return discovered


def suggest_replacement_urls(
    problematic_urls: List[Tuple[str, str]],  # List of (institution_name, problematic_url)
    timeout: int = 5,
) -> List[dict]:
    """Suggest replacement URLs for problematic URLs.
    
    Args:
        problematic_urls: List of (institution_name, url) tuples
        timeout: Request timeout in seconds
        
    Returns:
        List of suggestions with alternatives
    """
    suggestions = []
    
    for institution_name, prob_url in problematic_urls:
        # Try to fix common mistakes
        parsed = urlparse(prob_url)
        base_domain = f"{parsed.scheme}://{parsed.netloc}"
        
        # Common fixes for US universities
        alternatives = []
        
        # If it's a department subdomain, try main domain
        if parsed.netloc.startswith("economics.") or parsed.netloc.startswith("business."):
            # Extract main domain
            parts = parsed.netloc.split(".")
            if len(parts) > 2:
                # Try main domain's careers page
                main_domain = ".".join(parts[1:])
                alternatives.append(f"{parsed.scheme}://{main_domain}/careers")
                alternatives.append(f"{parsed.scheme}://{main_domain}/jobs")
                alternatives.append(f"{parsed.scheme}://{main_domain}/")
        
        # Discover alternative paths on the same domain
        discovered = discover_urls(prob_url, test_paths=True, test_subdomains=True, timeout=timeout)
        alternatives.extend(discovered)
        
        suggestions.append({
            "institution": institution_name,
            "problematic_url": prob_url,
            "alternatives": alternatives[:5],  # Top 5 alternatives
        })
    
    return suggestions


# Predefined better URLs for known institutions
INSTITUTION_URLS = {
    "Princeton": [
        "https://www.princeton.edu/careers",
        "https://www.princeton.edu/",
        "https://www.princeton.edu/academics/departments",
    ],
    "UPenn": [
        "https://www.upenn.edu/careers",
        "https://careers.upenn.edu/",
        "https://www.upenn.edu/",
    ],
    "Columbia": [
        "https://www.columbia.edu/careers",
        "https://careers.columbia.edu/",
        "https://www.columbia.edu/",
    ],
    "NYU": [
        "https://www.nyu.edu/careers",
        "https://careers.nyu.edu/",
        "https://www.nyu.edu/",
    ],
    "University of Chicago": [
        "https://www.uchicago.edu/careers",
        "https://careers.uchicago.edu/",
        "https://www.uchicago.edu/",
    ],
    "MIT": [
        "https://careers.mit.edu/",
        "https://www.mit.edu/",
    ],
    "Stanford": [
        "https://careers.stanford.edu/",
        "https://www.stanford.edu/",
    ],
    "Harvard": [
        "https://www.harvard.edu/careers",
        "https://www.harvard.edu/",
    ],
    "Yale": [
        "https://www.yale.edu/careers",
        "https://www.yale.edu/",
    ],
    "Michigan": [
        "https://www.umich.edu/careers",
        "https://careers.umich.edu/",
        "https://www.umich.edu/",
    ],
    "Wisconsin-Madison": [
        "https://www.wisc.edu/careers",
        "https://careers.wisc.edu/",
        "https://www.wisc.edu/",
    ],
    "UC Berkeley": [
        "https://www.berkeley.edu/careers",
        "https://careers.berkeley.edu/",
        "https://www.berkeley.edu/",
    ],
}


def get_predefined_urls(institution_name: str) -> List[str]:
    """Get predefined good URLs for known institutions.
    
    Args:
        institution_name: Institution name (key in INSTITUTION_URLS)
        
    Returns:
        List of URLs to try
    """
    return INSTITUTION_URLS.get(institution_name, [])


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    problematic = [
        ("Princeton Economics", "https://economics.princeton.edu/"),
        ("UPenn Economics", "https://economics.upenn.edu/"),
    ]
    
    suggestions = suggest_replacement_urls(problematic, timeout=5)
    
    for suggestion in suggestions:
        print(f"\n{suggestion['institution']}:")
        print(f"  Problematic: {suggestion['problematic_url']}")
        print(f"  Alternatives:")
        for alt in suggestion['alternatives']:
            print(f"    - {alt}")
