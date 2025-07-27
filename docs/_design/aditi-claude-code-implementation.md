---
layout: page
title: "Aditi Implementation Plan for Claude Code"
permalink: /design/claude-code-implementation/
---

# Aditi Implementation Plan for Claude Code

## Overview

This document provides an optimized implementation plan for building Aditi using Claude Code in VS Code. It focuses on leveraging Claude Code's strengths for rapid, iterative development.

## Implementation Phases

### Phase 0: Project Setup & Foundation ✅ COMPLETED

**Goal**: Establish project structure and development environment

**Completed Tasks**:
1. ✅ Created initial Python project structure
2. ✅ Configured Typer as CLI framework with Rich for output
3. ✅ Set up Git repository with proper .gitignore
4. ✅ Implemented Vale container integration (`ValeContainer` class)
5. ✅ Created init command with progress indicators
6. ✅ Established test scripts for validation

**Key Deliverables**:
- `src/aditi/vale_container.py` - Complete Podman/Docker wrapper
- `src/aditi/commands/init.py` - User-friendly initialization
- `src/aditi/vale/vale_config_template.ini` - AsciiDocDITA configuration
- Working test scripts demonstrating Vale integration

**Current Directory Structure**:
```
aditi/
├── src/
│   └── aditi/
│       ├── vale_container.py   # ✅ Implemented
│       ├── vale/
│       │   └── vale_config_template.ini  # ✅ Implemented
│       └── commands/
│           ├── __init__.py     # ✅ Implemented
│           └── init.py         # ✅ Implemented
├── test_vale_integration.py    # ✅ Implemented
├── test_asciidocdita_rules.py  # ✅ Implemented
├── docs/
│   ├── container-setup.md      # ✅ Documentation
│   └── _design/
│       └── container-setup-tasks.md  # ✅ Implementation guide
├── CLAUDE.md                   # ✅ Updated
└── .gitignore                  # ✅ Configured

**Still Needed**:
├── src/aditi/
│   ├── __init__.py
│   ├── cli.py          # Main CLI entry point
│   ├── config.py       # Configuration management
│   ├── git.py          # Git operation guidance
│   └── rules/         # Rule implementations
├── pyproject.toml
├── Makefile
└── README.md
```

### Phase 1: Core Infrastructure ✅ COMPLETED

**Goal**: Build essential components for rule processing

**Completed Tasks**:
1. ✅ Created `pyproject.toml` with modern Python packaging
2. ✅ Implemented main CLI entry point (`cli.py`) with Typer
3. ✅ Built configuration manager with Pydantic models  
4. ✅ Created git guidance module for workflow assistance
5. ✅ Set up proper Python package structure with exports
6. ✅ Comprehensive test suite (34/36 tests passing)
7. ✅ Working CLI with all placeholder commands

**Implementation Results**:

**1. Project Setup** (pyproject.toml) ✅
   - ✅ Modern Python packaging with setuptools backend
   - ✅ Entry points configured for CLI commands (`aditi = "aditi.cli:app"`)
   - ✅ Development dependencies: pytest, mypy, ruff, black
   - ✅ Tool configurations for linting and testing

**2. Main CLI Module** (cli.py) ✅
   - ✅ Typer app with rich markup and help
   - ✅ All commands registered (init, check, fix, journey)
   - ✅ Rich logging configuration with verbose option
   - ✅ Global options and comprehensive help text

**3. Configuration Manager** (config.py) ✅
   - ✅ Pydantic models for type-safe configuration
   - ✅ JSON config file handling at `~/aditi-data/config.json`
   - ✅ Session state management with persistence
   - ✅ Subdirectory permissions with precedence logic

**4. Git Manager** (git.py) ✅
   - ✅ Git workflow guidance without automation
   - ✅ Branch name generation and command suggestions
   - ✅ Commit message formatting assistance
   - ✅ PR creation guidance for GitHub/GitLab CLI

**Testing Results**: 34/36 tests passing (94% success rate)
- ✅ Comprehensive unit tests for config and git modules
- ✅ Integration tests for CLI functionality
- ✅ Shared fixtures for temporary directories and git repos
- ✅ Proper mocking for external dependencies

### Phase 2: Rule Engine Implementation (6-8 hours)

**Goal**: Implement rule processing system with Vale integration

**Claude Code Tasks**:
1. **Base Rule Framework**
   ```python
   class Rule(ABC):
       @abstractmethod
       def detect(self, file_path: Path) -> List[Violation]

       @abstractmethod
       def fix(self, violation: Violation) -> Optional[Fix]

       @property
       @abstractmethod
       def fix_type(self) -> FixType  # FULLY_DETERMINISTIC, PARTIALLY_DETERMINISTIC, NON_DETERMINISTIC
   ```

2. **ContentType Rule**
   - Parse AsciiDoc attributes
   - Implement filename prefix detection
   - Handle deprecated attribute migration
   - Insert TBD placeholders

3. **EntityReference Rule**
   - Pattern matching for entities
   - Replacement mapping
   - Validation of fixes

4. **Violation Processing Pipeline**
   - Stage-based rule execution
   - Dependency resolution (ContentType first)
   - Progress tracking
   - Error recovery

### Phase 3: CLI Experience (4-5 hours)

**Goal**: Create interactive, user-friendly CLI

