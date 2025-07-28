---
layout: page
title: "Aditi CLI User Interaction Mockup"
permalink: /design/phase-2-mockup/
---

# Aditi CLI User Interaction Mockup

This document demonstrates typical user interactions with the Aditi CLI, showing the complete workflow:
- initial setup
- The interactions show user-CLI interaction patterns for three types of issues: those who have deterministic, partially-deterministic, and non-deterministic fixes.
- It presents the setup and rules in the correct sequence
  - Configuration and prerequisite rules first
  - "Error"-level rules in the first stage
  - "Warning"-level rules in the second stage
  - "Suggestion"-level rules in the final stage

## Scenario: Technical Writer Preparing Documentation

Sarah is a technical writer with a repository containing 50+ AsciiDoc files that need to be prepared for migration to DITA format. She's heard about Aditi and wants to use it to prepare her files.

## 1. Initial Setup

### First Run - Discovery

```bash
$ aditi --help

IMPORTANT:
- cd to the root directory of your repository before running aditi commands.
- Create a working branch with the latest changes in it.

 Usage: aditi [OPTION]||[COMMAND]

 AsciiDoc DITA Integration - Prepare AsciiDoc files for migration to DITA

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --version             -V        Show version and exit                        │
│ --help                          Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ init      Initialize Vale configuration for AsciiDocDITA rules.              │
│ journey   Start an interactive journey to migrate AsciiDoc files to DITA.    │
│ check     Check AsciiDoc files for DITA compatibility issues.                │
│ fix       Fix deterministic DITA compatibility issues in AsciiDoc files.     │
╰──────────────────────────────────────────────────────────────────────────────╯

Examples:

$ aditi --version
aditi version 0.1.0

$ aditi init

$ aditi journey

$ aditi check

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
Fix: Replace missing content type attributes
  docs/procedures/install.adoc:1
  docs/concepts/overview.adoc:1
  docs/reference/api.adoc:1
  ... and 5 more

🔴 EntityReference (23 issues)
Fix: Replace missing content type attributes or insert `TBD` for reviewer.
  docs/concepts/overview.adoc:15
  docs/concepts/overview.adoc:23
  docs/concepts/overview.adoc:45
  docs/procedures/install.adoc:12
  ... and 19 more

🔵 TaskSection (3 issues)
Fix: Comment task sections that require numbered lists for reviewer.
  docs/procedures/install.adoc:34
  docs/procedures/config.adoc:22
  docs/procedures/deploy.adoc:45

📈 Summary:
  Files processed: 12
  Total issues: 34
  Can be auto-fixed: 23 fully deterministic issues
  Most can be auto-fixed: 8 partially deterministic issues
  Manual intervention required: 3

✨ Good news! 68% of issues can be fixed automatically.

Next step: Run 'aditi journey' for guided workflow
```

## 3. Guided Journey - Interactive Workflow

### Starting the Journey

```bash
$ aditi journey

🚀 Welcome to Aditi's guided journey!

This interactive workflow will help you:
  ✓ Configure Aditi for your repository
  ✓ Automatically fix or flag issues for you
  ✓ Prompt you to review automatic fixes
  ✓ Prompt you to fix flagged issues

📁 Current directory: /home/sarah/product-docs

? Is this the root directory of your repostory? (Y/n) Y

[If user enters n, tell them to "cd to the root directory of the repository and rerun the 'aditi journey' command". Then exit Aditi.]

? Customize subdirectory access? (y/N) y

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

Question: Can Clause Code design Aditi to use the path information in ~/aditi-data/config.json to select or exclude specific directories.

Also, Aditi must ignore symlinks.

## 4. Applying Fixes - Rule by Rule

### ContentType Rule (Partially Deterministic)

Aditi starts with the ContentType rule. Having the content type attributes correctly defined is a prerequisite for type-specific rules to function correctly For example, rules that have "Task" are only valid for files that have ':_mod-docs-content-type: TASK'.

```bash
🔧 Processing ContentType issues (8 found)

ContentType: Without a clear content type definition, the Vale style cannot reliably report type-specific issues for modules such as TaskSection,  TaskExample, TaskDuplicate, TaskStep, and TaskTitle.

These files need valid content type attributes and values:

  docs/procedures/install.adoc:1
  docs/concepts/overview.adoc:1
  docs/reference/api.adoc:1
  [show the full list of files]

