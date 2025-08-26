# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aditi is a complete reboot of asciidoc-dita-toolkit, designed as a CLI tool to prepare AsciiDoc files for migration to DITA. The name is short for "asciidoc dita integration."

## Development Environment

### Prerequisites
- Python 3.11 or later
- Podman (preferred) or Docker (for running Vale linter with AsciiDocDITA ruleset)
- Git
- Ruby 3.1+ and Bundler (for Jekyll documentation site)
- GitLab CLI (`glab`) for GitLab integration
- GitHub CLI (`gh`) if GitHub support is needed

<!-- AUTO-GENERATED:DEPENDENCIES -->
### Core Dependencies
- **CLI Framework**: typer>=0.9.0
- **Data Validation**: pydantic>=2.5.0, pydantic-settings>=2.1.0
- **Other**: rich>=13.7.0, questionary>=2.0.0

### Development Dependencies
- **Testing**: pytest>=7.4.0, pytest-cov>=4.1.0, pytest-mock>=3.12.0
- **Code Quality**: mypy>=1.8.0, ruff>=0.1.9, black>=23.12.0
- **Other**: pyyaml>=6.0.0, pre-commit>=3.6.0
<!-- /AUTO-GENERATED:DEPENDENCIES -->

## Architecture

Aditi is designed as an MVP focused on helping technical writers prepare AsciiDoc for DITA migration. The tool:
1. Runs Vale linter with AsciiDocDITA rules against *.adoc files using containerized execution
2. Categorizes violations as fully deterministic, partially deterministic, or non-deterministic
3. Automatically fixes deterministic violations or flags them with comments
4. Guides users through git workflow for creating branches, commits, and pull requests

## Key Concepts

### Violation Fix Types
1. **Fully deterministic**: Can be fixed automatically (e.g., EntityReference rule)
2. **Partially deterministic**: Can be partially fixed with placeholders (e.g., ContentType rule)
3. **Non-deterministic**: Must be fixed manually by the user

### Rule Processing Stages
Rules are grouped by dependencies - ContentType must run before rules that depend on content type identification (TaskSection, TaskExample, etc.).

### Examples of Violation Fix Types

#### Fully Deterministic Example (EntityReference)
```asciidoc
// Before
Use the -> arrow and the (R) symbol.

// After (automatically fixed)
Use the &#8594; arrow and the &#174; symbol.
```

#### Partially Deterministic Example (ContentType)
```asciidoc
// Before (missing content type)
= My Document Title

// After (with placeholder)
= My Document Title
:_mod-docs-content-type: <PLACEHOLDER: Choose from ASSEMBLY, CONCEPT, PROCEDURE, REFERENCE, or SNIPPET>
```

#### Non-Deterministic Example (TaskSection)
```asciidoc
// Flagged with comment
// ADITI-ERROR: TaskSection - Task sections must use specific heading syntax
== Installing the Software
```

<!-- AUTO-GENERATED:COMMANDS -->
### Development
- **Install dependencies**: `pip install -e ".[dev]"`
- **Run tests**: `pytest`
- **Type checking**: `mypy src/`
- **Format code**: `black src/ tests/`
- **Lint code**: `ruff check src/ tests/`

### Usage
- **Initialize Vale**: `aditi init`
- **Check files**: `aditi check`
- **Start journey**: `aditi journey`
- **Fix issues**: `aditi fix --rule EntityReference`
<!-- /AUTO-GENERATED:COMMANDS -->

## Important Rules

### Template Reference Standards
- **Canonical Templates**: Use `mod-docs-templates/` directory as the authoritative reference for mod-docs compliant AsciiDoc structure
- **Content Placement**: When implementing fixes or modifications, refer to template files to determine proper content organization and placement
- **Compliance Validation**: Templates serve as the gold standard for DITA migration readiness

### ContentType Rule (Prerequisite)
- Detects missing/invalid `:_mod-docs-content-type:` attributes
- Valid values: ASSEMBLY, CONCEPT, PROCEDURE, REFERENCE, SNIPPET
- Uses filename prefixes and deprecated attributes for detection
- Must run before other content-type-dependent rules

