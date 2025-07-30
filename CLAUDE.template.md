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
### Key Dependencies
- **Container image**: `docker.io/jdkato/vale:latest` (Official Vale linter)
- **AsciiDocDITA styles**: Downloaded automatically via Vale's package system
- **Python CLI**: Typer framework with Rich progress indicators
- **Documentation**: Jekyll with Just the Docs theme
- **Testing**: pytest with PyYAML for front matter validation
- **CI/CD**: GitHub Actions for deployment and validation workflows
- **Quality Assurance**: Comprehensive blog post validation test suite
- **Distribution**: PyPI packaging with modern pyproject.toml
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

<!-- AUTO-GENERATED:COMMANDS -->
## Common Commands

### Container Setup & Testing
- Test Vale integration: `python test_vale_integration.py`
- Test AsciiDocDITA rules: `python test_asciidocdita_rules.py`
- Initialize project with Vale: `aditi init` (when CLI is built)

### Blog Post Management
- **Validate blog posts**: `python tests/test_blog_post_validation.py`
- **Run specific validation tests**: `python -m pytest tests/test_blog_post_validation.py -v`
- **Create new post**: Follow filename pattern `YYYY-MM-DD-HHMM-title.md`
- **Check front matter**: Ensure all required fields are present

### GitHub Pages Development
- **Local development**: `cd docs && bundle exec jekyll serve`
- **Validation URL**: `http://localhost:4000/aditi/`
- **Theme**: Just the Docs with custom styling and drop shadows
- **Auto-updates**: Recent commits section via GitHub Actions
- **Link testing**: Verify `/aditi/` prefix for internal links

### Python Development
- **Package management**: Modern pyproject.toml with development dependencies
- **CLI framework**: Typer with Rich progress indicators
- **Container integration**: Podman/Docker support for Vale
- **Test suite**: Unit, integration, and blog post validation tests
- **Quality assurance**: Blog post validation prevents Jekyll deployment failures
- **Dependencies**: PyYAML added for YAML parsing in tests
<!-- /AUTO-GENERATED:COMMANDS -->

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

<!-- AUTO-GENERATED:COMPLETED -->
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

### Completed (Phase 3)
- ✅ Journey session management with pause/resume functionality
- ✅ Session backup system with automatic rotation (keeps last 5)
- ✅ Journey command flags: --clear, --status, --dry-run
- ✅ Session validation with repository and directory checks
- ✅ Enhanced session tracking (current rule, progress, timestamps)
- ✅ Age warnings for sessions older than 7 days

### Completed (Documentation & Quality Assurance)
- ✅ Jekyll front matter standardization across all blog posts
- ✅ Blog post validation test suite with regression prevention
- ✅ GitHub Actions workflow for automated blog post validation
- ✅ Comprehensive documentation with test README
- ✅ Template file safety and exclusion management
- ✅ GitHub Pages deployment reliability improvements
<!-- /AUTO-GENERATED:COMPLETED -->

### Next Phases
- **Phase 4**: Reporting and Distribution
- **Phase 5**: Advanced Features (git integration, rule customization)

<!-- AUTO-GENERATED:ARCHITECTURE -->
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
├── test_blog_post_validation.py  # Jekyll front matter validation
├── README.md                 # Test documentation
└── conftest.py              # Shared test fixtures
docs/
├── _posts/                   # Blog posts with standardized front matter
├── _config.yml              # Jekyll config with proper exclusions
├── post-template.md          # Safe template file
└── assets/                   # Blog assets and images
.github/workflows/
├── jekyll-gh-pages.yml       # GitHub Pages deployment
├── update-commits.yml        # Recent commits automation
└── validate-blog-posts.yml   # Blog post validation CI
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
## Recent Development Focus ({{ current_month }} {{ current_year }})

### Latest Achievements
<!-- This section will be automatically updated based on recent commits and project analysis -->

### Current Focus Areas
<!-- This section will be automatically updated based on active development patterns -->

### Key Lessons Learned
<!-- This section will be automatically updated based on commit messages and project history -->
<!-- /AUTO-GENERATED:RECENT -->

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.