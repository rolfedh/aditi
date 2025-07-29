# Aditi - AsciiDoc DITA Integration Tool

[![PyPI version](https://badge.fury.io/py/aditi.svg)](https://badge.fury.io/py/aditi)
[![Python versions](https://img.shields.io/pypi/pyversions/aditi.svg)](https://pypi.org/project/aditi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Aditi** (Sanskrit: आदिति, "boundless") - A CLI tool that prepares AsciiDoc files for seamless migration to DITA.

Aditi helps technical writers identify and fix compatibility issues when migrating from AsciiDoc to DITA. It uses the Vale linter with comprehensive AsciiDocDITA rules to categorize issues as automatically fixable, partially fixable, or requiring manual review.

## ✨ Key Features

- 🔍 **Comprehensive Analysis**: Detects all 27 AsciiDocDITA compatibility issues
- 🔧 **Smart Auto-Fixing**: Automatically resolves deterministic issues (entities, content types)
- 📊 **Intelligent Categorization**: Sorts issues by fix complexity and priority  
- 🚀 **Performance Optimized**: Parallel processing with container resource limits
- 🛡️ **Production Ready**: Robust error handling and graceful interruption support
- 📋 **Clear Reporting**: Visual progress indicators and actionable results

## 🚀 Installation

### Quick Install

```bash
pip install --upgrade aditi
```

### System Requirements

- **Python**: 3.11 or later
- **Container Runtime**: Podman (preferred) or Docker
- **Platform**: Linux, macOS, Windows (with WSL2)

### Installation Verification

```bash
aditi --help
```

### Container Setup

Aditi will automatically pull the Vale container image on first use. To pre-download:

```bash
# For Podman (default)
podman pull docker.io/jdkato/vale:latest

# For Docker  
docker pull docker.io/jdkato/vale:latest
```

## 🏁 Quick Start (5 minutes)

### 1. Initialize Your Project

```bash
cd /path/to/your/asciidoc-project
aditi init
```

**What this does:**
- Downloads Vale container image
- Installs AsciiDocDITA rules  
- Creates `.vale.ini` configuration
- Sets up project for analysis

### 2. Configure Access Paths

```bash
aditi journey
```

**Interactive setup:**
- Select directories containing AsciiDoc files
- Configure repository permissions
- Set working preferences

### 3. Analyze Your Files

```bash
# Check all configured files
aditi check

# Check specific files/directories  
aditi check docs/ user-guide.adoc

# Focus on specific issues
aditi check --rule ContentType --verbose
```

### 4. Apply Automatic Fixes

```bash  
# Preview changes (recommended first step)
aditi fix --dry-run

# Apply fixes interactively
aditi fix

# Apply fixes automatically (CI/CD)
aditi fix --non-interactive
```

## 📚 Complete Example

```bash
# Start fresh project
mkdir my-dita-migration && cd my-dita-migration

# Install and initialize
pip install --upgrade aditi
aditi init

# Set up paths (follow prompts)
aditi journey  

# Analyze current state
aditi check --verbose

# Fix obvious problems first
aditi fix --rule EntityReference  # Fix character entities
aditi fix --rule ContentType      # Add missing content types

# Review remaining issues  
aditi check

# Apply additional fixes as needed
aditi fix --dry-run               # Preview all remaining fixes
aditi fix                         # Apply interactively
```

## 📖 Documentation

| Resource | Description |
|----------|-------------|
| **[Quick Start Guide](docs/QUICKSTART.md)** | Get up and running in under 5 minutes |
| **[Full Documentation](https://rolfedh.github.io/aditi/)** | Complete reference with examples |
| **[Example Files](docs/examples/)** | Sample AsciiDoc files demonstrating each rule |
| **[Troubleshooting](docs/QUICKSTART.md#troubleshooting)** | Common issues and solutions |

## 🎯 Rule Coverage

Aditi implements all **27 AsciiDocDITA rules** with intelligent categorization:

### 🔴 Fully Deterministic (Auto-fixable)
- **EntityReference**: Replaces unsupported character entities

### 🟡 Partially Deterministic (Partial auto-fix)  
- **ContentType**: Adds missing content type attributes with placeholders

### 🔵 Non-Deterministic (Manual review required)
- **Structure Rules**: NestedSection, TaskSection, ExampleBlock
- **Content Rules**: AdmonitionTitle, AuthorLine, BlockTitle  
- **Format Rules**: DiscreteHeading, ThematicBreak, PageBreak
- **Reference Rules**: CrossReference, LinkAttribute, IncludeDirective
- **And 18 more** covering all DITA compatibility concerns

## ⚠️ Known Limitations

- **Interactive Journey**: The `aditi journey` command requires interactive input
- **Container Dependency**: Requires Podman or Docker for Vale execution  
- **Path Restrictions**: Files must be within configured allowed directories
- **Large Files**: Processing very large files (>10MB) may be slower
- **Windows**: Best experience on Linux/macOS; Windows requires WSL2

## 🔮 Future Enhancements

- Non-interactive mode for `journey` command (CI/CD support)
- Direct DITA output generation
- Custom rule configuration
- Integration with popular documentation platforms
- Batch processing optimizations for large repositories

## Development

To contribute to Aditi:

```bash
# Clone the repository
git clone https://github.com/rolfedh/aditi.git
cd aditi

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on the [Vale](https://vale.sh/) linter
- Uses [AsciiDocDITA](https://github.com/jhradilek/asciidoctor-dita-vale) rules by Jaromir Hradilek
- Powered by [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)