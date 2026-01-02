"""
Data deduplication module for identifying and merging duplicate job listings.

Handles fuzzy matching, merge logic, source aggregation, conflict resolution,
and new/active listing detection.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from datetime import date
from collections import defaultdict

from rapidfuzz import fuzz

from .diagnostics import DiagnosticTracker

logger = logging.getLogger(__name__)

# Source priority for conflict resolution (higher = preferred)
SOURCE_PRIORITY = {
    "aea": 3,
    "university_website": 2,
    "institute_website": 1,
    "job_portal": 2
}

# Default similarity thresholds
DEFAULT_TITLE_SIMILARITY = 85
DEFAULT_INSTITUTION_SIMILARITY = 90


class Deduplicator:
    """Deduplicates job listings using fuzzy matching and merges duplicates."""
    
    def __init__(
        self,
        diagnostics: Optional[DiagnosticTracker] = None,
        title_similarity_threshold: int = DEFAULT_TITLE_SIMILARITY,
        institution_similarity_threshold: int = DEFAULT_INSTITUTION_SIMILARITY
    ):
        self.diagnostics = diagnostics
        self.title_similarity_threshold = title_similarity_threshold
        self.institution_similarity_threshold = institution_similarity_threshold
    
    def deduplicate(
        self,
        listings: List[Dict[str, Any]],
        previous_listings: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Deduplicate listings and detect new/active listings."""
        if not listings:
            return [], {"input_count": 0, "output_count": 0, "duplicates_found": 0, "merges_performed": 0}
        
        logger.info(f"Starting deduplication of {len(listings)} listings")
        
        # Group by institution + deadline, then merge duplicates within groups
        grouped = self._group_by_institution_and_deadline(listings)
        deduplicated = []
        merge_count = 0
        
        for group_listings in grouped.values():
            if len(group_listings) == 1:
                deduplicated.append(group_listings[0])
            else:
                merged_group, group_merges = self._merge_duplicates_in_group(group_listings)
                deduplicated.extend(merged_group)
                merge_count += group_merges
        
        # Detect new/active listings
        if previous_listings:
            deduplicated = self._detect_new_and_active_listings(deduplicated, previous_listings)
        
        stats = {
            "input_count": len(listings),
            "output_count": len(deduplicated),
            "duplicates_found": len(listings) - len(deduplicated),
            "merges_performed": merge_count
        }
        
        logger.info(f"Deduplication complete: {stats['input_count']} -> {stats['output_count']} ({merge_count} merges)")
        return deduplicated, stats
    
    def _group_by_institution_and_deadline(
        self,
        listings: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group listings by normalized institution and deadline."""
        groups = defaultdict(list)
        for listing in listings:
            institution = self._normalize_institution_name(listing.get("institution", ""))
            deadline = listing.get("deadline", "")
            key = f"{institution}||{deadline}"
            groups[key].append(listing)
        return dict(groups)
    
    def _normalize_institution_name(self, institution: str) -> str:
        """Normalize institution name for grouping."""
        if not institution:
            return ""
        normalized = institution.lower().strip()
        suffixes = [" university", " college", " school", " institute", " institution", " center", " centre"]
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        return " ".join(normalized.split())
    
    def _merge_duplicates_in_group(
        self,
        group_listings: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Merge duplicate listings within a group using fuzzy title matching."""
        if len(group_listings) == 1:
            return group_listings, 0
        
        # Sort by priority for merge order
        sorted_listings = sorted(
            group_listings,
            key=lambda x: (SOURCE_PRIORITY.get(x.get("source", ""), 0), self._calculate_completeness_score(x)),
            reverse=True
        )
        
        merged = []
        processed = set()
        merge_count = 0
        
        for i, listing in enumerate(sorted_listings):
            if i in processed:
                continue
            
            # Find duplicates
            duplicates = [i]
            title1 = (listing.get("title") or "").strip()
            
            for j in range(i + 1, len(sorted_listings)):
                if j in processed:
                    continue
                title2 = (sorted_listings[j].get("title") or "").strip()
                if fuzz.ratio(title1, title2) >= self.title_similarity_threshold:
                    duplicates.append(j)
            
            # Merge duplicates
            if len(duplicates) > 1:
                merged_listing = self._merge_listings([sorted_listings[idx] for idx in duplicates])
                merged.append(merged_listing)
                processed.update(duplicates)
                merge_count += len(duplicates) - 1
                
                if self.diagnostics:
                    self.diagnostics.track_validation_issue(
                        source=merged_listing.get("source", "unknown"),
                        field="deduplication",
                        error=f"Merged {len(duplicates)} duplicates",
                        validation_type="DUPLICATE_MERGE"
                    )
            else:
                merged.append(listing)
                processed.add(i)
        
        return merged, merge_count
    
    def _merge_listings(self, listings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple duplicate listings into one."""
        if not listings:
            raise ValueError("Cannot merge empty list")
        if len(listings) == 1:
            return listings[0].copy()
        
        # Sort by priority
        sorted_listings = sorted(
            listings,
            key=lambda x: (
                SOURCE_PRIORITY.get(x.get("source", ""), 0),
                self._calculate_completeness_score(x),
                self._parse_date_safely(x.get("last_updated", "")) or date.min
            ),
            reverse=True
        )
        
        merged = sorted_listings[0].copy()
        # Initialize sources from first listing (always include source field if present)
        all_sources = set(merged.get("sources", []))
        if merged.get("source"):
            all_sources.add(merged.get("source"))
        all_source_urls = {merged.get("source_url", "")}
        
        # Merge fields from other listings
        for listing in sorted_listings[1:]:
            listing_sources = set(listing.get("sources", []))
            if listing.get("source"):
                listing_sources.add(listing.get("source"))
            all_sources.update(listing_sources)
            all_source_urls.add(listing.get("source_url", ""))
            
            for key, value in listing.items():
                if key in ["sources", "source_url", "id"]:
                    continue
                
                if key not in merged or not merged[key]:
                    merged[key] = value
                elif isinstance(value, dict) and isinstance(merged.get(key), dict):
                    merged[key] = self._merge_dicts(merged[key], value)
                elif isinstance(value, list) and isinstance(merged.get(key), list):
                    merged[key] = list(set(merged[key] + value))
        
        merged["sources"] = sorted(list(all_sources))
        
        # Prefer highest priority source URL
        if all_source_urls:
            priority_urls = sorted(
                all_source_urls,
                key=lambda url: self._get_url_priority(url, sorted_listings),
                reverse=True
            )
            merged["source_url"] = priority_urls[0] if priority_urls else merged.get("source_url", "")
        
        return merged
    
    def _merge_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two dictionaries, preferring non-empty values from dict1."""
        merged = dict1.copy()
        for key, value in dict2.items():
            if key not in merged or not merged[key]:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._merge_dicts(merged[key], value)
            elif isinstance(value, list) and isinstance(merged.get(key), list):
                merged[key] = list(set(merged[key] + value))
        return merged
    
    def _calculate_completeness_score(self, listing: Dict[str, Any]) -> int:
        """Calculate completeness score (0-100)."""
        fields = [
            "title", "institution", "department", "location", "deadline",
            "description", "requirements", "application_link", "contact_email",
            "contact_person", "specializations", "materials_required"
        ]
        filled = sum(1 for f in fields if listing.get(f) and (
            not isinstance(listing.get(f), (dict, list)) or listing.get(f)
        ))
        return int((filled / len(fields)) * 100)
    
    def _get_url_priority(self, url: str, listings: List[Dict[str, Any]]) -> int:
        """Get priority score for a URL based on source."""
        for listing in listings:
            if listing.get("source_url") == url:
                return SOURCE_PRIORITY.get(listing.get("source", ""), 0)
        return 0
    
    def _parse_date_safely(self, date_str: Optional[str]) -> Optional[date]:
        """Safely parse a date string in YYYY-MM-DD format."""
        if not date_str:
            return None
        try:
            return date.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None
    
    def _detect_new_and_active_listings(
        self,
        current_listings: List[Dict[str, Any]],
        previous_listings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect new listings and update is_active flags."""
        today = date.today()
        
        if not previous_listings:
            for listing in current_listings:
                listing["is_new"] = True
                # Check deadline even with no previous data
                deadline = self._parse_date_safely(listing.get("deadline"))
                listing["is_active"] = deadline >= today if deadline else True
            return current_listings
        
        # Create lookup maps
        previous_by_id = {l.get("id"): l for l in previous_listings if l.get("id")}
        previous_by_key = {}
        for listing in previous_listings:
            key = self._create_listing_key(listing)
            if key:
                previous_by_key[key] = listing
        
        updated = []
        
        for listing in current_listings:
            listing_id = listing.get("id")
            listing_key = self._create_listing_key(listing)
            
            # Find previous listing
            previous = None
            if listing_id and listing_id in previous_by_id:
                previous = previous_by_id[listing_id]
            elif listing_key and listing_key in previous_by_key:
                previous = previous_by_key[listing_key]
            else:
                previous = self._find_similar_listing(listing, previous_listings)
            
            # Set is_new flag
            listing["is_new"] = previous is None
            
            # Set is_active flag based on deadline
            deadline = self._parse_date_safely(listing.get("deadline"))
            if deadline:
                listing["is_active"] = deadline >= today
            elif previous:
                prev_deadline = self._parse_date_safely(previous.get("deadline"))
                listing["is_active"] = prev_deadline >= today if prev_deadline else True
            else:
                listing["is_active"] = True
            
            updated.append(listing)
        
        new_count = sum(1 for l in updated if l.get("is_new"))
        active_count = sum(1 for l in updated if l.get("is_active"))
        logger.info(f"New/active detection: {new_count} new, {active_count} active out of {len(updated)}")
        
        return updated
    
    def _create_listing_key(self, listing: Dict[str, Any]) -> Optional[str]:
        """Create a unique key for a listing."""
        institution = (listing.get("institution") or "").strip().lower()
        title = (listing.get("title") or "").strip().lower()
        deadline = listing.get("deadline") or ""
        
        if not institution or not title or not deadline:
            return None
        
        normalized_institution = self._normalize_institution_name(institution)
        return f"{normalized_institution}||{title}||{deadline}"
    
    def _find_similar_listing(
        self,
        listing: Dict[str, Any],
        previous_listings: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find a similar listing using fuzzy matching."""
        current_institution = (listing.get("institution") or "").strip().lower()
        current_title = (listing.get("title") or "").strip().lower()
        current_deadline = listing.get("deadline") or ""
        
        if not current_institution or not current_title:
            return None
        
        best_match = None
        best_score = 0
        
        for prev_listing in previous_listings:
            if prev_listing.get("deadline") != current_deadline:
                continue
            
            prev_institution = (prev_listing.get("institution") or "").strip().lower()
            prev_title = (prev_listing.get("title") or "").strip().lower()
            
            inst_sim = fuzz.ratio(current_institution, prev_institution)
            title_sim = fuzz.ratio(current_title, prev_title)
            combined = (inst_sim * 0.4) + (title_sim * 0.6)
            
            if combined > best_score and combined >= 85:
                best_score = combined
                best_match = prev_listing
        
        return best_match
    
    def load_previous_listings(self, archive_dir: Path) -> List[Dict[str, Any]]:
        """Load previous listings from archive directory."""
        if not archive_dir.exists():
            logger.warning(f"Archive directory does not exist: {archive_dir}")
            return []
        
        archive_files = list(archive_dir.glob("*_jobs.json"))
        if not archive_files:
            logger.info("No archive files found")
            return []
        
        archive_files.sort(reverse=True)
        most_recent = archive_files[0]
        
        try:
            with open(most_recent, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            listings = data if isinstance(data, list) else data.get("listings", [])
            logger.info(f"Loaded {len(listings)} previous listings from {most_recent.name}")
            return listings
            
        except Exception as e:
            logger.error(f"Error loading archive file {most_recent}: {e}")
            if self.diagnostics:
                self.diagnostics.track_validation_issue(
                    source="archive",
                    field="file_loading",
                    error=f"Failed to load archive: {e}",
                    validation_type="ARCHIVE_LOAD_ERROR"
                )
            return []