Fix: Replace missing content type attributes

? Auto-fix, flag, or skip? (A/f/s) A

[Y = Auto-fix adds the attribute, adds the detected value, and positions the attribute 2-3 lines above the first id and title. If the attribute value cannot be autodetected (based on the commented out attribute, filename prefix, or obsolete attribute values) then insert `TBD` as a placeholder value. Replace commented-out or obsolete attributes with the new one.]
[f = Flags the issue by inserting a comment that contains the Vale AsciiDocDITA-generated message for the ContentType rule.]
[s = Skips to the end of the interaction for the ContentType rule.]

⠏ Applying ContentType fixes...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02

✓ Applied 8 ContentType fixes.
  • docs/concepts/overview.adoc (1 fix)
  • docs/procedures/install.adoc (1 fix)
  • docs/reference/api.adoc (1 fix)
  • ...
  [show the full list of files]

💡 To do:
- Review and fix all changes before continuing.
- Search for `TBD` and replace it with valid attribute values.
- Optional: Commit and push your changes to a pull request.
- Ensure these changes are available in the current working branch before proceding.

For more information, see <URL>

? Continue with next rule? (Y/n) Y
```

### EntityReference Rule (Fully Deterministic)

```bash
🔧 Processing EntityReference issues (23 found)

EntityReference: DITA 1.3 supports five character entity references defined in the XML standard: &amp;, &lt;, &gt;, &apos;, and &quot;. Replace any other character entity references with an appropriate built-in AsciiDoc attribute.

These files have this issue:
• docs/procedures/install.adoc:1
• docs/concepts/overview.adoc:1
• docs/reference/api.adoc:1
  [show the full list of files]

Fix: Replace with valid entity references

? Auto-fix, flag, or skip? (A/f/s) A

⠏ Applying changes...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:03

✓ Applied 8 EntityReference fixes.
  • docs/concepts/overview.adoc (3 fixes)
  • docs/procedures/install.adoc (1 fix)
  • docs/reference/api.adoc (5 fixes)
  • ...
  [show the full list of files]

💡 To do:
- Review and fix all changes before continuing.
- Ensure these changes are available in the current working branch before proceding.
- Optional: Commit and push your changes to a pull request.

? Continue with next rule? (Y/n) Y
```

### ExampleBlock rule (Non-deterministic pattern)

```bash
🔧 Processing ExampleBlock issues (23 found)

ExampleBlock: DITA 1.3 allows the <example> element to appear only within the main body of the topic. Do not use example blocks in sections, within other blocks, or as part of lists.

To fix this issue, you need to review and edit each file.
Follow the guidance provided in <URL>

These files have this issue:
• docs/procedures/install.adoc:1
• docs/concepts/overview.adoc:1
• docs/reference/api.adoc:1
  [show the full list of files]

Fix: Flag the issue for user review

? Flag or skip? (F/s) F

⠏ Applying changes...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:03

✓ Applied 8 ExampleBlock flags.
  • docs/concepts/overview.adoc (3 fixes)
  • docs/procedures/install.adoc (1 fix)
  • docs/reference/api.adoc (5 fixes)
  • ...
  [show the full list of files]

💡 To do:
- Review and fix all changes before continuing.
- Ensure these changes are available in the current working branch before proceding.
- Optional: Commit and push your changes to a pull request.

? Continue with next rule? (Y/n) Y
```

### NestedSection (Non-deterministic pattern)

Repeat the non-deterministic CLI pattern for NestedSection.

NestedSection: DITA 1.3 allows the <section> element to appear only within the main body of the topic. If a level 2 section is needed, move it to a separate file.

### TaskExample rule (Non-deterministic pattern)

Repeat the non-deterministic CLI pattern for TaskExample.

TaskExample: DITA 1.3 allows only one <example> element in a task topic. If multiple examples are needed, combine them in a single example block.

### TaskSection rule (Non-deterministic pattern)

Repeat the non-deterministic CLI pattern for TaskSection.

TaskSection: DITA 1.3 does not allow sections in a task topic. If a section is needed, move it to a separate file.

## 5. Completion and Next Steps

### Summary and Final Report

```bash
🎉 Preparation journey complete!

📋 Preparation Report Generated:
  ~/aditi-data/reports/2025-07-27-preparation-report.md

Thank you for using Aditi! 🚀
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