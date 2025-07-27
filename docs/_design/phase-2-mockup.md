---
layout: page
title: "Aditi CLI User Interaction Mockup"
permalink: /design/phase-2-mockup/
---

# Aditi CLI User Interaction Mockup

This document demonstrates typical user interactions with the Aditi CLI, showing the complete workflow from initial setup through successful migration of AsciiDoc files to DITA-compatible format.

## Scenario: Technical Writer Migrating Documentation

Sarah is a technical writer with a repository containing 50+ AsciiDoc files that need to be migrated to DITA format. She's heard about Aditi and wants to use it to prepare her files.

## 1. Initial Setup

### First Run - Discovery

```bash
$ aditi --help

 Usage: aditi [OPTIONS] COMMAND [ARGS]...                                       
                                                                                
 AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA       

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --version             -V        Show version and exit                        │
│ --verbose             -v        Enable verbose output                        │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ init      Initialize Vale configuration for AsciiDocDITA rules.              │
│ check     Check AsciiDoc files for DITA compatibility issues.                │
│ fix       Fix deterministic DITA compatibility issues in AsciiDoc files.     │
│ journey   Start an interactive journey to migrate AsciiDoc files to DITA.    │
╰──────────────────────────────────────────────────────────────────────────────╯

$ aditi --version
aditi version 0.1.0
```

### Initialize Vale Configuration

```bash
$ aditi init

[17:21:26] INFO     Created Vale configuration at .vale.ini
           INFO     Downloading AsciiDocDITA styles...
[17:21:27] INFO     Successfully downloaded AsciiDocDITA styles

⠼ Pulling Vale container image...
⠼ Creating Vale configuration... 

✓ Aditi initialized successfully!
Vale configuration created at: .vale.ini
AsciiDocDITA styles downloaded to: .vale/styles/

Next steps:
1. Run 'aditi check' to validate your AsciiDoc files
2. Run 'aditi journey' for a guided migration workflow
```

## 2. First Check - Discovery Phase

### Running Check on Documentation

```bash
$ aditi check docs/

🔍 Analyzing AsciiDoc files in docs/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:12

📊 Analysis Results for docs/

🔴 EntityReference (23 violations)
  docs/concepts/overview.adoc:15    Replace '&nbsp;' with '{nbsp}'
  docs/concepts/overview.adoc:23    Replace '&mdash;' with '{mdash}'
  docs/concepts/overview.adoc:45    Replace '&copy;' with '{copy}'
  docs/procedures/install.adoc:12   Replace '&trade;' with '{trade}'
  ... and 19 more

🟡 ContentType (8 violations)  
  docs/procedures/install.adoc:1    Missing content type attribute (detected: PROCEDURE)
  docs/concepts/overview.adoc:1     Missing content type attribute (detected: CONCEPT)
  docs/reference/api.adoc:1         Missing content type attribute (detected: REFERENCE)
  ... and 5 more

🔵 TaskSection (3 violations)
  docs/procedures/install.adoc:34   Task sections require numbered lists
  docs/procedures/config.adoc:22    Task sections require numbered lists
  docs/procedures/deploy.adoc:45    Task sections require numbered lists

📈 Summary:
  Files processed: 12
  Total violations: 34
  Fully deterministic fixes: 23 (can be auto-fixed)
  Partially deterministic fixes: 8 (require review)
  Manual intervention required: 3

✨ Good news! 68% of issues can be fixed automatically.

Next steps:
  Run 'aditi fix' to apply automatic fixes
  Run 'aditi journey' for guided workflow with git integration
```

## 3. Guided Journey - Interactive Workflow

### Starting the Journey

```bash
$ aditi journey

🚀 Welcome to Aditi's guided migration journey!

This interactive workflow will help you:
  ✓ Configure Aditi for your repository
  ✓ Create a feature branch for changes
  ✓ Apply fixes systematically
  ✓ Review and commit changes
  ✓ Create a pull request

📁 Current directory: /home/sarah/product-docs
🔍 Git repository detected

? Is this the repository you want to work with? (Y/n) Y

? What's your default branch? (main) main

? Would you like to configure any subdirectory permissions? (y/N) y

? Which directories should Aditi process? (Space to select, Enter to confirm)
  ❯◉ docs/
   ○ internal/  
   ◯ archived/
   ◉ modules/

✓ Configuration saved to ~/aditi-data/config.json

? What would you like to name your feature branch? 
  Suggested: aditi/2025-07-27-asciidoc-dita-migration
  > aditi/dita-migration-phase1

Creating feature branch...

📋 Please run the following git commands:

[bold blue]Git Command: Create and switch to new branch[/bold blue]
╭────────────────────────────────────────────────────────────╮
│ git checkout -b aditi/dita-migration-phase1                │
╰────────────────────────────────────────────────────────────╯

? Have you created the branch? (Y/n) Y

✓ Great! Let's start migrating your files.
```

