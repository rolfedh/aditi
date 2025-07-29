#!/usr/bin/env python3
"""Test script to verify Vale container integration."""

import json
import tempfile
from pathlib import Path

from src.aditi.vale_container import ValeContainer, check_container_runtime


def test_vale_integration():
    """Test the Vale container integration."""
    print("Testing Vale container integration...\n")
    
    # Check runtime availability
    try:
        runtime = check_container_runtime()
        print(f"✓ Container runtime available: {runtime}")
    except RuntimeError as e:
        print(f"✗ {e}")
        return False
    
    # Create Vale container manager
    vale = ValeContainer(use_podman=(runtime == "podman"))
    
    # Test image pulling
    print("\nPulling Vale image...")
    try:
        vale.ensure_image_exists()
        print("✓ Vale image ready")
    except Exception as e:
        print(f"✗ Failed to pull image: {e}")
        return False
    
    # Create test environment
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create test .vale.ini
        vale_ini = test_dir / ".vale.ini"
        vale_ini.write_text("""
StylesPath = .vale/styles
MinAlertLevel = warning

[*.adoc]
BasedOnStyles = Vale
        """)
        
        # Create styles directory
        styles_dir = test_dir / ".vale" / "styles" / "Vale"
        styles_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test AsciiDoc file
        test_file = test_dir / "test.adoc"
        test_file.write_text("""
= Test Document

This is a test document with some issues.

This sentence is very very very very very very long and might trigger a vale warning about sentence length.

:_mod-docs-content-type: CONCEPT

== Section Title

Some content here.
        """)
        
        # Run Vale
        print("\nRunning Vale on test file...")
        try:
            result = vale.run_vale(test_file, test_dir)
            print("✓ Vale executed successfully")
            print(f"\nVale output: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"✗ Failed to run Vale: {e}")
            return False
    
    print("\n✓ All tests passed!")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if test_vale_integration() else 1)