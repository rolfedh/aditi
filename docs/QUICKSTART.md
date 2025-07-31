# Aditi Quick Start Guide

Get started with Aditi in under 5 minutes! This guide will help you prepare your AsciiDoc files for DITA migration.

## What is Aditi?

Aditi is a CLI tool that analyzes AsciiDoc files using Vale with AsciiDocDITA rules to identify and fix compatibility issues before migrating to DITA. It categorizes issues as:

- 🔴 **Fully Deterministic**: Can be auto-fixed (e.g., character entities)
- 🟡 **Partially Deterministic**: Partially auto-fixed with placeholders (e.g., content types)  
- 🔵 **Non-Deterministic**: Require manual review (e.g., nested sections)

## Prerequisites

- Python 3.11 or later
- Podman (preferred) or Docker
- AsciiDoc files to analyze

## Installation

```bash
pip install --upgrade aditi
```

## Basic Workflow

### 1. Initialize Your Project

Navigate to your AsciiDoc project root and initialize Aditi:

```bash
cd /path/to/your/asciidoc-project
aditi init
```

This will:
- Pull the Vale container image
- Download AsciiDocDITA rules
- Create `.vale.ini` configuration

### 2. Configure Paths (Interactive)

Set up which directories Aditi can analyze:

```bash
aditi journey
```

Follow the interactive prompts to:
- Configure repository paths
- Select directories containing AsciiDoc files
- Set up your working preferences

### 3. Check for Issues

Analyze your files for DITA compatibility:

```bash
# Check all configured directories
aditi check

# Check specific files/directories
aditi check docs/ README.adoc

# Check only specific rule
aditi check --rule ContentType

# Verbose output with detailed violations
aditi check --verbose
```

### 4. Apply Automatic Fixes

Fix deterministic issues automatically:

```bash
# Preview what would be fixed (dry run)
aditi fix --dry-run

# Apply fixes interactively (recommended)
aditi fix

# Apply fixes non-interactively
aditi fix --non-interactive

# Fix only specific rule
aditi fix --rule EntityReference
```

## Common Use Cases

### New Project Setup

```bash
# 1. Install and initialize
pip install --upgrade aditi
cd my-asciidoc-project
aditi init

# 2. Configure paths
aditi journey

# 3. Get overview of issues
aditi check

# 4. Fix obvious problems first
aditi fix --rule EntityReference
aditi fix --rule ContentType

# 5. Review remaining issues
aditi check --verbose
```

### Continuous Integration

```bash
# Non-interactive checking in CI/CD
aditi init --force
aditi check docs/
```

### Specific Content Types

```bash
# Focus on procedure documents
aditi check --rule TaskSection
aditi check --rule TaskStep

# Focus on concept documents  
aditi check --rule NestedSection
aditi check --rule ExampleBlock
```

### Large Projects

```bash
# Check specific subdirectories
aditi check user-guide/
aditi check admin-guide/

# Process in stages
aditi fix --rule ContentType    # Fix content types first
aditi fix --rule EntityReference # Fix entities next
aditi check --verbose          # Review remaining issues
```

## Understanding Output

### Check Command Output

```bash
🔍 Analyzing AsciiDoc files in docs/

📊 Analysis Results

🔴 Fully Deterministic Issues
  EntityReference (3 issues)

🟡 Partially Deterministic Issues  
  ContentType (2 issues)

🔵 Non-Deterministic Issues
  NestedSection (15 issues)
  TaskSection (8 issues)

📈 Summary:
  Files processed: 12
  Total issues: 28
  Can be auto-fixed: 5

✨ Good news! 18% of issues can be fixed automatically.
```

### Fix Command Output

```bash
🔧 Applying fixes to 12 files...

✅ EntityReference: Fixed 3 issues
  - Replaced &nbsp; with {nbsp} in user-guide.adoc
  - Replaced &copy; with © in legal.adoc

🟡 ContentType: Applied 2 partial fixes
  - Added :_mod-docs-content-type: TBD to procedure.adoc
  - Added :_mod-docs-content-type: TBD to concept.adoc

📈 Summary:
  Files modified: 4
  Issues fixed: 5
  Manual review needed: 23
```

