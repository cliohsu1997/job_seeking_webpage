"""
Configuration loader utility for scraping sources.

Provides efficient functions to load and filter scraping configuration.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "data/config"
MASTER_CONFIG_FILE = CONFIG_DIR / "scraping_sources.json"
ACCESSIBLE_CONFIG_FILE = CONFIG_DIR / "scraping_sources_accessible.json"


def load_master_config() -> Dict:
    """Load the master configuration file."""
    with open(MASTER_CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_accessible_config() -> Optional[Dict]:
    """Load the accessible-only configuration file if it exists."""
    if ACCESSIBLE_CONFIG_FILE.exists():
        with open(ACCESSIBLE_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def filter_accessible_urls(config: Dict) -> Dict:
    """
    Filter configuration to include only accessible URLs.
    
    Returns a new dict with the same structure but only containing
    entries with url_status="accessible".
    """
    filtered = {"job_portals": {}, "regions": {}}
    
    # Filter job portals
    if "job_portals" in config:
        for portal_key, portal_data in config["job_portals"].items():
            if portal_data.get("url_status") == "accessible":
                filtered["job_portals"][portal_key] = portal_data.copy()
    
    # Filter regions
    if "regions" in config:
        regions = config["regions"]
        filtered_regions = filtered["regions"]
        
        # Mainland China
        if "mainland_china" in regions:
            china_config = filter_region(regions["mainland_china"])
            if any(china_config.values()):
                filtered_regions["mainland_china"] = china_config
        
        # United States
        if "united_states" in regions:
            us_config = filter_region(regions["united_states"])
            if any(us_config.values()):
                filtered_regions["united_states"] = us_config
        
        # Other countries
        if "other_countries" in regions:
            oc_config = filter_other_countries(regions["other_countries"])
            if oc_config.get("countries"):
                filtered_regions["other_countries"] = oc_config
    
    return filtered


def filter_region(region_data: Dict) -> Dict:
    """Filter a region (mainland_china or united_states) to only accessible URLs."""
    filtered = {}
    
    # Copy metadata
    for key in ["ranking_source", "coverage"]:
        if key in region_data:
            filtered[key] = region_data[key]
    
    # Filter universities
    if "universities" in region_data:
        filtered_universities = []
        for uni in region_data["universities"]:
            filtered_depts = []
            for dept in uni.get("departments", []):
                if dept.get("url_status") == "accessible":
                    filtered_depts.append(dept.copy())
            
            if filtered_depts:
                filtered_uni = uni.copy()
                filtered_uni["departments"] = filtered_depts
                filtered_universities.append(filtered_uni)
        
        if filtered_universities:
            filtered["universities"] = filtered_universities
    
    # Filter research institutes
    if "research_institutes" in region_data:
        filtered_institutes = [
            inst.copy() for inst in region_data["research_institutes"]
            if inst.get("url_status") == "accessible"
        ]
        if filtered_institutes:
            filtered["research_institutes"] = filtered_institutes
    
    # Filter think tanks
    if "think_tanks" in region_data:
        filtered_tanks = [
            tank.copy() for tank in region_data["think_tanks"]
            if tank.get("url_status") == "accessible"
        ]
        if filtered_tanks:
            filtered["think_tanks"] = filtered_tanks
    
    return filtered


def filter_other_countries(oc_data: Dict) -> Dict:
    """Filter other_countries region to only accessible URLs."""
    filtered = {"countries": {}}
    
    if "countries" in oc_data:
        for country_key, country_data in oc_data["countries"].items():
            filtered_country = filter_region(country_data)
            if any(filtered_country.values()):
                filtered["countries"][country_key] = filtered_country
    
    return filtered


def save_accessible_config(config: Dict):
    """Save the filtered accessible-only configuration to file."""
    filtered = filter_accessible_urls(config)
    with open(ACCESSIBLE_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)


def get_config(accessible_only: bool = False) -> Dict:
    """
    Get configuration, optionally filtered to only accessible URLs.
    
    Args:
        accessible_only: If True, return only accessible URLs.
                        First tries to load from accessible config file,
                        otherwise filters master config.
    
    Returns:
        Configuration dictionary
    """
    if accessible_only:
        # Try to load from accessible config file first
        accessible_config = load_accessible_config()
        if accessible_config:
            return accessible_config
        
        # Otherwise filter master config
        master_config = load_master_config()
        return filter_accessible_urls(master_config)
    else:
        return load_master_config()


def count_urls(config: Dict) -> Tuple[int, int]:
    """
    Count total URLs and accessible URLs in configuration.
    
    Returns:
        Tuple of (total_urls, accessible_urls)
    """
    total = 0
    accessible = 0
    
    # Count job portals
    if "job_portals" in config:
        for portal_data in config["job_portals"].values():
            if "url" in portal_data:
                total += 1
                if portal_data.get("url_status") == "accessible":
                    accessible += 1
    
    # Count regions
    if "regions" in config:
        regions = config["regions"]
        
        # Count function for region
        def count_region(region_data: Dict):
            nonlocal total, accessible
            
            # Universities
            if "universities" in region_data:
                for uni in region_data["universities"]:
                    for dept in uni.get("departments", []):
                        if "url" in dept:
                            total += 1
                            if dept.get("url_status") == "accessible":
                                accessible += 1
            
            # Research institutes
            if "research_institutes" in region_data:
                for inst in region_data["research_institutes"]:
                    if "url" in inst:
                        total += 1
                        if inst.get("url_status") == "accessible":
                            accessible += 1
            
            # Think tanks
            if "think_tanks" in region_data:
                for tank in region_data["think_tanks"]:
                    if "url" in tank:
                        total += 1
                        if tank.get("url_status") == "accessible":
                            accessible += 1
        
        # Count each region
        if "mainland_china" in regions:
            count_region(regions["mainland_china"])
        if "united_states" in regions:
            count_region(regions["united_states"])
        if "other_countries" in regions and "countries" in regions["other_countries"]:
            for country_data in regions["other_countries"]["countries"].values():
                count_region(country_data)
    
    return total, accessible

