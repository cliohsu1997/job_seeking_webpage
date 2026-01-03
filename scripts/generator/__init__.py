"""
Generator module for creating static website from processed job listings.

This module provides tools to:
1. Render Jinja2 templates with job data
2. Build static HTML/CSS/JS website
3. Generate output for deployment
"""

from scripts.generator.template_renderer import TemplateRenderer
from scripts.generator.build_site import build_static_site

__all__ = ['TemplateRenderer', 'build_static_site']
