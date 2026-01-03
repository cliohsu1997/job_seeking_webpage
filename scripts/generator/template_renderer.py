"""
Template renderer for generating static HTML from Jinja2 templates.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders Jinja2 templates with job listing data."""
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialize the template renderer.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = Path(template_dir)
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
        
        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters
        self._register_filters()
        
        logger.info(f"Template renderer initialized with directory: {template_dir}")
    
    def _register_filters(self):
        """Register custom Jinja2 filters."""
        self.env.filters['format_date'] = self._format_date
        self.env.filters['relative_date'] = self._relative_date
        self.env.filters['truncate_text'] = self._truncate_text
        self.env.filters['format_deadline'] = self._format_deadline
    
    @staticmethod
    def _format_date(date_str: str, format_str: str = "%B %d, %Y") -> str:
        """
        Format date string.
        
        Args:
            date_str: Date string in ISO format
            format_str: Output format string
            
        Returns:
            Formatted date string
        """
        if not date_str:
            return "Not specified"
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime(format_str)
        except (ValueError, AttributeError):
            return date_str
    
    @staticmethod
    def _relative_date(date_str: str) -> str:
        """
        Get relative date string (e.g., "2 days left", "Expired").
        
        Args:
            date_str: Date string in ISO format
            
        Returns:
            Relative date string
        """
        if not date_str:
            return "No deadline"
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now(date_obj.tzinfo)
            delta = date_obj - now
            
            if delta.days < 0:
                return "Expired"
            elif delta.days == 0:
                return "Today"
            elif delta.days == 1:
                return "Tomorrow"
            elif delta.days < 7:
                return f"{delta.days} days left"
            elif delta.days < 30:
                weeks = delta.days // 7
                return f"{weeks} {'week' if weeks == 1 else 'weeks'} left"
            elif delta.days < 365:
                months = delta.days // 30
                return f"{months} {'month' if months == 1 else 'months'} left"
            else:
                return date_obj.strftime("%B %d, %Y")
        except (ValueError, AttributeError):
            return date_str
    
    @staticmethod
    def _truncate_text(text: str, length: int = 150, suffix: str = "...") -> str:
        """
        Truncate text to specified length.
        
        Args:
            text: Text to truncate
            length: Maximum length
            suffix: Suffix to append if truncated
            
        Returns:
            Truncated text
        """
        if not text or len(text) <= length:
            return text or ""
        
        return text[:length].rsplit(' ', 1)[0] + suffix
    
    @staticmethod
    def _format_deadline(date_str: str) -> Dict[str, Any]:
        """
        Format deadline with urgency level.
        
        Args:
            date_str: Date string in ISO format
            
        Returns:
            Dictionary with formatted date and urgency level
        """
        if not date_str:
            return {"text": "No deadline", "urgency": "none", "class": ""}
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now(date_obj.tzinfo)
            delta = date_obj - now
            
            # Determine urgency
            if delta.days < 0:
                urgency = "expired"
                css_class = "deadline-expired"
            elif delta.days <= 7:
                urgency = "high"
                css_class = "deadline-urgent"
            elif delta.days <= 30:
                urgency = "medium"
                css_class = "deadline-soon"
            else:
                urgency = "low"
                css_class = "deadline-normal"
            
            # Format date
            relative = TemplateRenderer._relative_date(date_str)
            formatted = date_obj.strftime("%b %d, %Y")
            
            return {
                "text": relative,
                "full_date": formatted,
                "urgency": urgency,
                "class": css_class,
                "days_left": delta.days
            }
        except (ValueError, AttributeError):
            return {"text": date_str, "urgency": "none", "class": ""}
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with given context.
        
        Args:
            template_name: Name of template file
            context: Context dictionary for template
            
        Returns:
            Rendered HTML string
        """
        try:
            template = self.env.get_template(template_name)
            html = template.render(**context)
            logger.info(f"Successfully rendered template: {template_name}")
            return html
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise
    
    def prepare_context(self, listings: List[Dict[str, Any]], 
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Prepare context data for template rendering.
        
        Args:
            listings: List of job listings
            metadata: Optional metadata dictionary
            
        Returns:
            Context dictionary for template
        """
        # Calculate statistics
        total_listings = len(listings)
        
        # Count by various categories
        by_region = {}
        by_job_type = {}
        by_institution_type = {}
        new_listings = 0
        active_listings = 0
        
        for listing in listings:
            # Region
            region = listing.get('location', {}).get('region', 'Unknown')
            by_region[region] = by_region.get(region, 0) + 1
            
            # Job type
            job_type = listing.get('job_type', 'Unknown')
            by_job_type[job_type] = by_job_type.get(job_type, 0) + 1
            
            # Institution type
            inst_type = listing.get('institution_type', 'Unknown')
            by_institution_type[inst_type] = by_institution_type.get(inst_type, 0) + 1
            
            # New/Active flags
            if listing.get('is_new'):
                new_listings += 1
            if listing.get('is_active'):
                active_listings += 1
        
        # Build context
        context = {
            'listings': listings,
            'stats': {
                'total': total_listings,
                'new': new_listings,
                'active': active_listings,
                'by_region': by_region,
                'by_job_type': by_job_type,
                'by_institution_type': by_institution_type
            },
            'metadata': metadata or {},
            'generated_at': datetime.now().isoformat(),
            'page_title': 'Economics Faculty Job Openings'
        }
        
        logger.info(f"Prepared context with {total_listings} listings")
        return context
