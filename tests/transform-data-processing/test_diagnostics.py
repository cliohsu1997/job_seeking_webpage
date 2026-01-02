"""
Tests for diagnostic tracker report generation.

Tests report generation functionality including:
- Root cause analysis
- Category statistics
- Report generation
- Report saving
- Human-readable summaries
"""

import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.processor.diagnostics import DiagnosticTracker


class TestRootCauseAnalysis:
    """Tests for root cause analysis."""
    
    def test_analyze_by_source(self):
        """Test analysis by source."""
        diagnostics = DiagnosticTracker()
        
        # Add some issues from different sources
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        diagnostics.track_url_issue("http://example2.com", "404", source="source2")
        diagnostics.track_parsing_issue("source1", error="Parse error")
        
        analysis = diagnostics.analyze_root_causes()
        
        assert "by_source" in analysis
        assert "source1" in analysis["by_source"]
        assert "source2" in analysis["by_source"]
        assert analysis["by_source"]["source1"]["url_issues"] == 1
        assert analysis["by_source"]["source1"]["parsing_issues"] == 1
    
    def test_analyze_by_error_type(self):
        """Test analysis by error type."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_scraping_issue("source1", "http://example.com", "Timeout", error_type="TIMEOUT")
        diagnostics.track_scraping_issue("source2", "http://example2.com", "404", error_type="HTTP_ERROR")
        diagnostics.track_scraping_issue("source1", "http://example3.com", "Timeout", error_type="TIMEOUT")
        
        analysis = diagnostics.analyze_root_causes()
        
        assert "by_error_type" in analysis
        assert analysis["by_error_type"]["TIMEOUT"] == 2
        assert analysis["by_error_type"]["HTTP_ERROR"] == 1
    
    def test_most_common_errors(self):
        """Test identification of most common errors."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_validation_issue("source1", field="deadline", error="Invalid date format", validation_type="DATE_FORMAT")
        diagnostics.track_validation_issue("source2", field="deadline", error="Invalid date format", validation_type="DATE_FORMAT")
        diagnostics.track_validation_issue("source1", field="url", error="Invalid URL format", validation_type="URL_FORMAT")
        
        analysis = diagnostics.analyze_root_causes()
        
        assert "most_common_errors" in analysis
        assert len(analysis["most_common_errors"]) > 0
        # Should have "Invalid date format" as most common
        assert any("date" in error[0].lower() for error in analysis["most_common_errors"])


class TestCategoryStatistics:
    """Tests for category statistics generation."""
    
    def test_generate_category_statistics(self):
        """Test category statistics generation."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        diagnostics.track_url_issue("http://example2.com", "404", source="source2")
        diagnostics.track_parsing_issue("source1", error="Parse error")
        
        stats = diagnostics._generate_category_statistics()
        
        assert "url_issues" in stats
        assert stats["url_issues"]["total"] == 2
        assert stats["url_issues"]["sources_affected"] == 2
        assert "source1" in stats["url_issues"]["unique_sources"]
        assert "source2" in stats["url_issues"]["unique_sources"]
        
        assert "parsing_issues" in stats
        assert stats["parsing_issues"]["total"] == 1
    
    def test_category_statistics_empty(self):
        """Test category statistics with no issues."""
        diagnostics = DiagnosticTracker()
        
        stats = diagnostics._generate_category_statistics()
        
        assert stats == {}


class TestCategoryReport:
    """Tests for category-specific reports."""
    
    def test_generate_category_report(self):
        """Test category report generation."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        diagnostics.track_url_issue("http://example2.com", "404", source="source2")
        
        report = diagnostics.generate_category_report("url_issues")
        
        assert report["category"] == "url_issues"
        assert report["total"] == 2
        assert "source1" in report["unique_sources"]
        assert "source2" in report["unique_sources"]
        assert len(report["issues"]) == 2
    
    def test_generate_category_report_empty(self):
        """Test category report for empty category."""
        diagnostics = DiagnosticTracker()
        
        report = diagnostics.generate_category_report("url_issues")
        
        assert report["category"] == "url_issues"
        assert report["total"] == 0
        assert report["issues"] == []


class TestReportGeneration:
    """Tests for full report generation."""
    
    def test_generate_report(self):
        """Test full report generation."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        diagnostics.track_parsing_issue("source1", error="Parse error")
        
        report = diagnostics.generate_report(include_root_causes=True)
        
        assert "summary" in report
        assert "statistics_by_category" in report
        assert "issues" in report
        assert "root_cause_analysis" in report
        assert report["summary"]["total_issues"] == 2
    
    def test_generate_report_without_root_causes(self):
        """Test report generation without root causes."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        
        report = diagnostics.generate_report(include_root_causes=False)
        
        assert "summary" in report
        assert "statistics_by_category" in report
        assert "root_cause_analysis" not in report


class TestHumanReadableSummary:
    """Tests for human-readable summary generation."""
    
    def test_generate_human_readable_summary(self):
        """Test human-readable summary generation."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        diagnostics.track_parsing_issue("source1", error="Parse error")
        
        summary = diagnostics.generate_human_readable_summary()
        
        assert isinstance(summary, str)
        assert "DIAGNOSTIC REPORT SUMMARY" in summary
        assert "Total Issues: 2" in summary
        assert "url_issues" in summary
        assert "parsing_issues" in summary
    
    def test_human_readable_summary_empty(self):
        """Test human-readable summary with no issues."""
        diagnostics = DiagnosticTracker()
        
        summary = diagnostics.generate_human_readable_summary()
        
        assert isinstance(summary, str)
        assert "DIAGNOSTIC REPORT SUMMARY" in summary
        assert "Total Issues: 0" in summary


class TestReportSaving:
    """Tests for saving reports to files."""
    
    def test_save_report(self):
        """Test saving reports to files."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        diagnostics.track_parsing_issue("source1", error="Parse error")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            saved_files = diagnostics.save_report(
                output_dir=output_dir,
                include_category_files=True,
                include_text_summary=True
            )
            
            # Check that files were created
            assert "full_report" in saved_files
            assert saved_files["full_report"].exists()
            
            assert "summary_report" in saved_files
            assert saved_files["summary_report"].exists()
            
            assert "category_reports" in saved_files
            assert "url_issues" in saved_files["category_reports"]
            assert saved_files["category_reports"]["url_issues"].exists()
            
            assert "text_summary" in saved_files
            assert saved_files["text_summary"].exists()
            
            # Check that JSON files are valid
            with open(saved_files["full_report"], "r", encoding="utf-8") as f:
                data = json.load(f)
                assert "summary" in data
                assert "issues" in data
            
            # Check that text summary is readable
            with open(saved_files["text_summary"], "r", encoding="utf-8") as f:
                text = f.read()
                assert "DIAGNOSTIC REPORT SUMMARY" in text
    
    def test_save_report_minimal(self):
        """Test saving reports with minimal options."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            saved_files = diagnostics.save_report(
                output_dir=output_dir,
                include_category_files=False,
                include_text_summary=False
            )
            
            assert "full_report" in saved_files
            assert "summary_report" in saved_files
            assert "category_reports" not in saved_files
            assert "text_summary" not in saved_files
    
    def test_save_report_latest_files(self):
        """Test that latest files are created."""
        diagnostics = DiagnosticTracker()
        
        diagnostics.track_url_issue("http://example.com", "Timeout", source="source1")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            saved_files = diagnostics.save_report(output_dir=output_dir)
            
            assert "latest_full" in saved_files
            assert saved_files["latest_full"].exists()
            assert "latest_summary" in saved_files
            assert saved_files["latest_summary"].exists()

