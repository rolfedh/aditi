---
layout: post
title: "Introducing Aditi: AsciiDoc to DITA Migration Made Easy"
date: 2025-07-29 08:16:42 -0400
author: Rolfe Dlugy-Hegwer
tags: [aditi, asciidoc, dita, migration, technical-writing, cli-tool, vale, announcement]
summary: "A new CLI tool that automates AsciiDoc to DITA migration analysis and fixes, helping technical writers prepare documentation with confidence and speed."
---

# Introducing Aditi: AsciiDoc to DITA Migration Made Easy

After months of development and real-world testing, I'm excited to announce **Aditi** - a CLI tool designed to make AsciiDoc to DITA migration straightforward and reliable.

## The Problem

Technical writers love AsciiDoc's simplicity and power, but when it comes time to migrate to DITA for enterprise publishing workflows, the transition can be daunting. DITA has strict structural requirements that don't always align with AsciiDoc's flexible authoring approach.

Common challenges include:
- **Incompatible markup patterns** that work in AsciiDoc but break in DITA
- **Structural issues** like nested sections or improper example placement
- **Character entities** that aren't supported in DITA 1.3
- **Missing metadata** required for proper DITA topic categorization

Manual migration is time-consuming and error-prone. Automated tools often miss edge cases or provide unclear guidance about what needs to be fixed.

## The Solution

> **Aditi** (Sanskrit: आदिति, "boundless") - because your documentation migration shouldn't be constrained by technical barriers.

Aditi leverages the powerful Vale linter with comprehensive AsciiDocDITA rules to analyze your content and categorize issues by how they can be resolved:

### 🔴 Fully Deterministic (Auto-fixable)
- **Character entities**: Automatically converts `&nbsp;` to `{nbsp}`, `&copy;` to `©`, etc.

### 🟡 Partially Deterministic (Smart placeholders)  
- **Content types**: Adds missing `:_mod-docs-content-type:` attributes with `TBD` placeholders for manual completion

### 🔵 Non-Deterministic (Guided manual review)
- **Structural issues**: Identifies nested sections, improper example placement, and other patterns that need manual restructuring
- **Content patterns**: Flags admonition titles, discrete headings, and other elements requiring author decision

### Key Implementation Details

Aditi uses a containerized approach with the official Vale Docker image, ensuring consistent results across development environments:

```bash
# Get started in under 5 minutes
pip install aditi
cd your-asciidoc-project
aditi init

# Configure which directories to analyze
aditi journey

# See what needs attention
aditi check --verbose

# Fix the obvious problems automatically  
aditi fix --rule EntityReference
aditi fix --rule ContentType

# Review what's left  
aditi check
```

Technical features include:
- **Container isolation** for reproducible Vale execution
- **Resource limits** (512MB RAM, 2 CPUs) prevent runaway processes
- **Thread-safe processing** with intelligent file caching
- **Signal handling** for graceful interruption during long operations
- **Comprehensive error messages** with actionable guidance

## Results and Impact

During development, we tested Aditi on comprehensive example files containing all 27 rule types. Here's what we found:

- **53 total issues** identified across 6 test files
- **3 issues (6%)** automatically fixed with zero manual intervention  
- **Clear categorization** of remaining issues by complexity and urgency
- **Processing time**: Under 3 seconds for analysis, 2 seconds for applying fixes

The tool consistently identifies structural issues that would cause DITA conversion failures, while automatically handling tedious character entity replacements.

### Production Ready Features

- **Performance optimized** with parallel processing and container resource limits
- **Robust error handling** with graceful interruption support (Ctrl+C works properly!)
- **Clear error messages** that tell you exactly how to fix configuration issues
- **Comprehensive test coverage** with 40+ passing tests across all functionality

## Lessons Learned

Building Aditi taught us several important lessons:

1. **Automation should be surgical**: Rather than trying to fix everything automatically, focus on reliably fixing obvious issues while clearly flagging complex problems
2. **Error messages matter**: Spending time on clear, actionable error messages dramatically improves user experience
3. **Performance is critical**: Technical writers often work with large document sets - optimization from day one prevents scaling problems
4. **Real-world testing is essential**: Synthetic test cases miss edge cases that appear in actual documentation projects

## Next Steps

Aditi 1.0 focuses on analysis and basic auto-fixing. Future enhancements include:

- **Non-interactive mode** for CI/CD pipelines  
- **Direct DITA output generation** for complete migration workflows
- **Custom rule configuration** for organization-specific requirements
- **Integration** with popular documentation platforms
- **Batch processing optimizations** for large repositories

## Conclusion

AsciiDoc to DITA migration doesn't have to be a painful manual process. With Aditi, technical writers can approach migration projects with confidence, knowing that compatibility issues will be caught early and obvious fixes will be handled automatically.

The tool is production-ready today and available via PyPI. Whether you're evaluating a potential migration or actively working through hundreds of files, Aditi provides the automation and guidance you need to succeed.

---

### Resources

- **[Quick Start Guide](/aditi/docs/QUICKSTART.md)**: Get up and running in 5 minutes
- **[GitHub Repository](https://github.com/rolfedh/aditi)**: Source code and issue tracking
- **[Example Files](/aditi/docs/examples/)**: Sample AsciiDoc demonstrating each rule
- **[PyPI Package](https://pypi.org/project/aditi/)**: Installation and version history
- **[Documentation Site](/aditi/)**: Complete reference documentation

### Getting Started

Ready to simplify your AsciiDoc to DITA migration? 

```bash
pip install aditi
```

Have feedback or questions? We'd love to hear about your migration experience! Share your thoughts via our [feedback template](https://github.com/rolfedh/aditi/issues/new?template=user_feedback.yml) or start a [discussion](https://github.com/rolfedh/aditi/discussions).

### About the Author

Rolfe Dlugy-Hegwer is a technical writer and developer focused on documentation tooling and automation. When not building tools for technical writers, he can be found contributing to open source projects and sharing knowledge about modern documentation workflows.