### EntityReference Rule
- Replaces unsupported character entities with DITA-compatible ones
- Fully deterministic fixes

## Git Workflow

Aditi guides users through:
1. Creating feature branches
2. Running rules and making fixes
3. Reviewing changes before commits
4. Creating commits with descriptive messages
5. Creating pull requests
6. User review and merge process

Note: Git operations are user-guided rather than automated for security and transparency.

## Configuration

### Vale Configuration
- Created automatically by `aditi init`
- Template: `src/aditi/vale/vale_config_template.ini`
- Downloads AsciiDocDITA styles from GitHub releases
- Stored as `.vale.ini` in project root

### User Configuration
User configuration stored in `~/aditi-data/config.json`:
- Repository root and branch settings
- Subdirectory permissions (allow/block)
- Feature branch naming conventions
- Session state management for current operations

## Session Management

### Overview
Aditi maintains session state to provide continuity across command invocations, allowing users to resume interrupted workflows.

### Session Features
- **Automatic state persistence**: Sessions are saved to `~/aditi-data/sessions/`
- **Graceful recovery**: Resume from where you left off after interruptions
- **Progress tracking**: Visual indicators show completion status
- **Branch management**: Tracks current working branch and changes

### Session Workflow
1. Start a journey: `aditi journey`
2. Session ID is generated and displayed
3. Progress is saved after each step
4. If interrupted, run `aditi journey` to continue
5. Sessions expire after 7 days of inactivity

## Implementation Status

<!-- AUTO-GENERATED:COMPLETED -->
### Completed (Phase 0)
✅ Vale container integration with Podman/Docker support
✅ Init command with Rich progress indicators

### Completed (Phase 1)
✅ Modern Python packaging with pyproject.toml
✅ Complete CLI structure with Typer framework
✅ Configuration management with Pydantic models
✅ Comprehensive test suite (unit and integration)

### Completed (Phase 2)
✅ Complete AsciiDocDITA rule engine with 27 implemented rules
✅ Non-deterministic pattern implementation for consistent rule structure
✅ Rule registry system for dynamic rule discovery and execution
✅ ContentType rule (prerequisite for content-dependent rules)
✅ EntityReference rule with deterministic fixes
✅ Vale output parsing and violation processing
✅ Document processing pipeline with rule application
✅ File scanning and AsciiDoc document discovery

### Completed (Documentation & Quality Assurance)
✅ Blog post validation test suite with regression prevention
✅ Jekyll front matter standardization across all blog posts
✅ GitHub Actions workflow for automated blog post validation

### Completed (Phase 3 - Journey Session Management)
✅ Session state persistence and recovery
✅ Interactive journey workflow with user guidance
✅ Git workflow integration for branch management
✅ Rule execution with progress tracking
✅ Session continuity across command invocations
<!-- /AUTO-GENERATED:COMPLETED -->

### Next Phases
- **Phase 4**: Reporting and Distribution
- **Phase 5**: Advanced Features (rule customization)

<!-- AUTO-GENERATED:ARCHITECTURE -->
### Current Architecture
```
src/aditi/
├── __init__.py
├── cli.py                 # Main CLI interface
├── config.py              # Configuration management
├── commands/
│   ├── init.py           # Vale initialization
│   ├── check.py          # Rule checking
│   ├── fix.py            # Auto-fixing
│   └── journey.py        # Interactive workflow
├── rules/
│   ├── base.py           # Base rule classes
│   ├── registry.py       # Rule discovery
│   └── ...               # Individual rule implementations
├── vale_container.py      # Container management
└── processor.py          # Rule processing engine

tests/
├── unit/                 # Unit tests
└── integration/          # Integration tests

docs/
├── _posts/              # Blog posts
└── _design/             # Design documents
```
<!-- /AUTO-GENERATED:ARCHITECTURE -->

## Role and Capabilities

- You are a world class software architect and python developer.

## GitHub Pages Setup

The project includes a Jekyll-based documentation site at `/docs` with:
- Just the Docs theme for professional technical documentation
- Custom CSS with drop shadows for all images
- Recent commits section that auto-updates via GitHub Actions
- Blog functionality for development updates
- Proper asset organization in `/docs/assets/images/blog/`

