"""
Generate accessible-only configuration file from master configuration.

This creates scraping_sources_accessible.json which contains only URLs
marked as accessible, making it faster to load for scripts that only
need accessible URLs.
"""

from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config_loader import load_master_config, save_accessible_config, count_urls

def main():
    """Generate accessible-only configuration file."""
    print("Generating accessible-only configuration file...")
    print()
    
    # Load master config
    config = load_master_config()
    
    # Count URLs
    total, accessible = count_urls(config)
    print(f"Total URLs in master config: {total}")
    print(f"Accessible URLs: {accessible}")
    print()
    
    # Generate and save accessible config
    save_accessible_config(config)
    
    # Verify
    from utils.config_loader import load_accessible_config
    accessible_config = load_accessible_config()
    accessible_total, _ = count_urls(accessible_config)
    
    print(f"✓ Generated accessible config with {accessible_total} accessible URLs")
    print(f"  Saved to: data/config/scraping_sources_accessible.json")
    print()


if __name__ == "__main__":
    main()

