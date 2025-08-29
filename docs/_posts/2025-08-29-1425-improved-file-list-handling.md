---
layout: post
title: "Improved File List Handling in aditi check Command"
date: 2025-08-29 14:25:00 -0400
author: Aditi Development Team
tags: [features, ui, usability]
summary: "New options for complete file list visibility in check command output"
---

## Better Visibility for Large-Scale DITA Migration Projects

When working with large documentation repositories, the `aditi check` command helps identify DITA compatibility issues across hundreds or even thousands of AsciiDoc files. Previously, when a rule violation affected many files, the output would truncate the file list after 10 entries, showing "... and X more" to keep the terminal output manageable.

While this truncation keeps the output clean, users often need to see the complete list of affected files for planning and tracking purposes. Today's update introduces two new options that give you full control over how file lists are displayed.

## New Options

### `--show-all` Flag

The `--show-all` flag displays all affected files directly in the terminal without truncation:

```bash
aditi check --rule ContentType --show-all
```

This is particularly useful when you need to quickly see all affected files for a specific rule violation without exporting to a file.

### `--export-files` Option

For more permanent records or when dealing with very large file lists, the `--export-files` option saves the complete list to a file:

```bash
aditi check --export-files violations-report.txt
```

The exported file includes:
- Generation timestamp
- Total files processed and issues found
- Files grouped by rule name
- Sorted file paths for easy navigation

Example export format:
```
# Aditi Check Results - Files with Issues
# Generated: 2025-08-29T14:25:22.565988
# Total files: 150
# Total issues: 342

## ContentType (45 files)
  - modules/getting-started.adoc
  - modules/installation-guide.adoc
  - modules/troubleshooting.adoc
  ...

## EntityReference (23 files)
  - assemblies/product-overview.adoc
  - assemblies/quick-start.adoc
  ...
```

## Using Both Options Together

You can combine both options for maximum flexibility:

```bash
aditi check --show-all --export-files full-report.txt --rule BlockTitle
```

This displays all files in the terminal while also creating a permanent record.

## Consistent Experience Across Commands

The same file list display logic is now used in both the `check` command and the `journey` command, ensuring a consistent user experience throughout the tool.

## Implementation Details

The implementation adds a reusable `_display_file_list()` helper method to the processor module, which handles:
- Truncation logic (show 10 files by default)
- Full display when requested
- Consistent formatting across different commands

This approach maintains backward compatibility while providing the flexibility needed for large-scale documentation projects.

## Next Steps

These improvements make it easier to track and manage DITA migration progress across large documentation sets. Combined with the journey workflow, teams can now better plan and execute their migration strategies with full visibility into the scope of work required.

Try out the new options with:
```bash
aditi check --help
```

Happy migrating!