### Jekyll URL Structure and Link Guidelines

**CRITICAL**: To prevent broken links, always follow these URL patterns:

#### Internal Links in Blog Posts and Documentation:
- **Design docs**: `/aditi/design/[document-name]/`
  - Example: `/aditi/design/claude-code-todo-list/`
  - Example: `/aditi/design/container-setup-tasks/`
- **Blog posts**: `/aditi/blog/YYYY/MM/DD/post-title/`
- **Images**: `/aditi/assets/images/blog/YYYY-MM-DD/image.png`

#### Why the `/aditi/` prefix is required:
- Jekyll is configured with `baseurl: "/aditi"` in `_config.yml`
- GitHub Pages hosts the site at `https://rolfedh.github.io/aditi/`
- Missing this prefix results in 404 errors on the live site

#### Design Document Requirements:
All design documents in `docs/_design/` must have Jekyll front matter:
```yaml
---
layout: page
title: "Document Title"
permalink: /design/document-name/
---
```

#### Link Verification:
- Test all internal links locally with `bundle exec jekyll serve`
- Verify links work at `http://localhost:4000/aditi/`
- Use relative paths starting with `/aditi/` for internal content

## Post Writing Guidelines

### Standardized Front Matter Format
**CRITICAL**: All blog posts must use this exact front matter structure to prevent Jekyll build failures:

```yaml
---
layout: post
title: "Your Blog Post Title Here"
date: YYYY-MM-DD HH:MM:SS -0400
author: Author Name
tags: [tag1, tag2, tag3]
summary: "Brief 1-2 sentence summary for listings"
---
```

### Blog Post Validation
A comprehensive test suite prevents Jekyll deployment failures:
- **Automated validation**: `python tests/test_blog_post_validation.py`
- **GitHub Actions**: Validates all posts on push/PR
- **Catches issues**: Missing fields, invalid dates, placeholder content
- **Template safety**: Ensures template files are excluded from processing

### Manual Blog Post Creation
1. **Filename Format**: `YYYY-MM-DD-HHMM-post-title.md`
   - Get timestamp: `date '+%Y-%m-%d-%H%M'`
   - Example: `2025-07-29-1400-implementing-new-feature.md`

2. **Front Matter Requirements**:
   - **layout**: Must be `post`
   - **title**: In quotes, descriptive
   - **date**: `YYYY-MM-DD HH:MM:SS -0400` format (get with `date '+%Y-%m-%d %H:%M:%S %z'`)
   - **author**: Full name or team
   - **tags**: Array format `[tag1, tag2, tag3]`
   - **summary**: Brief description for blog listings

3. **Template Usage**: Use `docs/_posts/post-template.md` as reference
4. **Link Guidelines**: Follow `/aditi/` prefix rules for internal links
5. **Validation**: Run `python tests/test_blog_post_validation.py` before committing

<!-- AUTO-GENERATED:RECENT -->
## Recent Development Focus (August 2025)

### Statistics
- Total commits: 231
- ⚠️  Breaking changes: 1

### Latest Achievements
- ✅ Add file path arguments to journey command for direct processing.
- ✅ Implement automation plan for aditi rule creation from vale rules.
- ✅ Entityreference rule now respects asciidoc subs attributes.
- ✅ Implement single-source versioning.
- ✅ Add intermediate recheck step and fix accurate fix counting in journey workflow.

### Development Focus
- **Ci/Cd**: 95 commits
- **Features**: 25 commits
- **Bug Fixes**: 18 commits
- **Documentation**: 16 commits
- **Testing**: 14 commits

### Most Active Files
- `docs/_data/recent_commits.yml`: 91 changes
- `CLAUDE.md`: 68 changes
- `src/aditi/commands/journey.py`: 20 changes
<!-- /AUTO-GENERATED:RECENT -->

## Building and Publishing

