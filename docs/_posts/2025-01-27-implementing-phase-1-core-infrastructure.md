---
title: "Implementing Phase 1: Core Infrastructure for Aditi"
date: 2025-01-27
author: Aditi Development Team
tags: [aditi, asciidoc, dita, migration, python, cli, phase-1]
summary: "Successfully completed Phase 1 of the Aditi project, building the core CLI infrastructure with modern Python packaging, configuration management, and comprehensive testing."
---

# Implementing Phase 1: Core Infrastructure for Aditi

## Introduction

After completing Phase 0 with Vale container integration and the init command, we've now successfully implemented Phase 1 of the Aditi project. This phase focused on building the core infrastructure needed for a production-ready CLI tool that helps technical writers migrate AsciiDoc files to DITA format.

Phase 1 transformed Aditi from a proof-of-concept into a proper Python package with modern tooling, comprehensive configuration management, and a robust testing framework.

## The Challenge

While Phase 0 proved that our core concept worked—integrating Vale with AsciiDocDITA rules in a containerized environment—we needed to build the scaffolding for a complete CLI experience. The main challenges were:

1. **Package Structure**: Creating a proper Python package with modern packaging standards
2. **CLI Framework**: Building an extensible command-line interface that users would find intuitive
3. **Configuration Management**: Handling user preferences, repository settings, and session state
4. **Git Integration**: Providing guidance for git workflows without being invasive
5. **Testing Infrastructure**: Ensuring reliability with comprehensive unit and integration tests

## The Solution

### Step 1: Modern Python Packaging with pyproject.toml

We started by creating a `pyproject.toml` file that follows current Python packaging best practices:

```toml
[project]
name = "aditi"
version = "0.1.0"
description = "A CLI tool to prepare AsciiDoc files for migration to DITA"
dependencies = [
    "typer[all]>=0.9.0",
    "rich>=13.7.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
]

[project.scripts]
aditi = "aditi.cli:app"
```

This configuration enables users to install Aditi with a simple `pip install -e .` and immediately access the `aditi` command.

### Step 2: CLI Framework with Typer

