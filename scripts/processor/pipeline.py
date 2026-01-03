"""
Main processing pipeline orchestrator for transforming raw data into structured job listings.

This module coordinates all processing steps: parsing, normalization, enrichment,
deduplication, validation, and output generation.
"""

import json
import csv
import logging
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .diagnostics import DiagnosticTracker
from .parser_manager import ParserManager
from .normalizer import DataNormalizer
from .enricher import DataEnricher
from .deduplicator import Deduplicator
from .validator import DataValidator

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """
    Main pipeline orchestrator for processing job listings.
    """
    
    def __init__(
        self,
        raw_data_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        diagnostics: Optional[DiagnosticTracker] = None,
        archive_dir: Optional[Path] = None
    ):
        """
        Initialize the processing pipeline.
        
        Args:
            raw_data_dir: Directory containing raw HTML/XML files (default: data/raw/)
            output_dir: Directory for output files (default: data/processed/)
            diagnostics: Optional DiagnosticTracker instance (will create one if not provided)
            archive_dir: Directory for archive snapshots (default: data/processed/archive/)
        """
        self.raw_data_dir = raw_data_dir or Path("data/raw")
        self.output_dir = output_dir or Path("data/processed")
        self.archive_dir = archive_dir or (self.output_dir / "archive")
        self.diagnostics_dir = self.output_dir / "diagnostics"
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.diagnostics_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize diagnostics tracker
        self.diagnostics = diagnostics or DiagnosticTracker()
        
        # Initialize pipeline components
        self.parser_manager = ParserManager(
            raw_data_dir=self.raw_data_dir,
            diagnostics=self.diagnostics
        )
        self.normalizer = DataNormalizer(diagnostics=self.diagnostics)
        self.enricher = DataEnricher(diagnostics=self.diagnostics)
        self.deduplicator = Deduplicator(diagnostics=self.diagnostics)
        self.validator = DataValidator(diagnostics=self.diagnostics)
        
        logger.info("Processing pipeline initialized")
    
    def process(self, save_archive: bool = True) -> Dict[str, Any]:
        """
        Run the complete processing pipeline.
        
        Pipeline stages:
        1. Parse raw files
        2. Normalize data
        3. Enrich data (IDs, classifications, metadata)
        4. Deduplicate listings
        5. Validate data quality
        6. Generate diagnostics
        7. Output to JSON and CSV
        8. Save archive snapshot (optional)
        
        Args:
            save_archive: If True, save a snapshot to archive directory
        
        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("=" * 70)
        logger.info("Starting complete processing pipeline")
        logger.info("=" * 70)
        start_time = datetime.now()
        
        try:
            # Stage 1: Parse raw files
            logger.info("Stage 1: Parsing raw files...")
            raw_listings = self._run_stage(
                "parsing",
                lambda: self.parser_manager.parse_all_files(),
                "Error parsing raw files"
            )
            logger.info(f"✓ Parsed {len(raw_listings)} job listings")
            
            # Stage 2: Normalize data
            logger.info("Stage 2: Normalizing data...")
            normalized_listings = self._run_stage(
                "normalization",
                lambda: self._normalize_listings(raw_listings),
                "Error normalizing listings"
            )
            logger.info(f"✓ Normalized {len(normalized_listings)} job listings")
            
            # Stage 3: Enrich data
            logger.info("Stage 3: Enriching data...")
            enriched_listings = self._run_stage(
                "enrichment",
                lambda: self._enrich_listings(normalized_listings),
                "Error enriching listings"
            )
            logger.info(f"✓ Enriched {len(enriched_listings)} job listings")
            
            # Stage 4: Deduplicate listings
            logger.info("Stage 4: Deduplicating listings...")
            previous_listings = self._load_previous_listings()
            deduplicated_listings, dedup_stats = self._run_stage(
                "deduplication",
                lambda: self.deduplicator.deduplicate(enriched_listings, previous_listings),
                "Error deduplicating listings"
            )
            logger.info(
                f"✓ Deduplicated: {dedup_stats['input_count']} -> {dedup_stats['output_count']} "
                f"({dedup_stats['merges_performed']} merges)"
            )
            
            # Stage 5: Validate data
            logger.info("Stage 5: Validating data quality...")
            validation_results = self._run_stage(
                "validation",
                lambda: self.validator.validate_batch(deduplicated_listings, strict=False),
                "Error validating listings"
            )
            logger.info(
                f"✓ Validation: {validation_results['valid']}/{validation_results['total']} valid "
                f"({validation_results['total_critical_errors']} critical errors, "
                f"{validation_results['total_warnings']} warnings)"
            )
            
            # Stage 6: Generate diagnostics
            logger.info("Stage 6: Generating diagnostic reports...")
            diagnostic_files = self._run_stage(
                "diagnostics",
                lambda: self.diagnostics.save_report(
                    output_dir=self.diagnostics_dir,
                    include_category_files=True,
                    include_text_summary=True
                ),
                "Error generating diagnostic reports"
            )
            logger.info(f"✓ Diagnostic reports saved to {self.diagnostics_dir}")
            
            # Stage 7: Output to JSON and CSV
            logger.info("Stage 7: Writing output files...")
            output_files = self._run_stage(
                "output",
                lambda: self._write_outputs(deduplicated_listings),
                "Error writing output files"
            )
            logger.info(f"✓ Output files written: {', '.join(str(f) for f in output_files.values())}")
            
            # Stage 8: Save archive (optional)
            if save_archive:
                logger.info("Stage 8: Saving archive snapshot...")
                archive_file = self._run_stage(
                    "archive",
                    lambda: self._save_archive(deduplicated_listings),
                    "Error saving archive"
                )
                logger.info(f"✓ Archive saved: {archive_file}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            processed_date = datetime.now().strftime("%Y-%m-%d")
            
            # Generate comprehensive summary
            summary = {
                "processing_date": processed_date,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "statistics": {
                    "raw_listings": len(raw_listings),
                    "normalized_listings": len(normalized_listings),
                    "enriched_listings": len(enriched_listings),
                    "deduplicated_listings": len(deduplicated_listings),
                    "valid_listings": validation_results["valid"],
                    "invalid_listings": validation_results["invalid"],
                    "duplicates_removed": dedup_stats["duplicates_found"],
                    "merges_performed": dedup_stats["merges_performed"],
                    "critical_errors": validation_results["total_critical_errors"],
                    "warnings": validation_results["total_warnings"]
                },
                "output_files": {k: str(v) for k, v in output_files.items()},
                "diagnostics_summary": self.diagnostics.get_summary(),
                "validation_summary": {
                    "total": validation_results["total"],
                    "valid": validation_results["valid"],
                    "invalid": validation_results["invalid"],
                    "critical_errors": validation_results["total_critical_errors"],
                    "warnings": validation_results["total_warnings"]
                }
            }
            
            logger.info("=" * 70)
            logger.info(f"Processing complete in {duration:.2f} seconds")
            logger.info(f"Final output: {len(deduplicated_listings)} job listings")
            logger.info("=" * 70)
            
            return summary
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            # Still try to save diagnostics
            try:
                self.diagnostics.save_report(output_dir=self.diagnostics_dir)
            except Exception as diag_error:
                logger.error(f"Failed to save diagnostics: {diag_error}")
            raise
    
    def _run_stage(
        self,
        stage_name: str,
        stage_func,
        error_message: str
    ) -> Any:
        """
        Run a pipeline stage with error handling and logging.
        
        Args:
            stage_name: Name of the stage (for logging)
            stage_func: Function to execute for this stage
            error_message: Error message prefix if stage fails
        
        Returns:
            Result from stage_func
        """
        try:
            return stage_func()
        except Exception as e:
            logger.error(f"{error_message}: {e}", exc_info=True)
            raise
    
    def _normalize_listings(
        self,
        raw_listings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Normalize a list of job listings."""
        normalized_listings = []
        for listing in raw_listings:
            try:
                # Extract source_url from listing for URL resolution
                source_url = listing.get("source_url")
                normalized = self.normalizer.normalize_job_listing(listing, source_url=source_url)
                normalized_listings.append(normalized)
            except Exception as e:
                logger.warning(f"Error normalizing listing: {e}")
                if self.diagnostics:
                    self.diagnostics.track_normalization_issue(
                        source=listing.get("source", "unknown"),
                        field="listing",
                        original_value=str(listing)[:200],  # Truncate for storage
                        error=str(e)
                    )
        return normalized_listings
    
    def _enrich_listings(
        self,
        normalized_listings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enrich a list of normalized job listings."""
        enriched_listings = []
        for listing in normalized_listings:
            try:
                enriched = self.enricher.enrich_job_listing(listing)
                enriched_listings.append(enriched)
            except Exception as e:
                logger.warning(f"Error enriching listing: {e}")
                if self.diagnostics:
                    self.diagnostics.track_enrichment_issue(
                        source=listing.get("source", "unknown"),
                        field="listing",
                        error=str(e),
                        available_data={k: v for k, v in listing.items() if k in ["title", "institution", "location"]}
                    )
                # Still add the listing even if enrichment partially failed
                enriched_listings.append(listing)
        return enriched_listings
    
    def _load_previous_listings(self) -> Optional[List[Dict[str, Any]]]:
        """
        Load previous processed listings from archive for deduplication.
        
        Returns:
            List of previous listings or None if no archive exists
        """
        # Try to load the most recent archive file
        archive_files = sorted(self.archive_dir.glob("jobs_*.json"), reverse=True)
        if not archive_files:
            # Fall back to current jobs.json if it exists
            current_file = self.output_dir / "jobs.json"
            if current_file.exists():
                try:
                    with open(current_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "listings" in data:
                            return data["listings"]
                        elif isinstance(data, list):
                            return data
                except Exception as e:
                    logger.warning(f"Could not load previous listings: {e}")
            return None
        
        # Load most recent archive
        try:
            with open(archive_files[0], "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "listings" in data:
                    return data["listings"]
                elif isinstance(data, list):
                    return data
        except Exception as e:
            logger.warning(f"Could not load archive file {archive_files[0]}: {e}")
            return None
    
    def _write_outputs(
        self,
        listings: List[Dict[str, Any]]
    ) -> Dict[str, Path]:
        """
        Write job listings to JSON and CSV files.
        
        Args:
            listings: List of job listing dictionaries
        
        Returns:
            Dictionary mapping output type to file path
        """
        output_files = {}
        
        # Write JSON output
        json_file = self.output_dir / "jobs.json"
        self._write_json_output(listings, json_file)
        output_files["json"] = json_file
        
        # Write CSV output
        csv_file = self.output_dir / "jobs.csv"
        self._write_csv_output(listings, csv_file)
        output_files["csv"] = csv_file
        
        return output_files
    
    def _write_json_output(
        self,
        listings: List[Dict[str, Any]],
        output_file: Path
    ):
        """
        Write job listings to JSON file.
        
        Args:
            listings: List of job listing dictionaries
            output_file: Path to output JSON file
        """
        output_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_listings": len(listings),
                "version": "1.0"
            },
            "listings": listings
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Wrote {len(listings)} listings to {output_file}")
    
    def _write_csv_output(
        self,
        listings: List[Dict[str, Any]],
        output_file: Path
    ):
        """
        Write job listings to CSV file.
        
        Args:
            listings: List of job listing dictionaries
            output_file: Path to output CSV file
        """
        if not listings:
            # Create empty CSV with headers
            with open(output_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "title", "institution", "location", "deadline"])
            return
        
        # Extract all possible field names from listings
        all_fields = set()
        for listing in listings:
            all_fields.update(listing.keys())
        
        # Define field order (important fields first, then others)
        priority_fields = [
            "id", "title", "institution", "location", "deadline",
            "job_type", "department", "description", "requirements",
            "application_link", "source", "source_url", "contact_email",
            "contact_person", "region", "specializations", "materials_required",
            "is_active", "is_new", "processed_date", "scraped_date"
        ]
        
        # Build field list: priority fields first, then remaining fields
        field_list = []
        for field in priority_fields:
            if field in all_fields:
                field_list.append(field)
                all_fields.remove(field)
        
        # Add remaining fields in sorted order
        field_list.extend(sorted(all_fields))
        
        # Write CSV
        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=field_list, extrasaction="ignore")
            writer.writeheader()
            
            for listing in listings:
                # Flatten nested structures (like location dict) for CSV
                row = {}
                for field in field_list:
                    value = listing.get(field)
                    if isinstance(value, dict):
                        # Convert dict to string representation
                        row[field] = json.dumps(value, ensure_ascii=False)
                    elif isinstance(value, list):
                        # Convert list to comma-separated string
                        row[field] = ", ".join(str(v) for v in value)
                    else:
                        row[field] = value
                writer.writerow(row)
        
        logger.debug(f"Wrote {len(listings)} listings to {output_file}")
    
    def _save_archive(
        self,
        listings: List[Dict[str, Any]],
        keep_latest: int = 3
    ) -> Path:
        """
        Save a snapshot of processed listings to archive directory.
        
        Automatically removes older archives, keeping only the latest N versions.
        
        Args:
            listings: List of job listing dictionaries
            keep_latest: Number of latest archive files to keep (default: 3)
        
        Returns:
            Path to the archive file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"jobs_{timestamp}.json"
        
        output_data = {
            "metadata": {
                "archived_at": datetime.now().isoformat(),
                "total_listings": len(listings),
                "version": "1.0"
            },
            "listings": listings
        }
        
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Archived {len(listings)} listings to {archive_file}")
        
        # Clean up old archives, keeping only the latest N
        self._cleanup_old_archives(keep_latest)
        
        return archive_file
    
    def _cleanup_old_archives(self, keep_latest: int = 3):
        """
        Remove old archive files, keeping only the latest N versions.
        
        Args:
            keep_latest: Number of latest archive files to keep
        """
        try:
            # Find all archive files matching the pattern
            archive_files = sorted(
                self.archive_dir.glob("jobs_*.json"),
                key=lambda p: p.stat().st_mtime,  # Sort by modification time
                reverse=True  # Newest first
            )
            
            if len(archive_files) <= keep_latest:
                # No cleanup needed
                return
            
            # Keep the latest N files, delete the rest
            files_to_delete = archive_files[keep_latest:]
            deleted_count = 0
            
            for old_file in files_to_delete:
                try:
                    old_file.unlink()
                    deleted_count += 1
                    logger.debug(f"Deleted old archive: {old_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete old archive {old_file.name}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old archive file(s), kept {keep_latest} latest")
        
        except Exception as e:
            logger.warning(f"Error during archive cleanup: {e}")
            # Don't fail the pipeline if cleanup fails


def main():
    """Main entry point for running the processing pipeline."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run pipeline
    pipeline = ProcessingPipeline()
    try:
        summary = pipeline.process(save_archive=True)
        
        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"\nStatistics:")
        stats = summary['statistics']
        print(f"  Raw listings: {stats['raw_listings']}")
        print(f"  After normalization: {stats['normalized_listings']}")
        print(f"  After enrichment: {stats['enriched_listings']}")
        print(f"  After deduplication: {stats['deduplicated_listings']}")
        print(f"  Valid listings: {stats['valid_listings']}/{stats['deduplicated_listings']}")
        print(f"  Duplicates removed: {stats['duplicates_removed']}")
        print(f"  Merges performed: {stats['merges_performed']}")
        print(f"  Critical errors: {stats['critical_errors']}")
        print(f"  Warnings: {stats['warnings']}")
        print(f"\nOutput files:")
        for output_type, file_path in summary['output_files'].items():
            print(f"  {output_type.upper()}: {file_path}")
        print(f"\nDiagnostics: {pipeline.diagnostics_dir}")
        print("=" * 70)
        
        return 0
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\nERROR: Pipeline failed: {e}")
        print("Check logs for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

