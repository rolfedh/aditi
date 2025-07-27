# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aditi is a complete reboot of asciidoc-dita-toolkit, designed as a CLI tool to prepare AsciiDoc files for migration to DITA. The name is short for "asciidoc dita integration."

## Development Environment

### Prerequisites
- Python 3.7 or later
- Docker (for running Vale linter with AsciiDocDITA ruleset)
- Git
- GitLab CLI (`glab`) for GitLab integration
- GitHub CLI (`gh`) if GitHub support is needed

### Key Dependencies
- Docker image: `ghcr.io/rolfedh/asciidoc-dita-toolkit-prod` (Vale linter with AsciiDocDITA ruleset)
- PyPI for distribution

## Architecture

Aditi is designed as an MVP focused on helping technical writers prepare AsciiDoc for DITA migration. The tool:
1. Runs Vale linter with AsciiDocDITA rules against *.adoc files
2. Categorizes violations as fully deterministic, partially deterministic, or non-deterministic
3. Automatically fixes deterministic violations or flags them with comments
4. Manages git workflow for creating branches, commits, and pull requests

## Key Concepts

### Violation Fix Types
1. **Fully deterministic**: Can be fixed automatically (e.g., EntityReference rule)
2. **Partially deterministic**: Can be partially fixed with placeholders (e.g., ContentType rule)
3. **Non-deterministic**: Must be fixed manually by the user

### Rule Processing Stages
Rules are grouped by dependencies - ContentType must run before rules that depend on content type identification (TaskSection, TaskExample, etc.).

## Common Commands

Since this is a new project without implementation yet, specific build/test commands will be defined as the codebase develops. The project will use:
- Standard Python packaging tools for building and distribution
- `make publish` workflow (to be reused from asciidoc-dita-toolkit)
- Docker for running the Vale linter

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

Aditi automates:
1. Creating feature branches
2. Running rules and making fixes
3. Committing changes with descriptive messages
4. Creating pull requests
5. Prompting user review and merge

## Configuration

User configuration stored in `~/aditi-data/config.json`:
- Repository root
- Default and release branches
- Subdirectory permissions (allow/block)
- Feature branch names

## Role and Capabilities

- You are a world class software architect and python developer.