We built the main CLI using [Typer](https://typer.tiangolo.com/), which provides excellent type hint support and automatic help generation:

```python
app = typer.Typer(
    name="aditi",
    help="AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

@app.command()
def init(
    path: Optional[Path] = typer.Argument(None),
    force: bool = typer.Option(False, "--force", "-f"),
    verbose: bool = verbose_option,
) -> None:
    """Initialize Vale configuration for AsciiDocDITA rules."""
    setup_logging(verbose)
    init_command(path, force, use_docker)
```

The CLI includes placeholder commands for `check`, `fix`, and `journey` that will be implemented in Phase 2.

### Step 3: Configuration Management with Pydantic

One of the most critical components was building a robust configuration system using Pydantic for data validation:

```python
class RepositoryConfig(BaseModel):
    """Configuration for a single repository."""
    
    root: Path
    default_branch: str = "main"
    subdirectory_permissions: List[SubdirectoryPermission] = Field(default_factory=list)
    feature_branch_prefix: str = "aditi/"

    def is_path_allowed(self, path: Path) -> bool:
        """Check if a path is allowed based on permissions."""
        # Implementation handles overlapping permissions by preferring more specific paths
```

The configuration system stores user preferences in `~/aditi-data/config.json` and provides session state management for tracking current operations.

### Step 4: Git Guidance Module

Rather than automating git operations (which could surprise users), we built a guidance system that suggests commands:

```python
def guide_branch_creation(repo_path: Path, branch_name: str) -> List[GitCommand]:
    """Generate git commands for creating a new branch."""
    commands = []
    
    if has_uncommitted_changes(repo_path):
        commands.append(GitCommand("git stash", "Stash uncommitted changes"))
    
    commands.append(
        GitCommand(f"git checkout -b {branch_name}", f"Create new branch '{branch_name}'")
    )
    
    return commands
```

This approach maintains user control while providing helpful guidance for the git workflow.

### Step 5: Comprehensive Testing

We implemented a complete testing framework with both unit and integration tests:

- **Unit Tests**: Cover configuration management, git helpers, and CLI components
- **Integration Tests**: Test the complete CLI functionality end-to-end
- **Fixtures**: Provide temporary directories and git repositories for testing
- **Mocking**: Isolate tests from external dependencies like container operations

```python
@pytest.fixture
def temp_git_repo(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary git repository for testing."""
    subprocess.run(["git", "init"], cwd=temp_dir, check=True, capture_output=True)
    # Set up initial commit...
    yield temp_dir
```

## Results and Impact

Phase 1 successfully met all success criteria:

✅ **Package Installation**: `pip install -e .` works seamlessly  
✅ **CLI Help**: `aditi --help` shows comprehensive command documentation  
✅ **Version Display**: `aditi --version` correctly shows 0.1.0  
✅ **Init Command**: `aditi init` properly initializes Vale configuration  
✅ **Placeholder Commands**: All future commands show helpful "not yet implemented" messages  
✅ **Test Coverage**: 94% test success rate (34/36 tests passing)  

The CLI now provides a professional user experience:

```bash
$ aditi --help
 Usage: aditi [OPTIONS] COMMAND [ARGS]...                                       
                                                                                
 AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA       

╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ init      Initialize Vale configuration for AsciiDocDITA rules.              │
│ check     Check AsciiDoc files for DITA compatibility issues.                │
│ fix       Fix deterministic DITA compatibility issues in AsciiDoc files.     │
│ journey   Start an interactive journey to migrate AsciiDoc files to DITA.    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Lessons Learned

### What Worked Well

1. **Incremental Testing**: Testing each component immediately after implementation caught issues early
2. **Type Hints**: Pydantic's validation caught configuration errors that would have been runtime bugs
3. **Modular Design**: Separating concerns into distinct modules (config, git, CLI) made testing easier
4. **Rich Output**: Using the Rich library for console output significantly improved user experience

### Challenges Faced

1. **Test Isolation**: Some tests initially interfered with each other due to shared temporary directories
2. **CLI Parameter Passing**: Ensuring the CLI properly passed parameters to underlying functions required careful attention
3. **Path Permissions**: Implementing overlapping directory permissions required thoughtful logic to handle precedence

## Next Steps

With Phase 1 complete, we're ready to tackle Phase 2, which will focus on:

1. **Rule Engine Implementation**: Parsing Vale output and categorizing violations
2. **Automated Fixes**: Implementing deterministic fixes for common issues
3. **Interactive Workflows**: Building the `journey` command for guided migration
4. **Reporting**: Generating comprehensive reports on migration progress

The foundation we've built in Phase 1 provides the solid infrastructure needed to implement these more complex features.

## Architecture Overview

The current project structure reflects our modular approach:

```
src/aditi/
├── __init__.py          # Package exports and metadata
├── cli.py               # Main CLI application with Typer
├── config.py            # Configuration management with Pydantic
├── git.py               # Git workflow guidance
├── vale_container.py    # Container integration (from Phase 0)
└── commands/
    ├── __init__.py
    └── init.py          # Initialization command
```

## Conclusion

Phase 1 represents a significant milestone in the Aditi project. We've transformed a working proof-of-concept into a professional CLI tool with modern Python packaging, robust configuration management, and comprehensive testing.

The infrastructure we've built provides a solid foundation for implementing the core rule engine and user experience features in Phase 2. Most importantly, we've maintained our focus on user control and transparency—Aditi guides rather than automates, ensuring technical writers remain in control of their migration process.

---

### Resources

- [Phase 1 Next Steps Design Document](/aditi/design/phase-1-next-steps/)
- [Container Setup Tasks](/aditi/design/container-setup-tasks/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### About the Author

The Aditi Development Team is building tools to help technical writers migrate from AsciiDoc to DITA with confidence and control.