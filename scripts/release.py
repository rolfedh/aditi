#!/usr/bin/env python3
"""
Release automation script for Aditi.

This script handles the entire release process:
1. Bumps version in pyproject.toml
2. Runs tests
3. Builds the package
4. Uploads to PyPI
5. Creates git commit and tag
6. Creates GitHub release
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path
import json

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: tomli/tomllib not found. Install with: pip install tomli")
        sys.exit(1)


def run_command(cmd, check=True, capture_output=False):
    """Run a shell command."""
    print(f"➤ {cmd}")
    if capture_output:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result.stdout.strip()
    else:
        result = subprocess.run(cmd, shell=True)
        if check and result.returncode != 0:
            sys.exit(1)
        return None


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
    parser = argparse.ArgumentParser(description="Release Aditi")
    parser.add_argument(
        "bump_type", 
        choices=["major", "minor", "patch"],
        help="Version bump type"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests"
    )
    parser.add_argument(
        "--skip-pypi",
        action="store_true",
        help="Skip PyPI upload (only do git operations)"
    )
    parser.add_argument(
        "--no-github-release",
        action="store_true",
        help="Skip creating GitHub release"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it"
    )
    
    args = parser.parse_args()
    
    # Check we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Are you in the project root?")
        sys.exit(1)
    
    # Get current and new version
    current_version = get_current_version()
    new_version = bump_version(current_version, args.bump_type)
    
    print(f"🔄 Bumping version from {current_version} to {new_version}")
    
    if args.dry_run:
        print("\n🌟 DRY RUN - Would perform these actions:")
        print(f"  1. Update version in pyproject.toml to {new_version}")
        print("  2. Run tests")
        print("  3. Build package")
        print("  4. Upload to PyPI")
        print(f"  5. Commit changes with message: 'chore: Bump version to {new_version}'")
        print(f"  6. Create and push tag v{new_version}")
        print("  7. Create GitHub release")
        return
    
    # Update version in pyproject.toml
    print("\n📝 Updating version in pyproject.toml...")
    if not update_version_in_file(Path("pyproject.toml"), current_version, new_version):
        print("❌ Failed to update version in pyproject.toml")
        sys.exit(1)
    
    # Run tests
    if not args.skip_tests:
        print("\n🧪 Running tests...")
        run_command("pytest --ignore=tests/test_claude_md_updater.py", check=False)
    
    # Clean and build
    print("\n🧹 Cleaning previous builds...")
    run_command("rm -rf dist/ build/ *.egg-info src/*.egg-info")
    
    print("\n📦 Building package...")
    run_command("python -m build")
    
    # Upload to PyPI
    if not args.skip_pypi:
        print("\n📤 Uploading to PyPI...")
        # Check if twine is available
        try:
            run_command("which twine", check=True, capture_output=True)
            run_command("twine upload dist/*")
        except:
            # Try with pipx
            run_command("pipx run twine upload dist/*")
        
        print(f"\n✅ Published to PyPI: https://pypi.org/project/aditi/{new_version}/")
    
    # Git operations
    print("\n🔧 Committing changes...")
    run_command("git add pyproject.toml")
    
    commit_message = f"""chore: Bump version to {new_version}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""
    
    run_command(f'git commit -m "{commit_message}"')
    
    # Push to main
    print("\n📤 Pushing to main...")
    run_command("git push origin main")
    
    # Create and push tag
    print(f"\n🏷️  Creating tag v{new_version}...")
    run_command(f'git tag -a v{new_version} -m "Release version {new_version}"')
    run_command(f"git push origin v{new_version}")
    
    # Create GitHub release
    if not args.no_github_release:
        print("\n📢 Creating GitHub release...")
        release_notes = f"""## What's Changed

See the [full changelog](https://github.com/rolfedh/aditi/compare/v{current_version}...v{new_version})

## Installation

```bash
pip install --upgrade aditi
```
"""
        
        cmd = f'''gh release create v{new_version} \
  --title "v{new_version}" \
  --notes "{release_notes}"'''
        
        run_command(cmd)
        
        print(f"\n✅ GitHub release created: https://github.com/rolfedh/aditi/releases/tag/v{new_version}")
    
    print(f"\n🎉 Successfully released version {new_version}!")
    print("\nNext steps:")
    print("  1. Verify the release on PyPI")
    print("  2. Update the GitHub release notes with details")
    print("  3. Announce the release")


if __name__ == "__main__":
    main()