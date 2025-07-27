# Container Setup for Aditi

This document explains how Aditi integrates with Vale using Podman/Docker containers.

## Overview

Aditi uses the official Vale Docker image (`jdkato/vale`) to run the Vale linter with AsciiDocDITA style rules. This approach ensures:

1. **Consistency**: All users run the same version of Vale
2. **Isolation**: No need to install Vale locally
3. **Simplicity**: Automatic setup with `aditi init`

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Aditi CLI     │────▶│ Podman/Docker    │────▶│  Vale Container │
│                 │     │    Runtime       │     │   (jdkato/vale) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                                                  │
         │                                                  │
         ▼                                                  ▼
┌─────────────────┐                              ┌─────────────────┐
│  Project Files  │                              │ AsciiDocDITA    │
│  (.vale.ini,    │◀─────────────────────────────│    Styles       │
│   *.adoc)       │                              └─────────────────┘
└─────────────────┘
```

## Implementation Details

### ValeContainer Class

The `ValeContainer` class in `src/aditi/vale_container.py` manages:

- Container runtime detection (prefers Podman over Docker)
- Image pulling and caching
- Volume mounting for project files
- Vale execution and output parsing

### Initialization Process

When users run `aditi init`:

1. **Runtime Check**: Detects Podman or Docker availability
2. **Image Pull**: Downloads `jdkato/vale:latest` if not present
3. **Config Creation**: Copies `.vale.ini` template to project
4. **Style Download**: Runs `vale sync` to fetch AsciiDocDITA rules

### File Structure

After initialization, the project will have:

```
project-root/
├── .vale.ini              # Vale configuration
├── .vale/
│   └── styles/
│       └── AsciiDocDITA/  # Downloaded style rules
└── *.adoc                 # Your AsciiDoc files
```

## Testing Container Setup

Run the test script to verify your container setup:

```bash
python test_vale_integration.py
```

This will:
1. Check for Podman/Docker availability
2. Pull the Vale image
3. Run Vale on a test file
4. Display the results

## Troubleshooting

### Neither Podman nor Docker found

Install Podman (recommended):
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install podman

# Fedora
sudo dnf install podman

# macOS
brew install podman
```

Or install Docker:
```bash
# Follow instructions at https://docs.docker.com/get-docker/
```

### Permission denied errors

For Podman (rootless by default):
- No special permissions needed

For Docker:
- Add your user to the docker group: `sudo usermod -aG docker $USER`
- Log out and back in

### Vale sync fails

This might happen if:
- Network connectivity issues
- GitHub rate limiting
- Firewall blocking container network access

Try:
1. Check internet connectivity
2. Wait a few minutes and retry
3. Manually download styles from https://github.com/jhradilek/asciidoctor-dita-vale

## Next Steps

After successful setup:

1. Run `aditi check` to validate your AsciiDoc files
2. Run `aditi fix` to apply automatic fixes
3. Run `aditi journey` for guided migration workflow