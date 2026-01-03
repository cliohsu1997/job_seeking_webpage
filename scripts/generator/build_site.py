"""
Build script for generating static website from processed job listings.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from scripts.generator.template_renderer import TemplateRenderer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_jobs_data(jobs_file: str = "data/processed/jobs.json") -> Dict[str, Any]:
    """
    Load processed jobs data from JSON file.
    
    Args:
        jobs_file: Path to jobs JSON file
        
    Returns:
        Dictionary containing listings and metadata
    """
    jobs_path = Path(jobs_file)
    
    if not jobs_path.exists():
        raise FileNotFoundError(f"Jobs data file not found: {jobs_file}")
    
    logger.info(f"Loading jobs data from: {jobs_file}")
    
    with open(jobs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    listings = data.get('listings', [])
    metadata = data.get('metadata', {})
    
    logger.info(f"Loaded {len(listings)} job listings")
    return {'listings': listings, 'metadata': metadata}


def copy_static_assets(output_dir: Path):
    """
    Copy static assets (CSS, JS, images) to output directory.
    
    Args:
        output_dir: Output directory path
    """
    static_src = Path("static")
    
    # Skip if output directory is the same as source
    if output_dir.resolve() == static_src.resolve():
        logger.info("Output directory is same as static source, skipping asset copy")
        return
    
    # Directories to copy
    dirs_to_copy = ['css', 'js', 'images']
    
    for dir_name in dirs_to_copy:
        src_dir = static_src / dir_name
        if src_dir.exists():
            dest_dir = output_dir / dir_name
            
            # Remove existing directory if it exists
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            
            # Copy directory
            shutil.copytree(src_dir, dest_dir)
            logger.info(f"Copied {dir_name}/ to output directory")


def copy_jobs_data(output_dir: Path, jobs_file: str = "data/processed/jobs.json"):
    """
    Copy jobs.json to output directory's data folder.
    
    Args:
        output_dir: Output directory path
        jobs_file: Source jobs JSON file
    """
    # Create data directory in output
    data_dir = output_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Copy jobs.json
    src = Path(jobs_file)
    dest = data_dir / "jobs.json"
    
    shutil.copy2(src, dest)
    logger.info(f"Copied jobs.json to output/data/")


def build_static_site(
    output_dir: str = "static",
    jobs_file: str = "data/processed/jobs.json",
    template_file: str = "index.html.jinja"
) -> str:
    """
    Build complete static website.
    
    Args:
        output_dir: Output directory for generated site
        jobs_file: Path to jobs JSON file
        template_file: Template file name
        
    Returns:
        Path to generated index.html
    """
    logger.info("=" * 60)
    logger.info("Starting static site build")
    logger.info("=" * 60)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    try:
        # Load jobs data
        data = load_jobs_data(jobs_file)
        
        # Initialize template renderer
        renderer = TemplateRenderer(template_dir="templates")
        
        # Prepare context
        context = renderer.prepare_context(
            listings=data['listings'],
            metadata=data['metadata']
        )
        
        # Render template
        logger.info(f"Rendering template: {template_file}")
        html = renderer.render_template(template_file, context)
        
        # Write output HTML
        output_html = output_path / "index.html"
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Generated: {output_html}")
        
        # Copy static assets
        copy_static_assets(output_path)
        
        # Copy jobs data
        copy_jobs_data(output_path, jobs_file)
        
        logger.info("=" * 60)
        logger.info("✓ Static site build completed successfully")
        logger.info(f"✓ Output location: {output_path.absolute()}")
        logger.info(f"✓ Total listings: {len(data['listings'])}")
        logger.info("=" * 60)
        
        return str(output_html.absolute())
        
    except Exception as e:
        logger.error(f"✗ Build failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point for build script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build static job listings website")
    parser.add_argument(
        '--output', '-o',
        default='static',
        help='Output directory (default: static)'
    )
    parser.add_argument(
        '--jobs-file', '-j',
        default='data/processed/jobs.json',
        help='Jobs data file (default: data/processed/jobs.json)'
    )
    parser.add_argument(
        '--template', '-t',
        default='index.html.jinja',
        help='Template file name (default: index.html.jinja)'
    )
    
    args = parser.parse_args()
    
    try:
        output_html = build_static_site(
            output_dir=args.output,
            jobs_file=args.jobs_file,
            template_file=args.template
        )
        print(f"\n✓ Success! Open: {output_html}\n")
        return 0
    except Exception as e:
        print(f"\n✗ Build failed: {e}\n")
        return 1


if __name__ == '__main__':
    exit(main())
