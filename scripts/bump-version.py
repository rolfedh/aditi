#!/usr/bin/env python3
"""
Simple version bump script for Aditi.

This script only bumps the version in pyproject.toml.
Use this when you want to bump the version without doing a full release.
"""

import argparse
import sys
import re
from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: tomli/tomllib not found. Install with: pip install tomli")
        sys.exit(1)


def get_current_version():
    """Get current version from pyproject.toml."""
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
        return data["project"]["version"]


def bump_version(version, bump_type):
    """Bump version based on type (major, minor, patch)."""
    parts = version.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def update_version_in_file(file_path, old_version, new_version):
    """Update version in a file."""
    content = file_path.read_text()
    # Match version = "x.y.z" pattern
    pattern = f'version = "{re.escape(old_version)}"'
    replacement = f'version = "{new_version}"'
    
    if pattern in content:
        new_content = content.replace(pattern, replacement)
        file_path.write_text(new_content)
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Bump Aditi version")
    parser.add_argument(
        "bump_type", 
        choices=["major", "minor", "patch"],
        nargs="?",
        help="Version bump type (optional - will show current version if not provided)"
    )
    parser.add_argument(
        "--set",
        help="Set version to a specific value (e.g., --set 1.2.3)"
    )
    
    args = parser.parse_args()
    
    # Check we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Are you in the project root?")
        sys.exit(1)
    
    # Get current version
    current_version = get_current_version()
    
    # If no arguments, just show current version
    if not args.bump_type and not args.set:
        print(f"Current version: {current_version}")
        print("\nUsage:")
        print("  Bump version:  python scripts/bump-version.py [major|minor|patch]")
        print("  Set version:   python scripts/bump-version.py --set 1.2.3")
        return
    
    # Determine new version
    if args.set:
        new_version = args.set
        # Validate version format
        if not re.match(r'^\d+\.\d+\.\d+$', new_version):
            print(f"❌ Invalid version format: {new_version}")
            print("Version must be in format X.Y.Z (e.g., 1.2.3)")
            sys.exit(1)
    else:
        new_version = bump_version(current_version, args.bump_type)
    
    print(f"🔄 Bumping version from {current_version} to {new_version}")
    
    # Update version in pyproject.toml
    if not update_version_in_file(Path("pyproject.toml"), current_version, new_version):
        print("❌ Failed to update version in pyproject.toml")
        sys.exit(1)
    
    print(f"✅ Version updated to {new_version} in pyproject.toml")
    print("\nNext steps:")
    print("  1. Review the change: git diff pyproject.toml")
    print("  2. Run tests: pytest")
    print(f"  3. Full release: python scripts/release.py patch")


if __name__ == "__main__":
    main()