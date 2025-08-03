---
layout: page
title: "Local Configuration Management"
permalink: /design/local-configuration-management/
---

# Local Configuration Management Design

## Problem Statement

Aditi was using a global configuration file (`~/aditi-data/config.json`) that accumulated settings from all repositories ever initialized. This caused issues when working with multiple repositories:

1. Configuration from one repository would affect others
2. The `current_repository` setting would point to the last initialized repo, not the current working directory
3. Path settings from different repositories would conflict
4. No isolation between different projects

## Solution: Repository-Local Configuration

### Overview

Implement a repository-local configuration system similar to Git's `.git/` directory approach. Each repository gets its own `.aditi/` directory containing:

```
repository/
├── .aditi/
│   ├── config.json      # Repository-specific configuration
│   └── session.json     # Session state (gitignored)
├── .vale.ini           # Vale configuration
└── .vale/              # Vale styles
```

### Benefits

1. **Isolation**: Each repository has its own configuration
2. **Portability**: Configuration travels with the code
3. **Team-friendly**: Multiple developers can have different local settings
4. **Clean separation**: No mixing of different project configurations
5. **Standard practice**: Follows the pattern of `.git/`, `.vscode/`, etc.

### Implementation Details

#### LocalConfigManager Class

A new `LocalConfigManager` class extends `ConfigManager` with:

- **Repository detection**: Searches for `.aditi/` directory in current or parent directories
- **Automatic initialization**: Creates `.aditi/` directory when needed
- **Migration support**: Migrates settings from global config when appropriate
- **Gitignore management**: Automatically adds session files to `.gitignore`

#### Configuration Hierarchy

1. **Local config** (`.aditi/config.json`): Repository-specific settings
   - Repository root path
   - Branch configuration
   - Allowed/excluded paths
   - Session state

2. **Global config** (`~/aditi-data/`): User preferences only
   - Vale styles cache
   - Tool preferences
   - Legacy repository registry (for migration)

#### Migration Path (Implemented: Option 2)

Migration happens explicitly during `aditi init`:

1. **Detection**: When `aditi init` runs, it checks if the current repository exists in global config
2. **User Prompt**: If found, shows existing configuration and asks: "Would you like to migrate this configuration to local?"
3. **Migration**: If accepted, copies repository settings and relevant paths to local config
4. **Fresh Start**: If declined, creates a fresh local configuration

Commands (`check`, `journey`) will:
- Check for local config first
- If missing, inform user if migration is available
- Direct user to run `aditi init` to set up or migrate

### Command Updates

#### `aditi init`

- Creates `.aditi/` directory alongside `.vale.ini`
- Initializes local configuration
- Updates `.gitignore` to exclude session files

#### `aditi check` and `aditi journey`

- Use `LocalConfigManager` instead of `ConfigManager`
- Check for local config before running
- Prompt to run `aditi init` if no local config exists

### File Structure

```python
src/aditi/
├── config.py               # Original ConfigManager (unchanged)
├── local_config.py         # New LocalConfigManager
└── commands/
    ├── init.py            # Updated to create local config
    ├── check.py           # Updated to use LocalConfigManager
    └── journey.py         # Updated to use LocalConfigManager
```

### Backward Compatibility

- Global config files remain supported
- Automatic migration when detected
- No breaking changes for existing users

### Future Enhancements

1. **Config sync**: Optional sync between local and global preferences
2. **Team settings**: Shared configuration in `.aditi/team.json`
3. **Environment overrides**: Support for `.aditi/local.json` (gitignored)
4. **Config validation**: Schema validation for configuration files

## Implementation Status

✅ Completed:
- Created `LocalConfigManager` class
- Updated `init`, `check`, and `journey` commands
- Added automatic `.gitignore` updates
- Implemented migration from global config
- Added comprehensive unit tests

## Usage

```bash
# Initialize repository with local config
aditi init

# Check files (uses local config)
aditi check

# Start journey (uses local config)
aditi journey
```

The system automatically creates and manages `.aditi/` directories, providing clean isolation between different repositories while maintaining backward compatibility with existing global configurations.