## 4. Applying Fixes - Rule by Rule

### EntityReference Rule (Fully Deterministic)

```bash
🔧 Processing EntityReference violations (23 found)

These violations can be fixed automatically:
  • &nbsp; → {nbsp}
  • &mdash; → {mdash}
  • &copy; → {copy}
  • &trade; → {trade}

? Apply all EntityReference fixes? (Y/n) Y

⠏ Applying fixes...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:03

✓ Successfully applied 23 EntityReference fixes

📝 Files modified:
  • docs/concepts/overview.adoc (3 fixes)
  • docs/procedures/install.adoc (1 fix)
  • docs/reference/api.adoc (5 fixes)
  • ... and 6 more files

? Review the changes? (Y/n) Y

[Shows diff output with color highlighting]

? Commit these changes? (Y/n) Y

📋 Suggested commit message:
╭────────────────────────────────────────────────────────────╮
│ Fix EntityReference issues in AsciiDoc files               │
│                                                            │
│ Fixed the following AsciiDocDITA rules:                    │
│   - EntityReference                                        │
│                                                            │
│ Files updated:                                             │
│   - docs/concepts/overview.adoc                            │
│   - docs/procedures/install.adoc                           │
│   - docs/reference/api.adoc                                │
│   - ... and 6 more files                                  │
╰────────────────────────────────────────────────────────────╯

? Use this commit message? (Y/n) Y

📋 Please run the following git commands:

[bold blue]Git Command: Stage changes[/bold blue]
╭────────────────────────────────────────────────────────────╮
│ git add docs/concepts/overview.adoc                        │
╰────────────────────────────────────────────────────────────╯

[bold blue]Git Command: Stage changes[/bold blue]
╭────────────────────────────────────────────────────────────╮
│ git add docs/procedures/install.adoc                       │
╰────────────────────────────────────────────────────────────╯

... more git add commands ...

[bold blue]Git Command: Create commit[/bold blue]
╭────────────────────────────────────────────────────────────╮
│ git commit -m "Fix EntityReference issues in AsciiDoc files│
│                                                            │
│ Fixed the following AsciiDocDITA rules:                    │
│   - EntityReference                                        │
│                                                            │
│ Files updated:                                             │
│   - docs/concepts/overview.adoc                            │
│   - docs/procedures/install.adoc                           │
│   - docs/reference/api.adoc                                │
│   - ... and 6 more files"                                 │
╰────────────────────────────────────────────────────────────╯

? Have you committed the changes? (Y/n) Y

✓ Excellent! EntityReference fixes committed.
```

### ContentType Rule (Partially Deterministic)

```bash
🔧 Processing ContentType violations (8 found)

These files are missing content type attributes:

1. docs/procedures/install.adoc
   Detected type: PROCEDURE (based on filename prefix)
   
   ? Apply detected content type? 
     ❯ Yes, add ':_mod-docs-content-type: PROCEDURE'
       No, I'll set it manually
       Skip this file

2. docs/concepts/overview.adoc  
   Detected type: CONCEPT (based on filename prefix)
   
   ? Apply detected content type?
     ❯ Yes, add ':_mod-docs-content-type: CONCEPT'
       No, let me choose:
         ○ ASSEMBLY
         ○ CONCEPT
         ○ PROCEDURE
         ○ REFERENCE
         ○ SNIPPET
       Skip this file

[... continues for each file ...]

⠏ Applying content type fixes...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02

✓ Successfully applied 8 ContentType fixes
  • 6 automatic detections accepted
  • 2 manually specified

? Review and commit these changes? (Y/n) Y

[Shows diff, commit flow similar to above]
```

### TaskSection Rule (Non-Deterministic)

```bash
🔧 Processing TaskSection violations (3 found)

These violations require manual intervention:

📄 docs/procedures/install.adoc:34
   ⚠️  Task sections must use numbered lists
   
   Current:
   ```
   * Download the installer
   * Run the setup wizard  
   * Configure settings
   ```
   
   Should be:
   ```
   1. Download the installer
   2. Run the setup wizard
   3. Configure settings
   ```

? How would you like to proceed?
  ❯ Open file in editor
    Mark with TODO comment
    Skip for now
    View more context

[If "Mark with TODO comment" selected:]

✓ Added TODO comment to docs/procedures/install.adoc:34
  // TODO: [Aditi] Convert to numbered list for DITA compatibility

? Continue with next violation? (Y/n) Y

[... continues for remaining violations ...]
```

