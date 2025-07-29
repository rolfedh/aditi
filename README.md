# Aditi - AsciiDoc DITA Integration Tool

[![PyPI version](https://badge.fury.io/py/aditi.svg)](https://badge.fury.io/py/aditi)
[![Python versions](https://img.shields.io/pypi/pyversions/aditi.svg)](https://pypi.org/project/aditi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Aditi is a CLI tool designed to help technical writers prepare AsciiDoc files for migration to DITA. It leverages the Vale linter with AsciiDocDITA rules to identify and fix compatibility issues.

## Features

- **Automated Rule Checking**: Run Vale with AsciiDocDITA rules to identify DITA compatibility issues
- **Smart Fix Application**: Automatically fix deterministic issues or flag them for manual review
- **Git Workflow Integration**: Guided workflow for creating branches, commits, and pull requests
- **Progress Tracking**: Visual progress indicators and detailed reporting
- **Container Support**: Uses containerized Vale for consistent results across environments

## Installation

```bash
pip install aditi
```

### Prerequisites

- Python 3.11 or later
- Podman or Docker (for running Vale in a container)
- Git (for version control integration)

## Quick Start

1. Initialize Aditi in your project:
   ```bash
   aditi init
   ```

2. Check your AsciiDoc files:
   ```bash
   aditi check
   ```

3. Start the guided migration journey:
   ```bash
   aditi journey
   ```

4. Apply fixes interactively:
   ```bash
   aditi fix
   ```

## Documentation

For detailed documentation, visit [https://rolfedh.github.io/aditi/](https://rolfedh.github.io/aditi/)

## AsciiDocDITA Rules

Aditi implements all 26 AsciiDocDITA rules, including:

- **Error Level**: ContentType, EntityReference, ExampleBlock, etc.
- **Warning Level**: AdmonitionTitle, AuthorLine, BlockTitle, etc.
- **Suggestion Level**: AttributeReference, ConditionalCode, etc.

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