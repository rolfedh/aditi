---
layout: page
title: "Aditi CLI User Interaction Mockup"
permalink: /design/phase-2-mockup/
---

# Aditi CLI User Interaction Mockup

This document demonstrates typical user interactions with the Aditi CLI, showing the complete workflow from initial setup through successful preparation of AsciiDoc files to DITA-compatible format.

## Scenario: Technical Writer Preparing Documentation

Sarah is a technical writer with a repository containing 50+ AsciiDoc files that need to be prepared for migration to DITA format. She's heard about Aditi and wants to use it to prepare her files.

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

[17:21:26] INFO     Existing .vale.ini backed up to .vale.ini.backup.20250727172126
           INFO     Created Vale configuration at .vale.ini
           INFO     Downloading AsciiDocDITA styles...
[17:21:27] INFO     Successfully downloaded AsciiDocDITA styles

⠼ Pulling Vale container image...
⠼ Creating Vale configuration...

✓ Aditi initialized successfully!
Existing Vale config backed up: .vale.ini.backup.20250727172126
Vale configuration created at: .vale.ini
AsciiDocDITA styles downloaded to: .vale/styles/

IMPORTANT: Restore your original .vale.ini after DITA preparation:
  mv .vale.ini.backup.20250727172126 .vale.ini

Next steps:
- Run 'aditi check' to check your AsciiDoc files for issues
- Run 'aditi journey' for a guided workflow
```

FEEDBACK: If a `.vale.ini` file exists in the repository root, automatically back it up as `.vale.ini.backup.<timestamp>` before creating Aditi's configuration. The root `.vale.ini` always overrides the home directory version, so this prevents conflicts with existing Vale setups. Notify users of the backup and remind them to restore it after completing their DITA preparation.

## 2. First Check - Discovery Phase

### Running Check on Documentation

```bash
$ aditi check docs/

🔍 Analyzing AsciiDoc files in docs/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:12

📊 Analysis Results for docs/

🟡 ContentType (8 issues)
  docs/procedures/install.adoc:1    Missing content type attribute (detected: PROCEDURE)
  docs/concepts/overview.adoc:1     Missing content type attribute (detected: CONCEPT)
  docs/reference/api.adoc:1         Missing content type attribute (detected: REFERENCE)
  ... and 5 more

🔴 EntityReference (23 issues)
  docs/concepts/overview.adoc:15    Replace '&nbsp;' with '{nbsp}'
  docs/concepts/overview.adoc:23    Replace '&mdash;' with '{mdash}'
  docs/concepts/overview.adoc:45    Replace '&copy;' with '{copy}'
  docs/procedures/install.adoc:12   Replace '&trade;' with '{trade}'
  ... and 19 more

🔵 TaskSection (3 issues)
  docs/procedures/install.adoc:34   Task sections require numbered lists
  docs/procedures/config.adoc:22    Task sections require numbered lists
  docs/procedures/deploy.adoc:45    Task sections require numbered lists

📈 Summary:
  Files processed: 12
  Total issues: 34
  Fully deterministic fixes: 23 (can be auto-fixed)
  Partially deterministic fixes: 8 (require review)
  Manual intervention required: 3

✨ Good news! 68% of issues can be fixed automatically.

Next steps:
- Run 'aditi fix' to apply automatic fixes
- Run 'aditi journey' for guided workflow
```

## 3. Guided Journey - Interactive Workflow

### Starting the Journey

```bash
$ aditi journey

🚀 Welcome to Aditi's guided journey!

This interactive workflow will help you:
  ✓ Configure Aditi for your repository
  ✓ Apply fixes systematically
  ✓ Review changes
  ✓ Prepare files for DITA migration

📁 Current directory: /home/sarah/product-docs

? Is this the directory you want to work with? (Y/n) Y

? Would you like to configure any subdirectory permissions? (y/N) y

🔍 Scanning for AsciiDoc files...

