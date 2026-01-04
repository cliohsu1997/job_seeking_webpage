"""
Tests for configuration loader utility.
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts" / "scraper"))

from utils.config_loader import (
    load_config,
    save_config,
    get_accessible_config,
    get_non_accessible_config,
    get_all_config,
    count_urls
)


class TestConfigLoader(unittest.TestCase):
    """Test configuration loader functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.test_config = {
            "accessible": {
                "job_portals": {
                    "aea": {
                        "name": "AEA JOE",
                        "url": "https://www.aeaweb.org/joe"
                    }
                },
                "regions": {
                    "united_states": {
                        "universities": [
                            {
                                "name": "Test University",
                                "departments": [
                                    {"name": "Economics", "url": "https://example.com/econ"}
                                ]
                            }
                        ]
                    }
                }
            },
            "non_accessible": {
                "job_portals": {},
                "regions": {
                    "united_states": {
                        "universities": [
                            {
                                "name": "Test University 2",
                                "departments": [
                                    {"name": "Economics", "url": "https://example.com/econ2"}
                                ]
                            }
                        ]
                    }
                }
            }
        }
    
    def test_get_accessible_config(self):
        """Test getting accessible configuration."""
        accessible = get_accessible_config(self.test_config)
        self.assertIn("job_portals", accessible)
        self.assertIn("regions", accessible)
        self.assertIn("aea", accessible["job_portals"])
        self.assertNotIn("non_accessible", accessible)
    
    def test_get_non_accessible_config(self):
        """Test getting non-accessible configuration."""
        non_accessible = get_non_accessible_config(self.test_config)
        self.assertIn("job_portals", non_accessible)
        self.assertIn("regions", non_accessible)
        self.assertIn("united_states", non_accessible["regions"])
        self.assertNotIn("accessible", non_accessible)
    
    def test_get_all_config(self):
        """Test getting all configuration combined."""
        all_config = get_all_config(self.test_config)
        self.assertIn("job_portals", all_config)
        self.assertIn("regions", all_config)
        # Should have both accessible and non-accessible items
        self.assertIn("aea", all_config["job_portals"])
        # Should have universities from both sections
        us_unis = all_config["regions"]["united_states"]["universities"]
        self.assertGreaterEqual(len(us_unis), 1)
    
    def test_count_urls(self):
        """Test counting URLs in configuration."""
        total, accessible = count_urls(self.test_config)
        # Accessible: 1 job portal + 1 department = 2
        # Non-accessible: 0 job portals + 1 department = 1
        # Total: 3
        self.assertEqual(accessible, 2)
        self.assertEqual(total, 3)
    
    def test_count_urls_empty_config(self):
        """Test counting URLs in empty configuration."""
        empty_config = {
            "accessible": {"job_portals": {}, "regions": {}},
            "non_accessible": {"job_portals": {}, "regions": {}}
        }
        total, accessible = count_urls(empty_config)
        self.assertEqual(accessible, 0)
        self.assertEqual(total, 0)
    
    def test_count_urls_complex_structure(self):
        """Test counting URLs in complex configuration structure."""
        complex_config = {
            "accessible": {
                "job_portals": {
                    "portal1": {},
                    "portal2": {}
                },
                "regions": {
                    "united_states": {
                        "universities": [
                            {
                                "name": "Uni1",
                                "departments": [
                                    {"name": "Dept1", "url": "url1"},
                                    {"name": "Dept2", "url": "url2"}
                                ]
                            }
                        ],
                        "research_institutes": [
                            {"name": "Inst1", "url": "url3"}
                        ]
                    },
                    "other_countries": {
                        "countries": {
                            "country1": {
                                "universities": [
                                    {
                                        "name": "Uni2",
                                        "departments": [
                                            {"name": "Dept3", "url": "url4"}
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            "non_accessible": {
                "job_portals": {},
                "regions": {}
            }
        }
        total, accessible = count_urls(complex_config)
        # Accessible: 2 portals + 2 departments + 1 institute + 1 department = 6
        self.assertEqual(accessible, 6)
        self.assertEqual(total, 6)
    
    def test_get_accessible_config_none(self):
        """Test getting accessible config when config is None (loads from file)."""
        # This will try to load from actual config file
        # Just test that it doesn't crash
        try:
            accessible = get_accessible_config()
            self.assertIsInstance(accessible, dict)
        except FileNotFoundError:
            # Expected if config file doesn't exist in test environment
            pass
    
    def test_get_non_accessible_config_none(self):
        """Test getting non-accessible config when config is None."""
        try:
            non_accessible = get_non_accessible_config()
            self.assertIsInstance(non_accessible, dict)
        except FileNotFoundError:
            pass
    
    def test_get_all_config_none(self):
        """Test getting all config when config is None."""
        try:
            all_config = get_all_config()
            self.assertIsInstance(all_config, dict)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    unittest.main()

