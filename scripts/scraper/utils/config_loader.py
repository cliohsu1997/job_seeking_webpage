"""
Configuration loader utility for scraping sources.

Three-category structure used across the project:
{
    "accessible_verified": [ {"id": "...", "type": "...", "url": "...", ...} ],    # Confirmed working + validated
    "accessible_unverified": [ {"id": "...", "type": "...", "url": "...", ...} ],  # Accessible but not yet validated
    "potential_links": [ {"id": "...", "type": "...", "url": "...", ...} ]         # Not yet tested for accessibility
}
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "data/config"
MASTER_CONFIG_FILE = CONFIG_DIR / "scraping_sources.json"


def load_config() -> Dict[str, List[Dict[str, Any]]]:
    """Load the configuration file."""
    with open(MASTER_CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: Dict[str, List[Dict[str, Any]]]):
    """Save the configuration file."""
    with open(MASTER_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# Alias for backward compatibility
load_master_config = load_config


def get_accessible_verified_config(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return accessible and verified entries as a flat list.
    
    These URLs are confirmed working and their content has been validated.
    """
    if config is None:
        config = load_config()
    return config.get("accessible_verified", [])


def get_accessible_unverified_config(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return accessible but unverified entries as a flat list.
    
    These URLs are confirmed accessible but their content needs validation.
    """
    if config is None:
        config = load_config()
    return config.get("accessible_unverified", [])


def get_potential_links_config(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return potential links to be checked as a flat list.
    
    These URLs have not been tested for accessibility yet.
    """
    if config is None:
        config = load_config()
    return config.get("potential_links", [])


# Backward compatibility aliases
def get_accessible_config(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return accessible entries as a flat list.
    
    DEPRECATED: Use get_accessible_verified_config() instead.
    For backward compatibility, returns verified + unverified.
    """
    if config is None:
        config = load_config()
    verified = config.get("accessible_verified", [])
    unverified = config.get("accessible_unverified", [])
    return verified + unverified


def get_non_accessible_config(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return non-accessible entries as a flat list.
    
    DEPRECATED: Now returns potential_links (URLs not yet checked).
    """
    if config is None:
        config = load_config()
    return config.get("potential_links", [])


def get_all_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Return all entries organized by category."""
    if config is None:
        config = load_config()
    return {
        "accessible_verified": get_accessible_verified_config(config),
        "accessible_unverified": get_accessible_unverified_config(config),
        "potential_links": get_potential_links_config(config),
    }


def count_urls(config: Optional[Dict[str, Any]] = None) -> Tuple[int, int, int, int]:
    """Count URLs in each category.
    
    Returns:
        Tuple of (total, verified_accessible, unverified_accessible, potential)
    """
    if config is None:
        config = load_config()

    def count_in_section(entries: List[Dict[str, Any]]) -> int:
        return sum(1 for entry in entries if entry.get("url"))

    verified = count_in_section(get_accessible_verified_config(config))
    unverified = count_in_section(get_accessible_unverified_config(config))
    potential = count_in_section(get_potential_links_config(config))
    total = verified + unverified + potential

    return total, verified, unverified, potential
