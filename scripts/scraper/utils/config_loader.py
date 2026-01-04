"""
Configuration loader utility for scraping sources.

Flat structure used across the project:
{
    "accessible": [ {"id": "...", "type": "...", "url": "...", ...} ],
    "non_accessible": [ {"id": "...", "type": "...", "url": "...", ...} ]
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


def get_accessible_config(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return accessible entries as a flat list."""
    if config is None:
        config = load_config()
    return config.get("accessible", [])


def get_non_accessible_config(config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Return non-accessible entries as a flat list."""
    if config is None:
        config = load_config()
    return config.get("non_accessible", [])


def get_all_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Return both accessible and non-accessible entries."""
    if config is None:
        config = load_config()
    return {
        "accessible": get_accessible_config(config),
        "non_accessible": get_non_accessible_config(config),
    }


def count_urls(config: Optional[Dict[str, Any]] = None) -> Tuple[int, int]:
    """Count total and accessible URLs in flat configuration."""
    if config is None:
        config = load_config()

    def count_in_section(entries: List[Dict[str, Any]]) -> int:
        return sum(1 for entry in entries if entry.get("url"))

    accessible_count = count_in_section(get_accessible_config(config))
    non_accessible_count = count_in_section(get_non_accessible_config(config))
    total = accessible_count + non_accessible_count

    return total, accessible_count
