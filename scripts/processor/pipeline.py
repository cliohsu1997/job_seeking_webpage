"""
Main processing pipeline orchestrator for transforming raw data into structured job listings.

This module coordinates all processing steps: parsing, normalization, enrichment,
deduplication, validation, and output generation.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .diagnostics import DiagnosticTracker
from .parser_manager import ParserManager
from .normalizer import DataNormalizer
from .utils.id_generator import generate_id_from_dict

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """
    Main pipeline orchestrator for processing job listings.
    """
    
    def __init__(
        self,
        raw_data_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        diagnostics: Optional[DiagnosticTracker] = None
    ):
        """
        Initialize the processing pipeline.
        
        Args:
            raw_data_dir: Directory containing raw HTML/XML files (default: data/raw/)
            output_dir: Directory for output files (default: data/processed/)
            diagnostics: Optional DiagnosticTracker instance (will create one if not provided)
        """
        self.raw_data_dir = raw_data_dir or Path("data/raw")
        self.output_dir = output_dir or Path("data/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize diagnostics tracker
        self.diagnostics = diagnostics or DiagnosticTracker()
        
        # Initialize pipeline components
        self.parser_manager = ParserManager(
            raw_data_dir=self.raw_data_dir,
            diagnostics=self.diagnostics
        )
        self.normalizer = DataNormalizer(diagnostics=self.diagnostics)
        
        logger.info("Processing pipeline initialized")
    
    def process(self) -> Dict[str, Any]:
        """
        Run the complete processing pipeline.
        
        Pipeline stages:
        1. Parse raw files
        2. Normalize data
        3. Generate IDs
        4. Output to JSON
        
        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting processing pipeline")
        start_time = datetime.now()
        
        # Stage 1: Parse raw files
        logger.info("Stage 1: Parsing raw files...")
        raw_listings = self.parser_manager.parse_all_files()
        logger.info(f"Parsed {len(raw_listings)} job listings")
        
        # Stage 2: Normalize data
        logger.info("Stage 2: Normalizing data...")
        normalized_listings = []
        for listing in raw_listings:
            try:
                normalized = self.normalizer.normalize_job_listing(listing)
                normalized_listings.append(normalized)
            except Exception as e:
                logger.error(f"Error normalizing listing: {e}")
                if self.diagnostics:
                    self.diagnostics.track_normalization_issue(
                        source=listing.get("source", "unknown"),
                        field="listing",
                        original_value=str(listing),
                        error=str(e)
                    )
        
        logger.info(f"Normalized {len(normalized_listings)} job listings")
        
        # Stage 3: Generate IDs
        logger.info("Stage 3: Generating IDs...")
        for listing in normalized_listings:
            try:
                job_id = generate_id_from_dict(listing)
                if job_id:
                    listing["id"] = job_id
                else:
                    logger.warning(f"Failed to generate ID for listing: {listing.get('title', 'unknown')}")
                    # Use a fallback ID based on timestamp if generation fails
                    listing["id"] = f"fallback_{datetime.now().timestamp()}"
            except Exception as e:
                logger.error(f"Error generating ID: {e}")
                listing["id"] = f"error_{datetime.now().timestamp()}"
        
        # Stage 4: Add metadata
        processed_date = datetime.now().strftime("%Y-%m-%d")
        for listing in normalized_listings:
            if "processed_date" not in listing:
                listing["processed_date"] = processed_date
            if "is_active" not in listing:
                listing["is_active"] = True
            if "is_new" not in listing:
                listing["is_new"] = True
            if "sources" not in listing:
                source = listing.get("source", "unknown")
                listing["sources"] = [source]
        
        # Stage 5: Output to JSON
        logger.info("Stage 4: Writing output...")
        output_file = self.output_dir / "jobs.json"
        self._write_json_output(normalized_listings, output_file)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = {
            "processing_date": processed_date,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "statistics": {
                "raw_listings": len(raw_listings),
                "normalized_listings": len(normalized_listings),
                "output_file": str(output_file)
            },
            "diagnostics_summary": self.diagnostics.get_summary()
        }
        
        logger.info(f"Processing complete in {duration:.2f} seconds")
        logger.info(f"Processed {len(normalized_listings)} job listings")
        
        return summary
    
    def _write_json_output(self, listings: List[Dict[str, Any]], output_file: Path):
        """
        Write job listings to JSON file.
        
        Args:
            listings: List of job listing dictionaries
            output_file: Path to output JSON file
        """
        try:
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
            
            logger.info(f"Wrote {len(listings)} listings to {output_file}")
            
        except Exception as e:
            logger.error(f"Error writing JSON output to {output_file}: {e}")
            raise


def main():
    """Main entry point for running the processing pipeline."""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run pipeline
    pipeline = ProcessingPipeline()
    try:
        summary = pipeline.process()
        print(f"\nProcessing complete!")
        print(f"Processed {summary['statistics']['normalized_listings']} job listings")
        print(f"Output: {summary['statistics']['output_file']}")
        return 0
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

