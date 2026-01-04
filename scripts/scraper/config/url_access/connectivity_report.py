"""Generate accessibility reports for URLs."""

import json
import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
from .test_accessibility import test_accessibility
from .redirect_handler import follow_redirects


def generate_accessibility_report(
    sources_json_path: str,
    output_dir: str = "data/config/url_verification",
    output_formats: List[str] = None,
) -> Dict[str, any]:
    """
    Test all URLs in scraping sources and generate reports.
    
    Args:
        sources_json_path: Path to scraping_sources.json
        output_dir: Directory to save reports
        output_formats: List of output formats (json, markdown, csv)
    
    Returns:
        Dict with report summary and detailed results
    """
    if output_formats is None:
        output_formats = ["json", "markdown"]
    
    # Load sources
    with open(sources_json_path) as f:
        sources = json.load(f)
    
    # Collect all URLs
    urls = _extract_all_urls(sources)
    
    # Test each URL
    results = {
        "summary": {
            "total_urls": len(urls),
            "accessible": 0,
            "timeout": 0,
            "not_found": 0,
            "forbidden": 0,
            "ssl_error": 0,
            "connection_error": 0,
            "other": 0,
        },
        "by_region": defaultdict(lambda: {"accessible": 0, "failed": 0}),
        "by_category": defaultdict(lambda: {"accessible": 0, "failed": 0}),
        "detailed_results": [],
    }
    
    # Test each URL
    for i, (url, metadata) in enumerate(urls, 1):
        print(f"Testing {i}/{len(urls)}: {url[:60]}...")
        
        test_result = test_accessibility(url)
        redirect_result = follow_redirects(url) if test_result["accessible"] else {}
        
        detail = {
            "url": url,
            "accessible": test_result["accessible"],
            "status_code": test_result["status_code"],
            "error_type": test_result["error_type"],
            "error_message": test_result["error_message"],
            "region": metadata.get("region"),
            "category": metadata.get("category"),
            "has_redirects": redirect_result.get("has_redirects", False),
            "external_system": redirect_result.get("external_system"),
        }
        
        results["detailed_results"].append(detail)
        
        # Update summary
        if test_result["accessible"]:
            results["summary"]["accessible"] += 1
        else:
            error_type = test_result["error_type"] or "other"
            if error_type in results["summary"]:
                results["summary"][error_type] += 1
            else:
                results["summary"]["other"] += 1
        
        # Update by region
        region = metadata.get("region", "unknown")
        if test_result["accessible"]:
            results["by_region"][region]["accessible"] += 1
        else:
            results["by_region"][region]["failed"] += 1
        
        # Update by category
        category = metadata.get("category", "unknown")
        if test_result["accessible"]:
            results["by_category"][category]["accessible"] += 1
        else:
            results["by_category"][category]["failed"] += 1
    
    # Save reports
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    if "json" in output_formats:
        _save_json_report(results, output_dir)
    
    if "markdown" in output_formats:
        _save_markdown_report(results, output_dir)
    
    if "csv" in output_formats:
        _save_csv_report(results, output_dir)
    
    return results


def _extract_all_urls(sources: Dict) -> List[tuple]:
    """Extract all URLs from sources config."""
    urls = []
    
    for section in ["accessible", "non_accessible"]:
        if section not in sources:
            continue
        
        for category, items in sources[section].items():
            if isinstance(items, dict):
                for key, config in items.items():
                    if "url" in config:
                        urls.append((
                            config["url"],
                            {
                                "region": config.get("region"),
                                "category": category,
                            }
                        ))
    
    return urls


def _save_json_report(results: Dict, output_dir: str) -> None:
    """Save results as JSON."""
    output_path = Path(output_dir) / "accessibility_report.json"
    
    # Convert defaultdict to regular dict for JSON serialization
    report = {
        "summary": results["summary"],
        "by_region": dict(results["by_region"]),
        "by_category": dict(results["by_category"]),
        "detailed_results": results["detailed_results"],
    }
    
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"JSON report saved to {output_path}")


def _save_markdown_report(results: Dict, output_dir: str) -> None:
    """Save results as Markdown."""
    output_path = Path(output_dir) / "accessibility_report.md"
    
    lines = [
        "# Accessibility Report\n",
        "## Summary\n",
        f"- Total URLs: {results['summary']['total_urls']}\n",
        f"- Accessible: {results['summary']['accessible']}\n",
        f"- Timeouts: {results['summary']['timeout']}\n",
        f"- Not Found (404): {results['summary']['not_found']}\n",
        f"- Forbidden (403): {results['summary']['forbidden']}\n",
        f"- SSL Errors: {results['summary']['ssl_error']}\n",
        f"- Connection Errors: {results['summary']['connection_error']}\n",
        f"- Other Errors: {results['summary']['other']}\n",
    ]
    
    with open(output_path, "w") as f:
        f.writelines(lines)
    
    print(f"Markdown report saved to {output_path}")


def _save_csv_report(results: Dict, output_dir: str) -> None:
    """Save detailed results as CSV."""
    import csv
    
    output_path = Path(output_dir) / "accessibility_report.csv"
    
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "url",
                "accessible",
                "status_code",
                "error_type",
                "region",
                "category",
            ]
        )
        writer.writeheader()
        writer.writerows(results["detailed_results"])
    
    print(f"CSV report saved to {output_path}")
