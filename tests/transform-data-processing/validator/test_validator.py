"""
Tests for data validator.

Tests validation functionality including:
- Schema validation
- Date validation
- URL validation
- Completeness checks
- Data quality checks
- Consistency checks
- Batch validation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.processor.validator import DataValidator
from scripts.processor.diagnostics import DiagnosticTracker
from scripts.processor.schema import get_empty_schema


def create_valid_job_listing() -> dict:
    """Create a valid job listing for testing."""
    return {
        "id": "abc123def456",
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
        "description": "We are seeking applications for an Assistant Professor position.",
        "requirements": "PhD in Economics or related field required.",
        "specializations": ["Macroeconomics", "Monetary Economics"],
        "application_link": "https://academicpositions.harvard.edu/job/123",
        "materials_required": {
            "cv": True,
            "cover_letter": True,
            "research_statement": True
        },
        "source": "university_website",
        "source_url": "https://economics.harvard.edu/positions",
        "sources": ["university_website"],
        "scraped_date": "2025-12-31",
        "processed_date": "2026-01-01",
        "is_active": True,
        "is_new": True
    }


class TestSchemaValidation:
    """Tests for schema validation."""
    
    def test_validate_valid_listing(self):
        """Test validation of a valid job listing."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert len(critical_errors) == 0
    
    def test_validate_missing_required_field(self):
        """Test validation fails when required field is missing."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        del listing["title"]  # Remove required field
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is False
        assert len(critical_errors) > 0
        assert any("title" in error.lower() for error in critical_errors)
    
    def test_validate_invalid_institution_type(self):
        """Test validation fails for invalid institution_type."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["institution_type"] = "invalid_type"
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is False
        assert any("institution_type" in error.lower() for error in critical_errors)
    
    def test_validate_invalid_job_type(self):
        """Test validation fails for invalid job_type."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["job_type"] = "invalid_type"
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is False
        assert any("job_type" in error.lower() for error in critical_errors)


class TestDateValidation:
    """Tests for date validation."""
    
    def test_validate_valid_date(self):
        """Test validation of valid date format."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        # Should have no date-related errors
        assert not any("date" in error.lower() for error in critical_errors)
    
    def test_validate_invalid_date_format(self):
        """Test validation fails for invalid date format."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["deadline"] = "2025/01/15"  # Invalid format
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is False
        assert any("date" in error.lower() and "deadline" in error.lower() for error in critical_errors)
    
    def test_validate_old_deadline_warning(self):
        """Test warning for old deadline."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["deadline"] = "2020-01-15"  # Very old deadline
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        # Should still be valid (format is correct) but have warning
        assert is_valid is True
        assert any("old" in warning.lower() or "stale" in warning.lower() for warning in warnings)
    
    def test_validate_processed_before_scraped_warning(self):
        """Test warning when processed_date is before scraped_date."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["scraped_date"] = "2026-01-05"
        listing["processed_date"] = "2026-01-01"  # Before scraped_date
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("processed_date" in warning.lower() and "scraped_date" in warning.lower() 
                   for warning in warnings)


class TestURLValidation:
    """Tests for URL validation."""
    
    def test_validate_valid_url(self):
        """Test validation of valid URL."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert not any("url" in error.lower() for error in critical_errors)
    
    def test_validate_invalid_url_format(self):
        """Test validation fails for invalid URL format."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["application_link"] = "not-a-url"
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is False
        assert any("url" in error.lower() and "application_link" in error.lower() 
                   for error in critical_errors)
    
    def test_validate_suspicious_url_warning(self):
        """Test warning for suspicious URL (example.com)."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["application_link"] = "https://example.com/job"
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True  # Format is valid
        assert any("suspicious" in warning.lower() for warning in warnings)
    
    def test_validate_invalid_email_warning(self):
        """Test warning for invalid email format."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["contact_email"] = "invalid-email"
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("email" in warning.lower() for warning in warnings)


class TestCompletenessValidation:
    """Tests for completeness checks."""
    
    def test_validate_missing_important_field_warning(self):
        """Test warning for missing important field (but description is actually required, so this tests completeness check)."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        # Note: description is actually a required field, so missing it creates a critical error
        # But the completeness check in _validate_completeness should still warn about empty important fields
        listing["description"] = ""  # Empty string (not missing, but empty)
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing, strict=False)
        
        # Empty description should generate a warning from completeness check
        assert any("empty" in warning.lower() and "description" in warning.lower() for warning in warnings)
    
    def test_validate_empty_location_warning(self):
        """Test warning for incomplete location."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["location"] = {
            "country": "United States",
            "region": "united_states"
        }  # Missing city and state
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("location" in warning.lower() and ("city" in warning.lower() or "state" in warning.lower())
                   for warning in warnings)
    
    def test_validate_empty_materials_warning(self):
        """Test warning for empty materials_required."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["materials_required"] = {}
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("materials_required" in warning.lower() and "empty" in warning.lower()
                   for warning in warnings)
    
    def test_validate_empty_specializations_warning(self):
        """Test warning for empty specializations."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["specializations"] = []
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("specializations" in warning.lower() and "empty" in warning.lower()
                   for warning in warnings)


class TestQualityValidation:
    """Tests for data quality checks."""
    
    def test_validate_short_title_warning(self):
        """Test warning for suspiciously short title."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["title"] = "Job"
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("short" in warning.lower() and "title" in warning.lower()
                   for warning in warnings)
    
    def test_validate_long_title_warning(self):
        """Test warning for unusually long title."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["title"] = "A" * 250  # Very long title
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("long" in warning.lower() and "title" in warning.lower()
                   for warning in warnings)
    
    def test_validate_short_description_warning(self):
        """Test warning for very short description."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["description"] = "Short"
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("short" in warning.lower() and "description" in warning.lower()
                   for warning in warnings)
    
    def test_validate_job_type_title_mismatch_warning(self):
        """Test warning for job_type and title mismatch."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["job_type"] = "visiting"
        listing["title"] = "Tenure-Track Assistant Professor"
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("job type" in warning.lower() and "title" in warning.lower()
                   for warning in warnings)


class TestConsistencyValidation:
    """Tests for consistency checks."""
    
    def test_validate_region_country_mismatch_warning(self):
        """Test warning for region-country mismatch."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["location"]["region"] = "united_states"
        listing["location"]["country"] = "China"  # Mismatch
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("region" in warning.lower() and "country" in warning.lower()
                   for warning in warnings)
    
    def test_validate_source_consistency_warning(self):
        """Test warning when source not in sources list."""
        validator = DataValidator()
        listing = create_valid_job_listing()
        listing["source"] = "university_website"
        listing["sources"] = ["aea"]  # Mismatch
        
        is_valid, critical_errors, warnings = validator.validate_job_listing(listing)
        
        assert is_valid is True
        assert any("source" in warning.lower() and "sources" in warning.lower()
                   for warning in warnings)


