"""URL Replacement Strategy - Find and validate replacement URLs for problematic sources.

This module implements the REPLACE phase of the ACCESS -> VALIDATE -> REPLACE strategy.

Components:
  - url_discovery.py: Discover alternative URLs using common paths and subdomains
  - replacement_engine.py: Full workflow orchestration for URL replacement
  - batch_processor.py: Batch validate URLs and update configuration
  - find_replacements.py: Main orchestration script for finding replacements
  - run_pilot_replacement.py: Execute pilot replacement workflow
"""

__all__ = [
    'url_discovery',
    'replacement_engine',
    'batch_processor',
    'find_replacements',
    'run_pilot_replacement',
]
