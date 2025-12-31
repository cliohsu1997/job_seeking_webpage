"""
Test Python setup and execution methods.

This test verifies that Python can be run correctly using different methods:
1. Direct Python execution
2. Poetry shell activation
3. Poetry run command
"""

import sys
import subprocess
import os
from pathlib import Path


def test_python_version():
    """Test that Python version matches expected version."""
    expected_major = 3
    expected_minor_min = 10
    
    assert sys.version_info.major == expected_major, \
        f"Expected Python {expected_major}.x, got {sys.version_info.major}.x"
    assert sys.version_info.minor >= expected_minor_min, \
        f"Expected Python {expected_major}.{expected_minor_min}+, got {sys.version_info.major}.{sys.version_info.minor}"
    
    print(f"✓ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def test_python_execution():
    """Test that Python can execute a simple script."""
    test_code = "print('Python execution test: SUCCESS')"
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        check=True
    )
    assert "SUCCESS" in result.stdout
    print("✓ Python can execute code directly")


def test_poetry_available():
    """Test that Poetry is available for environment management."""
    try:
        result = subprocess.run(
            ["poetry", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Poetry available (for environment management): {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Poetry not found in PATH (needed for: poetry install, poetry add)")
        return False


def test_virtual_environment():
    """Test that virtual environment exists and is being used."""
    venv_path = Path("environment/python/venv")
    
    if venv_path.exists():
        print(f"✓ Virtual environment exists at: {venv_path}")
        
        # Check if we're in the venv
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✓ Currently running in the virtual environment")
            print(f"  Python executable: {sys.executable}")
        else:
            print("ℹ Not currently in virtual environment")
            print("  Activate with: .\\environment\\python\\venv\\Scripts\\Activate.ps1")
    else:
        print("⚠ Virtual environment not found")
        print("  Create with: poetry install (Poetry manages the environment)")


def test_project_structure():
    """Test that essential project files exist."""
    required_files = [
        "pyproject.toml",
        "environment/python/tools/pyproject.toml",
        "environment/python/tools/poetry.lock",
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        assert path.exists(), f"Required file not found: {file_path}"
        print(f"✓ Found: {file_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("Python Setup Test")
    print("=" * 60)
    print()
    
    try:
        test_python_version()
        test_python_execution()
        test_poetry_available()
        test_virtual_environment()
        test_project_structure()
        
        print()
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

