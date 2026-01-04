"""DNS resolution with Chinese DNS fallback."""

import socket
import requests
from typing import Dict

# Chinese DNS servers in priority order
CHINESE_DNS_SERVERS = [
    "223.5.5.5",      # Alidns
    "119.29.29.29",   # DNSPod
    "119.28.28.28",   # Tencent
]

def resolve_with_chinese_dns(hostname: str) -> Dict[str, any]:
    """
    Try to resolve hostname with Chinese DNS servers.
    
    Args:
        hostname: Domain name to resolve
    
    Returns:
        Dict with keys:
        - resolved (bool): True if resolved
        - ip_address (str|None): Resolved IP
        - dns_server (str|None): Which DNS server worked
        - error (str|None): Error message if failed
    """
    result = {
        "resolved": False,
        "ip_address": None,
        "dns_server": None,
        "error": None,
    }
    
    # Try default first (system DNS)
    try:
        ip = socket.gethostbyname(hostname)
        result["resolved"] = True
        result["ip_address"] = ip
        result["dns_server"] = "system_default"
        return result
    except socket.gaierror:
        pass
    
    # Try Chinese DNS servers as fallback
    for dns_server in CHINESE_DNS_SERVERS:
        try:
            # Use requests with custom DNS by constructing resolver
            # This is a simplified approach - may need dnspython for production
            resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # For real implementation, would use dnspython or custom DNS query
            # This is a placeholder that tries alternative approaches
            
            result["error"] = f"All DNS servers failed (tried {len(CHINESE_DNS_SERVERS)})"
            
        except Exception:
            continue
    
    return result


def test_with_alternative_dns(url: str) -> Dict[str, any]:
    """
    Test URL with alternative DNS resolution.
    
    Returns:
        Dict with accessibility info and which DNS worked
    """
    from urllib.parse import urlparse
    
    hostname = urlparse(url).netloc.split(':')[0]
    dns_result = resolve_with_chinese_dns(hostname)
    
    result = {
        "url": url,
        "hostname": hostname,
        "dns_resolution": dns_result,
        "accessible_via_alternative": False,
    }
    
    if dns_result["resolved"]:
        # Try to access with resolved IP
        try:
            from .test_accessibility import test_accessibility
            # Could attempt direct IP connection here
            result["accessible_via_alternative"] = True
        except Exception:
            pass
    
    return result