## 5. Completion and Pull Request

### Summary and Next Steps

```bash
🎉 Migration journey complete!

📊 Final Summary:
  ✓ EntityReference: 23 fixes applied (committed)
  ✓ ContentType: 8 fixes applied (committed)
  ⚠️ TaskSection: 3 marked with TODO comments (committed)

📁 Modified files: 12
💾 Commits created: 3
🌿 Current branch: aditi/dita-migration-phase1

? Ready to create a pull request? (Y/n) Y

📋 Suggested PR details:

Title: "Prepare AsciiDoc files for DITA migration"

Description:
This PR prepares our AsciiDoc documentation for DITA migration by fixing
compatibility issues identified by the AsciiDocDITA ruleset.

## Changes Made

### Automated Fixes
- **EntityReference** (23 fixes): Replaced HTML entities with AsciiDoc equivalents
- **ContentType** (8 fixes): Added missing content type attributes

### Manual Review Required  
- **TaskSection** (3 issues): Marked with TODO comments for manual conversion

## Testing
- All files validated with Vale AsciiDocDITA rules
- No AsciiDoc syntax errors introduced
- Preview builds successfully

## Next Steps
1. Review and address TODO comments
2. Run full DITA conversion test
3. Update CI pipeline if needed

? Create PR with GitHub CLI? (Y/n) Y

📋 Please run the following command:

[bold blue]GitHub CLI: Create pull request[/bold blue]
╭────────────────────────────────────────────────────────────────────────────╮
│ gh pr create --base main --title "Prepare AsciiDoc files for DITA         │
│ migration" --body "$(cat <<'EOF'                                          │
│ This PR prepares our AsciiDoc documentation for DITA migration by fixing  │
│ compatibility issues identified by the AsciiDocDITA ruleset.              │
│                                                                            │
│ ## Changes Made                                                            │
│                                                                            │
│ ### Automated Fixes                                                        │
│ - **EntityReference** (23 fixes): Replaced HTML entities                  │
│ - **ContentType** (8 fixes): Added content type attributes                │
│                                                                            │
│ ### Manual Review Required                                                 │
│ - **TaskSection** (3 issues): Marked with TODO comments                   │
│                                                                            │
│ ## Testing                                                                 │
│ - All files validated with Vale AsciiDocDITA rules                        │
│ - No AsciiDoc syntax errors introduced                                    │
│ - Preview builds successfully                                              │
│ EOF                                                                        │
│ )"                                                                         │
╰────────────────────────────────────────────────────────────────────────────╯

? PR created? (Y/n) Y

✨ Congratulations! Your AsciiDoc files are now ready for DITA migration.

📚 Resources:
  • View detailed report: ~/aditi-data/reports/2025-07-27-migration-report.md
  • Review TODO items: git grep "TODO: \[Aditi\]"
  • Run verification: aditi check --strict

Thank you for using Aditi! 🚀
```

## 6. Subsequent Runs - Incremental Progress

### Checking Progress After Manual Fixes

```bash
$ aditi check docs/

🔍 Analyzing AsciiDoc files in docs/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:10

📊 Analysis Results for docs/

✅ EntityReference - No violations found!
✅ ContentType - No violations found!

🔵 TaskSection (3 violations)
  docs/procedures/install.adoc:34   Task sections require numbered lists
  docs/procedures/config.adoc:22    Task sections require numbered lists  
  docs/procedures/deploy.adoc:45    Task sections require numbered lists

📈 Summary:
  Files processed: 12
  Total violations: 3 (down from 34!)
  Manual intervention required: 3

🎯 Progress: 91% of issues resolved!

Great work! Only manual fixes remain.
```

## Key Features Demonstrated

1. **Progressive Disclosure**: Commands provide increasing detail as needed
2. **Non-Invasive Git Integration**: Suggests commands but doesn't execute them
3. **Smart Detection**: Analyzes files to suggest appropriate fixes
4. **Interactive Choices**: User maintains control over all changes
5. **Clear Progress Tracking**: Visual indicators and summaries throughout
6. **Helpful Context**: Shows before/after examples and explanations
7. **Graceful Degradation**: Handles errors and allows skipping problematic files
8. **Comprehensive Reporting**: Detailed logs and reports for documentation

This mockup demonstrates how Aditi guides users through the migration process while keeping them in control, providing clear feedback, and ensuring a smooth workflow from start to finish.