"""
Phase 2: TRANSFORM - Data Processing Module

This module processes raw scraped HTML/XML data into clean, structured,
and deduplicated job listings ready for output generation.

Main Components:
- pipeline.py: Main processing pipeline orchestrator
- parser_manager.py: Routes raw data to appropriate parsers
- normalizer.py: Data normalization (dates, formats, etc.)
- enricher.py: Data enrichment (IDs, classifications, metadata)
- deduplicator.py: Duplicate detection and merging
- validator.py: Schema validation and quality checks
- schema.py: Data schema definition and validation rules
- diagnostics.py: Diagnostic tracking and root cause analysis
"""

__version__ = "0.1.0"

