"""HTTP connectivity testing for URLs."""

import time
import requests
from typing import Dict, Tuple
from urllib.error import URLError

# Cache to respect rate limits (URL -> last_test_time)
_test_cache = {}
MIN_REQUEST_INTERVAL = 1.0

def test_accessibility(
    url: str,
    timeout: int = 10,
) -> Dict[str, any]:
    """
    Test HTTP accessibility of a URL.
    
    Args:
        url: URL to test
        timeout: Request timeout in seconds (default: 10)
    
    Returns:
        Dict with keys:
        - accessible (bool): True if URL responds
        - status_code (int|None): HTTP status code
        - error_type (str|None): Error category
        - error_message (str): Detailed error message
        - response_time (float): Time to response in seconds
    """
    # Rate limiting
    if url in _test_cache:
        elapsed = time.time() - _test_cache[url]
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    
    _test_cache[url] = time.time()
    
    result = {
        "accessible": False,
        "status_code": None,
        "error_type": None,
        "error_message": "",
        "response_time": 0.0,
    }
    
    start_time = time.time()
    
    try:
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        result["response_time"] = time.time() - start_time
        result["status_code"] = response.status_code
        
        if response.status_code == 200:
            result["accessible"] = True
        elif response.status_code == 404:
            result["error_type"] = "not_found"
            result["error_message"] = "HTTP 404 Not Found"
        elif response.status_code == 403:
            result["error_type"] = "forbidden"
            result["error_message"] = "HTTP 403 Forbidden"
        else:
            result["error_type"] = f"http_{response.status_code}"
            result["error_message"] = f"HTTP {response.status_code}"
            
    except requests.Timeout:
        result["response_time"] = time.time() - start_time
        result["error_type"] = "timeout"
        result["error_message"] = f"Timeout after {timeout}s"
        
    except requests.ConnectionError as e:
        result["error_type"] = "connection_error"
        result["error_message"] = str(e)
        
    except requests.exceptions.SSLError as e:
        result["error_type"] = "ssl_error"
        result["error_message"] = "SSL certificate error"
        
    except Exception as e:
        result["error_type"] = "unknown_error"
        result["error_message"] = str(e)
    
    return result


def is_accessible(url: str, timeout: int = 10) -> bool:
    """Quick check if URL is accessible (200 status)."""
    return test_accessibility(url, timeout)["accessible"]