Detected documentation in (↑/↓ arrows to navigate,
  Space to select/deselect, Enter to confirm):
  ❯◉ docs/src/main/asciidoc/ (47 .adoc files)
   ○ internal/legacy/docs/ (3 .adoc files)
   ◯ archived/old-docs/ (12 .adoc files)
   ◉ modules/api/docs/ (8 .adoc files)

? Use these auto-detected paths or specify custom directory?
  ❯ Use detected paths
    Enter custom directory paths

✓ Configuration saved to ~/aditi-data/config.json

Selected directories:
  • docs/src/main/asciidoc/ (47 .adoc files)
  • modules/api/docs/ (8 .adoc files)

? These directory selections look correct? (Y/n/r)
  Y = Yes, continue  n = Exit  r = Reconfigure directories
  > Y

💡 Workflow Tip:
  Before starting, create a feature branch for your changes.
  This keeps your work organized and makes it easy to review.

? Ready to start preparing your files? (Y/n) Y

✓ Great! Let's start.
```

## 4. Applying Fixes - Rule by Rule

### ContentType Rule (Partially Deterministic)

Aditi starts with ContentType rule because having the content type attribute correctly defined is a prerequisite for type-specific rules, such as the rules that have "Task" in their names.

```bash
🔧 Processing ContentType issues (8 found)

ContentType: Without a clear content type definition, the Vale style cannot reliably report type-specific issues for modules such as TaskSection,  TaskExample, TaskDuplicate, TaskStep, and TaskTitle.

Add the correct :_mod-docs-content-type: definition at the top of the file.

These files need valid content type attributes and values:

1. docs/procedures/proc_install.adoc
   Detected type: PROCEDURE (based on filename prefix)

   ? Apply detected content type?
     ❯ Yes, add ':_mod-docs-content-type: PROCEDURE'
       No, I'll set it manually
       Skip this file

# 2. docs/concepts/conc_overview.adoc
#    Detected type: CONCEPT (based on filename prefix)

#    ? Apply detected content type?
#      ❯ Yes, add ':_mod-docs-content-type: CONCEPT'
#        No, let me choose:
#          ○ ASSEMBLY
#          ○ CONCEPT
#          ○ PROCEDURE
#          ○ REFERENCE
#          ○ SNIPPET
#        Skip this file

[... continues for each file ...]

⠏ Applying content type fixes...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02

✓ Successfully applied 8 ContentType fixes
  • 6 automatic detections accepted
  • 2 manually specified

? Review these changes? (Y/n) Y

[Shows diff output with content type additions]

🟡 ContentType (1 issues remaining)
  docs/procedures/uninstall.adoc:1    Missing content type attribute (detected: PROCEDURE)

✓ Content type attributes added successfully.

💡 Workflow Tip:
- Fix all issues before continuing.
- Review the auto-detected types for accuracy.

? Continue with next rule? (Y/n) Y
```

### EntityReference Rule (Fully Deterministic)

```bash
🔧 Processing EntityReference issues (23 found)

These issues can be fixed automatically:
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

📝 Summary of changes:
  • Replaced HTML entities with AsciiDoc equivalents
  • Modified 9 files with 23 total replacements
  • All changes are DITA-compatible

✓ Changes saved to your working directory.

💡 Workflow Tip:
  These changes are ready to be committed to your branch.
  Review them carefully before proceeding.

? Continue with next rule? (Y/n) Y
```

### ExampleBlock Rule (Fully Deterministic)

TBD

### NestedSection

TBD

### TaskExample

TBD

### TaskSection Rule (Non-Deterministic)

```bash
🔧 Processing TaskSection issues (3 found)

These issues require manual intervention:

📄 docs/procedures/install.adoc:34
   ⚠️  Task sections must use numbered lists

   Current:
   • Download the installer
   • Run the setup wizard
   • Configure settings

   Should be:
   1. Download the installer
   2. Run the setup wizard
   3. Configure settings

