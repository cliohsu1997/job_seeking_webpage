"""
Migrate scraping_sources.json to new structure with accessible/non_accessible top-level categories.

New structure:
{
  "accessible": {
    "job_portals": {...},
    "regions": {...}
  },
  "non_accessible": {
    "job_portals": {...},
    "regions": {...}
  }
}
"""

import json
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "data/config/scraping_sources.json"
BACKUP_FILE = PROJECT_ROOT / "data/config/scraping_sources.json.backup"


def get_url_status(config_obj: dict) -> str:
    """Get url_status from a config object (job portal, department, institute, etc.)."""
    return config_obj.get("url_status", "pending_verification")


def split_by_accessibility(old_config: dict) -> dict:
    """Split old config structure into accessible and non_accessible."""
    new_config = {
        "accessible": {
            "job_portals": {},
            "regions": {}
        },
        "non_accessible": {
            "job_portals": {},
            "regions": {}
        }
    }
    
    # Split job portals
    if "job_portals" in old_config:
        for portal_key, portal_data in old_config["job_portals"].items():
            status = get_url_status(portal_data)
            if status == "accessible":
                new_config["accessible"]["job_portals"][portal_key] = portal_data.copy()
                # Remove url_status since it's implied by the category
                if "url_status" in new_config["accessible"]["job_portals"][portal_key]:
                    del new_config["accessible"]["job_portals"][portal_key]["url_status"]
            else:
                new_config["non_accessible"]["job_portals"][portal_key] = portal_data.copy()
    
    # Split regions
    if "regions" in old_config:
        regions = old_config["regions"]
        
        # Process each region type
        for region_key in ["mainland_china", "united_states", "other_countries"]:
            if region_key not in regions:
                continue
            
            region_data = regions[region_key]
            
            # Handle other_countries separately (has nested "countries" structure)
            if region_key == "other_countries":
                continue  # Will handle after this loop
            
            accessible_region = {}
            non_accessible_region = {}
            
            # Copy metadata
            for meta_key in ["ranking_source", "coverage"]:
                if meta_key in region_data:
                    accessible_region[meta_key] = region_data[meta_key]
                    non_accessible_region[meta_key] = region_data[meta_key]
            
            # Split universities
            if "universities" in region_data:
                accessible_universities = []
                non_accessible_universities = []
                
                for uni in region_data["universities"]:
                    accessible_depts = []
                    non_accessible_depts = []
                    
                    for dept in uni.get("departments", []):
                        dept_copy = dept.copy()
                        status = get_url_status(dept)
                        
                        # Remove url_status from copy
                        if "url_status" in dept_copy:
                            del dept_copy["url_status"]
                        
                        if status == "accessible":
                            accessible_depts.append(dept_copy)
                        else:
                            non_accessible_depts.append(dept_copy)
                    
                    # Create university copies with appropriate departments
                    if accessible_depts:
                        uni_copy = uni.copy()
                        uni_copy["departments"] = accessible_depts
                        accessible_universities.append(uni_copy)
                    
                    if non_accessible_depts:
                        uni_copy = uni.copy()
                        uni_copy["departments"] = non_accessible_depts
                        non_accessible_universities.append(uni_copy)
                
                if accessible_universities:
                    accessible_region["universities"] = accessible_universities
                if non_accessible_universities:
                    non_accessible_region["universities"] = non_accessible_universities
            
            # Split research institutes
            if "research_institutes" in region_data:
                accessible_institutes = []
                non_accessible_institutes = []
                
                for inst in region_data["research_institutes"]:
                    inst_copy = inst.copy()
                    status = get_url_status(inst)
                    
                    if "url_status" in inst_copy:
                        del inst_copy["url_status"]
                    
                    if status == "accessible":
                        accessible_institutes.append(inst_copy)
                    else:
                        non_accessible_institutes.append(inst_copy)
                
                if accessible_institutes:
                    accessible_region["research_institutes"] = accessible_institutes
                if non_accessible_institutes:
                    non_accessible_region["research_institutes"] = non_accessible_institutes
            
            # Split think tanks
            if "think_tanks" in region_data:
                accessible_tanks = []
                non_accessible_tanks = []
                
                for tank in region_data["think_tanks"]:
                    tank_copy = tank.copy()
                    status = get_url_status(tank)
                    
                    if "url_status" in tank_copy:
                        del tank_copy["url_status"]
                    
                    if status == "accessible":
                        accessible_tanks.append(tank_copy)
                    else:
                        non_accessible_tanks.append(tank_copy)
                
                if accessible_tanks:
                    accessible_region["think_tanks"] = accessible_tanks
                if non_accessible_tanks:
                    non_accessible_region["think_tanks"] = non_accessible_tanks
            
            # Add to appropriate category if non-empty
            if any(accessible_region.values()):
                new_config["accessible"]["regions"][region_key] = accessible_region
            if any(non_accessible_region.values()):
                new_config["non_accessible"]["regions"][region_key] = non_accessible_region
        
        # Handle other_countries separately (has nested "countries" structure)
        if "other_countries" in regions and "countries" in regions["other_countries"]:
            region_data = regions["other_countries"]
            accessible_oc = {"countries": {}}
            non_accessible_oc = {"countries": {}}
            
            for country_key, country_data in region_data["countries"].items():
                accessible_country = {}
                non_accessible_country = {}
                
                # Split universities (by department status)
                if "universities" in country_data:
                    accessible_universities = []
                    non_accessible_universities = []
                    
                    for uni in country_data["universities"]:
                        accessible_depts = []
                        non_accessible_depts = []
                        
                        for dept in uni.get("departments", []):
                            dept_copy = dept.copy()
                            status = get_url_status(dept)
                            if "url_status" in dept_copy:
                                del dept_copy["url_status"]
                            
                            if status == "accessible":
                                accessible_depts.append(dept_copy)
                            else:
                                non_accessible_depts.append(dept_copy)
                        
                        if accessible_depts:
                            uni_copy = uni.copy()
                            uni_copy["departments"] = accessible_depts
                            accessible_universities.append(uni_copy)
                        if non_accessible_depts:
                            uni_copy = uni.copy()
                            uni_copy["departments"] = non_accessible_depts
                            non_accessible_universities.append(uni_copy)
                    
                    if accessible_universities:
                        accessible_country["universities"] = accessible_universities
                    if non_accessible_universities:
                        non_accessible_country["universities"] = non_accessible_universities
                
                # Split research institutes
                if "research_institutes" in country_data:
                    accessible_institutes = []
                    non_accessible_institutes = []
                    
                    for inst in country_data["research_institutes"]:
                        inst_copy = inst.copy()
                        status = get_url_status(inst)
                        if "url_status" in inst_copy:
                            del inst_copy["url_status"]
                        
                        if status == "accessible":
                            accessible_institutes.append(inst_copy)
                        else:
                            non_accessible_institutes.append(inst_copy)
                    
                    if accessible_institutes:
                        accessible_country["research_institutes"] = accessible_institutes
                    if non_accessible_institutes:
                        non_accessible_country["research_institutes"] = non_accessible_institutes
                
                # Split think tanks
                if "think_tanks" in country_data:
                    accessible_tanks = []
                    non_accessible_tanks = []
                    
                    for tank in country_data["think_tanks"]:
                        tank_copy = tank.copy()
                        status = get_url_status(tank)
                        if "url_status" in tank_copy:
                            del tank_copy["url_status"]
                        
                        if status == "accessible":
                            accessible_tanks.append(tank_copy)
                        else:
                            non_accessible_tanks.append(tank_copy)
                    
                    if accessible_tanks:
                        accessible_country["think_tanks"] = accessible_tanks
                    if non_accessible_tanks:
                        non_accessible_country["think_tanks"] = non_accessible_tanks
                
                if any(accessible_country.values()):
                    accessible_oc["countries"][country_key] = accessible_country
                if any(non_accessible_country.values()):
                    non_accessible_oc["countries"][country_key] = non_accessible_country
            
            if accessible_oc["countries"]:
                new_config["accessible"]["regions"]["other_countries"] = accessible_oc
            if non_accessible_oc["countries"]:
                new_config["non_accessible"]["regions"]["other_countries"] = non_accessible_oc
    
    return new_config