### Prerequisites for Publishing
**CRITICAL**: Ensure these tools are available before releasing:
```bash
# Check if required tools are installed
python -m pip list | grep -E "(build|twine|wheel)"

# If missing, install via pipx (recommended for system-wide tools)
pipx install twine
pipx install build

# Or ensure requirements-publish.txt includes:
# build>=1.0.0
# twine>=4.0.0
# wheel>=0.40.0
```

### Pre-Release Checklist
**IMPORTANT**: Complete these checks before starting the release:
1. [ ] All tests pass: `pytest --ignore=tests/test_claude_md_updater.py`
2. [ ] No import errors: `python -c "import aditi; print(aditi.__version__)"`
3. [ ] Clean working directory: `git status` shows no uncommitted changes
4. [ ] On main branch: `git branch --show-current` shows `main`
5. [ ] Up to date with remote: `git pull origin main`

### PyPI Release Process

#### 1. Version Management
**CRITICAL**: Version must be updated in THREE places:
- `pyproject.toml`: Update the `version` field
- `src/aditi/__init__.py`: Update the `__version__` variable  
- `tests/integration/test_cli_integration.py`: Update version assertion

```bash
# Example: Bumping to version 0.1.5
# Edit pyproject.toml
version = "0.1.5"

# Edit src/aditi/__init__.py
__version__ = "0.1.5"

# Edit tests/integration/test_cli_integration.py
assert "aditi version 0.1.5" in result.stdout
```

**TIP**: To verify all versions match:
```bash
# Check version consistency
grep -n "0\.1\.[0-9]" pyproject.toml src/aditi/__init__.py tests/integration/test_cli_integration.py
```

#### 2. Build the Package
```bash
# Clean previous builds - IMPORTANT!
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Build source distribution and wheel
python -m build

# Verify the build
ls -la dist/
# Should show: aditi-0.1.5.tar.gz and aditi-0.1.5-py3-none-any.whl
```

#### 3. Test with TestPyPI (Optional but Recommended)
```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
# Or with pipx: pipx run twine upload --repository testpypi dist/*

# Test installation in a clean environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ aditi
aditi --version  # Verify it works
deactivate
rm -rf test-env
```

#### 4. Upload to PyPI
```bash
# Upload to PyPI (requires PyPI API token)
python -m twine upload dist/*
# Or with pipx: pipx run twine upload dist/*

# Verify installation
pip install --upgrade aditi
```

**Note**: If you encounter "externally-managed-environment" errors, use `pipx run twine` instead of installing twine directly.

### GitHub Release Process

#### 1. Commit and Push Changes
```bash
# Stage version changes
git add pyproject.toml src/aditi/__init__.py tests/integration/test_cli_integration.py

# Commit with semantic version message
git commit -m "chore: Bump version to 0.1.5 in pyproject.toml and __init__.py"

# Push to main (handle any conflicts with pull --rebase if needed)
git push origin main
```

#### 2. Create and Push Version Tag
```bash
# Create annotated tag AFTER pushing the commit
git tag -a v0.1.5 -m "Release version 0.1.5"

# Push tag to GitHub
git push origin v0.1.5
```

#### 3. Create GitHub Release with gh CLI
```bash
# Create release with auto-generated notes (recommended)
gh release create v0.1.5 \
  --title "v0.1.5" \
  --generate-notes

# Or create with custom changelog
gh release create v0.1.5 \
  --title "v0.1.5" \
  --notes "## What's Changed
- Feature: Add new functionality
- Fix: Resolve issue with X
- Docs: Update documentation

**Full Changelog**: https://github.com/rolfedh/aditi/compare/v0.1.4...v0.1.5"

# Upload built artifacts (optional)
gh release upload v0.1.5 dist/*
```

#### 4. Alternative: Draft Release for Review
```bash
# Create draft release for team review
gh release create v0.1.5 --draft \
  --title "v0.1.5" \
  --generate-notes

# Review at: https://github.com/rolfedh/aditi/releases
# Edit and publish when ready
gh release edit v0.1.5 --draft=false
```

