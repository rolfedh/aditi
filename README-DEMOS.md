# Aditi VHS Demo Tapes

This directory contains VHS tape files for demonstrating Aditi (AsciiDoc DITA Toolkit) commands and features.

## Prerequisites

Install VHS to generate the demo GIFs:
```bash
# Using Go
go install github.com/charmbracelet/vhs@latest

# Using Homebrew (macOS/Linux)
brew install vhs

# Using package managers
# See: https://github.com/charmbracelet/vhs#installation
```

## Demo Tapes

1. **demo-01-getting-started.tape** - Getting Started - Essential First Steps
   - Navigate to repository
   - Check version and help
   - Initialize Vale configuration
   - Essential workflow for new repositories

2. **demo-02-interactive-journey.tape** - Interactive Journey - Guided DITA Migration Workflow
   - Start interactive journey
   - Accept default configuration options
   - Process ExampleBlock rule fixes
   - Demonstration of guided workflow

3. **demo-03-check-command.tape** - Check Command - Analyze DITA Compatibility Issues
   - Run compatibility analysis
   - View violation reports
   - Understand issue categorization

4. **demo-04-fix-command.tape** - Fix Command - Automatically Repair Deterministic Issues
   - Apply automatic fixes for specific rules
   - See before/after comparisons
   - Handle deterministic corrections

5. **demo-05-vale-command.tape** - Vale Command - Direct Access to Raw Vale Output
   - Access unfiltered Vale linter results
   - Debug and analyze detailed rule violations
   - Raw output for advanced users

6. **demo-06-completion-command.tape** - Completion Command - Shell Autocompletion Setup
   - Install shell completion
   - Enable tab-completion for commands
   - Improve command-line productivity

## Generating GIFs

Run VHS on individual tape files:
```bash
vhs demo-01-getting-started.tape
vhs demo-02-interactive-journey.tape
# ... etc
```

Or generate all demos:
```bash
for tape in demo-*.tape; do vhs "$tape"; done
```

## Usage Notes

- All demos assume you're starting from the project root directory
- The test-repo/ directory contains sample AsciiDoc files for demonstration
- Demos use realistic timing and pauses for natural viewing experience
- Each demo focuses on specific user goals and workflows