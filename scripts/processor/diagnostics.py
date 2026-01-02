"""
Diagnostic tracking system for the data processing pipeline.

This module tracks issues throughout the pipeline stages to help identify
root causes of data extraction and processing failures.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class DiagnosticTracker:
    """
    Tracks diagnostic information throughout the processing pipeline.
    
    Stores issues by category (URL, scraping, parsing, extraction, normalization, enrichment)
    and provides methods to retrieve and analyze diagnostic data.
    """
    
    def __init__(self):
        """Initialize an empty diagnostic tracker."""
        self._data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._start_time = datetime.now()
        self._statistics: Dict[str, int] = defaultdict(int)
    
    def track_url_issue(self, url: str, error: str, source: Optional[str] = None):
        """
        Track a URL accessibility or validation issue.
        
        Args:
            url: The problematic URL
            error: Error message or description
            source: Optional source identifier
        """
        self._data["url_issues"].append({
            "url": url,
            "error": error,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["url_issues"] += 1
    
    def track_scraping_issue(self, source: str, url: str, error: str, error_type: Optional[str] = None):
        """
        Track a scraping failure.
        
        Args:
            source: Source identifier (e.g., "aea", "university_website")
            url: URL that failed to scrape
            error: Error message or description
            error_type: Optional error type (e.g., "HTTP_ERROR", "TIMEOUT", "EMPTY_RESPONSE")
        """
        self._data["scraping_issues"].append({
            "source": source,
            "url": url,
            "error": error,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["scraping_issues"] += 1
    
    def track_parsing_issue(self, source: str, file_path: Optional[str] = None, 
                           error: str = "", error_type: Optional[str] = None):
        """
        Track a parsing failure (HTML/XML parsing issues).
        
        Args:
            source: Source identifier
            file_path: Optional path to the file that failed to parse
            error: Error message or description
            error_type: Optional error type (e.g., "PARSE_ERROR", "MISSING_ELEMENTS")
        """
        self._data["parsing_issues"].append({
            "source": source,
            "file_path": file_path,
            "error": error,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["parsing_issues"] += 1
    
    def track_extraction_issue(self, source: str, field: Optional[str] = None,
                              error: str = "", extracted_data: Optional[Dict] = None):
        """
        Track an extraction failure (data extraction from parsed HTML).
        
        Args:
            source: Source identifier
            field: Optional field name that failed to extract
            error: Error message or description
            extracted_data: Optional partial extracted data for debugging
        """
        self._data["extraction_issues"].append({
            "source": source,
            "field": field,
            "error": error,
            "extracted_data": extracted_data,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["extraction_issues"] += 1
    
    def track_normalization_issue(self, source: str, field: str, original_value: Any,
                                  error: str = "", normalized_value: Optional[Any] = None):
        """
        Track a normalization failure (format conversion, standardization issues).
        
        Args:
            source: Source identifier
            field: Field name that failed normalization
            original_value: Original value that couldn't be normalized
            error: Error message or description
            normalized_value: Optional normalized value (if partial success)
        """
        self._data["normalization_issues"].append({
            "source": source,
            "field": field,
            "original_value": str(original_value) if original_value is not None else None,
            "normalized_value": str(normalized_value) if normalized_value is not None else None,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["normalization_issues"] += 1
    
    def track_enrichment_issue(self, source: str, field: str, error: str = "",
                              available_data: Optional[Dict] = None):
        """
        Track an enrichment failure (computed field generation issues).
        
        Args:
            source: Source identifier
            field: Field name that failed enrichment (e.g., "region", "job_type")
            error: Error message or description
            available_data: Optional available data that was used for enrichment attempt
        """
        self._data["enrichment_issues"].append({
            "source": source,
            "field": field,
            "error": error,
            "available_data": available_data,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["enrichment_issues"] += 1
    
    def track_validation_issue(self, source: str, field: Optional[str] = None,
                              error: str = "", validation_type: Optional[str] = None):
        """
        Track a validation failure (schema validation, data quality issues).
        
        Args:
            source: Source identifier
            field: Optional field name that failed validation
            error: Error message or description
            validation_type: Optional validation type (e.g., "SCHEMA", "DATE_FORMAT", "URL_FORMAT")
        """
        self._data["validation_issues"].append({
            "source": source,
            "field": field,
            "error": error,
            "validation_type": validation_type,
            "timestamp": datetime.now().isoformat()
        })
        self._statistics["validation_issues"] += 1
    
    def get_issues_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all issues for a specific category.
        
        Args:
            category: Category name (e.g., "url_issues", "parsing_issues", "normalization_issues")
        
        Returns:
            List of issue dictionaries for the category
        """
        return self._data.get(category, []).copy()
    
    def get_all_issues(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all tracked issues organized by category.
        
        Returns:
            Dictionary mapping category names to lists of issues
        """
        return dict(self._data)
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get summary statistics of tracked issues.
        
        Returns:
            Dictionary mapping category names to issue counts
        """
        return dict(self._statistics)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all diagnostic data.
        
        Returns:
            Dictionary containing summary statistics and issue counts
        """
        end_time = datetime.now()
        duration = (end_time - self._start_time).total_seconds()
        
        return {
            "start_time": self._start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "statistics": self.get_statistics(),
            "total_issues": sum(self._statistics.values()),
            "categories": list(self._data.keys())
        }
    
    def clear(self):
        """Clear all tracked diagnostic data."""
        self._data.clear()
        self._statistics.clear()
        self._start_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert diagnostic data to a dictionary for serialization (JSON).
        
        Returns:
            Dictionary representation of all diagnostic data
        """
        return {
            "summary": self.get_summary(),
            "issues": self.get_all_issues()
        }
    
    def analyze_root_causes(self) -> Dict[str, Any]:
        """
        Analyze diagnostic data to identify root causes.
        
        Groups issues by source, error type, and patterns to identify
        common problems.
        
        Returns:
            Dictionary containing root cause analysis:
            {
                "by_source": {source: {category: count, ...}, ...},
                "by_error_type": {error_type: count, ...},
                "most_common_errors": [...],
                "source_failure_rates": {source: rate, ...}
            }
        """
        analysis = {
            "by_source": defaultdict(lambda: defaultdict(int)),
            "by_error_type": defaultdict(int),
            "most_common_errors": [],
            "source_failure_rates": {}
        }
        
        # Analyze by source
        source_counts = defaultdict(int)
        for category, issues in self._data.items():
            for issue in issues:
                source = issue.get("source", "unknown")
                analysis["by_source"][source][category] += 1
                source_counts[source] += 1
                
                # Analyze error types
                error_type = issue.get("error_type") or issue.get("validation_type")
                if error_type:
                    analysis["by_error_type"][error_type] += 1
        
        # Get most common errors (by error message pattern)
        error_patterns = defaultdict(int)
        for category, issues in self._data.items():
            for issue in issues:
                error = issue.get("error", "")
                if error:
                    # Extract key error pattern (first part before colon or first 50 chars)
                    pattern = error.split(":")[0] if ":" in error else error[:50]
                    error_patterns[pattern] += 1
        
        # Sort most common errors
        analysis["most_common_errors"] = sorted(
            error_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10
        
        # Calculate source failure rates (if we have total counts per source)
        # This is simplified - in real scenario, we'd need total attempts per source
        total_issues = sum(self._statistics.values())
        if total_issues > 0:
            for source in source_counts:
                analysis["source_failure_rates"][source] = (
                    source_counts[source] / total_issues
                ) * 100
        
        return analysis
    
    def generate_report(self, include_root_causes: bool = True) -> Dict[str, Any]:
        """
        Generate a comprehensive diagnostic report.
        
        Args:
            include_root_causes: If True, include root cause analysis
        
        Returns:
            Dictionary containing full diagnostic report
        """
        report = {
            "summary": self.get_summary(),
            "statistics_by_category": self._generate_category_statistics(),
            "issues": self.get_all_issues()
        }
        
        if include_root_causes:
            report["root_cause_analysis"] = self.analyze_root_causes()
        
        return report
    
    def _generate_category_statistics(self) -> Dict[str, Any]:
        """
        Generate detailed statistics for each category.
        
        Returns:
            Dictionary with statistics per category
        """
        category_stats = {}
        
        for category, issues in self._data.items():
            if not issues:
                continue
            
            stats = {
                "total": len(issues),
                "sources_affected": len(set(issue.get("source", "unknown") for issue in issues)),
                "error_types": {}
            }
            
            # Count error types in this category
            error_type_counts = defaultdict(int)
            for issue in issues:
                error_type = (
                    issue.get("error_type") or 
                    issue.get("validation_type") or 
                    "unknown"
                )
                error_type_counts[error_type] += 1
            
            stats["error_types"] = dict(error_type_counts)
            
            # Get unique sources
            stats["unique_sources"] = sorted(list(set(
                issue.get("source", "unknown") for issue in issues
            )))
            
            category_stats[category] = stats
        
        return category_stats
    
    def generate_category_report(self, category: str) -> Dict[str, Any]:
        """
        Generate a report for a specific category.
        
        Args:
            category: Category name (e.g., "url_issues", "parsing_issues")
        
        Returns:
            Dictionary containing category-specific report
        """
        issues = self.get_issues_by_category(category)
        
        if not issues:
            return {
                "category": category,
                "total": 0,
                "issues": []
            }
        
        # Analyze issues in this category
        sources = [issue.get("source", "unknown") for issue in issues]
        unique_sources = sorted(list(set(sources)))
        
        error_types = defaultdict(int)
        for issue in issues:
            error_type = (
                issue.get("error_type") or 
                issue.get("validation_type") or 
                "unknown"
            )
            error_types[error_type] += 1
        
        return {
            "category": category,
            "total": len(issues),
            "unique_sources": unique_sources,
            "error_type_counts": dict(error_types),
            "issues": issues
        }
    
    def generate_human_readable_summary(self) -> str:
        """
        Generate a human-readable text summary of diagnostic data.
        
        Returns:
            String containing formatted summary report
        """
        summary = self.get_summary()
        stats = summary["statistics"]
        total_issues = summary["total_issues"]
        
        lines = [
            "=" * 70,
            "DIAGNOSTIC REPORT SUMMARY",
            "=" * 70,
            f"Start Time: {summary['start_time']}",
            f"End Time: {summary['end_time']}",
            f"Duration: {summary['duration_seconds']:.2f} seconds",
            "",
            f"Total Issues: {total_issues}",
            ""
        ]
        
        if total_issues > 0:
            lines.append("Issues by Category:")
            lines.append("-" * 70)
            for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_issues) * 100
                lines.append(f"  {category:30s}: {count:5d} ({percentage:5.1f}%)")
            lines.append("")
        
        # Root cause analysis summary
        root_causes = self.analyze_root_causes()
        if root_causes.get("most_common_errors"):
            lines.append("Most Common Errors:")
            lines.append("-" * 70)
            for error, count in root_causes["most_common_errors"][:5]:
                lines.append(f"  {error[:60]:60s}: {count}")
            lines.append("")
        
        if root_causes.get("by_source"):
            lines.append("Issues by Source (Top 10):")
            lines.append("-" * 70)
            source_totals = {
                source: sum(cats.values())
                for source, cats in root_causes["by_source"].items()
            }
            for source, total in sorted(source_totals.items(), key=lambda x: x[1], reverse=True)[:10]:
                lines.append(f"  {source:40s}: {total}")
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def save_report(
        self,
        output_dir: Optional[Path] = None,
        include_category_files: bool = True,
        include_text_summary: bool = True
    ) -> Dict[str, Path]:
        """
        Save diagnostic reports to files in the diagnostics directory.
        
        Args:
            output_dir: Directory to save reports (default: data/processed/diagnostics/)
            include_category_files: If True, save category-specific JSON files
            include_text_summary: If True, save human-readable text summary
        
        Returns:
            Dictionary mapping report type to file path:
            {
                "full_report": Path,
                "summary_report": Path,
                "category_reports": {category: Path, ...},
                "text_summary": Path
            }
        """
        if output_dir is None:
            output_dir = Path("data/processed/diagnostics")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full report
        full_report = self.generate_report(include_root_causes=True)
        full_report_path = output_dir / f"diagnostics_full_{timestamp}.json"
        with open(full_report_path, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        saved_files["full_report"] = full_report_path
        
        # Save summary report (just summary, no detailed issues)
        summary_report = {
            "summary": self.get_summary(),
            "statistics_by_category": self._generate_category_statistics(),
            "root_cause_analysis": self.analyze_root_causes()
        }
        summary_report_path = output_dir / f"diagnostics_summary_{timestamp}.json"
        with open(summary_report_path, "w", encoding="utf-8") as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False)
        saved_files["summary_report"] = summary_report_path
        
        # Save category-specific reports
        if include_category_files:
            category_reports = {}
            for category in self._data.keys():
                category_report = self.generate_category_report(category)
                category_file = output_dir / f"diagnostics_{category}_{timestamp}.json"
                with open(category_file, "w", encoding="utf-8") as f:
                    json.dump(category_report, f, indent=2, ensure_ascii=False)
                category_reports[category] = category_file
            saved_files["category_reports"] = category_reports
        
        # Save human-readable text summary
        if include_text_summary:
            text_summary = self.generate_human_readable_summary()
            text_summary_path = output_dir / f"diagnostics_summary_{timestamp}.txt"
            with open(text_summary_path, "w", encoding="utf-8") as f:
                f.write(text_summary)
            saved_files["text_summary"] = text_summary_path
        
        # Save latest symlinks (or copies) for easy access
        latest_full = output_dir / "diagnostics_full_latest.json"
        latest_summary = output_dir / "diagnostics_summary_latest.json"
        latest_text = output_dir / "diagnostics_summary_latest.txt"
        
        # Copy files (since symlinks may not work on Windows)
        import shutil
        shutil.copy2(full_report_path, latest_full)
        shutil.copy2(summary_report_path, latest_summary)
        if include_text_summary:
            shutil.copy2(text_summary_path, latest_text)
        
        saved_files["latest_full"] = latest_full
        saved_files["latest_summary"] = latest_summary
        if include_text_summary:
            saved_files["latest_text"] = latest_text
        
        return saved_files