### Complete Release Checklist
1. [ ] Run pre-release checks (see Pre-Release Checklist above)
2. [ ] Update version in `pyproject.toml`
3. [ ] Update version in `src/aditi/__init__.py`
4. [ ] Update version in `tests/integration/test_cli_integration.py`
5. [ ] Verify versions match: `grep -n "0\.1\.[0-9]" pyproject.toml src/aditi/__init__.py tests/integration/test_cli_integration.py`
6. [ ] Run tests: `pytest --ignore=tests/test_claude_md_updater.py`
7. [ ] Clean and build package: `rm -rf dist/ && python -m build`
8. [ ] (Optional) Test on TestPyPI with clean venv
9. [ ] Upload to PyPI: `pipx run twine upload dist/*`
10. [ ] Commit and push version changes
11. [ ] Create and push git tag
12. [ ] Create GitHub release with `gh release create`
13. [ ] Verify PyPI installation: `pip install --upgrade aditi && aditi --version`

### Common Issues and Solutions

#### Version Mismatch
```
Error: Tests fail with version assertion error
Solution: Update version in tests/integration/test_cli_integration.py
Check: grep -n "version" tests/integration/test_cli_integration.py
```

#### Build Artifacts from Previous Versions
```
Error: Uploading wrong version to PyPI
Solution: Always clean ALL build directories:
rm -rf dist/ build/ *.egg-info src/*.egg-info
```

#### Missing PyPI Token
```
Error: Authentication failed
Solution: Configure ~/.pypirc or use environment variable:
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
```

#### Externally Managed Environment
```
Error: Cannot install twine due to externally-managed-environment
Solution: Use pipx instead of pip:
pipx run twine upload dist/*
```

#### Git Push Conflicts
```
Error: Updates were rejected because the tip of your current branch is behind
Solution: Pull with rebase before pushing:
git pull --rebase origin main
git push origin main
```

#### Broken Tests
```
Error: ModuleNotFoundError in tests
Solution: Exclude broken tests temporarily:
pytest --ignore=tests/test_claude_md_updater.py
TODO: Fix or remove the broken test file
```

### Future Release Automation Improvements

**Recommended Enhancements:**
1. **Version Sync Script**: Create a script to update all version references automatically
2. **Pre-release Validation**: GitHub Action to run all checks before release
3. **Release Script**: Automate the entire release process with proper error handling
4. **Post-release Tasks**: Auto-create next version branch, update CHANGELOG template

**Example Version Update Script** (`scripts/update-version.py`):
```python
#!/usr/bin/env python3
import re
import sys

def update_version(old_version, new_version):
    files = [
        ('pyproject.toml', f'version = "{old_version}"', f'version = "{new_version}"'),
        ('src/aditi/__init__.py', f'__version__ = "{old_version}"', f'__version__ = "{new_version}"'),
        ('tests/integration/test_cli_integration.py', f'aditi version {old_version}', f'aditi version {new_version}')
    ]
    
    for filepath, old_text, new_text in files:
        with open(filepath, 'r') as f:
            content = f.read()
        content = content.replace(old_text, new_text)
        with open(filepath, 'w') as f:
            f.write(content)
    
    print(f"Updated version from {old_version} to {new_version}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update-version.py OLD_VERSION NEW_VERSION")
        sys.exit(1)
    update_version(sys.argv[1], sys.argv[2])
```

## Testing Guidelines

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/aditi --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_rules.py

# Run tests matching pattern
pytest -k "test_content_type"

# Run with verbose output
pytest -v
```

### Testing Vale Container
```bash
# Test container availability
pytest tests/integration/test_vale_container.py

# Test with specific container runtime
ADITI_CONTAINER_RUNTIME=docker pytest tests/integration/

# Test container timeout handling
pytest tests/integration/test_vale_container.py::test_timeout
```

### Testing Rules
Each rule should have:
1. Unit tests for rule logic
2. Integration tests with sample .adoc files
3. Edge case handling tests
4. Performance tests for large files

Example test structure:
```python
def test_entity_reference_rule():
    # Test basic replacement
    assert rule.fix("Use ->") == "Use &#8594;"

    # Test multiple entities
    assert rule.fix("(R) and (TM)") == "&#174; and &#8482;"

    # Test edge cases
    assert rule.fix("") == ""
