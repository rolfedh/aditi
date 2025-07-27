#!/usr/bin/env python3
"""Test script to verify Vale with AsciiDocDITA rules."""

import json
import tempfile
from pathlib import Path

from src.aditi.vale_container import ValeContainer, check_container_runtime


def test_asciidocdita_rules():
    """Test Vale with AsciiDocDITA rules."""
    print("Testing Vale with AsciiDocDITA rules...\n")
    
    # Check runtime availability
    try:
        runtime = check_container_runtime()
        print(f"✓ Container runtime available: {runtime}")
    except RuntimeError as e:
        print(f"✗ {e}")
        return False
    
    # Create Vale container manager
    vale = ValeContainer(use_podman=(runtime == "podman"))
    
    # Ensure image exists
    vale.ensure_image_exists()
    
    # Create test environment
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create .vale.ini with AsciiDocDITA
        vale_ini = test_dir / ".vale.ini"
        vale_ini.write_text("""StylesPath = .vale/styles
MinAlertLevel = warning

Packages = https://github.com/jhradilek/asciidoctor-dita-vale/releases/latest/download/AsciiDocDITA.zip

[*.adoc]
BasedOnStyles = AsciiDocDITA
""")
        
        # Create test AsciiDoc file with known violations
        test_file = test_dir / "test_violations.adoc"
        test_file.write_text("""= Test Document

This document contains violations that AsciiDocDITA should catch.

== Missing Content Type

This document is missing the content type attribute.

== Entity References

Here are some problematic entities: &mdash; &ndash; &hellip;

== Short Description

Too short.

== Task Section

.Procedure
. Step one
. Step two

== Deprecated Attributes

:_content-type: CONCEPT

This uses the deprecated content type attribute.
""")
        
        print("Downloading AsciiDocDITA styles...")
        # Run vale sync to download styles
        try:
            vale._run_vale_sync(test_dir)
            print("✓ AsciiDocDITA styles downloaded\n")
        except Exception as e:
            print(f"✗ Failed to download styles: {e}")
            return False
        
        # Run Vale
        print("Running Vale with AsciiDocDITA rules...")
        try:
            result = vale.run_vale(test_file, test_dir)
            print("✓ Vale executed successfully\n")
            
            # Display violations
            if test_file.name in result and result[test_file.name]:
                print(f"Found {len(result[test_file.name])} violations:\n")
                for violation in result[test_file.name]:
                    print(f"Line {violation.get('Line', '?')}: {violation.get('Message', 'No message')}")
                    print(f"  Rule: {violation.get('Check', 'Unknown')}")
                    print(f"  Severity: {violation.get('Severity', 'Unknown')}")
                    print()
            else:
                print("No violations found (this might indicate the rules aren't working)")
                
        except Exception as e:
            print(f"✗ Failed to run Vale: {e}")
            return False
    
    print("✓ Test completed!")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if test_asciidocdita_rules() else 1)