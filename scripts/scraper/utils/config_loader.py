"""
Configuration loader utility for scraping sources.

Provides efficient functions to load scraping configuration with new structure:
{
  "accessible": { "job_portals": {...}, "regions": {...} },
  "non_accessible": { "job_portals": {...}, "regions": {...} }
}
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "data/config"
MASTER_CONFIG_FILE = CONFIG_DIR / "scraping_sources.json"


def load_config() -> Dict:
    """Load the configuration file."""
    with open(MASTER_CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: Dict):
    """Save the configuration file."""
    with open(MASTER_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# Alias for backward compatibility
load_master_config = load_config


def get_accessible_config(config: Optional[Dict] = None) -> Dict:
    """
    Get only the accessible URLs section from configuration.
    
    Args:
        config: Optional config dict. If None, loads from file.
    
    Returns:
        Configuration dictionary with only accessible URLs
    """
    if config is None:
        config = load_config()
    return config.get("accessible", {"job_portals": {}, "regions": {}})


def get_non_accessible_config(config: Optional[Dict] = None) -> Dict:
    """
    Get only the non-accessible URLs section from configuration.
    
    Args:
        config: Optional config dict. If None, loads from file.
    
    Returns:
        Configuration dictionary with only non-accessible URLs
    """
    if config is None:
        config = load_config()
    return config.get("non_accessible", {"job_portals": {}, "regions": {}})


def get_all_config(config: Optional[Dict] = None) -> Dict:
    """
    Get all configuration (both accessible and non-accessible combined).
    
    Args:
        config: Optional config dict. If None, loads from file.
    
    Returns:
        Combined configuration dictionary
    """
    if config is None:
        config = load_config()
    
    accessible = get_accessible_config(config)
    non_accessible = get_non_accessible_config(config)
    
    # Combine (for backward compatibility, return in old structure format)
    combined = {
        "job_portals": {},
        "regions": {}
    }
    
    # Combine job portals
    combined["job_portals"].update(accessible.get("job_portals", {}))
    combined["job_portals"].update(non_accessible.get("job_portals", {}))
    
    # Combine regions
    for category in ["accessible", "non_accessible"]:
        source = accessible if category == "accessible" else non_accessible
        if "regions" in source:
            for region_key, region_data in source["regions"].items():
                if region_key not in combined["regions"]:
                    combined["regions"][region_key] = {}
                    # Copy metadata
                    for meta_key in ["ranking_source", "coverage"]:
                        if meta_key in region_data:
                            combined["regions"][region_key][meta_key] = region_data[meta_key]
                
                # Merge universities, institutes, tanks
                for item_type in ["universities", "research_institutes", "think_tanks"]:
                    if item_type in region_data:
                        if item_type not in combined["regions"][region_key]:
                            combined["regions"][region_key][item_type] = []
                        combined["regions"][region_key][item_type].extend(region_data[item_type])
                
                # Handle other_countries structure
                if region_key == "other_countries" and "countries" in region_data:
                    if "countries" not in combined["regions"][region_key]:
                        combined["regions"][region_key]["countries"] = {}
                    for country_key, country_data in region_data["countries"].items():
                        if country_key not in combined["regions"][region_key]["countries"]:
                            combined["regions"][region_key]["countries"][country_key] = {}
                        for item_type in ["universities", "research_institutes", "think_tanks"]:
                            if item_type in country_data:
                                if item_type not in combined["regions"][region_key]["countries"][country_key]:
                                    combined["regions"][region_key]["countries"][country_key][item_type] = []
                                combined["regions"][region_key]["countries"][country_key][item_type].extend(country_data[item_type])
    
    return combined


def count_urls(config: Optional[Dict] = None) -> Tuple[int, int]:
    """
    Count total URLs and accessible URLs in configuration.
    
    Args:
        config: Optional config dict. If None, loads from file.
    
    Returns:
        Tuple of (total_urls, accessible_urls)
    """
    if config is None:
        config = load_config()
    
    def count_in_section(section: Dict) -> int:
        count = 0
        # Job portals
        count += len(section.get("job_portals", {}))
        # Regions
        for region_data in section.get("regions", {}).values():
            # Universities
            for uni in region_data.get("universities", []):
                count += len(uni.get("departments", []))
            # Institutes and tanks
            count += len(region_data.get("research_institutes", []))
            count += len(region_data.get("think_tanks", []))
            # Other countries
            if "countries" in region_data:
                for country_data in region_data["countries"].values():
                    for uni in country_data.get("universities", []):
                        count += len(uni.get("departments", []))
                    count += len(country_data.get("research_institutes", []))
                    count += len(country_data.get("think_tanks", []))
        return count
    
    accessible = count_in_section(get_accessible_config(config))
    non_accessible = count_in_section(get_non_accessible_config(config))
    total = accessible + non_accessible
    
    return total, accessible
