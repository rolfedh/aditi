---
layout: post
title: "Running Vale AsciiDocDITA Directly from Command Line"
date: 2025-07-28 20:30:34 -0400
author: Claude Code
tags: [aditi, asciidoc, dita, vale, containerization, technical-writing]
summary: "Learn how to bypass Aditi and run Vale with AsciiDocDITA styles directly using Podman/Docker containers for debugging and advanced workflows."
---

# Running Vale AsciiDocDITA Directly from Command Line

## Introduction

While Aditi provides a user-friendly interface for preparing AsciiDoc files for DITA migration, sometimes you need direct access to the underlying Vale linter with AsciiDocDITA styles. Whether you're debugging issues, integrating with CI/CD pipelines, or just prefer working with raw tools, this post shows you how to run Vale+AsciiDocDITA directly from the command line.

## The Challenge

When you try to run `vale` directly on your system, you'll likely encounter:

```bash
$ vale .
Command 'vale' not found, but can be installed with:
sudo snap install vale
```

Even if you install Vale locally, you'd still need to:
1. Download and configure AsciiDocDITA styles manually
2. Set up proper `.vale.ini` configuration
3. Manage style paths and dependencies

Aditi solves this by using a containerized approach with everything pre-configured.

## The Solution: Container-Based Vale

Since Aditi already creates the `.vale.ini` configuration file with AsciiDocDITA styles, you can leverage the same containerized Vale setup that Aditi uses internally.

### Basic Container Command

The core command structure is:

```bash
podman run --rm -v "$PWD:/docs" -w /docs docker.io/jdkato/vale:latest [options] [files]
```

**What this does:**
- `--rm`: Remove container after running
- `-v "$PWD:/docs"`: Mount current directory as `/docs` in container  
- `-w /docs`: Set working directory inside container
- `docker.io/jdkato/vale:latest`: Official Vale container image

### Practical Examples

**Check Vale version:**
```bash
podman run --rm docker.io/jdkato/vale:latest --version
# Output: vale version v3.11.2
```

**Check specific file with line output:**
```bash
podman run --rm -v "$PWD:/docs" -w /docs docker.io/jdkato/vale:latest --output=line example-docs/test-content-type.adoc
```

Output:
```
example-docs/test-content-type.adoc:1:1:AsciiDocDITA.ShortDescription:Assign [role="_abstract"] to a paragraph to use it as <shortdesc> in DITA.
example-docs/test-content-type.adoc:1:1:AsciiDocDITA.ContentType:The '_mod-docs-content-type' attribute definition is missing.
```

**Check all AsciiDoc files in a directory:**
```bash
podman run --rm -v "$PWD:/docs" -w /docs docker.io/jdkato/vale:latest --output=line example-docs/*.adoc
```

**Get JSON output for programmatic use:**
```bash
podman run --rm -v "$PWD:/docs" -w /docs docker.io/jdkato/vale:latest --output=JSON example-docs/test-content-type.adoc
```

**Recursive check of entire project:**
```bash
podman run --rm -v "$PWD:/docs" -w /docs docker.io/jdkato/vale:latest --output=line .
```

### Docker Alternative

If you're using Docker instead of Podman, simply replace `podman` with `docker`:

```bash
docker run --rm -v "$PWD:/docs" -w /docs docker.io/jdkato/vale:latest --output=line .
```

## Results and Integration

This approach gives you:

✅ **Native Vale experience** with familiar command-line interface  
✅ **All AsciiDocDITA rules** automatically available  
✅ **Multiple output formats** (line, JSON, CLI)  
✅ **Perfect for automation** and CI/CD integration  
✅ **No local installation** required  

### CI/CD Integration Example

Add this to your GitHub Actions workflow:

```yaml
- name: Run Vale AsciiDocDITA checks
  run: |
    podman run --rm -v "$PWD:/docs" -w /docs docker.io/jdkato/vale:latest --output=line docs/
```

### Shell Alias for Convenience

Add this to your `~/.bashrc` or `~/.zshrc`:

```bash
alias vale-aditi='podman run --rm -v "$PWD:/docs" -w /docs docker.io/jdkato/vale:latest'
```

Then use it like native Vale:
```bash
vale-aditi --output=line .
vale-aditi --help
```

## Comparison with Aditi Commands

| Direct Container | Aditi Equivalent | Use Case |
|------------------|------------------|----------|
| `podman run ... --output=line .` | `aditi vale --output=line` | Quick debugging |
| `podman run ... --output=JSON file.adoc` | `aditi vale file.adoc` | Programmatic use |
| `podman run ... --help` | `aditi vale --help` | Learning Vale options |

## Prerequisites

You'll need:
1. **Podman or Docker** installed
2. **`.vale.ini` configuration** (created by `aditi init`)
3. **AsciiDocDITA styles** (downloaded by `aditi init`)

If you haven't run `aditi init` yet, do that first to set up the Vale configuration and download the necessary style files.

## Lessons Learned

**When to use direct Vale:**
- Debugging specific rule behavior
- CI/CD pipeline integration  
- Advanced Vale features not exposed in Aditi
- Learning Vale's native capabilities

**When to stick with Aditi:**
- Interactive fixing workflows
- Guided DITA preparation process
- User-friendly violation summaries
- Integrated git workflow guidance

## Next Steps

The containerized approach opens up possibilities for:
- **Custom Vale plugins** for organization-specific rules
- **Automated reporting** in CI/CD pipelines  
- **IDE integrations** using Vale's Language Server Protocol
- **Batch processing** of large documentation sets

Consider exploring Vale's [configuration options](https://vale.sh/docs/topics/config/) and [custom rule creation](https://vale.sh/docs/topics/styles/) for advanced use cases.

## Conclusion

Running Vale+AsciiDocDITA directly from the command line gives you the raw power of these tools while leveraging Aditi's configuration setup. This hybrid approach lets you choose the right tool for each task - Aditi for guided workflows and direct Vale for automation and debugging.

The containerized approach ensures consistency across environments while avoiding the complexity of local Vale installations and style management.

---

### Resources

- [Vale Documentation](https://vale.sh/docs/)
- [AsciiDocDITA Style Repository](https://github.com/redhat-documentation/asciidoc-dita-toolkit)
- [Aditi Documentation](/aditi/)
- [Podman Documentation](https://podman.io/docs)

### About the Author

This post was generated by Claude Code while working on the Aditi project, demonstrating real-world container usage and documentation workflow integration.