"""
Location parsing utilities for normalizing location data.

This module provides functions for parsing location strings into structured format,
detecting regions, and normalizing location data for various countries/regions.
"""

import re
import json
from pathlib import Path
from typing import Dict, Optional, Any, Tuple

# Path to processing rules config
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "data/config/processing_rules.json"

# Complete US state abbreviations (extended from config)
US_STATE_ABBREVIATIONS = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
}

# Reverse mapping: state name -> abbreviation
US_STATE_NAMES_TO_ABBR = {v.upper(): k for k, v in US_STATE_ABBREVIATIONS.items()}

# Country to region mapping
COUNTRY_TO_REGION = {
    "united states": "united_states",
    "usa": "united_states",
    "us": "united_states",
    "u.s.a.": "united_states",
    "u.s.": "united_states",
    "china": "mainland_china",
    "prc": "mainland_china",
    "people's republic of china": "mainland_china",
    "united kingdom": "united_kingdom",
    "uk": "united_kingdom",
    "britain": "united_kingdom",
    "great britain": "united_kingdom",
    "england": "united_kingdom",
    "scotland": "united_kingdom",
    "wales": "united_kingdom",
    "canada": "canada",
    "australia": "australia",
}


def load_config() -> Dict[str, Any]:
    """Load processing rules configuration."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get("location_parsing", {})
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}


def detect_region_from_country(country: str) -> str:
    """
    Detect region from country name.
    
    Args:
        country: Country name string
        
    Returns:
        Region string (united_states, mainland_china, united_kingdom, canada, australia, other_countries)
    """
    if not country:
        return "other_countries"
    
    country_lower = country.lower().strip()
    
    # Check direct mapping
    if country_lower in COUNTRY_TO_REGION:
        return COUNTRY_TO_REGION[country_lower]
    
    # Check if country contains region keywords
    for country_key, region in COUNTRY_TO_REGION.items():
        if country_key in country_lower:
            return region
    
    # Default to other_countries
    return "other_countries"


def parse_us_location(location_str: str) -> Dict[str, Optional[str]]:
    """
    Parse US location string (e.g., "Cambridge, MA" or "Boston, Massachusetts").
    
    Args:
        location_str: Location string to parse
        
    Returns:
        Dictionary with city, state, country, region
    """
    if not location_str:
        return {
            "city": None,
            "state": None,
            "country": "United States",
            "region": "united_states"
        }
    
    location_str = location_str.strip()
    
    # Common separators
    separators = [',', '，', '-', '–', '—']
    parts = []
    current_sep = None
    
    for sep in separators:
        if sep in location_str:
            parts = [p.strip() for p in location_str.split(sep, 1)]
            current_sep = sep
            break
    
    if not parts:
        # No separator found, try to extract city/state from single string
        # Check if it's a state abbreviation (2 uppercase letters)
        if len(location_str) == 2 and location_str.isupper():
            return {
                "city": None,
                "state": location_str,
                "country": "United States",
                "region": "united_states"
            }
        # Check if it's a full state name
        location_upper = location_str.upper()
        if location_upper in US_STATE_NAMES_TO_ABBR:
            return {
                "city": None,
                "state": US_STATE_NAMES_TO_ABBR[location_upper],
                "country": "United States",
                "region": "united_states"
            }
        # Otherwise treat as city
        return {
            "city": location_str,
            "state": None,
            "country": "United States",
            "region": "united_states"
        }
    
    # Parse with separator
    city = parts[0] if len(parts) > 0 else None
    state_part = parts[1] if len(parts) > 1 else None
    
    # Try to identify state
    state = None
    if state_part:
        state_part_upper = state_part.upper()
        
        # Check if it's a state abbreviation
        if state_part_upper in US_STATE_ABBREVIATIONS:
            state = state_part_upper
        # Check if it's a state name
        elif state_part_upper in US_STATE_NAMES_TO_ABBR:
            state = US_STATE_NAMES_TO_ABBR[state_part_upper]
        # Try case-insensitive match
        else:
            state_part_normalized = state_part.title()
            for state_name, abbr in US_STATE_NAMES_TO_ABBR.items():
                if state_name == state_part_upper or state_name == state_part_normalized.upper():
                    state = abbr
                    break
            # If still not found, use as-is (could be city, state format)
            if not state:
                state = state_part
    
    return {
        "city": city,
        "state": state,
        "country": "United States",
        "region": "united_states"
    }


def parse_china_location(location_str: str) -> Dict[str, Optional[str]]:
    """
    Parse China location string (e.g., "北京市" or "北京, 中国").
    
    Args:
        location_str: Location string to parse
        
    Returns:
        Dictionary with city, province, country, region
    """
    if not location_str:
        return {
            "city": None,
            "province": None,
            "country": "China",
            "region": "mainland_china"
        }
    
    location_str = location_str.strip()
    
    # Check for Chinese province keywords
    config = load_config()
    china_config = config.get("country_patterns", {}).get("mainland_china", {})
    province_keywords = china_config.get("province_keywords", ["省", "市", "自治区"])
    
    # Check if location contains province keywords
    has_province_keyword = any(keyword in location_str for keyword in province_keywords)
    
    # Try to split by common separators
    separators = [',', '，', '-', '–', '—']
    parts = []
    
    for sep in separators:
        if sep in location_str:
            parts = [p.strip() for p in location_str.split(sep, 1)]
            break
    
    if parts and len(parts) >= 2:
        # Has separator: first part is city/province, second part might be country
        city_province = parts[0]
        country_part = parts[1] if len(parts) > 1 else None
        
        # Extract province if keyword present
        province = None
        city = city_province
        
        for keyword in province_keywords:
            if keyword in city_province:
                # Extract province name
                province = city_province
                city = None  # If it's a province, city might be in a different field
                break
        
        return {
            "city": city if city != city_province else city_province,
            "province": province,
            "country": "China",
            "region": "mainland_china"
        }
    else:
        # No separator, treat as single location string
        province = None
        city = location_str
        
        for keyword in province_keywords:
            if keyword in location_str:
                province = location_str
                city = None
                break
        
        return {
            "city": city,
            "province": province,
            "country": "China",
            "region": "mainland_china"
        }


def parse_generic_location(location_str: str, country: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Parse generic location string (for countries other than US/China).
    
    Args:
        location_str: Location string to parse
        country: Country name (optional)
        
    Returns:
        Dictionary with city, country, region
    """
    if not location_str:
        country = country or "Unknown"
        region = detect_region_from_country(country)
        return {
            "city": None,
            "country": country,
            "region": region
        }
    
    location_str = location_str.strip()
    
    # Try to split by common separators
    separators = [',', '，', '-', '–', '—']
    parts = []
    
    for sep in separators:
        if sep in location_str:
            parts = [p.strip() for p in location_str.split(sep)]
            break
    
    if parts:
        # Last part is usually country
        city = parts[0] if len(parts) > 0 else None
        detected_country = parts[-1] if len(parts) > 1 and parts[-1] else (country or None)
        
        # If country not in parts, use provided country or try to detect
        if not detected_country:
            detected_country = country or "Unknown"
        
        region = detect_region_from_country(detected_country)
        
        return {
            "city": city if city != detected_country else None,
            "country": detected_country,
            "region": region
        }
    else:
        # No separator, use entire string
        detected_country = country or location_str
        region = detect_region_from_country(detected_country)
        
        return {
            "city": location_str if region == "other_countries" else None,
            "country": detected_country,
            "region": region
        }


