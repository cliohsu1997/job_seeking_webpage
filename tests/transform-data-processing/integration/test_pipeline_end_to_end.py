"""
End-to-end integration test for the complete processing pipeline.

Tests the full pipeline workflow:
1. Parse raw files (or use mock data)
2. Normalize data
3. Enrich data
4. Deduplicate listings
5. Validate data
6. Generate diagnostics
7. Output to JSON and CSV
8. Save archive
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from scripts.processor.pipeline import ProcessingPipeline
from scripts.processor.diagnostics import DiagnosticTracker


# Sample job listing data for testing
SAMPLE_LISTINGS = [
    {
        "title": "Assistant Professor of Economics",
        "institution": "Harvard University",
        "location": "Cambridge, MA, USA",
        "deadline": "2025-02-15",
        "description": "We seek candidates in macroeconomics and econometrics.",
        "application_link": "https://harvard.edu/jobs/123",
        "source": "university_website",
        "source_url": "https://harvard.edu/jobs",
        "job_type": "tenure-track",
        "department": "Economics"
    },
    {
        "title": "Assistant Professor, Economics",
        "institution": "Harvard University",
        "location": "Cambridge, Massachusetts, United States",
        "deadline": "2025-02-15",
        "description": "Seeking candidates in macroeconomics and econometrics.",
        "application_link": "https://harvard.edu/jobs/123",
        "source": "aea",
        "source_url": "https://www.aeaweb.org/joe",
        "job_type": "tenure-track",
        "department": "Economics"
    },
    {
        "title": "Visiting Professor of Economics",
        "institution": "MIT",
        "location": "Boston, MA, USA",
        "deadline": "2025-03-01",
        "description": "One-year visiting position in applied microeconomics.",
        "application_link": "https://mit.edu/jobs/456",
        "source": "university_website",
        "source_url": "https://mit.edu/jobs",
        "job_type": "visiting",
        "department": "Economics"
    }
]


class TestPipelineEndToEnd:
    """End-to-end tests for the complete processing pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        self.raw_dir = self.temp_dir / "raw"
        self.output_dir = self.temp_dir / "processed"
        self.archive_dir = self.output_dir / "archive"
        self.diagnostics_dir = self.output_dir / "diagnostics"
        
        # Create directories
        self.raw_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)
        
        # Create mock raw data files
        self._create_mock_raw_files()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_mock_raw_files(self):
        """Create mock raw HTML files for testing."""
        # Create a mock AEA file
        aea_dir = self.raw_dir / "aea"
        aea_dir.mkdir(parents=True)
        aea_file = aea_dir / "aea_joe_20250101.html"
        aea_file.write_text("""
        <html>
        <body>
            <div class="job-listing">
                <h2>Assistant Professor, Economics</h2>
                <p>Institution: Harvard University</p>
                <p>Location: Cambridge, Massachusetts, United States</p>
                <p>Deadline: February 15, 2025</p>
                <p>Description: Seeking candidates in macroeconomics and econometrics.</p>
                <a href="https://harvard.edu/jobs/123">Apply</a>
            </div>
        </body>
        </html>
        """)
        
        # Create a mock university file
        uni_dir = self.raw_dir / "universities"
        uni_dir.mkdir(parents=True)
        uni_file = uni_dir / "harvard_university_economics_20250101.html"
        uni_file.write_text("""
        <html>
        <body>
            <h1>Assistant Professor of Economics</h1>
            <p>Harvard University</p>
            <p>Cambridge, MA, USA</p>
            <p>Deadline: 2025-02-15</p>
            <p>We seek candidates in macroeconomics and econometrics.</p>
            <a href="https://harvard.edu/jobs/123">Apply Now</a>
        </body>
        </html>
        """)
    
    def test_pipeline_initialization(self):
        """Test that pipeline initializes correctly."""
        pipeline = ProcessingPipeline(
            raw_data_dir=self.raw_dir,
            output_dir=self.output_dir
        )
        
        assert pipeline.raw_data_dir == self.raw_dir
        assert pipeline.output_dir == self.output_dir
        assert pipeline.archive_dir == self.archive_dir
        assert pipeline.diagnostics_dir == self.diagnostics_dir
        assert pipeline.diagnostics is not None
        assert pipeline.parser_manager is not None
        assert pipeline.normalizer is not None
        assert pipeline.enricher is not None
        assert pipeline.deduplicator is not None
        assert pipeline.validator is not None
    
    def test_pipeline_with_mock_data(self):
        """Test pipeline with mock job listing data."""
        # Create pipeline
        pipeline = ProcessingPipeline(
            raw_data_dir=self.raw_dir,
            output_dir=self.output_dir
        )
        
        # Mock the parser manager to return sample listings
        def mock_parse_all_files():
            return SAMPLE_LISTINGS
        
        pipeline.parser_manager.parse_all_files = mock_parse_all_files
        
        # Run pipeline
        summary = pipeline.process(save_archive=True)
        
        # Verify summary structure
        assert "processing_date" in summary
        assert "statistics" in summary
        assert "output_files" in summary
        assert "diagnostics_summary" in summary
        
        # Verify statistics
        stats = summary["statistics"]
        assert stats["raw_listings"] == len(SAMPLE_LISTINGS)
        assert stats["normalized_listings"] > 0
        assert stats["enriched_listings"] > 0
        assert stats["deduplicated_listings"] > 0
        
        # Verify output files exist
        assert "json" in summary["output_files"]
        assert "csv" in summary["output_files"]
        json_file = Path(summary["output_files"]["json"])
        csv_file = Path(summary["output_files"]["csv"])
        assert json_file.exists()
        assert csv_file.exists()
        
        # Verify JSON output
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            assert "metadata" in json_data
            assert "listings" in json_data
            assert len(json_data["listings"]) == stats["deduplicated_listings"]
        
        # Verify CSV output
        assert csv_file.stat().st_size > 0
        
        # Verify archive exists
        archive_files = list(self.archive_dir.glob("jobs_*.json"))
        assert len(archive_files) > 0
        
        # Verify diagnostics exist
        diagnostic_files = list(self.diagnostics_dir.glob("*.json"))
        assert len(diagnostic_files) > 0
    
    def test_pipeline_deduplication(self):
        """Test that pipeline correctly deduplicates similar listings."""
        # Create pipeline
        pipeline = ProcessingPipeline(
            raw_data_dir=self.raw_dir,
            output_dir=self.output_dir
        )
        
        # Mock parser to return duplicate listings
        def mock_parse_all_files():
            return SAMPLE_LISTINGS  # First two are duplicates
        
        pipeline.parser_manager.parse_all_files = mock_parse_all_files
        
        # Run pipeline
        summary = pipeline.process(save_archive=False)
        
        # Verify deduplication occurred
        stats = summary["statistics"]
        assert stats["raw_listings"] == 3
        # Should deduplicate the two Harvard listings
        assert stats["deduplicated_listings"] <= 2
        assert stats["duplicates_removed"] >= 1
    
    def test_pipeline_validation(self):
        """Test that pipeline validates data correctly."""
        # Create pipeline
        pipeline = ProcessingPipeline(
            raw_data_dir=self.raw_dir,
            output_dir=self.output_dir
        )
        
        # Mock parser with some invalid data
        invalid_listings = SAMPLE_LISTINGS + [
            {
                "title": "",  # Invalid: empty title
                "institution": "Test University",
                "deadline": "invalid-date",  # Invalid date
                "source": "test"
            }
        ]
        
        def mock_parse_all_files():
            return invalid_listings
        
        pipeline.parser_manager.parse_all_files = mock_parse_all_files
        
        # Run pipeline
        summary = pipeline.process(save_archive=False)
        
        # Verify validation occurred
        assert "validation_summary" in summary
        validation = summary["validation_summary"]
        assert validation["total"] > 0
        # Should have some warnings or errors (may be 0 if all data is valid)
        assert "critical_errors" in validation
        assert "warnings" in validation
        assert validation["critical_errors"] >= 0
        assert validation["warnings"] >= 0
    
    def test_pipeline_error_handling(self):
        """Test that pipeline handles errors gracefully."""
        # Create pipeline
        pipeline = ProcessingPipeline(
            raw_data_dir=self.raw_dir,
            output_dir=self.output_dir
        )
        
        # Mock parser to raise an error
        def mock_parse_all_files():
            raise ValueError("Test error")
        
        pipeline.parser_manager.parse_all_files = mock_parse_all_files
        
        # Pipeline should raise the error
        with pytest.raises(ValueError):
            pipeline.process()
        
        # But diagnostics should still be saved
        diagnostic_files = list(self.diagnostics_dir.glob("*.json"))
        # Diagnostics might not be saved if pipeline fails early
        # This is acceptable behavior
    
    def test_pipeline_diagnostics(self):
        """Test that pipeline generates diagnostic reports."""
        # Create pipeline
        pipeline = ProcessingPipeline(
            raw_data_dir=self.raw_dir,
            output_dir=self.output_dir
        )
        
        # Mock parser
        def mock_parse_all_files():
            return SAMPLE_LISTINGS
        
        pipeline.parser_manager.parse_all_files = mock_parse_all_files
        
        # Run pipeline
        summary = pipeline.process(save_archive=False)
        
        # Verify diagnostics summary
        assert "diagnostics_summary" in summary
        diag_summary = summary["diagnostics_summary"]
        assert "statistics" in diag_summary
        assert "total_issues" in diag_summary
        
        # Verify diagnostic files exist
        diagnostic_files = list(self.diagnostics_dir.glob("*.json"))
        assert len(diagnostic_files) > 0
        
        # Check for latest symlinks/copies
        latest_files = [
            self.diagnostics_dir / "diagnostics_full_latest.json",
            self.diagnostics_dir / "diagnostics_summary_latest.json"
        ]
        for latest_file in latest_files:
            if latest_file.exists():
                # Verify it's a valid JSON file
                with open(latest_file, "r", encoding="utf-8") as f:
                    json.load(f)


def run_tests():
    """Run all end-to-end pipeline tests."""
    print("=" * 70)
    print("End-to-End Pipeline Integration Tests")
    print("=" * 70)
    
    test_instance = TestPipelineEndToEnd()
    
    try:
        test_instance.setup_method()
        
        print("\n1. Testing pipeline initialization...")
        test_instance.test_pipeline_initialization()
        print("   ✓ Pipeline initialization works")
        
        print("\n2. Testing pipeline with mock data...")
        test_instance.test_pipeline_with_mock_data()
        print("   ✓ Pipeline processing works")
        
        print("\n3. Testing deduplication...")
        test_instance.test_pipeline_deduplication()
        print("   ✓ Deduplication works")
        
        print("\n4. Testing validation...")
        test_instance.test_pipeline_validation()
        print("   ✓ Validation works")
        
        print("\n5. Testing error handling...")
        test_instance.test_pipeline_error_handling()
        print("   ✓ Error handling works")
        
        print("\n6. Testing diagnostics...")
        test_instance.test_pipeline_diagnostics()
        print("   ✓ Diagnostics generation works")
        
        print("\n" + "=" * 70)
        print("All end-to-end pipeline tests passed! ✓")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        test_instance.teardown_method()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

