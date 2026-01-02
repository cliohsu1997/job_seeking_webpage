"""
Tests for the deduplicator module.
"""

import unittest
from datetime import date, timedelta
from pathlib import Path
import json
import tempfile

from scripts.processor.deduplicator import (
    Deduplicator,
    DEFAULT_TITLE_SIMILARITY,
    DEFAULT_INSTITUTION_SIMILARITY
)
from scripts.processor.diagnostics import DiagnosticTracker


class TestDeduplicator(unittest.TestCase):
    """Test cases for the Deduplicator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.diagnostics = DiagnosticTracker()
        self.deduplicator = Deduplicator(diagnostics=self.diagnostics)
        
        # Sample listing template
        self.base_listing = {
            "id": "test_id_1",
            "title": "Assistant Professor of Economics",
            "institution": "Harvard University",
            "institution_type": "university",
            "department": "Department of Economics",
            "department_category": "Economics",
            "location": {
                "city": "Cambridge",
                "state": "MA",
                "country": "United States",
                "region": "united_states"
            },
            "job_type": "tenure-track",
            "deadline": "2025-01-15",
            "deadline_display": "January 15, 2025",
            "description": "Full job description",
            "requirements": "PhD required",
            "specializations": ["Macroeconomics"],
            "application_link": "https://example.com/apply",
            "materials_required": {"cv": True, "cover_letter": True},
            "source": "university_website",
            "source_url": "https://example.com/job",
            "sources": ["university_website"],
            "scraped_date": "2025-12-31",
            "processed_date": "2026-01-01",
            "is_active": True,
            "is_new": True
        }
    
    def test_init(self):
        """Test deduplicator initialization."""
        dedup = Deduplicator()
        self.assertEqual(dedup.title_similarity_threshold, DEFAULT_TITLE_SIMILARITY)
        self.assertEqual(dedup.institution_similarity_threshold, DEFAULT_INSTITUTION_SIMILARITY)
        
        dedup_custom = Deduplicator(title_similarity_threshold=80, institution_similarity_threshold=85)
        self.assertEqual(dedup_custom.title_similarity_threshold, 80)
        self.assertEqual(dedup_custom.institution_similarity_threshold, 85)
    
    def test_deduplicate_empty(self):
        """Test deduplication with empty list."""
        listings, stats = self.deduplicator.deduplicate([])
        self.assertEqual(listings, [])
        self.assertEqual(stats["input_count"], 0)
        self.assertEqual(stats["output_count"], 0)
    
    def test_deduplicate_no_duplicates(self):
        """Test deduplication with no duplicates."""
        listing1 = self.base_listing.copy()
        listing2 = self.base_listing.copy()
        listing2["id"] = "test_id_2"
        listing2["institution"] = "MIT"
        listing2["title"] = "Associate Professor"
        
        deduplicated, stats = self.deduplicator.deduplicate([listing1, listing2])
        
        self.assertEqual(len(deduplicated), 2)
        self.assertEqual(stats["input_count"], 2)
        self.assertEqual(stats["merges_performed"], 0)
    
    def test_deduplicate_exact_duplicates(self):
        """Test deduplication with exact duplicates."""
        listing1 = self.base_listing.copy()
        listing2 = self.base_listing.copy()
        listing2["id"] = "test_id_2"
        
        deduplicated, stats = self.deduplicator.deduplicate([listing1, listing2])
        
        self.assertEqual(len(deduplicated), 1)
        self.assertEqual(stats["merges_performed"], 1)
    
    def test_deduplicate_fuzzy_match(self):
        """Test deduplication with fuzzy title matching."""
        listing1 = self.base_listing.copy()
        listing2 = self.base_listing.copy()
        listing2["id"] = "test_id_2"
        listing2["title"] = "Assistant Prof. of Economics"  # Slight variation
        
        deduplicated, stats = self.deduplicator.deduplicate([listing1, listing2])
        
        self.assertEqual(len(deduplicated), 1)
        self.assertEqual(stats["merges_performed"], 1)
    
    def test_deduplicate_different_deadlines(self):
        """Test that listings with different deadlines are not merged."""
        listing1 = self.base_listing.copy()
        listing2 = self.base_listing.copy()
        listing2["id"] = "test_id_2"
        listing2["deadline"] = "2025-02-15"
        
        deduplicated, stats = self.deduplicator.deduplicate([listing1, listing2])
        
        self.assertEqual(len(deduplicated), 2)
        self.assertEqual(stats["merges_performed"], 0)
    
    def test_merge_listings(self):
        """Test merging duplicate listings."""
        listing1 = self.base_listing.copy()
        listing1["source"] = "aea"
        listing1["sources"] = ["aea"]
        listing1["contact_email"] = None
        
        listing2 = self.base_listing.copy()
        listing2["id"] = "test_id_2"
        listing2["source"] = "university_website"
        listing2["sources"] = ["university_website"]
        listing2["contact_email"] = "jobs@example.com"
        listing2["specializations"] = ["Macroeconomics", "Labor Economics"]
        
        merged = self.deduplicator._merge_listings([listing1, listing2])
        
        # Should aggregate sources
        self.assertIn("aea", merged["sources"])
        self.assertIn("university_website", merged["sources"])
        # Should fill missing fields
        self.assertEqual(merged["contact_email"], "jobs@example.com")
        # Should merge specializations
        self.assertIn("Labor Economics", merged["specializations"])
        # Should prefer AEA source
        self.assertEqual(merged["source"], "aea")
    
    def test_completeness_score(self):
        """Test completeness score calculation."""
        complete_score = self.deduplicator._calculate_completeness_score(self.base_listing)
        self.assertGreater(complete_score, 80)
        
        incomplete_score = self.deduplicator._calculate_completeness_score({"title": "Test"})
        self.assertLess(incomplete_score, 30)
    
    def test_normalize_institution_name(self):
        """Test institution name normalization."""
        normalized = self.deduplicator._normalize_institution_name("Harvard University")
        self.assertIn("harvard", normalized.lower())
        
        normalized = self.deduplicator._normalize_institution_name("  MIT  ")
        self.assertIn("mit", normalized.lower())
    
    def test_detect_new_and_active(self):
        """Test new and active listing detection."""
        # No previous data with future deadline - should be new and active
        listing = self.base_listing.copy()
        future_date = (date.today() + timedelta(days=60)).strftime("%Y-%m-%d")
        listing["deadline"] = future_date
        result = self.deduplicator._detect_new_and_active_listings([listing], [])
        self.assertTrue(result[0]["is_new"])
        self.assertTrue(result[0]["is_active"])
        
        # Past deadline - should not be active
        past_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        listing["deadline"] = past_date
        result = self.deduplicator._detect_new_and_active_listings([listing], [])
        self.assertFalse(result[0]["is_active"])
        
        # Existing listing - should not be new
        listing["deadline"] = future_date  # Reset to future for active check
        listing["id"] = "same_id"
        previous = [self.base_listing.copy()]
        previous[0]["id"] = "same_id"
        previous[0]["deadline"] = future_date
        result = self.deduplicator._detect_new_and_active_listings([listing], previous)
        self.assertFalse(result[0]["is_new"])
    
    def test_load_previous_listings(self):
        """Test loading previous listings from archive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_dir = Path(tmpdir)
            archive_file = archive_dir / "2025-12-31_jobs.json"
            
            # Test wrapped format
            archive_data = {
                "metadata": {"generated_at": "2025-12-31T00:00:00"},
                "listings": [self.base_listing.copy()]
            }
            with open(archive_file, "w", encoding="utf-8") as f:
                json.dump(archive_data, f)
            
            previous = self.deduplicator.load_previous_listings(archive_dir)
            self.assertEqual(len(previous), 1)
            
            # Test array format
            archive_data = [self.base_listing.copy()]
            with open(archive_file, "w", encoding="utf-8") as f:
                json.dump(archive_data, f)
            
            previous = self.deduplicator.load_previous_listings(archive_dir)
            self.assertEqual(len(previous), 1)
        
        # Test nonexistent directory
        previous = self.deduplicator.load_previous_listings(Path("/nonexistent"))
        self.assertEqual(previous, [])
    
    def test_parse_date_safely(self):
        """Test safe date parsing."""
        parsed = self.deduplicator._parse_date_safely("2025-01-15")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.year, 2025)
        
        self.assertIsNone(self.deduplicator._parse_date_safely("invalid"))
        self.assertIsNone(self.deduplicator._parse_date_safely(None))
    
    def test_multiple_duplicates(self):
        """Test merging multiple duplicates."""
        listing1 = self.base_listing.copy()
        listing1["id"] = "id_1"
        listing1["source"] = "aea"
        
        listing2 = self.base_listing.copy()
        listing2["id"] = "id_2"
        listing2["source"] = "university_website"
        
        listing3 = self.base_listing.copy()
        listing3["id"] = "id_3"
        listing3["source"] = "institute_website"
        
        deduplicated, stats = self.deduplicator.deduplicate([listing1, listing2, listing3])
        
        self.assertEqual(len(deduplicated), 1)
        self.assertEqual(stats["merges_performed"], 2)
        self.assertEqual(len(deduplicated[0]["sources"]), 3)


if __name__ == "__main__":
    unittest.main()
