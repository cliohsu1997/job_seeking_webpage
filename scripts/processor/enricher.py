"""
Data enrichment module for adding computed fields and classifications.

This module enriches job listing data with:
- Unique IDs
- Region detection
- Job type classification
- Specialization extraction
- Materials parsing
- Metadata addition
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Import processor utilities
from .utils.id_generator import generate_job_id
from .utils.location_parser import detect_region_from_country, normalize_location
from .diagnostics import DiagnosticTracker

logger = logging.getLogger(__name__)

# Path to processing rules config
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_FILE = PROJECT_ROOT / "data/config/processing_rules.json"

# Valid regions list (cached for performance)
VALID_REGIONS = {
    "united_states", "mainland_china", "united_kingdom",
    "canada", "australia", "other_countries"
}

# Compiled regex patterns (cached for performance)
LETTERS_NUMBER_PATTERNS = [
    re.compile(r'(\d+)\s*(?:letters?|references?)\s*(?:of\s*)?(?:recommendation)?', re.IGNORECASE),
    re.compile(r'(?:letters?|references?)\s*(?:of\s*)?(?:recommendation\s*)?[:\-]?\s*(\d+)', re.IGNORECASE),
    re.compile(r'(\d+)\s*(?:letters?|references?)\s*(?:will\s*be|are|required)', re.IGNORECASE),
]
RESEARCH_PAPER_PATTERNS = [
    re.compile(r'job\s*market\s*paper(?:\s*\+\s*(\d+))?\s*(?:additional\s*)?(?:papers?|publications?)?', re.IGNORECASE),
    re.compile(r'(\d+)\s*(?:papers?|publications?|writing\s*samples?)', re.IGNORECASE),
    re.compile(r'writing\s*sample(?:s)?(?:\s*\+\s*(\d+))?\s*(?:additional\s*)?(?:papers?)?', re.IGNORECASE),
]


class DataEnricher:
    """
    Enriches job listing data with computed fields and classifications.
    """
    
    def __init__(self, diagnostics: Optional[DiagnosticTracker] = None):
        """
        Initialize the enricher.
        
        Args:
            diagnostics: Optional DiagnosticTracker instance for tracking enrichment issues
        """
        self.diagnostics = diagnostics
        self._load_processing_rules()
    
    def _load_processing_rules(self) -> None:
        """Load processing rules from configuration file."""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.processing_rules = json.load(f)
            # Cache frequently accessed rule sections
            self._job_type_keywords = self.processing_rules.get("job_type_keywords", {})
            self._specialization_keywords = self.processing_rules.get("specialization_keywords", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load processing rules from {CONFIG_FILE}: {e}")
            self.processing_rules = {}
            self._job_type_keywords = {}
            self._specialization_keywords = {}
    
    def enrich_job_listing(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a job listing with computed fields and classifications.
        
        Args:
            job_data: Dictionary containing job listing data (should be normalized first)
        
        Returns:
            Dictionary with enriched fields
        """
        enriched = job_data.copy()
        
        # Ensure optional fields have default values (from schema.py)
        from .schema import OPTIONAL_FIELDS_DEFAULTS
        for field, default_value in OPTIONAL_FIELDS_DEFAULTS.items():
            if field not in enriched:
                enriched[field] = default_value
        
        # Generate unique ID if not present
        if "id" not in enriched or not enriched["id"]:
            enriched["id"] = self._generate_id(enriched)
        
        # Detect/enhance region from location
        if "location" in enriched:
            enriched["location"] = self._detect_region(enriched["location"])
        
        # Classify job type if not already normalized
        if "job_type" not in enriched or not enriched["job_type"] or enriched["job_type"] == "other":
            enriched["job_type"] = self._classify_job_type(
                enriched.get("title", ""),
                enriched.get("description", "")
            )
        
        # Extract specializations
        enriched["specializations"] = self._extract_specializations(
            enriched.get("description", ""),
            enriched.get("requirements", ""),
            enriched.get("specializations", [])
        )
        
        # Enhance materials_required parsing
        if "materials_required" in enriched:
            enriched["materials_required"] = self._enhance_materials_parsing(
                enriched.get("description", ""),
                enriched.get("requirements", ""),
                enriched.get("materials_required", {})
            )
        
        # Add metadata
        enriched = self._add_metadata(enriched)
        
        return enriched
    
    def _generate_id(self, job_data: Dict[str, Any]) -> str:
        """
        Generate unique ID for job listing.
        
        Args:
            job_data: Job listing data
        
        Returns:
            Unique ID string
        """
        try:
            institution = job_data.get("institution", "")
            title = job_data.get("title", "")
            deadline = job_data.get("deadline", "")
            
            job_id = generate_job_id(institution, title, deadline)
            return job_id
        except Exception as e:
            if self.diagnostics:
                self.diagnostics.track_enrichment_issue(
                    source="enricher",
                    field="id",
                    error=f"ID generation error: {str(e)}",
                    available_data={"institution": job_data.get("institution", ""), "title": job_data.get("title", "")}
                )
            logger.warning(f"Error generating ID: {e}")
            # Fallback: use hash of string representation
            import hashlib
            job_str = f"{institution}{title}{deadline}"
            return hashlib.sha256(job_str.encode()).hexdigest()[:32]
    
    def _detect_region(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect and enhance region information in location.
        
        Args:
            location: Location dictionary
        
        Returns:
            Location dictionary with region information
        """
        try:
            # If region already exists and is valid, return as-is
            if location.get("region") in VALID_REGIONS:
                return location
            
            # Try to detect region from country
            country = location.get("country")
            if country:
                region = detect_region_from_country(country)
                location["region"] = region
            else:
                # If no country, default to other_countries
                location["region"] = "other_countries"
                if not country:
                    location["country"] = "Unknown"
            
            return location
        except Exception as e:
            if self.diagnostics:
                self.diagnostics.track_enrichment_issue(
                    source="enricher",
                    field="location.region",
                    error=f"Region detection error: {str(e)}",
                    available_data=location
                )
            logger.warning(f"Error detecting region: {e}")
            location["region"] = "other_countries"
            return location
    
    def _classify_job_type(self, title: str, description: str) -> str:
        """
        Classify job type from title and description keywords.
        
        Args:
            title: Job title
            description: Job description
        
        Returns:
            Job type classification (tenure-track, visiting, postdoc, lecturer, other)
        """
        combined_text = f"{title} {description}".lower().strip()
        
        if not combined_text:
            return "other"
        
        # Score each job type based on keyword matches (use cached keywords)
        scores = {}
        for job_type, keywords in self._job_type_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences (case-insensitive)
                score += combined_text.count(keyword.lower())
            if score > 0:
                scores[job_type] = score
        
        # Return job type with highest score, or "other" if no matches
        if scores:
            return max(scores, key=scores.get)
        else:
            return "other"
    
    def _extract_specializations(self, description: str, requirements: str, 
                                existing_specializations: List[str]) -> List[str]:
        """
        Extract specializations from description and requirements using keyword matching.
        
        Args:
            description: Job description text
            requirements: Requirements text
            existing_specializations: Existing specializations list (if any)
        
        Returns:
            List of specialization strings
        """
        specializations = set(existing_specializations) if existing_specializations else set()
        
        # Combine text for searching (only if needed)
        if not description and not requirements:
            return sorted(list(specializations)) if specializations else []
        
        combined_text = f"{description} {requirements}".lower()
        
        # Check for each specialization (use cached keywords)
        for specialization, keywords in self._specialization_keywords.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    # Capitalize specialization name properly
                    specialization_name = specialization.replace("_", " ").title()
                    specializations.add(specialization_name)
                    break
        
        # Convert to sorted list
        return sorted(list(specializations)) if specializations else []
    
    def _enhance_materials_parsing(self, description: str, requirements: str,
                                  existing_materials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance materials_required parsing from description/requirements.
        
        This complements the normalizer's materials parsing with more detailed extraction.
        
        Args:
            description: Job description text
            requirements: Requirements text
            existing_materials: Existing materials_required dict (from normalizer)
        
        Returns:
            Enhanced materials_required dictionary
        """
        materials = existing_materials.copy() if existing_materials else {}
        
        # Combine text for parsing
        combined_text = f"{description} {requirements}".lower()
        
        # Get materials keywords from processing rules
        materials_keywords = self.processing_rules.get("materials_keywords", {})
        
        # Early return if no text to parse
        if not combined_text:
            return materials
        
        # Enhanced parsing for letters of recommendation
        # Check if not already set or if we need to enhance
        if "letters_of_recommendation" not in materials or not materials.get("letters_of_recommendation"):
            # Use pre-compiled patterns
            for pattern in LETTERS_NUMBER_PATTERNS:
                match = pattern.search(combined_text)
                if match:
                    try:
                        materials["letters_of_recommendation"] = int(match.group(1))
                        break
                    except (ValueError, IndexError):
                        pass
        
        # Enhanced parsing for research papers
        if "research_papers" not in materials or not materials.get("research_papers"):
            # Use pre-compiled patterns
            for pattern in RESEARCH_PAPER_PATTERNS:
                match = pattern.search(combined_text)
                if match:
                    # Extract full description
                    materials["research_papers"] = match.group(0)
                    break
        
        # Ensure "other" field is a list
        if "other" not in materials:
            materials["other"] = []
        elif not isinstance(materials["other"], list):
            if materials["other"]:
                materials["other"] = [str(materials["other"])]
            else:
                materials["other"] = []
        
        return materials
    
    def _add_metadata(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add metadata fields (processing timestamp, source tracking).
        
        Args:
            job_data: Job listing data
        
        Returns:
            Job listing with metadata added
        """
        # Add processed_date if not present
        if "processed_date" not in job_data or not job_data["processed_date"]:
            job_data["processed_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Ensure sources is a list
        if "sources" not in job_data:
            # If source exists, use it
            if "source" in job_data:
                job_data["sources"] = [job_data["source"]]
            else:
                job_data["sources"] = []
        elif not isinstance(job_data["sources"], list):
            job_data["sources"] = [job_data["sources"]] if job_data["sources"] else []
        
        # Ensure is_active is set (default to True if not present)
        if "is_active" not in job_data:
            job_data["is_active"] = True
        
        # Ensure is_new is set (default to True if not present)
        if "is_new" not in job_data:
            job_data["is_new"] = True
        
        return job_data

