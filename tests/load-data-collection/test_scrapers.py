"""
Test suite runner for all scraper tests.

This file loads and runs all separate test modules organized by category:
- scraper/ - Scraper class tests
- parser/ - Parser module tests
- configuration/ - Configuration loader tests
- utils/ - Utility module tests

Individual test files can also be run separately from their subfolders.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "scraper"))

# Add tests directory to path for test modules
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir))


def load_tests(loader, standard_tests, pattern):
    """Load all test modules from subfolders."""
    suite = unittest.TestSuite()
    
    # Organize test modules by category
    test_modules = {
        # Scraper tests
        'scraper.test_base_scraper',
        'scraper.test_aea_scraper',
        'scraper.test_university_scraper',
        'scraper.test_institute_scraper',
        
        # Parser tests
        'parser.test_html_parser',
        'parser.test_rss_parser',
        'parser.test_text_extractor',
        'parser.test_date_parser',
        
        # Configuration tests
        'configuration.test_config_loader',
        
        # Utils tests
        'utils.test_rate_limiter',
        'utils.test_retry_handler',
        'utils.test_user_agent',
    }
    
    for module_name in test_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")
    
    return suite


if __name__ == "__main__":
    # Run all tests
    loader = unittest.TestLoader()
    suite = load_tests(loader, None, None)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

