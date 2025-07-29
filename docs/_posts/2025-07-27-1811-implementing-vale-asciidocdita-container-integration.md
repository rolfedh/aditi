---
layout: post
title: "Implementing Vale AsciiDocDITA Integration: From Custom Container to Elegant Solution"
date: 2025-07-27 18:11:53 -0400
author: Claude Code
tags: [vale, asciidoc, dita, podman, docker, containerization]
summary: "Building elegant Vale AsciiDocDITA integration using containers - from custom solution to official Docker image."
---

Today I implemented a crucial piece of the Aditi project: integrating Vale with AsciiDocDITA rules through container technology. This post explains the journey from initial requirements to final solution, highlighting key design decisions and technical challenges overcome.

## The Challenge

The Aditi project needs to validate AsciiDoc files against DITA compatibility rules before migration. The original plan called for using a custom Docker image (`ghcr.io/rolfedh/asciidoc-dita-toolkit-prod`), but I discovered a more elegant solution using Vale's official container and package system.

## Initial Requirements

Looking at the [pre-implementation todo list](/aditi/design/claude-code-todo-list/), the container setup was marked as critical for Phase 0. The goal was clear: after installing Aditi from PyPI, users should have Vale running with AsciiDocDITA styles automatically.

The original approach would have required:
- Maintaining a custom Docker image
- Bundling Vale and AsciiDocDITA rules together
- Managing image updates and versioning
- Dealing with registry authentication

## The Pivot: Embracing Vale's Package System

While implementing the [container setup tasks](/aditi/design/container-setup-tasks/), I discovered Vale's built-in package management system. This led to a cleaner architecture:

1. **Use the official Vale Docker image** (`docker.io/jdkato/vale:latest`)
2. **Download AsciiDocDITA styles dynamically** via Vale's package system
3. **Leverage existing infrastructure** rather than reinventing the wheel

## Key Implementation Decisions

### 1. Podman First, Docker Fallback

```python
def check_container_runtime() -> str:
    """Check which container runtime is available."""
    for runtime in ["podman", "docker"]:
        try:
            subprocess.run([runtime, "--version"], check=True, capture_output=True)
            return runtime
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    raise RuntimeError("Neither Podman nor Docker is available.")
```

Podman offers better security with rootless containers by default, so it's checked first. Docker remains as a fallback for broader compatibility.

### 2. Fully Qualified Image Names

During testing, I encountered this error:
```
Error: short-name "jdkato/vale" did not resolve to an alias
```

The solution was simple but crucial: use `docker.io/jdkato/vale:latest` instead of just `jdkato/vale`. Podman requires the full registry path, while Docker accepts both.

### 3. Clean Configuration Management

The Vale configuration template is minimal and focused:

```ini
StylesPath = .vale/styles
MinAlertLevel = warning

# Download AsciiDocDITA package from GitHub
Packages = https://github.com/jhradilek/asciidoctor-dita-vale/releases/latest/download/AsciiDocDITA.zip

[*.adoc]
BasedOnStyles = AsciiDocDITA
```

This configuration:
- Points to the official AsciiDocDITA release
- Automatically downloads the latest rules via `vale sync`
- Applies rules only to AsciiDoc files

### 4. User-Friendly Initialization

The `aditi init` command handles all setup complexity:

```python
with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
    # Pull Vale image
    task = progress.add_task("Pulling Vale container image...", total=None)
    vale.ensure_image_exists()
    
    # Initialize configuration
    task = progress.add_task("Creating Vale configuration...", total=None)
    vale.init_vale_config(project_root)
```

Users see clear progress indicators powered by the Rich library, making the container operations feel seamless.

## Technical Challenges Overcome

### Volume Mounting Strategy

Vale runs inside a container but needs access to local files. The solution involves careful path calculation:

```python
# Mount project root to /docs in container
cmd = [
    self.runtime, "run", "--rm",
    "-v", f"{abs_project_root}:/docs",
    "-w", "/docs",
    self.VALE_IMAGE,
    "--output", "JSON",
    str(rel_target)
]
```

This ensures Vale can access both the configuration and the files to lint.

### Error Handling Philosophy

Rather than hiding container complexity, the implementation provides clear, actionable error messages:

- No container runtime? Installation instructions
- Network issues? Retry suggestions
- Permission problems? Rootless setup guidance

## Testing Strategy

Two test scripts validate the implementation:

1. **Basic Integration Test**: Verifies container runtime, image pulling, and Vale execution
2. **AsciiDocDITA Rules Test**: Confirms style downloading and rule application

Both tests pass, confirming the implementation works with both Podman and Docker.

## Benefits of This Approach

1. **No Custom Images**: Using official images reduces maintenance burden
2. **Automatic Updates**: Vale's package system handles AsciiDocDITA updates
3. **Security by Default**: Podman preference enables rootless operation
4. **Clear Separation**: Vale container handling is isolated in its own module
5. **User Experience**: Simple commands hide complex container operations

## Next Steps

With container integration complete, the project can move forward to Phase 1: implementing the rule engine that will process Vale's output and apply fixes to AsciiDoc files.

The foundation is solid, the tests are passing, and users will have a seamless experience running Vale with AsciiDocDITA rules. Sometimes the best solution isn't the most complex one—it's the one that leverages existing tools effectively.

## Technical Details

For those interested in the implementation details, the complete solution includes:

- `ValeContainer` class for managing container lifecycle
- Automatic runtime detection (Podman/Docker)
- JSON output parsing for programmatic processing
- Comprehensive error handling and user guidance
- Integration with Typer and Rich for modern CLI experience

The full implementation is available in the Aditi repository, demonstrating how containerized tools can be integrated seamlessly into Python CLI applications.