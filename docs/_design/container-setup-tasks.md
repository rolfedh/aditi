---
layout: page
title: "Container Setup Implementation Guide"
permalink: /design/container-setup-tasks/
---

# Container Setup Implementation Guide

This document provides step-by-step instructions for implementing Vale container integration in Aditi.

## Goal

After installing the aditi package from PyPI, users should be able to run Vale with AsciiDocDITA styles through simple commands like `aditi init` and `aditi check`.

## Implementation Requirements

### 1. Container Runtime Integration

Create a `ValeContainer` class in `src/aditi/vale_container.py` that:

- **Detects available container runtime**: Check for Podman first (preferred for security), fall back to Docker
- **Uses fully qualified image name**: `docker.io/jdkato/vale:latest` (Podman requires registry prefix)
- **Manages container lifecycle**: Pull image, run containers, handle cleanup
- **Mounts project volumes**: Mount user's project directory to `/docs` in container
- **Parses JSON output**: Convert Vale's JSON output to Python dictionaries

### 2. Vale Configuration Management

Create Vale configuration template in `src/aditi/vale/vale_config_template.ini`:

```ini
StylesPath = .vale/styles
MinAlertLevel = warning

# Download AsciiDocDITA package from GitHub
Packages = https://github.com/jhradilek/asciidoctor-dita-vale/releases/latest/download/AsciiDocDITA.zip

[*.adoc]
BasedOnStyles = AsciiDocDITA
```

### 3. Initialization Command

Create `src/aditi/commands/init.py` with an init command that:

- **Checks prerequisites**: Verify Podman/Docker availability
- **Pulls Vale image**: Download `docker.io/jdkato/vale:latest`
- **Creates configuration**: Copy template to user's project as `.vale.ini`
- **Downloads styles**: Run `vale sync` in container to fetch AsciiDocDITA rules
- **Provides user feedback**: Use Rich progress bars and clear success messages

### 4. Key Implementation Details

**Container Command Pattern**:
```bash
podman run --rm -v /path/to/project:/docs -w /docs docker.io/jdkato/vale:latest [vale-args]
```

**Error Handling**:
- Check container runtime availability with `--version` flag
- Handle image pull failures gracefully
- Provide helpful error messages for common issues (permissions, network, etc.)

**Volume Mounting**:
- Mount project root (containing `.vale.ini`) to `/docs`
- Calculate relative paths from project root to target files
- Ensure Vale can access both config and content files

### 5. Testing Strategy

Create test scripts to verify:

**Basic Integration** (`test_vale_integration.py`):
- Container runtime detection
- Image pulling
- Basic Vale execution
- Output parsing

**AsciiDocDITA Rules** (`test_asciidocdita_rules.py`):
- Style package downloading via `vale sync`
- Rule execution on test files
- Violation detection and reporting

### 6. Directory Structure

After implementation:
```
src/aditi/
├── vale_container.py          # Main container wrapper
├── vale/
│   └── vale_config_template.ini
└── commands/
    ├── __init__.py
    └── init.py                # Initialization command

tests/
├── test_vale_integration.py
└── test_asciidocdita_rules.py
```

### 7. User Workflow

After implementation, users will:

1. **Install**: `pip install aditi`
2. **Initialize**: `aditi init` (downloads Vale, creates config, fetches AsciiDocDITA styles)
3. **Use**: `aditi check file.adoc` (runs Vale with AsciiDocDITA rules)

### 8. Dependencies

Required Python packages:
- `typer` - CLI framework
- `rich` - Progress bars and formatted output
- Standard library: `subprocess`, `json`, `pathlib`

### 9. Error Recovery

Handle common failure scenarios:
- **No container runtime**: Clear error message with installation instructions
- **Network issues**: Retry logic for image pulls and style downloads
- **Permission errors**: Guide users to rootless Podman or Docker group setup
- **Missing config**: Prompt user to run `aditi init`

## Implementation Notes

- Use the official Vale Docker image rather than custom containers
- Leverage Vale's built-in package system for AsciiDocDITA styles
- Prefer Podman for security (rootless by default)
- Provide comprehensive error messages and troubleshooting guidance
- Test thoroughly with both Podman and Docker

This approach provides a clean, maintainable solution that automatically handles Vale setup and AsciiDocDITA rule integration for end users.