class TestDiagnosticIntegration:
    """Tests for diagnostic tracker integration."""
    
    def test_validator_tracks_validation_issues(self):
        """Test that validator tracks issues in diagnostics."""
        diagnostics = DiagnosticTracker()
        validator = DataValidator(diagnostics=diagnostics)
        listing = create_valid_job_listing()
        listing["deadline"] = "invalid-date"
        
        validator.validate_job_listing(listing)
        
        validation_issues = diagnostics.get_issues_by_category("validation_issues")
        assert len(validation_issues) > 0
        assert any("deadline" in issue.get("field", "").lower() or "date" in issue.get("error", "").lower()
                   for issue in validation_issues)


class TestBatchValidation:
    """Tests for batch validation."""
    
    def test_validate_batch_valid_listings(self):
        """Test batch validation of valid listings."""
        validator = DataValidator()
        listings = [
            create_valid_job_listing(),
            create_valid_job_listing()
        ]
        # Make second listing unique
        listings[1]["id"] = "xyz789"
        listings[1]["title"] = "Associate Professor"
        
        results = validator.validate_batch(listings)
        
        assert results["total"] == 2
        assert results["valid"] == 2
        assert results["invalid"] == 0
        assert len(results["results"]) == 2
        assert all(r["is_valid"] for r in results["results"])
    
    def test_validate_batch_mixed_listings(self):
        """Test batch validation with valid and invalid listings."""
        validator = DataValidator()
        listings = [
            create_valid_job_listing(),
            create_valid_job_listing()
        ]
        # Make second listing invalid
        listings[1]["id"] = "xyz789"
        listings[1]["deadline"] = "invalid-date"
        
        results = validator.validate_batch(listings)
        
        assert results["total"] == 2
        assert results["valid"] == 1
        assert results["invalid"] == 1
        assert results["total_critical_errors"] > 0
    
    def test_validate_batch_summary_statistics(self):
        """Test batch validation summary statistics."""
        validator = DataValidator()
        listings = [
            create_valid_job_listing(),
            create_valid_job_listing()
        ]
        listings[1]["id"] = "xyz789"
        listings[1]["title"] = "A"  # Short title (warning)
        listings[1]["description"] = "Short"  # Short description (warning)
        
        results = validator.validate_batch(listings)
        
        assert results["total"] == 2
        assert results["total_warnings"] > 0
        assert len(results["results"]) == 2