def parse_location(location_str: Optional[str], country: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Parse location string into structured format.
    
    Main entry point for location parsing. Determines country/region and routes
    to appropriate parser.
    
    Args:
        location_str: Location string to parse (e.g., "Cambridge, MA", "Beijing, China")
        country: Optional country name hint
        
    Returns:
        Dictionary with keys: city, state (US only), province (China only), country, region
        Structure matches schema.py location definition
    """
    if not location_str and not country:
        return {
            "city": None,
            "state": None,
            "province": None,
            "country": "Unknown",
            "region": "other_countries"
        }
    
    location_str = location_str.strip() if location_str else ""
    
    # Normalize country hint
    country_lower = country.lower().strip() if country else ""
    
    # Check if country hint suggests US
    if country_lower in ["united states", "usa", "us", "u.s.a.", "u.s."]:
        return parse_us_location(location_str)
    
    # Check if country hint suggests China
    if country_lower in ["china", "prc", "people's republic of china"] or "中国" in location_str:
        return parse_china_location(location_str)
    
    # Check location string for country indicators
    location_lower = location_str.lower()
    
    # Check for US indicators in location string
    if any(indicator in location_lower for indicator in [", us", ", usa", ", united states"]):
        # Extract city, state part
        us_part = location_str.rsplit(",", 1)[0] if "," in location_str else location_str
        return parse_us_location(us_part)
    
    # Check for China indicators
    if "中国" in location_str or any(indicator in location_lower for indicator in [", china", ", prc"]):
        china_part = location_str.rsplit(",", 1)[0] if "," in location_str else location_str
        return parse_china_location(china_part)
    
    # Check for US state abbreviations or state names in location
    # Pattern: "City, ST" or "City, State"
    us_pattern = r'^([^,]+),\s*([A-Z]{2}|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)$'
    match = re.match(us_pattern, location_str)
    if match:
        city_part = match.group(1).strip()
        state_part = match.group(2).strip()
        # Verify it's actually a US state
        if state_part.upper() in US_STATE_ABBREVIATIONS or state_part.title() in US_STATE_ABBREVIATIONS.values():
            return parse_us_location(location_str)
    
    # Check for Chinese province keywords
    config = load_config()
    china_config = config.get("country_patterns", {}).get("mainland_china", {})
    province_keywords = china_config.get("province_keywords", ["省", "市", "自治区"])
    if any(keyword in location_str for keyword in province_keywords):
        return parse_china_location(location_str)
    
    # Default to generic parser
    return parse_generic_location(location_str, country)


def normalize_location(location_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Normalize location dictionary to match schema format.
    
    Converts various location dictionary formats to standard schema format.
    
    Args:
        location_data: Location dictionary (may be in various formats)
        
    Returns:
        Normalized location dictionary with: city, state, province, country, region
    """
    # Handle None or empty
    if not location_data:
        return {
            "city": None,
            "state": None,
            "province": None,
            "country": "Unknown",
            "region": "other_countries"
        }
    
    # If it's already a string, parse it
    if isinstance(location_data, str):
        return parse_location(location_data)
    
    # Extract fields
    city = location_data.get("city")
    state = location_data.get("state")
    province = location_data.get("province")
    country = location_data.get("country")
    region = location_data.get("region")
    
    # If region not provided, detect from country
    if not region and country:
        region = detect_region_from_country(country)
    elif not region:
        region = "other_countries"
    
    # If country not provided, try to infer from region
    if not country:
        region_to_country = {
            "united_states": "United States",
            "mainland_china": "China",
            "united_kingdom": "United Kingdom",
            "canada": "Canada",
            "australia": "Australia"
        }
        country = region_to_country.get(region, "Unknown")
    
    return {
        "city": city,
        "state": state,
        "province": province,
        "country": country,
        "region": region
    }

