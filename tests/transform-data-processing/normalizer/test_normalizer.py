"""
Tests for data normalizer.

Tests normalization functionality including:
- Date normalization
- Text normalization
- URL normalization
- Location normalization
- Job type normalization
- Department category mapping
- Contact information normalization
- Materials required parsing
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import with absolute path
from scripts.processor.normalizer import DataNormalizer
from scripts.processor.diagnostics import DiagnosticTracker


class TestDateNormalization:
    """Tests for date normalization."""
    
    def test_normalize_date_valid(self):
        """Test normalizing valid date strings."""
        normalizer = DataNormalizer()
        
        # Test various date formats
        date1, display1 = normalizer.normalize_date("2025-01-15", "deadline")
        assert date1 == "2025-01-15"
        assert "January" in display1 and "2025" in display1
        
        date2, display2 = normalizer.normalize_date("Jan 15, 2025", "deadline")
        assert date2 == "2025-01-15"
        
        date3, display3 = normalizer.normalize_date("01/15/2025", "deadline")
        assert date3 == "2025-01-15"
    
    def test_normalize_date_invalid(self):
        """Test normalizing invalid date strings."""
        normalizer = DataNormalizer()
        diagnostics = DiagnosticTracker()
        normalizer.diagnostics = diagnostics
        
        date, display = normalizer.normalize_date("invalid date", "deadline")
        assert date is None
        assert display is None
        assert len(diagnostics.get_issues_by_category("normalization_issues")) > 0
    
    def test_normalize_date_none(self):
        """Test normalizing None date."""
        normalizer = DataNormalizer()
        date, display = normalizer.normalize_date(None, "deadline")
        assert date is None
        assert display is None


class TestTextNormalization:
    """Tests for text normalization."""
    
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        normalizer = DataNormalizer()
        
        result = normalizer.normalize_text("  Hello   World  ", "title")
        assert result == "Hello World"
        
        result2 = normalizer.normalize_text("Test\n\nText", "description")
        assert "Test" in result2 and "Text" in result2
    
    def test_normalize_text_none(self):
        """Test normalizing None text."""
        normalizer = DataNormalizer()
        result = normalizer.normalize_text(None, "title")
        assert result is None


class TestURLNormalization:
    """Tests for URL normalization."""
    
    def test_normalize_url_valid(self):
        """Test normalizing valid URLs."""
        normalizer = DataNormalizer()
        
        url1 = normalizer.normalize_url("https://example.com/job", None, "application_link")
        assert url1 == "https://example.com/job"
        
        url2 = normalizer.normalize_url("http://example.com/job", None, "application_link")
        assert url2 == "http://example.com/job"
    
    def test_normalize_url_relative(self):
        """Test normalizing relative URLs with base URL."""
        normalizer = DataNormalizer()
        
        url = normalizer.normalize_url("/job", "https://example.com", "application_link")
        assert url == "https://example.com/job"
    
    def test_normalize_url_invalid(self):
        """Test normalizing invalid URLs."""
        normalizer = DataNormalizer()
        diagnostics = DiagnosticTracker()
        normalizer.diagnostics = diagnostics
        
        url = normalizer.normalize_url("not a url", None, "application_link")
        assert url is None
        assert len(diagnostics.get_issues_by_category("normalization_issues")) > 0


class TestLocationNormalization:
    """Tests for location normalization."""
    
    def test_normalize_location_us_string(self):
        """Test normalizing US location string."""
        normalizer = DataNormalizer()
        
        location = normalizer.normalize_location_field("Cambridge, MA")
        assert location["city"] == "Cambridge"
        assert location["state"] == "MA"
        assert location["country"] == "United States"
        assert location["region"] == "united_states"
    
    def test_normalize_location_china_string(self):
        """Test normalizing China location string."""
        normalizer = DataNormalizer()
        
        location = normalizer.normalize_location_field("北京市")
        assert location["country"] == "China"
        assert location["region"] == "mainland_china"
    
    def test_normalize_location_dict(self):
        """Test normalizing location dictionary."""
        normalizer = DataNormalizer()
        
        location_dict = {"city": "Boston", "state": "MA", "country": "United States"}
        location = normalizer.normalize_location_field(location_dict)
        assert location["city"] == "Boston"
        assert location["state"] == "MA"
        assert location["country"] == "United States"
        assert location["region"] == "united_states"


class TestJobTypeNormalization:
    """Tests for job type normalization."""
    
    def test_normalize_job_type_tenure_track(self):
        """Test normalizing tenure-track job type."""
        normalizer = DataNormalizer()
        
        job_type = normalizer.normalize_job_type("Tenure Track Assistant Professor", "Assistant Professor")
        assert job_type == "tenure-track"
        
        job_type2 = normalizer.normalize_job_type("tenure-track", "")
        assert job_type2 == "tenure-track"
    
    def test_normalize_job_type_visiting(self):
        """Test normalizing visiting job type."""
        normalizer = DataNormalizer()
        
        job_type = normalizer.normalize_job_type("Visiting Professor", "")
        assert job_type == "visiting"
    
    def test_normalize_job_type_postdoc(self):
        """Test normalizing postdoc job type."""
        normalizer = DataNormalizer()
        
        job_type = normalizer.normalize_job_type("Postdoctoral Fellow", "")
        assert job_type == "postdoc"
    
    def test_normalize_job_type_lecturer(self):
        """Test normalizing lecturer job type."""
        normalizer = DataNormalizer()
        
        job_type = normalizer.normalize_job_type("Lecturer", "")
        assert job_type == "lecturer"


class TestDepartmentCategoryNormalization:
    """Tests for department category mapping."""
    
    def test_normalize_department_economics(self):
        """Test mapping Economics department."""
        normalizer = DataNormalizer()
        
        category = normalizer.normalize_department_category("Department of Economics")
        assert category == "Economics"
        
        category2 = normalizer.normalize_department_category("Economics Department")
        assert category2 == "Economics"
    
    def test_normalize_department_management(self):
        """Test mapping Management department."""
        normalizer = DataNormalizer()
        
        category = normalizer.normalize_department_category("Business Administration")
        assert category == "Management"
    
    def test_normalize_department_marketing(self):
        """Test mapping Marketing department."""
        normalizer = DataNormalizer()
        
        category = normalizer.normalize_department_category("Marketing Department")
        assert category == "Marketing"
    
    def test_normalize_department_other(self):
        """Test mapping unknown department to Other."""
        normalizer = DataNormalizer()
        
        category = normalizer.normalize_department_category("Unknown Department")
        assert category == "Other"


class TestContactInformationNormalization:
    """Tests for contact information normalization."""
    
    def test_normalize_contact_email_valid(self):
        """Test normalizing valid email."""
        normalizer = DataNormalizer()
        
        email = normalizer.normalize_contact_email("test@example.com")
        assert email == "test@example.com"
        
        email2 = normalizer.normalize_contact_email("  TEST@EXAMPLE.COM  ")
        assert email2 == "test@example.com"
    
    def test_normalize_contact_email_with_prefix(self):
        """Test normalizing email with mailto: prefix."""
        normalizer = DataNormalizer()
        
        email = normalizer.normalize_contact_email("mailto:test@example.com")
        assert email == "test@example.com"
    
    def test_normalize_contact_email_invalid(self):
        """Test normalizing invalid email."""
        normalizer = DataNormalizer()
        diagnostics = DiagnosticTracker()
        normalizer.diagnostics = diagnostics
        
        email = normalizer.normalize_contact_email("not an email")
        assert email is None
    
    def test_normalize_contact_person(self):
        """Test normalizing contact person name."""
        normalizer = DataNormalizer()
        
        person = normalizer.normalize_contact_person("Dr. Jane Smith")
        assert "Jane" in person and "Smith" in person
        
        person2 = normalizer.normalize_contact_person("  john doe  ")
        assert "John" in person2 and "Doe" in person2


class TestMaterialsRequiredNormalization:
    """Tests for materials required parsing."""
    
    def test_normalize_materials_basic(self):
        """Test basic materials parsing."""
        normalizer = DataNormalizer()
        
        description = "Please submit CV, cover letter, and research statement."
        materials = normalizer.normalize_materials_required(description, "", None)
        
        assert materials.get("cv") is True
        assert materials.get("cover_letter") is True
        assert materials.get("research_statement") is True
    
    def test_normalize_materials_letters(self):
        """Test parsing letters of recommendation."""
        normalizer = DataNormalizer()
        
        description = "Submit 3 letters of recommendation."
        materials = normalizer.normalize_materials_required(description, "", None)
        
        assert materials.get("letters_of_recommendation") == 3
    
    def test_normalize_materials_research_papers(self):
        """Test parsing research papers."""
        normalizer = DataNormalizer()
        
        description = "Submit job market paper + 2 additional papers."
        materials = normalizer.normalize_materials_required(description, "", None)
        
        assert materials.get("research_papers") is not None


class TestCompleteJobListingNormalization:
    """Tests for complete job listing normalization."""
    
    def test_normalize_complete_listing(self):
        """Test normalizing a complete job listing."""
        normalizer = DataNormalizer()
        
        job_data = {
            "title": "  Assistant Professor of Economics  ",
            "institution": "Harvard University",
            "department": "Department of Economics",
            "location": "Cambridge, MA",
            "job_type": "Tenure Track",
            "deadline": "2025-01-15",
            "description": "Full description here.",
            "requirements": "PhD required.",
            "application_link": "https://example.com/apply",
            "contact_email": "  TEST@EXAMPLE.COM  ",
            "contact_person": "Dr. Jane Smith"
        }
        
        normalized = normalizer.normalize_job_listing(job_data)
        
        assert normalized["title"] == "Assistant Professor of Economics"
        assert normalized["deadline"] == "2025-01-15"
        assert "January" in normalized["deadline_display"]
        assert normalized["location"]["city"] == "Cambridge"
        assert normalized["location"]["state"] == "MA"
        assert normalized["job_type"] == "tenure-track"
        assert normalized["department_category"] == "Economics"
        assert normalized["contact_email"] == "test@example.com"
        assert normalized["application_link"] == "https://example.com/apply"
    
    def test_normalize_listing_with_materials(self):
        """Test normalizing listing with materials in description."""
        normalizer = DataNormalizer()
        
        job_data = {
            "title": "Assistant Professor",
            "institution": "MIT",
            "department": "Economics",
            "location": "Cambridge, MA",
            "job_type": "tenure-track",
            "deadline": "2025-01-15",
            "description": "Submit CV, cover letter, research statement, and 3 letters of recommendation.",
            "requirements": "PhD required.",
            "application_link": "https://example.com/apply"
        }
        
        normalized = normalizer.normalize_job_listing(job_data)
        
        materials = normalized.get("materials_required", {})
        assert materials.get("cv") is True
        assert materials.get("cover_letter") is True
        assert materials.get("research_statement") is True
        assert materials.get("letters_of_recommendation") == 3


if __name__ == "__main__":
    # Run tests
    print("Running Normalizer Tests...")
    print("=" * 60)
    
    test_classes = [
        TestDateNormalization,
        TestTextNormalization,
        TestURLNormalization,
        TestLocationNormalization,
        TestJobTypeNormalization,
        TestDepartmentCategoryNormalization,
        TestContactInformationNormalization,
        TestMaterialsRequiredNormalization,
        TestCompleteJobListingNormalization
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        for test_name in dir(test_class):
            if test_name.startswith("test_"):
                test_method = getattr(test_class, test_name)
                try:
                    instance = test_class()
                    test_method(instance)
                    print(f"  [PASS] {test_name}")
                    passed += 1
                except Exception as e:
                    print(f"  [FAIL] {test_name}: {e}")
                    failed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}, Tests failed: {failed}")
    print("=" * 60)

