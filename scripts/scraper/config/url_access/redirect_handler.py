"""Redirect following and chain tracking."""

import requests
from typing import Dict, List, Tuple

def follow_redirects(
    url: str,
    timeout: int = 10,
    max_redirects: int = 5,
) -> Dict[str, any]:
    """
    Follow redirects and track the chain.
    
    Args:
        url: Starting URL
        timeout: Request timeout
        max_redirects: Max hops to follow (default: 5)
    
    Returns:
        Dict with keys:
        - original_url (str): Starting URL
        - final_url (str): Final destination after redirects
        - redirect_chain (list): All URLs in chain
        - status_codes (list): HTTP codes for each step
        - loop_detected (bool): True if redirect loop found
        - external_system (str|None): ICIMS, Workday, PeopleSoft, etc.
        - error (str|None): Error message if any
    """
    result = {
        "original_url": url,
        "final_url": url,
        "redirect_chain": [url],
        "status_codes": [],
        "loop_detected": False,
        "external_system": None,
        "error": None,
    }
    
    try:
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        
        # Record redirect chain from response history
        for resp in response.history:
            result["redirect_chain"].append(resp.url)
            result["status_codes"].append(resp.status_code)
            
            # Check for loop
            if result["redirect_chain"].count(resp.url) > 1:
                result["loop_detected"] = True
        
        # Add final response
        result["redirect_chain"].append(response.url)
        result["status_codes"].append(response.status_code)
        result["final_url"] = response.url
        
        # Detect external system from URL
        result["external_system"] = _detect_external_system(response.url)
        
    except Exception as e:
        result["error"] = str(e)
    
    # Remove duplicate if no actual redirects
    if len(result["redirect_chain"]) > 1:
        result["has_redirects"] = True
    else:
        result["has_redirects"] = False
        result["redirect_chain"] = [url]
    
    return result


def record_redirect_chain(
    url: str,
    timeout: int = 10,
) -> Dict[str, any]:
    """Alias for follow_redirects with clearer intent."""
    return follow_redirects(url, timeout)


def _detect_external_system(url: str) -> str | None:
    """Detect if URL redirects to external HR systems."""
    url_lower = url.lower()
    
    systems = {
        "icims": "ICIMS",
        "workday": "Workday",
        "peoplesoft": "PeopleSoft",
        "successfactors": "SuccessFactors",
        "lever": "Lever",
        "greenhouse": "Greenhouse",
        "jobs.lever": "Lever",
        "boards.greenhouse": "Greenhouse",
    }
    
    for keyword, system in systems.items():
        if keyword in url_lower:
            return system
    
    return None
