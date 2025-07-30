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
- **Core Dependencies**: Typer CLI framework with type hints, Rich console output and progress indicators, Pydantic data validation and settings management, Interactive prompts and user input, Vale linter via Podman/Docker containers
- **Development Tools**: YAML parsing for configuration, Static type checking, Fast Python linter and formatter, Git pre-commit hooks
- **Testing Framework**: pytest testing framework, pytest coverage reporting, pytest mocking utilities
- **Documentation**: Jekyll with Just the Docs theme
- **CI/CD**: GitHub Actions for automated workflows
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

### Blog Post Management
- **Validate blog posts**: `python tests/test_blog_post_validation.py`
- **Run specific validation tests**: `python -m pytest tests/test_blog_post_validation.py -v`

### GitHub Pages Development
- **Local development**: `cd docs && bundle exec jekyll serve`
- **Validation URL**: `http://localhost:4000/aditi/`

### Python Development
- **Install dependencies**: `pip install -e ".[dev]"`
- **Run tests**: `pytest`
- **Type checking**: `mypy src/`
- **Code formatting**: `black src/ tests/`
- **Linting**: `ruff check src/ tests/`
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
<!-- /AUTO-GENERATED:COMPLETED -->

### Next Phases
- **Phase 3**: CLI Experience (journey command, interactive workflows)  
- **Phase 4**: Reporting and Distribution

