"""
Test script for Parser Manager integration with Phase 1 parsers.

Tests the parser manager's ability to:
- Scan raw HTML/XML files
- Parse filenames to extract metadata
- Route files to appropriate parsers (AEA, university, institute)
- Extract job listings from raw files
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.processor.parser_manager import ParserManager


def test_parser_manager_scanning():
    """Test that parser manager can scan raw files."""
    print("=" * 60)
    print("Test 1: File Scanning")
    print("=" * 60)
    
    pm = ParserManager()
    files = pm.scan_raw_files()
    
    print(f"✓ Found {len(files)} files")
    
    # Check file distribution by source type
    by_source = {}
    for file_meta in files:
        source = file_meta['source_type']
        by_source[source] = by_source.get(source, 0) + 1
    
    print(f"  - AEA files: {by_source.get('aea', 0)}")
    print(f"  - University files: {by_source.get('university', 0)}")
    print(f"  - Institute files: {by_source.get('institute', 0)}")
    
    return files


def test_filename_parsing():
    """Test filename parsing to extract metadata."""
    print("\n" + "=" * 60)
    print("Test 2: Filename Parsing")
    print("=" * 60)
    
    pm = ParserManager()
    
    # Test university filename
    uni_metadata = pm._parse_filename("us_harvard_university_economics.html", "university")
    print(f"✓ University filename parsed:")
    print(f"  - University: {uni_metadata.get('university_name', 'N/A')}")
    print(f"  - Department: {uni_metadata.get('department', 'N/A')}")
    print(f"  - Country: {uni_metadata.get('country', 'N/A')}")
    
    # Test institute filename
    inst_metadata = pm._parse_filename("us_institute_brookings_institution.html", "institute")
    print(f"✓ Institute filename parsed:")
    print(f"  - Institute: {inst_metadata.get('institute_name', 'N/A')}")
    print(f"  - Country: {inst_metadata.get('country', 'N/A')}")
    
    # Test AEA filename
    aea_metadata = pm._parse_filename("portal_american_economic_association_joe.html", "aea")
    print(f"✓ AEA filename parsed:")
    print(f"  - Source: {aea_metadata.get('source_name', 'N/A')}")


def test_file_parsing(files):
    """Test parsing actual files."""
    print("\n" + "=" * 60)
    print("Test 3: File Parsing")
    print("=" * 60)
    
    pm = ParserManager()
    
    # Test parsing a few files from each source type
    test_files_by_type = {}
    for file_meta in files:
        source_type = file_meta['source_type']
        if source_type not in test_files_by_type:
            test_files_by_type[source_type] = file_meta
        if len(test_files_by_type) >= 3:
            break
    
    for source_type, test_file in test_files_by_type.items():
        print(f"\nTesting {source_type} file: {test_file['filename']}")
        try:
            listings = pm.parse_file(test_file)
            print(f"  ✓ Extracted {len(listings)} listings")
            
            if listings:
                first_listing = listings[0]
                print(f"  ✓ First listing keys: {list(first_listing.keys())[:5]}...")
                print(f"  ✓ Sample title: {first_listing.get('title', 'N/A')[:60]}...")
                print(f"  ✓ Source: {first_listing.get('source', 'N/A')}")
                if 'institution' in first_listing:
                    print(f"  ✓ Institution: {first_listing.get('institution', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()


def test_parsing_statistics():
    """Test parsing statistics."""
    print("\n" + "=" * 60)
    print("Test 4: Parsing Statistics")
    print("=" * 60)
    
    pm = ParserManager()
    stats = pm.get_parsing_statistics()
    
    print(f"✓ Total files: {stats['total_files']}")
    print(f"✓ By source type: {stats['by_source_type']}")
    print(f"✓ By directory: {stats['by_directory']}")


def main():
    """Run all tests."""
    print("Testing Parser Manager Integration")
    print("=" * 60)
    
    # Test 1: File scanning
    files = test_parser_manager_scanning()
    
    # Test 2: Filename parsing
    test_filename_parsing()
    
    # Test 3: File parsing (only if files found)
    if files:
        test_file_parsing(files)
    
    # Test 4: Statistics
    test_parsing_statistics()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

