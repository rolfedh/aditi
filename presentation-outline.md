# Aditi: AsciiDoc to DITA Migration Tool
## Presentation Outline for Technical Writers

### 1. Introduction: Name and Purpose

• **Aditi** "AsciiDoc DITA Integration"

• **Purpose**: CLI tool to prepare AsciiDoc files for migration to DITA

• **Target Audience**: Technical writers working with AsciiDoc who need to migrate to DITA

• **Goal**: Automate detection and fixing of DITA compatibility issues

### 2. Key Features

• **Automated Rule Engine**: 27+ implemented rules for AsciiDoc-to-DITA compatibility

• **Three Fix Types**:
  - **Fully Deterministic**: Automatic fixes (e.g., character entity replacements)
  - **Partially Deterministic**: Fixes with placeholders (e.g., missing content types)
  - **Non-Deterministic**: Flagged with comments for manual review

• **Vale Integration**: Uses containerized Vale linter with AsciiDocDITA ruleset

• **Git Workflow Guidance**: Helps create branches, commits, and pull requests

• **Session Management**: Resume interrupted workflows seamlessly

• **Batch Processing**: Handle entire repositories or specific directories

### 3. Key Points About `aditi init`

• **First Step**: Must run before using other commands

• **Vale Setup**: Downloads and configures Vale linter with AsciiDocDITA styles

• **Container Management**: Sets up Podman/Docker integration automatically

• **Configuration Creation**: Creates `.vale.ini` in your project root

• **One-Time Setup**: Only needs to be run once per project

• **Verification**: Confirms Vale container is working correctly

• **Rich Progress**: Visual progress indicators show setup status

### 4. Key Points About `aditi journey`

• **Interactive Workflow**: Guided step-by-step process for DITA migration

• **Repository Configuration**:
  - Validates Git repository status
  - Configures allowed/blocked subdirectories
  - Sets up branch naming conventions

• **Rule Execution Process**:
  - Scans for AsciiDoc files automatically
  - Runs Vale linter with AsciiDocDITA rules
  - Processes violations by fix type (deterministic → non-deterministic)
  - Shows progress for each rule and file

• **Session Persistence**:
  - Saves progress automatically
  - Resume with `aditi journey --resume`
  - 7-day session expiration
  - Handles interruptions gracefully

• **User Control**: You review and approve all changes before commits

### 5. Demo Flow (Suggested)

1. **Show `aditi init`**: Quick setup demonstration

2. **Show `aditi journey`**: Walk through interactive workflow

3. **Show Results**: Before/after AsciiDoc files with DITA-ready changes


### 6. Benefits for Technical Writers

• **Reduces Manual Work**: Automates repetitive DITA compatibility fixes

• **Maintains Quality**: Consistent application of mod-docs standards

• **Provides Guidance**: Clear explanations for manual fixes needed

• **Preserves Workflow**: Integrates with existing Git-based processes

• **Enables Confidence**: Test and review changes before committing

• **Scales Efficiently**: Handle large documentation sets systematically

### 7. Getting Started

• **Prerequisites**: Python 3.11+, Git, Podman/Docker

• **Installation**: `pip install aditi` (when released)

• **Quick Start**:
  ```bash
  aditi init          # One-time setup
  aditi journey       # Start migration process
  ```

• **Documentation**: Available at project GitHub/GitLab repository

• **Support**: Issue tracking and community support available