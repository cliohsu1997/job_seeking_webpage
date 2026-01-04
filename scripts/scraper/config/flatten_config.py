"""
Flatten hierarchical scraping_sources.json to a simple list structure.

This script converts the nested structure (regions → universities → departments → url)
into a flat list where each entry is a direct item with all relevant properties.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def flatten_job_portals(portals: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten job_portals section - already mostly flat."""
    flattened = []
    for portal_id, portal_data in portals.items():
        entry = {
            "id": portal_id,
            "type": "job_portal",
            **portal_data
        }
        flattened.append(entry)
    return flattened


def flatten_universities(universities_list: List[Dict[str, Any]], region: str, parent_location: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Flatten universities array into individual department entries."""
    flattened = []
    
    for university in universities_list:
        university_name = university.get("name", "Unknown")
        location = university.get("location", parent_location or {})
        university_notes = university.get("notes", "")
        
        departments = university.get("departments", [])
        
        for dept in departments:
            entry = {
                "id": f"{university_name.lower().replace(' ', '_')}_{dept.get('name', 'dept').lower()}",
                "type": "university_department",
                "name": f"{university_name} - {dept.get('name', 'Department')}",
                "university": university_name,
                "department": dept.get("name", "Unknown Department"),
                "url": dept.get("url", ""),
                "scraping_method": dept.get("scraping_method", university.get("scraping_method", "html_parser")),
                "region": region,
                "country": location.get("country", "Unknown"),
                "city": location.get("city", "Unknown"),
                "job_nature": "university",
                "notes": dept.get("notes", university_notes),
                "departments": dept.get("departments", [])
            }
            flattened.append(entry)
    
    return flattened


def flatten_institutes(institutes: Dict[str, Any], region: str) -> List[Dict[str, Any]]:
    """Flatten institutes section."""
    flattened = []
    
    for institute_id, institute_data in institutes.items():
        if "departments" in institute_data and isinstance(institute_data["departments"], list):
            # Institute with departments
            for dept in institute_data["departments"]:
                entry = {
                    "id": f"{institute_id}_{dept.get('name', 'dept').lower().replace(' ', '_')}",
                    "type": "research_institute",
                    "name": f"{institute_data.get('name', 'Unknown')} - {dept.get('name', 'Department')}",
                    "institute": institute_data.get("name", "Unknown"),
                    "department": dept.get("name", "Unknown Department"),
                    "url": dept.get("url", institute_data.get("url", "")),
                    "scraping_method": dept.get("scraping_method", institute_data.get("scraping_method", "html_parser")),
                    "region": region,
                    "country": institute_data.get("location", {}).get("country", "Unknown"),
                    "city": institute_data.get("location", {}).get("city", "Unknown"),
                    "job_nature": "institute",
                    "notes": dept.get("notes", institute_data.get("notes", "")),
                    "departments": []
                }
                flattened.append(entry)
        else:
            # Institute without departments
            entry = {
                "id": institute_id,
                "type": "research_institute",
                "name": institute_data.get("name", "Unknown"),
                "institute": institute_data.get("name", "Unknown"),
                "department": "",
                "url": institute_data.get("url", ""),
                "scraping_method": institute_data.get("scraping_method", "html_parser"),
                "region": region,
                "country": institute_data.get("location", {}).get("country", "Unknown"),
                "city": institute_data.get("location", {}).get("city", "Unknown"),
                "job_nature": "institute",
                "notes": institute_data.get("notes", ""),
                "departments": institute_data.get("departments", [])
            }
            flattened.append(entry)
    
    return flattened


def flatten_regions(regions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten regions section into individual entries."""
    flattened = []
    
    for region_name, region_data in regions.items():
        # Check if region has universities
        if "universities" in region_data and isinstance(region_data["universities"], list):
            flattened.extend(flatten_universities(region_data["universities"], region_name))
        
        # Check for nested sub-regions (e.g., "north_america" might have "us" and "canada")
        for key, value in region_data.items():
            if key not in ["universities", "ranking_source", "coverage", "notes"] and isinstance(value, dict):
                # This is a sub-region
                if "universities" in value:
                    flattened.extend(flatten_universities(value["universities"], f"{region_name}.{key}", value.get("location")))
                if "institutes" in value:
                    flattened.extend(flatten_institutes(value["institutes"], f"{region_name}.{key}"))
    
    return flattened


def flatten_config(input_path: Path, output_path: Path) -> None:
    """Main function to flatten the configuration."""
    with open(input_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    flattened = {
        "accessible": [],
        "non_accessible": []
    }
    
    # Flatten accessible section
    if "accessible" in config:
        accessible = config["accessible"]
        
        # Job portals
        if "job_portals" in accessible:
            flattened["accessible"].extend(flatten_job_portals(accessible["job_portals"]))
        
        # Regions (universities and institutes)
        if "regions" in accessible:
            flattened["accessible"].extend(flatten_regions(accessible["regions"]))
    
    # Flatten non_accessible section (same structure)
    if "non_accessible" in config:
        non_accessible = config["non_accessible"]
        
        if "job_portals" in non_accessible:
            flattened["non_accessible"].extend(flatten_job_portals(non_accessible["job_portals"]))
        
        if "regions" in non_accessible:
            flattened["non_accessible"].extend(flatten_regions(non_accessible["regions"]))
    
    # Write flattened config
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(flattened, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Flattened config written to {output_path}")
    print(f"  - Accessible entries: {len(flattened['accessible'])}")
    print(f"  - Non-accessible entries: {len(flattened['non_accessible'])}")


if __name__ == "__main__":
    # Get paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    config_dir = project_root / "data" / "config"
    
    input_file = config_dir / "scraping_sources.json"
    output_file = config_dir / "scraping_sources_flat.json"
    
    flatten_config(input_file, output_file)