<!-- AUTO-GENERATED:ARCHITECTURE -->
### Current Architecture
```
src/aditi/
│   ├── __init__.py  # Package initialization
│   ├── __main__.py
│   ├── cli.py  # Main CLI interface
│   ├── cli_prototype.py
│   ├── commands/
│   │   ├── __init__.py  # Package initialization
│   │   ├── check.py
│   │   ├── fix.py
│   │   ├── init.py
│   │   ├── journey.py
│       └── vale.py
│   ├── config.py  # Configuration management
│   ├── git.py
│   ├── processor.py
│   ├── py.typed
│   ├── rules/
│   │   ├── __init__.py  # Package initialization
│   │   ├── admonition_title.py
│   │   ├── attribute_reference.py
│   │   ├── author_line.py
│   │   ├── base.py
│   │   ├── block_title.py
│   │   ├── conditional_code.py
│   │   ├── content_type.py
│   │   ├── cross_reference.py
│   │   ├── discrete_heading.py
│   │   ├── entity_reference.py
│   │   ├── equation_formula.py
│   │   ├── example_block.py
│   │   ├── include_directive.py
│   │   ├── line_break.py
│   │   ├── link_attribute.py
│   │   ├── nested_section.py
│   │   ├── page_break.py
│   │   ├── registry.py
│   │   ├── related_links.py
│   │   ├── short_description.py
│   │   ├── sidebar_block.py
│   │   ├── table_footer.py
│   │   ├── tag_directive.py
│   │   ├── task_duplicate.py
│   │   ├── task_example.py
│   │   ├── task_section.py
│   │   ├── task_step.py
│   │   ├── task_title.py
│       └── thematic_break.py
│   ├── scanner.py
│   ├── vale/
│       └── vale_config_template.ini
│   ├── vale_container.py
    └── vale_parser.py
tests/
│   ├── README.md  # Documentation
│   ├── __init__.py  # Package initialization
│   ├── conftest.py  # Shared test fixtures
│   ├── integration/
│   ├── __init__.py  # Package initialization
│   ├── test_check_command.py  # Test module
    └── test_cli_integration.py  # Test module
│   ├── test_blog_post_validation.py  # Test module
    └── unit/
│   ├── __init__.py  # Package initialization
│   ├── test_config.py  # Test module
│   ├── test_fix_command.py  # Test module
│   ├── test_git.py  # Test module
│   ├── test_journey_command.py  # Test module
│   ├── test_journey_workflow.py  # Test module
│   ├── test_non_deterministic_rules.py  # Test module
│   ├── test_processor.py  # Test module
│   ├── test_rules.py  # Test module
│   ├── test_vale_backup.py  # Test module
    └── test_vale_parser.py  # Test module
docs/
│   ├── CLAUDE-MD-AUTOMATION.md  # Documentation
│   ├── Gemfile
│   ├── QUICKSTART.md  # Documentation
│   ├── Screenshot from 2025-07-29 09-49-16.png
│   ├── Screenshot from 2025-07-29 09-50-12.png
│   ├── Screenshot from 2025-07-29 09-51-01.png
│   ├── Screenshot from 2025-07-29 09-51-31.png
│   ├── Screenshot from 2025-07-29 09-52-11.png
│   ├── Screenshot from 2025-07-29 09-53-39.png
│   ├── _config.yml  # Jekyll configuration
│   ├── _data/
    └── recent_commits.yml
│   ├── _design/
│   ├── aditi-claude-code-implementation.md  # Documentation
│   ├── aditi-claude-code-todo-list.md  # Documentation
│   ├── aditi-plan.md  # Documentation
│   ├── container-setup-tasks.md  # Documentation
│   ├── phase-1-next-steps.md  # Documentation
│   ├── phase-2-completion-summary.md  # Documentation
│   ├── phase-2-mockup-revised.md  # Documentation
│   ├── phase-2-mockup.md  # Documentation
│   ├── phase-2-next-steps.md  # Documentation
    └── remaining-work-to-complete.txt
│   ├── _posts/
│   ├── 2025-07-27-0723-i-finally-speak-a-programming-language.md  # Documentation
│   ├── 2025-07-27-0832-setting-up-github-pages.md  # Documentation
│   ├── 2025-07-27-0845-minima-vs-just-the-docs.md  # Documentation
│   ├── 2025-07-27-0848-organizing-blog-assets-with-claude.md  # Documentation
│   ├── 2025-07-27-1811-implementing-phase-1-core-infrastructure.md  # Documentation
│   ├── 2025-07-27-1811-implementing-vale-asciidocdita-container-integration.md  # Documentation
│   ├── 2025-07-27-2035-removing-git-integration-from-aditi-cli-design.md  # Documentation
│   ├── 2025-07-28-2030-running-vale-asciidocdita-directly-from-command-line.md  # Documentation
│   ├── 2025-07-28-2111-complete-asciidocdita-rule-coverage-implemented.md  # Documentation
│   ├── 2025-07-29-0607-fixing-jekyll-front-matter-standardization.md  # Documentation
│   ├── 2025-07-29-0638-claude-md-hybrid-automation-system.md  # Documentation
│   ├── 2025-07-29-0816-introducing-aditi-asciidoc-to-dita-migration-made-easy.md  # Documentation
│   ├── 2025-07-29-0959-example-workflow.md  # Documentation
│   ├── 2025-07-29-2021-improved-comment-flags-with-dynamic-vale-data.md  # Documentation
│   ├── 2025-07-29-2104-fixing-comment-flag-insertion-bug.md  # Documentation
    └── post-template.md  # Blog post template
│   ├── _sass/
│   ├── custom/
│       └── custom.scss
    └── just-the-docs-default.scss
│   ├── about.md  # Documentation
│   ├── assets/
│   ├── css/
    └── images/
│       └── blog/
│   ├── container-setup.md  # Documentation
│   ├── design/
│   ├── design.md  # Documentation
│   ├── drafts/
    └── workflow-feedback.md  # Documentation
│   ├── examples/
│   ├── README.md  # Documentation
│   ├── clean-example.adoc
│   ├── comprehensive-example.adoc
    └── rule-examples/
│   ├── inbox/
│   ├── index.md  # Documentation
    └── publishing.md  # Documentation
.github/workflows/
│   ├── jekyll-gh-pages.yml  # GitHub Actions workflow
│   ├── update-claude-md.yml  # GitHub Actions workflow
│   ├── update-commits.yml  # GitHub Actions workflow
    └── validate-blog-posts.yml  # GitHub Actions workflow
scripts/
│   ├── README.md  # Documentation
│   ├── claude_md_updater.py
│   ├── install-git-hooks.sh
│   ├── manage-git-hooks.sh
│   ├── new-blog-post.sh
│   ├── publish-to-pypi.sh
│   ├── test-package-install.sh
    └── upload-to-pypi.sh
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
<!-- /AUTO-GENERATED:RECENT -->

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.