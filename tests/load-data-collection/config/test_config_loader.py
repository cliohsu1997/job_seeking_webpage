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
    get_accessible_verified_config,
    get_accessible_unverified_config,
    get_potential_links_config,
    get_accessible_config,  # Backward compatibility
    get_non_accessible_config,  # Backward compatibility
    get_all_config,
    count_urls
)


class TestConfigLoader(unittest.TestCase):
    """Test configuration loader functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test config with three categories
        self.test_config = {
            "accessible_verified": [
                {
                    "id": "aea",
                    "name": "AEA JOE",
                    "url": "https://www.aeaweb.org/joe",
                    "type": "job_portal",
                    "verified": True
                },
                {
                    "id": "test_uni_econ",
                    "name": "Test University - Economics",
                    "url": "https://example.com/econ",
                    "type": "university_department",
                    "verified": True
                }
            ],
            "accessible_unverified": [
                {
                    "id": "test_uni_business",
                    "name": "Test University 2 - Business",
                    "url": "https://example.com/business",
                    "type": "university_department",
                    "verified": False
                }
            ],
            "potential_links": [
                {
                    "id": "potential_uni",
                    "name": "Potential University",
                    "url": "https://example.com/potential",
                    "type": "university_department",
                    "verified": False
                }
            ]
        }
    
    def test_get_accessible_verified_config(self):
        """Test getting accessible verified configuration."""
        verified = get_accessible_verified_config(self.test_config)
        self.assertEqual(len(verified), 2)
        self.assertEqual(verified[0]["id"], "aea")
        self.assertEqual(verified[1]["id"], "test_uni_econ")
        self.assertTrue(all(item["verified"] for item in verified))
    
    def test_get_accessible_unverified_config(self):
        """Test getting accessible unverified configuration."""
        unverified = get_accessible_unverified_config(self.test_config)
        self.assertEqual(len(unverified), 1)
        self.assertEqual(unverified[0]["id"], "test_uni_business")
        self.assertFalse(unverified[0]["verified"])
    
    def test_get_potential_links_config(self):
        """Test getting potential links configuration."""
        potential = get_potential_links_config(self.test_config)
        self.assertEqual(len(potential), 1)
        self.assertEqual(potential[0]["id"], "potential_uni")
    
    def test_get_accessible_config_backward_compat(self):
        """Test backward compatibility - accessible includes both verified and unverified."""
        accessible = get_accessible_config(self.test_config)
        # Should include both verified and unverified
        self.assertEqual(len(accessible), 3)
        ids = [item["id"] for item in accessible]
        self.assertIn("aea", ids)
        self.assertIn("test_uni_econ", ids)
        self.assertIn("test_uni_business", ids)
    
    def test_get_non_accessible_config_backward_compat(self):
        """Test backward compatibility - non_accessible now returns potential_links."""
        potential = get_non_accessible_config(self.test_config)
        self.assertEqual(len(potential), 1)
        self.assertEqual(potential[0]["id"], "potential_uni")
    
    def test_get_all_config(self):
        """Test getting all configuration organized by category."""
        all_config = get_all_config(self.test_config)
        self.assertIn("accessible_verified", all_config)
        self.assertIn("accessible_unverified", all_config)
        self.assertIn("potential_links", all_config)
        
        self.assertEqual(len(all_config["accessible_verified"]), 2)
        self.assertEqual(len(all_config["accessible_unverified"]), 1)
        self.assertEqual(len(all_config["potential_links"]), 1)
    
    def test_count_urls(self):
        """Test counting URLs in each category."""
        total, verified, unverified, potential = count_urls(self.test_config)
        # Verified: 2, Unverified: 1, Potential: 1, Total: 4
        self.assertEqual(total, 4)
        self.assertEqual(verified, 2)
        self.assertEqual(unverified, 1)
        self.assertEqual(potential, 1)
    
    def test_count_urls_empty_config(self):
        """Test counting URLs in empty configuration."""
        empty_config = {
            "accessible_verified": [],
            "accessible_unverified": [],
            "potential_links": []
        }
        total, verified, unverified, potential = count_urls(empty_config)
        self.assertEqual(total, 0)
        self.assertEqual(verified, 0)
        self.assertEqual(unverified, 0)
        self.assertEqual(potential, 0)
    
    def test_get_accessible_verified_config_none(self):
        """Test getting verified config when config is None (loads from file)."""
        # This will try to load from actual config file
        # Just test that it doesn't crash and returns a list
        try:
            verified = get_accessible_verified_config()
            self.assertIsInstance(verified, list)
        except FileNotFoundError:
            # Config file might not exist in test environment
            pass
    
    def test_get_potential_links_config_none(self):
        """Test getting potential links config when config is None (loads from file)."""
        # This will try to load from actual config file
        # Just test that it doesn't crash and returns a list
        try:
            potential = get_potential_links_config()
            self.assertIsInstance(potential, list)
        except FileNotFoundError:
            # Config file might not exist in test environment
            pass


class TestConfigLoaderIntegration(unittest.TestCase):
    """Integration tests with actual config file."""
    
    def test_real_config_structure(self):
        """Test that real config has the expected structure."""
        try:
            config = load_config()
            
            # Check that all three categories exist
            self.assertIn("accessible_verified", config)
            self.assertIn("accessible_unverified", config)
            self.assertIn("potential_links", config)
            
            # Check that they're lists
            self.assertIsInstance(config["accessible_verified"], list)
            self.assertIsInstance(config["accessible_unverified"], list)
            self.assertIsInstance(config["potential_links"], list)
            
            # Check that entries are dictionaries with required fields
            for entry in config["accessible_verified"]:
                self.assertIn("id", entry)
                self.assertIn("url", entry)
                
        except FileNotFoundError:
            # Config file might not exist in test environment
            self.skipTest("Config file not found")


if __name__ == '__main__':
    unittest.main()

