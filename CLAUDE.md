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

### Key Dependencies
- Container image: `docker.io/jdkato/vale:latest` (Official Vale linter)
- AsciiDocDITA styles: Downloaded automatically via Vale's package system
- Typer: Modern CLI framework with type hints
- Rich: Enhanced console output with progress bars
- Jekyll with Just the Docs theme for documentation
- GitHub Actions for automated workflows
- PyPI for distribution

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

## Common Commands

### Container Setup & Testing
- Test Vale integration: `python test_vale_integration.py`
- Test AsciiDocDITA rules: `python test_asciidocdita_rules.py`
- Initialize project with Vale: `aditi init` (when CLI is built)

### GitHub Pages Development
- Local development: `cd docs && bundle exec jekyll serve`
- The site uses Just the Docs theme with custom styling
- Images automatically get drop shadows via custom CSS
- Recent commits section auto-updates via GitHub Actions

### Python Development
Current implementation includes:
- Vale container integration with Podman/Docker support
- Typer CLI framework with Rich progress indicators
- AsciiDocDITA rule downloading via Vale's package system
- Comprehensive test scripts for validation
- Standard Python packaging tools for building and distribution

## Important Rules

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

## Implementation Status

### Completed (Phase 0)
- ✅ Vale container integration with Podman/Docker support
- ✅ ValeContainer class for container lifecycle management
- ✅ Automatic AsciiDocDITA style downloading
- ✅ Init command with Rich progress indicators
- ✅ Comprehensive test scripts
- ✅ Container setup documentation

### Completed (Phase 1) 
- ✅ Modern Python packaging with pyproject.toml
- ✅ Complete CLI structure with Typer framework
- ✅ Configuration management with Pydantic models
- ✅ Git guidance module for workflow assistance
- ✅ Comprehensive test suite (unit and integration)
- ✅ Package structure with proper exports
- ✅ Working CLI with placeholder commands

### Next Phases
- **Phase 2**: Rule Engine Implementation (parsing Vale output, applying fixes)
- **Phase 3**: CLI Experience (journey command, interactive workflows)  
- **Phase 4**: Reporting and Distribution

### Current Architecture
```
src/aditi/
├── __init__.py               # Package exports and metadata
├── cli.py                    # Main CLI with Typer
├── config.py                 # Configuration management with Pydantic
├── git.py                    # Git workflow guidance
├── vale_container.py         # Container runtime management
├── vale/
│   └── vale_config_template.ini
└── commands/
    ├── __init__.py
    └── init.py               # Initialization command
tests/
├── unit/                     # Unit tests for all modules
├── integration/              # CLI integration tests
└── conftest.py              # Shared test fixtures
```

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

### Automated Blog Post Creation
Use the helper script for consistent filenames and timestamps:
```bash
./scripts/new-blog-post.sh "Your Blog Post Title"
```

This automatically creates:
- Correct filename: `YYYY-MM-DD-HHMM-post-title.md`
- Proper timestamp in front matter with current timezone
- Template content based on `docs/_posts/YYYY-MM-DD-post-template.md`

### Manual Blog Post Creation
If creating manually:
1. **Filename Format**: `YYYY-MM-DD-HHMM-post-title.md`
   - Get timestamp: `date '+%Y-%m-%d-%H%M'`
   - Example: `2025-07-27-1423-implementing-new-feature.md`

2. **Front Matter Timestamp**: `YYYY-MM-DD HH:MM:SS -0400`
   - Get timestamp: `date '+%Y-%m-%d %H:%M:%S %z'`  
   - Example: `2025-07-27 14:23:45 -0400`

3. **Always use** `docs/_posts/YYYY-MM-DD-post-template.md` as template
4. **IMPORTANT**: Follow the link guidelines above when creating internal links in blog posts