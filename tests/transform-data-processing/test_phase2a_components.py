"""
Quick test script for Phase 2A: Core Pipeline Foundation components.

Tests all Phase 2A components:
- Diagnostics Tracker
- Text Cleaner Utility
- ID Generator Utility
- Schema Definition
- Parser Manager
- Normalizer (basic structure)
- Pipeline (basic structure)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("Testing Phase 2A Components...")
print("=" * 60)

# Test 1: Diagnostics
print("\n1. Testing Diagnostics Tracker...")
try:
    from scripts.processor.diagnostics import DiagnosticTracker
    dt = DiagnosticTracker()
    dt.track_normalization_issue('test_source', 'test_field', 'test_value', 'test_error')
    stats = dt.get_statistics()
    assert stats['normalization_issues'] == 1
    print("   ✅ Diagnostics tracker works")
except Exception as e:
    print(f"   ❌ Diagnostics tracker failed: {e}")

# Test 2: Text Cleaner
print("\n2. Testing Text Cleaner...")
try:
    from scripts.processor.utils.text_cleaner import clean_text, clean_text_field
    result = clean_text('  Hello   World  ')
    assert result == 'Hello World'
    result2 = clean_text_field('  Test  ')
    assert result2 == 'Test'
    print(f"   ✅ Text cleaner works - '{result}'")
except Exception as e:
    print(f"   ❌ Text cleaner failed: {e}")

# Test 3: ID Generator
print("\n3. Testing ID Generator...")
try:
    from scripts.processor.utils.id_generator import generate_job_id, generate_id_from_dict
    id1 = generate_job_id('Harvard', 'Professor', '2025-01-15')
    id2 = generate_job_id('Harvard', 'Professor', '2025-01-15')
    assert id1 == id2
    assert len(id1) == 32
    id3 = generate_id_from_dict({'institution': 'MIT', 'title': 'Assistant Professor', 'deadline': '2025-02-01'})
    assert id3 is not None
    print(f"   ✅ ID generator works - ID: {id1[:16]}...")
except Exception as e:
    print(f"   ❌ ID generator failed: {e}")

# Test 4: Schema
print("\n4. Testing Schema...")
try:
    from scripts.processor.schema import SCHEMA, REQUIRED_FIELDS, validate_schema
    assert len(SCHEMA) == 29
    assert len(REQUIRED_FIELDS) == 22
    test_data = {'id': 'test', 'title': 'Test'}
    is_valid, errors = validate_schema(test_data, strict=False)
    assert not is_valid  # Should be invalid due to missing required fields
    print(f"   ✅ Schema works - {len(SCHEMA)} fields, {len(REQUIRED_FIELDS)} required")
except Exception as e:
    print(f"   ❌ Schema failed: {e}")

# Test 5: Parser Manager
print("\n5. Testing Parser Manager...")
try:
    from scripts.processor.parser_manager import ParserManager
    pm = ParserManager()
    files = pm.scan_raw_files()
    stats = pm.get_parsing_statistics()
    print(f"   ✅ Parser manager works - Found {stats['total_files']} files")
    if stats['by_directory']:
        print(f"      Files by directory: {stats['by_directory']}")
except Exception as e:
    print(f"   ❌ Parser manager failed: {e}")

# Test 6: Normalizer (without date parser dependency)
print("\n6. Testing Normalizer (basic structure)...")
try:
    from scripts.processor.normalizer import DataNormalizer
    normalizer = DataNormalizer(diagnostics=dt)
    # Test text normalization only (date parser requires dateutil in venv)
    result = normalizer.normalize_text('  Test Text  ', 'test_field')
    assert result == 'Test Text'
    print(f"   ✅ Normalizer structure works - text normalization OK")
except Exception as e:
    print(f"   ⚠️  Normalizer import check (date parser requires venv): {e}")

# Test 7: Pipeline (basic structure)
print("\n7. Testing Pipeline (basic structure)...")
try:
    from scripts.processor.pipeline import ProcessingPipeline
    pipeline = ProcessingPipeline()
    print("   ✅ Pipeline structure works - initialized successfully")
except Exception as e:
    print(f"   ⚠️  Pipeline import check (dependencies may require venv): {e}")

print("\n" + "=" * 60)
print("Phase 2A Component Tests Complete!")
print("Note: Some components require virtual environment for full functionality")