def main():
    """Migrate configuration file to new structure."""
    print("=" * 80)
    print("Migrating scraping_sources.json to new structure")
    print("=" * 80)
    print()
    
    # Load old config
    print(f"Loading {CONFIG_FILE}...")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        old_config = json.load(f)
    print("✓ Loaded")
    print()
    
    # Create backup
    print(f"Creating backup: {BACKUP_FILE}")
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(old_config, f, indent=2, ensure_ascii=False)
    print("✓ Backup created")
    print()
    
    # Migrate to new structure
    print("Migrating to new structure...")
    new_config = split_by_accessibility(old_config)
    print("✓ Migration complete")
    print()
    
    # Count URLs
    def count_urls_in_section(section):
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
    
    accessible_count = count_urls_in_section(new_config["accessible"])
    non_accessible_count = count_urls_in_section(new_config["non_accessible"])
    total_count = accessible_count + non_accessible_count
    
    print(f"Migration Summary:")
    print(f"  Total URLs: {total_count}")
    print(f"  Accessible: {accessible_count}")
    print(f"  Non-accessible: {non_accessible_count}")
    print()
    
    # Save new config
    print(f"Saving migrated config to {CONFIG_FILE}...")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=2, ensure_ascii=False)
    print("✓ Saved")
    print()
    
    print("=" * 80)
    print("Migration complete!")
    print(f"Backup saved to: {BACKUP_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    main()

