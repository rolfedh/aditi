---
layout: post
title: "Running Aditi Journey on Specific Files: Three Powerful Options"
date: 2025-09-02 16:32:16 -0400
author: Aditi Team
tags: [tips, workflow, journey]
summary: "Learn three different ways to run aditi journey on specific files for targeted DITA preparation"
---

When working with large documentation repositories, you often need to fix issues in specific files rather than processing an entire directory. The `aditi journey` command supports multiple ways to target specific files, giving you flexibility in your workflow.

## The Challenge

Imagine you've identified a set of files with `TaskStep` violations that need fixing:

```
TaskStep: DITA task steps should contain simple instructions.

These files have this issue:
  • modules/network-observability-filtering-ebpf-rule.adoc
  • modules/network-observability-enriched-flows.adoc
  • modules/network-observability-working-with-topology.adoc
  • modules/network-observability-flowmetrics-charts.adoc
  • modules/network-observability-dns-tracking.adoc
  • modules/network-observability-flowcollector-kafka-config.adoc
  • modules/network-observability-packet-translation.adoc
  • modules/network-observability-viewing-dashboards.adoc
  • modules/network-observability-working-with-overview.adoc
  • modules/network-observability-working-with-trafficflow.adoc
```

Instead of processing your entire `modules/` directory, you want to focus just on these files. Here are three ways to do it.

## Option 1: Direct File Listing

The most straightforward approach is to list all files directly on the command line:

```bash
aditi journey \
  modules/network-observability-filtering-ebpf-rule.adoc \
  modules/network-observability-enriched-flows.adoc \
  modules/network-observability-working-with-topology.adoc \
  modules/network-observability-flowmetrics-charts.adoc \
  modules/network-observability-dns-tracking.adoc \
  modules/network-observability-flowcollector-kafka-config.adoc \
  modules/network-observability-packet-translation.adoc \
  modules/network-observability-viewing-dashboards.adoc \
  modules/network-observability-working-with-overview.adoc \
  modules/network-observability-working-with-trafficflow.adoc
```

**Pros:**
- Explicit and clear about which files are being processed
- Works on all shells and platforms
- Easy to modify by adding or removing specific files

**Cons:**
- Can be verbose for many files
- Requires typing or copying each filename

**Tip:** Use backslashes (`\`) for line continuation to make the command more readable.

## Option 2: Shell Brace Expansion

When your files share a common prefix, you can use shell brace expansion for a more compact command:

```bash
aditi journey modules/network-observability-{filtering-ebpf-rule,enriched-flows,working-with-topology,flowmetrics-charts,dns-tracking,flowcollector-kafka-config,packet-translation,viewing-dashboards,working-with-overview,working-with-trafficflow}.adoc
```

Or with line breaks for readability:

```bash
aditi journey modules/network-observability-{filtering-ebpf-rule,\
enriched-flows,\
working-with-topology,\
flowmetrics-charts,\
dns-tracking,\
flowcollector-kafka-config,\
packet-translation,\
viewing-dashboards,\
working-with-overview,\
working-with-trafficflow}.adoc
```

**Pros:**
- More compact than listing full paths
- Reduces repetition of common path components
- Still explicit about which files are included

**Cons:**
- Requires bash or zsh (doesn't work in all shells)
- Can be hard to read with many items
- All files must share the same prefix and suffix

**Tip:** This works great when your files follow a naming convention!

## Option 3: File List with xargs

For maximum flexibility, maintain a list of files in a text file and use `xargs`:

First, create your file list:

```bash
cat > taskstep-files.txt << EOF
modules/network-observability-filtering-ebpf-rule.adoc
modules/network-observability-enriched-flows.adoc
modules/network-observability-working-with-topology.adoc
modules/network-observability-flowmetrics-charts.adoc
modules/network-observability-dns-tracking.adoc
modules/network-observability-flowcollector-kafka-config.adoc
modules/network-observability-packet-translation.adoc
modules/network-observability-viewing-dashboards.adoc
modules/network-observability-working-with-overview.adoc
modules/network-observability-working-with-trafficflow.adoc
EOF
```

Then run the journey:

```bash
xargs aditi journey < taskstep-files.txt
```

**Pros:**
- File list is reusable and version-controllable
- Easy to maintain and update
- Can generate file lists programmatically
- Works well with other Unix tools

**Cons:**
- Requires creating an additional file
- Less immediate than direct command-line options

**Tip:** You can generate file lists from Vale output or other tools:

```bash
# Example: Find all files with a specific violation
aditi check --rule TaskStep | grep "^  •" | cut -d' ' -f4 > taskstep-files.txt
```

## Practical Workflow Tips

### Using Wildcards

For files matching a pattern, you can also use shell wildcards:

```bash
# Process all network-observability files
aditi journey modules/network-observability-*.adoc

# Process specific patterns
aditi journey modules/network-observability-working-with-*.adoc
```

### Skipping to Specific Rules

When targeting specific files for a known issue, you'll often want to skip to the relevant rule. Just press `s` (skip) for rules you don't need:

```bash
aditi journey modules/my-files-*.adoc
# Press 's' to skip ContentType if already handled
# Press 's' to skip EntityReference if not relevant
# Press 'A' when you reach the rule you want to fix
```

### Combining with Git

Track your progress by creating targeted commits:

```bash
# Fix EntityReference issues in specific files
aditi journey modules/api-*.adoc
git add modules/api-*.adoc
git commit -m "fix: Resolve EntityReference violations in API modules"

# Fix TaskStep issues in another set
xargs aditi journey < taskstep-files.txt
git add -p  # Review changes
git commit -m "fix: Simplify task steps for DITA compliance"
```

## Which Option Should You Use?

- **Use Option 1 (direct listing)** when you have a small, specific set of files that don't follow a pattern
- **Use Option 2 (brace expansion)** when files share a common naming pattern
- **Use Option 3 (xargs with file list)** when:
  - You have many files to process
  - You want to reuse the same file list multiple times
  - You're generating the file list from another tool
  - You want to track which files need processing in version control

## Conclusion

The `aditi journey` command's flexibility in accepting file arguments makes it powerful for targeted DITA preparation work. Whether you're fixing issues reported in a ticket, working through a specific rule across multiple files, or focusing on a particular documentation module, these options give you the control you need for an efficient workflow.

Remember: the journey tracks your progress, so you can always interrupt and resume later with the same command. This makes it perfect for working through large sets of files incrementally.

Happy documenting! 🚀