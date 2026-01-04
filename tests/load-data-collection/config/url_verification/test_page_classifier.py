"""Tests for URL verification page classification."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from scripts.scraper.config.url_verification.page_classifier import (
    classify_page_type,
    PageType,
    is_job_portal,
    is_useful_for_jobs,
)


class TestClassifyPageType:
    """Test page type classification."""
    
    def test_classify_job_portal(self):
        """Test classification of job portal pages."""
        html = """
        <html>
            <title>Careers - University Economics Department</title>
            <meta name="description" content="Career opportunities in economics">
            <h1>Faculty Positions</h1>
            <div class="job-listing">
                <a href="/jobs/1">Assistant Professor</a>
                <a href="/jobs/2">Associate Professor</a>
                <a href="/jobs/3">Postdoctoral Fellow</a>
            </div>
        </html>
        """
        
        page_type, confidence, details = classify_page_type(
            html,
            url="https://university.edu/careers",
        )
        
        assert page_type == PageType.JOB_PORTAL
        assert confidence >= 0.5
        assert details["job_links_count"] >= 3
    
    def test_classify_faculty_directory(self):
        """Test classification of faculty directory pages."""
        html = """
        <html>
            <title>Faculty Directory - Economics Department</title>
            <h1>Our Faculty Members</h1>
            <div class="faculty-profile">
                <h3>Prof. John Smith</h3>
                <a href="mailto:john@university.edu">john@university.edu</a>
            </div>
            <div class="faculty-profile">
                <h3>Prof. Jane Doe</h3>
                <a href="mailto:jane@university.edu">jane@university.edu</a>
            </div>
        </html>
        """
        
        page_type, confidence, details = classify_page_type(html)
        
        assert page_type == PageType.FACULTY_DIRECTORY
        assert confidence >= 0.4
        assert details["email_count"] >= 2
    
    def test_classify_department_page(self):
        """Test classification of general department pages."""
        html = """
        <html>
            <title>About the Economics Department</title>
            <h1>About Us</h1>
            <p>Our department offers undergraduate and graduate programs...</p>
            <p>Research areas include microeconomics, macroeconomics...</p>
        </html>
        """
        
        page_type, confidence, details = classify_page_type(html)
        
        assert page_type in [PageType.DEPARTMENT_PAGE, PageType.UNKNOWN]
    
    def test_classify_single_job_posting(self):
        """Test classification of single job detail pages."""
        html = """
        <html>
            <title>Assistant Professor of Economics - University</title>
            <h1>Assistant Professor of Economics</h1>
            <p>The Economics Department invites applications for a tenure-track
               Assistant Professor position beginning Fall 2026...</p>
            <p>Qualifications: PhD in Economics required...</p>
            <button>Apply Now</button>
        </html>
        """
        
        page_type, confidence, details = classify_page_type(html)
        
        assert page_type in [PageType.SINGLE_JOB_POSTING, PageType.JOB_PORTAL]
        if page_type == PageType.SINGLE_JOB_POSTING:
            assert details.get("has_position_title") is True
    
    def test_classify_error_page(self):
        """Test classification of error pages."""
        html = """
        <html>
            <title>404 - Page Not Found</title>
            <h1>Error 404</h1>
            <p>The page you requested could not be found.</p>
        </html>
        """
        
        page_type, confidence, details = classify_page_type(html)
        
        assert page_type == PageType.ERROR_PAGE
        assert confidence >= 0.5
    
    def test_classify_external_hr_system(self):
        """Test classification of external HR systems."""
        page_type, confidence, details = classify_page_type(
            "<html><title>Jobs</title></html>",
            url="https://university.icims.com/jobs",
        )
        
        assert page_type == PageType.EXTERNAL_SYSTEM
        assert confidence == 1.0
        assert "icims" in details.get("external_system", "")
    
    def test_classify_unknown_page(self):
        """Test classification of unclear pages."""
        html = """
        <html>
            <title>University</title>
            <p>Some generic content...</p>
        </html>
        """
        
        page_type, confidence, details = classify_page_type(html)
        
        assert page_type == PageType.UNKNOWN or confidence < 0.5


class TestIsJobPortal:
    """Test job portal helper function."""
    
    def test_is_job_portal_high_confidence(self):
        """Test identification of job portal with high confidence."""
        assert is_job_portal(PageType.JOB_PORTAL, 0.8)
    
    def test_is_job_portal_medium_confidence(self):
        """Test identification of job portal with medium confidence."""
        assert is_job_portal(PageType.JOB_PORTAL, 0.5)
    
    def test_not_job_portal_low_confidence(self):
        """Test rejection of job portal with low confidence."""
        assert not is_job_portal(PageType.JOB_PORTAL, 0.4)
    
    def test_not_job_portal_wrong_type(self):
        """Test rejection of non-job-portal pages."""
        assert not is_job_portal(PageType.FACULTY_DIRECTORY, 0.9)
        assert not is_job_portal(PageType.DEPARTMENT_PAGE, 0.8)


class TestIsUsefulForJobs:
    """Test useful-for-jobs helper function."""
    
    def test_job_portal_is_useful(self):
        """Test that job portals are useful."""
        assert is_useful_for_jobs(PageType.JOB_PORTAL, 0.6)
    
    def test_single_posting_is_useful(self):
        """Test that single postings are useful."""
        assert is_useful_for_jobs(PageType.SINGLE_JOB_POSTING, 0.5)
    
    def test_faculty_directory_not_useful(self):
        """Test that faculty directories are not useful."""
        assert not is_useful_for_jobs(PageType.FACULTY_DIRECTORY, 0.8)
    
    def test_department_page_not_useful(self):
        """Test that department pages are not useful."""
        assert not is_useful_for_jobs(PageType.DEPARTMENT_PAGE, 0.7)
    
    def test_low_confidence_not_useful(self):
        """Test that low confidence pages are not useful."""
        assert not is_useful_for_jobs(PageType.JOB_PORTAL, 0.3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
