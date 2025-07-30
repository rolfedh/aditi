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
- **CLI Framework**: typer[all]>=0.9.0
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
4. If interrupted, run `aditi journey --resume` to continue
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
## Recent Development Focus (July 2025)

### Statistics
- Total commits: 174

### Latest Achievements
- ✅ Add automated gif to youtube mp4 conversion script and related demos.
- ✅ Add workflow to automate claude.md updates with project state.
- ✅ Implement robust claude.md updater with in-place updates.
- ✅ Complete phase 3 journey session management implementation.
- ✅ Add blockignores to vale configuration to prevent false positives for code and inline entities.

### Development Focus
- **Ci/Cd**: 68 commits
- **Features**: 19 commits
- **Bug Fixes**: 15 commits
- **Documentation**: 15 commits
- **Testing**: 11 commits

### Most Active Files
- `docs/_data/recent_commits.yml`: 67 changes
- `CLAUDE.md`: 50 changes
- `src/aditi/commands/journey.py`: 13 changes
<!-- /AUTO-GENERATED:RECENT -->

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
1. **Session recovery**: Use `aditi journey --resume`
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