```

## Performance Considerations

### Processing Large Repositories
- **Batch processing**: Files are processed in batches of 100
- **Memory usage**: ~50MB base + 2MB per 1000 files
- **Container overhead**: ~200MB for Vale container
- **Typical processing times**:
  - Small repo (< 100 files): 1-2 minutes
  - Medium repo (100-1000 files): 5-10 minutes
  - Large repo (> 1000 files): 15-30 minutes

### Optimization Tips
1. Use `.vale.ini` BlockIgnore patterns to skip generated files
2. Process specific directories instead of entire repository
3. Run deterministic rules first for quick wins
4. Use `--parallel` flag for multi-core processing (future feature)

## Container Permissions and Best Practices

### Overview
When working with containerized tools like Vale, proper handling of file permissions and path resolution is critical. Two common issues can arise:

1. **SELinux Context Issues**: Container cannot access mounted volumes due to missing security contexts
2. **Path Resolution Issues**: Absolute paths on host don't resolve correctly inside container

### Best Practices for Container File Access

#### 1. Always Use SELinux Contexts on Volume Mounts
```python
# ❌ Incorrect - May fail with permission denied
"-v", f"{project_root}:/docs"

# ✅ Correct - Includes SELinux context
"-v", f"{project_root}:/docs:z"  # :z allows container to access files
```

#### 2. Set Proper User ID Mapping
```python
# Add user ID mapping to ensure consistent file permissions
"--user", f"{os.getuid()}:{os.getgid()}"
```

#### 3. Set HOME Environment for Tools That Need It
```python
# Some tools look for config in HOME directory
"--env", "HOME=/docs"
```

#### 4. Convert Absolute Paths to Relative for Container
```python
# Convert host absolute paths to container-relative paths
project_root = Path.cwd()
path_args = []
for p in file_paths:
    try:
        # Try to make path relative to project root
        rel_path = p.relative_to(project_root)
        path_args.append(str(rel_path))
    except ValueError:
        # If outside project root, use absolute
        path_args.append(str(p))
```

#### 5. Ensure Files Are Flushed Before Container Access
```python
# When creating temporary files for container use
temp_config.write_text(content)

# Ensure file is flushed to disk
with temp_config.open('r+b') as f:
    f.flush()
    os.fsync(f.fileno())
```

#### 6. Pre-create Required Directories
```python
# Create directories before container needs them
styles_dir = project_root / ".vale" / "styles"
styles_dir.mkdir(parents=True, exist_ok=True)
```

### Common Container Permission Errors and Solutions

#### SELinux Permission Denied
```
Error: Permission denied when container tries to access files
Solution: Add :z or :Z flag to volume mounts
- :z = shared content label (multiple containers can access)
- :Z = private unshared content label (single container access)
```

#### File Not Found in Container
```
Error: Container reports file doesn't exist (but it exists on host)
Solution: 
1. Use relative paths from mount point
2. Ensure file is synced to disk before container runs
3. Verify mount point includes the file's directory
```

#### Home Directory Access Issues
```
Error: Tool can't find config in home directory
Solution: Set HOME environment variable to mounted directory
--env "HOME=/docs"
```

## Error Handling Guidelines

### Common Error Scenarios

#### Container Errors
```
Error: Vale container not found
Solution: Run 'aditi init' to set up Vale
```

#### Permission Errors
```
Error: Permission denied accessing file
Solution: Check file permissions or run with appropriate access
```

#### Configuration Errors
```
Error: Invalid configuration in ~/aditi-data/config.json
Solution: Delete config file and re-run 'aditi journey'
```

### Error Reporting
- Errors are displayed with Rich formatting
- Stack traces shown only with `--verbose` flag
- Errors logged to `~/aditi-data/logs/aditi.log`
- Non-fatal errors allow processing to continue

### Recovery Procedures
1. **Session recovery**: Use `aditi journey`
2. **Config reset**: Delete `~/aditi-data/config.json`
3. **Vale reset**: Run `aditi init --force`
4. **Clean state**: Remove `~/aditi-data/` directory

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

## Memory Annotations
- Create vhs *.tape files in the @vhs-cassettes/ directory.