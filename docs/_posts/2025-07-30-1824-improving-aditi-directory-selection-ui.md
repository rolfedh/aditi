---
layout: post
title: "Improving Aditi's Directory Selection UI: From Developer Jargon to User Clarity"
date: 2025-07-30 18:24:00 -0400
author: Aditi Development Team
tags: [ui, usability, development]
summary: "How we transformed Aditi's confusing directory selection into an intuitive experience for technical writers"
---

When building developer tools, it's easy to fall into the trap of using technical jargon that makes perfect sense to us but confuses our users. Today, we're addressing exactly that issue in Aditi's directory selection interface.

## The Problem

A user opened [issue #11](https://github.com/rolfedh/aditi/issues/11) pointing out that our directory selection prompts were confusing:

- "How would you like to specify directories to scan?" - Too technical
- "Use all auto-detected paths" - What does "auto-detected" mean?
- Custom path entry was frustrating - users couldn't get valid paths accepted

## Real-World Testing

We tested against two real documentation repositories:
- **OpenShift docs**: 10,529 .adoc files across 50+ directories
- **Quarkus**: 371 files, mostly in `docs/`

The scale difference revealed critical issues with our original approach.

## The Solution

### 1. Simplified Language

**Before:**
```
? How would you like to specify directories to scan?
  » Use all auto-detected paths
    Review and customize auto-detected paths
    Enter custom directory paths
```

**After:**
```
? Which directories do you want to work on?
  » Process all directories with .adoc files
    Let me choose specific directories
    Enter custom directory paths
```

### 2. Smart Directory Sorting

Instead of random order, directories are now sorted by file count:
```
🎯 Found documentation to process: 10,843 total files

Select directories (Space to toggle, Enter to continue):
    ✓ modules/ (7,615 files)
    ✓ docs/ (337 files)
    ✓ rest_api/ (306 files)
    ✓ snippets/ (187 files)
```

Users immediately see which directories have the most impact.

### 3. Better Defaults

All directories are now pre-selected by default. It's easier to deselect unwanted directories than to select wanted ones. This matches user expectations: "I want to process my documentation."

### 4. Custom Path Entry Improvements

The custom path entry now:
- Shows available directories upfront
- Provides clear examples
- Accepts multiple formats (`docs`, `./docs`, `/docs`, `docs/`)
- Offers autocomplete suggestions
- Gives helpful error messages

**Example:**
```
📁 Enter Custom Directory Paths

Available directories:
  • modules/ (7,615 .adoc files)
  • docs/ (337 .adoc files)
  • networking/ (151 .adoc files)

Examples:
  • docs
  • modules/api
  • src/main/asciidoc

Directory path: networ
  ✗ Directory not found: networ
    Did you mean one of these?
      • networking
```

## Performance Benefits

Directory filtering isn't just about UI - it's a massive performance optimization:
- Full OpenShift repo: ~25-30 minutes to process
- Just `docs/` directory: ~2-3 minutes
- Filtering saves up to 96% processing time

## Key Takeaways

1. **Use plain language** - Replace jargon with words users understand
2. **Show impact** - File counts help users make informed decisions
3. **Smart defaults** - Pre-select sensible options
4. **Forgive mistakes** - Accept multiple input formats, suggest corrections
5. **Progressive disclosure** - Show complexity only when needed

## Try It Out

Update to the latest version and experience the improved UI:
```bash
aditi journey
```

The new interface makes it clear what Aditi will do and gives you full control over which directories to process.

---

These changes are live in the latest version. We're committed to making Aditi as intuitive as possible for technical writers preparing their documentation for DITA migration.