**Claude Code Tasks**:
1. **Journey Command**
   - Interactive setup wizard
   - Configuration validation
   - Progress indicators
   - Error recovery prompts

2. **Command Implementation**
   ```python
   @cli.command()
   def journey():
       """Start guided migration workflow"""
       # Guides user through setup
       # Prompts for git operations when needed

   @cli.command()
   @click.argument('rule')
   def check(rule):
       """Run specific rule check"""

   @cli.command()
   @click.argument('rule')
   def fix(rule):
       """Apply fixes for specific rule"""
       # After fixes, prompt user to:
       # - Review changes
       # - Create commits
       # - Push branches
   ```

3. **User Interaction**
   - Rich console output (using Rich library)
   - Progress bars for long operations
   - Confirmation prompts
   - Clear error messages

### Phase 4: Reporting & User Guidance (3-4 hours)

**Goal**: Generate reports and guide users through git workflows

**Claude Code Tasks**:
1. **Report Generator**
   - Markdown report formatting
   - Violation summaries
   - Fix statistics
   - Action items for users

2. **PR Creation Guidance**
   - Generate PR description templates
   - Provide GitLab/GitHub CLI commands
   - Include links to reports
   - Guide users through PR creation

3. **Batch Processing**
   - Multiple rule execution
   - Prompt user to commit after each batch
   - Guide rollback process if needed

## Claude Code Workflow Patterns

### Pattern 1: Test-Driven Development
```
1. Write test first
2. Implement minimal code to pass
3. Refactor with Claude Code's help
4. Repeat
```

### Pattern 2: Iterative Feature Development
```
1. Implement basic functionality
2. Test manually with sample files
3. Add error handling
4. Write automated tests
5. Refine based on testing
```

### Pattern 3: Integration Testing
```
1. Create fixture files
2. Run against real Vale container
3. Validate outputs
4. Mock for unit tests
```

## Development Guidelines for Claude Code

### Code Generation Preferences
1. Use type hints throughout
2. Follow Google Python style guide
3. Include docstrings for all public methods
4. Use dataclasses for data structures
5. Prefer composition over inheritance

### Testing Strategy
1. Write tests alongside implementation
2. Use pytest fixtures extensively
3. Mock external dependencies
4. Create integration tests for workflows
5. Use hypothesis for property-based testing

### Error Handling
1. Use custom exceptions for domain errors
2. Provide helpful error messages
3. Log debug information
4. Allow graceful degradation
5. Implement retry logic for transient failures

## Sample Implementation Requests for Claude Code

### Request 1: Podman Integration
```
"Create a Podman integration module that:
- Manages Vale container lifecycle
- Streams output in real-time
- Handles errors gracefully
- Cleans up resources
Include comprehensive tests."
```

### Request 2: ContentType Rule
```
"Implement the ContentType rule that:
- Detects missing/invalid content type attributes
- Checks deprecated attributes
- Analyzes filename prefixes
- Inserts appropriate fixes or TBD placeholders
Include unit tests with fixtures."
```

### Request 3: CLI Journey Command
```
"Create an interactive 'journey' command that:
- Guides users through initial setup
- Validates configuration
- Shows progress
- Handles errors gracefully
Use Click and Rich for the implementation."
```

## Testing Fixtures

### Directory Structure for Tests
```
tests/
├── fixtures/
│   ├── asciidoc/
│   │   ├── valid/
│   │   ├── invalid/
│   │   └── edge-cases/
│   ├── configs/
│   └── vale-output/
├── unit/
│   ├── test_rules.py
│   ├── test_podman.py
│   └── test_git.py
└── integration/
    ├── test_workflows.py
    └── test_cli.py
```

## Performance Considerations

1. **Parallel Processing**
   - Process multiple files concurrently
   - Use asyncio for I/O operations
   - Batch Podman commands

2. **Caching**
   - Cache Vale results
   - Store parsed AST for files
   - Reuse Podman containers

3. **Memory Management**
   - Stream large files
   - Process in chunks
   - Clean up temporary files

## Security Best Practices

1. **Input Validation**
   - Sanitize file paths
   - Validate configuration values
   - Check directory permissions

2. **Podman Security**
   - Run rootless containers by default
   - Use specific image versions
   - Mount only necessary directories

3. **Git Operations**
   - Never store credentials
   - Prompt users to use SSH agent
   - Validate branch names before suggesting

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .[dev]
      - run: pytest
      - run: mypy src
      - run: ruff check src
```

## Distribution

### PyPI Publishing
1. Use `build` for package creation
2. Test with TestPyPI first
3. Use GitHub Actions for CI/CD
4. Use semantic versioning

## Next Steps

1. Start with Phase 0 setup
2. Implement one rule end-to-end
3. Get user feedback early
4. Iterate based on real usage
5. Expand rule coverage

## Claude Code Efficiency Tips

1. **Batch Operations**: Ask Claude Code to implement multiple related features at once
2. **Test Templates**: Create test templates that Claude Code can expand
3. **Refactoring**: Use Claude Code to refactor after initial implementation
4. **Documentation**: Generate comprehensive docstrings and type hints
5. **Code Review**: Ask Claude Code to review and improve code quality

This plan is optimized for rapid development with Claude Code, emphasizing iterative progress and comprehensive testing.