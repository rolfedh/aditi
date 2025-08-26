---
layout: post
title: "Direct File Processing in Journey Command"
date: 2025-08-25 21:51:56 -0400
author: Rolfe DH
tags: [features, journey, cli, workflow]
summary: "The journey command now accepts file paths directly, enabling targeted processing of specific AsciiDoc files without interactive selection."
---

## Streamlined Workflow with Direct File Arguments

We've just implemented a powerful enhancement to the `aditi journey` command that significantly improves workflow efficiency for users working with specific files or directories. You can now provide file paths directly on the command line, bypassing the interactive directory selection process entirely.

## The Problem It Solves

Previously, when users wanted to process specific files with `aditi journey`, they had to:
1. Start the journey command
2. Navigate through interactive prompts
3. Select directories from a list
4. Process all files in those directories

This was particularly cumbersome when working with a subset of files, such as all network-observability modules in a large documentation repository. Users expressed the need to target specific file patterns directly, similar to how they work with other command-line tools.

## The New Solution

Now you can specify exactly which files or directories to process right from the command line:

```bash
# Process specific files
aditi journey modules/network-observability-*.adoc

# Process a single file
aditi journey modules/network-observability-cli.adoc

# Process an entire directory
aditi journey modules/

# Mix files and directories
aditi journey README.adoc modules/api/ docs/guides/*.adoc
```

## How It Works

The enhanced journey command:

1. **Accepts file paths as arguments** - The CLI now accepts optional paths that can be files or directories
2. **Validates inputs** - Ensures all provided paths exist and are readable
3. **Handles wildcards** - Shell expansion works naturally with glob patterns
4. **Preserves state** - Selected files are stored in the session for workflow continuity
5. **Maintains compatibility** - When no paths are provided, the original interactive mode still works

## Technical Implementation

The implementation required changes across multiple components:

### CLI Layer
Added path arguments with proper validation:
```python
paths: Optional[List[Path]] = typer.Argument(
    None,
    help="Paths to process (files or directories).",
    exists=True,
    file_okay=True,
    dir_okay=True,
    readable=True,
)
```

### Configuration Flow
The `configure_repository` function now detects when paths are provided and processes them directly:
- Individual `.adoc` files are collected
- Directories are scanned for `.adoc` content
- File counts are displayed for transparency
- Selected files are stored in the session

### Rule Processing
The `apply_rules_workflow` prioritizes command-line paths over configured directories, ensuring the user's explicit selections are honored throughout the entire journey.

## Use Cases

This feature is particularly valuable for:

### Targeted Module Updates
When updating specific documentation modules:
```bash
aditi journey modules/authentication-*.adoc
```

### Pre-commit Hooks
Process only changed files before committing:
```bash
aditi journey $(git diff --name-only --cached '*.adoc')
```

### Incremental Migration
Work through large documentation sets file by file:
```bash
aditi journey docs/api/users.adoc
# Review and commit
aditi journey docs/api/products.adoc
# Review and commit
```

### Pattern-Based Processing
Focus on specific documentation types:
```bash
aditi journey **/README.adoc
aditi journey modules/*-procedure.adoc
```

## Benefits

1. **Efficiency** - No need to navigate through prompts when you know what to process
2. **Precision** - Target exactly the files you want to work on
3. **Automation** - Easier to integrate into scripts and CI/CD pipelines
4. **Flexibility** - Mix and match files and directories as needed
5. **Speed** - Faster workflow for experienced users

## Backward Compatibility

The interactive mode remains fully functional. Simply run `aditi journey` without arguments to access the familiar guided experience with directory selection prompts.

## What's Next?

This enhancement opens up new possibilities for workflow automation. Future improvements could include:
- Integration with git to automatically process changed files
- Batch processing with different rule sets for different file patterns
- Parallel processing for large file sets
- Progress persistence for interrupted batch operations

## Try It Out

Update to the latest version of Aditi and start using direct file paths with the journey command:

```bash
# Update Aditi
pip install --upgrade aditi

# Process specific files
aditi journey your/target/files/*.adoc
```

This feature represents our commitment to making the DITA migration process as smooth and efficient as possible. By giving users more control over what gets processed, we're helping teams work more effectively with their documentation workflows.