? How would you like to proceed?
  ❯ Open file in editor
    Mark with TODO comment
    Skip for now
    View more context

[If "Mark with TODO comment" selected:]

✓ Added TODO comment to docs/procedures/install.adoc:34
  // TODO: [Aditi] Convert to numbered list for DITA compatibility

? Continue with next issue? (Y/n) Y

[... continues for remaining issues ...]
```

## 5. Completion and Next Steps

### Summary and Final Report

```bash
🎉 Preparation journey complete!

📊 Final Summary:
  ✓ EntityReference: 23 fixes applied
  ✓ ContentType: 8 fixes applied
  ⚠️ TaskSection: 3 marked with TODO comments

📁 Modified files: 12
💾 All changes saved to your working directory

📋 Preparation Report Generated:
  ~/aditi-data/reports/2025-07-27-preparation-report.md

💡 Next Steps:

1. **Create a pull request with your changes**
   - Include the preparation report in your PR description
   - Reference the specific AsciiDocDITA rules addressed

2. **Review and address any issues identified in the PR**
   - Check for any CI/CD failures
   - Address reviewer comments
   - Fix remaining TODO items

3. **Merge the PR once all issues are resolved**
   - Ensure all tests pass
   - Get necessary approvals
   - Complete your team's merge process

📚 Additional Resources:
  • Review TODO items: Search for "TODO: [Aditi]" in modified files
  • Run verification: aditi check --strict
  • View detailed changes: Review the preparation report

Thank you for using Aditi! 🚀
```

## 6. Subsequent Runs - Incremental Progress

### Checking Progress After Manual Fixes

```bash
$ aditi check docs/

🔍 Analyzing AsciiDoc files in docs/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:10

📊 Analysis Results for docs/

✅ EntityReference - No issues found!
✅ ContentType - No issues found!

🔵 TaskSection (3 issues)
  docs/procedures/install.adoc:34   Task sections require numbered lists
  docs/procedures/config.adoc:22    Task sections require numbered lists
  docs/procedures/deploy.adoc:45    Task sections require numbered lists

📈 Summary:
  Files processed: 12
  Total issues: 3 (down from 34!)
  Manual intervention required: 3

🎯 Progress: 91% of issues resolved!

Great work! Only manual fixes remain.
```

## Key Features Demonstrated

1. **Progressive Disclosure**: Commands provide increasing detail as needed
2. **Workflow Guidance**: Provides high-level guidance without prescriptive commands
3. **Smart Detection**: Analyzes files to suggest appropriate fixes
4. **Interactive Choices**: User maintains control over all changes
5. **Clear Progress Tracking**: Visual indicators and summaries throughout
6. **Helpful Context**: Shows before/after examples and explanations
7. **Graceful Degradation**: Handles errors and allows skipping problematic files
8. **Comprehensive Reporting**: Detailed logs and reports for documentation

This mockup demonstrates how Aditi guides users through the preparation process while keeping them in control, providing clear feedback, and ensuring a smooth workflow from start to finish.

## Design Note: Nested Directory Discovery

The directory selection interface has been enhanced to handle deeply nested documentation structures commonly found in Maven/Gradle projects (e.g., `docs/src/main/asciidoc/`).

**Auto-detection**: Aditi recursively scans for directories containing `.adoc` files and shows the count of files found in each location. This helps users identify the actual documentation locations rather than just showing top-level directories.

**Custom paths**: Users can also specify custom directory paths for edge cases or when auto-detection doesn't find their documentation structure. This ensures Aditi works with any project layout while providing intelligent defaults for common scenarios.

**Interaction pattern**: Users navigate with ↑/↓ arrows, toggle selections with Space, and confirm with Enter. A confirmation step allows users to review their selections and reconfigure if needed (using the 'r' option) before proceeding with the preparation process.

## Terminology

With Aditi, the user is not "migrating" files. They are "preparing" files for migration to DITA. The migration will take place at some point in the distant future.

Prefer the term "issue" instead of "violation".