## Troubleshooting

### Installation Error: "Not a directory"

```bash
ERROR: Could not install packages due to an OSError: [Errno 20] Not a directory: '/home/user/.local/bin/typer'
```

**Problem**: A file named `typer` already exists in your bin directory, preventing pip from installing the typer package.

**Solutions**:
1. Remove the conflicting file:
   ```bash
   rm ~/.local/bin/typer
   ```

2. Then reinstall aditi:
   ```bash
   pip install --upgrade aditi
   ```

3. Alternative: Use pipx for isolated installation:
   ```bash
   pipx install aditi
   ```

### "No paths configured" Error

```bash
Error: No paths configured for checking.
To fix this, run: aditi journey to configure your repository paths.
```

**Solution**: Run `aditi journey` to set up allowed directories.

### "Skipping paths not in allowed directories" Warning

```bash
Warning: Skipping 2 path(s) not in allowed directories:
  • ../other-project/docs.adoc
  • /tmp/test.adoc

Allowed paths:
  • /home/user/my-project
```

**Solution**: Either move files to allowed directories or run `aditi journey` to add more paths.

### Vale Container Issues

```bash
Error: Failed to pull Vale image
```

**Solutions**:
- Check Podman/Docker is running: `podman ps` or `docker ps`
- Try with Docker: `aditi init --docker`
- Check network connectivity
- Try manual pull: `podman pull docker.io/jdkato/vale:latest`

### Permission Errors

```bash
Warning: Cannot access file /path/to/file.adoc (Permission denied)
```

**Solutions**:
- Check file permissions: `ls -la /path/to/file.adoc`
- Ensure you have read access to the directory
- Run with appropriate permissions

### Empty or Corrupted Files

```bash
Warning: Skipping 1 invalid file(s):
  • broken.adoc (empty file)
  • corrupt.adoc ([Errno 2] No such file or directory)
```

**Solutions**:
- Remove or fix empty files
- Check file encoding (should be UTF-8)
- Verify files exist and are readable

### Container Resource Issues

If processing is slow or times out:

```bash
# Check container resources
podman stats

# For large files, processing may take time
# Container limits: 512MB RAM, 2 CPUs, 5-minute timeout
```

## Example Files

### Triggering EntityReference Rule

```asciidoc
= Document Title

Text with problematic entities: &nbsp; &copy; &reg;

This will be fixed to: {nbsp} © ®
```

### Triggering ContentType Rule

```asciidoc
// Missing content type - will be detected and fixed
= Installation Procedure

Follow these steps to install the software.
```

After fix:
```asciidoc
:_mod-docs-content-type: TBD

= Installation Procedure

Follow these steps to install the software.
```

### Triggering NestedSection Rule

```asciidoc
= Main Topic

== Section 1

Content here.

=== Subsection 1.1  // ← This triggers NestedSection rule

DITA doesn't support nested sections. Consider splitting into separate topics.
```

### Triggering TaskSection Rule

```asciidoc
:_mod-docs-content-type: PROCEDURE

= Installing Software

== Prerequisites  // ← This triggers TaskSection rule

Before you begin, ensure you have admin access.

== Steps

1. Download the installer
2. Run the installer
```

## Next Steps

After running Aditi:

1. **Review auto-fixes**: Check what was automatically changed
2. **Address manual issues**: Work through non-deterministic violations
3. **Validate structure**: Ensure DITA topic structure is appropriate
4. **Test conversion**: Try converting with your DITA toolchain
5. **Iterate**: Re-run Aditi after making manual changes

## Getting Help

- **Documentation**: See [full documentation](README.md)
- **Issues**: Report bugs at [GitHub Issues](https://github.com/rolfedh/aditi/issues)
- **Verbose output**: Use `--verbose` flag for detailed information
- **Rule-specific help**: Use `--rule RuleName` to focus on specific issues

## Pro Tips

- **Start with deterministic fixes**: Run `aditi fix` early to handle obvious issues
- **Use dry-run first**: Always preview changes with `--dry-run` 
- **Process iteratively**: Fix issues in batches and re-check
- **Focus by rule**: Use `--rule` to tackle specific issue types
- **Check early and often**: Integrate into your writing workflow