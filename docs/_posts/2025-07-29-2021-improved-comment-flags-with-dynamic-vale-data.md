---
layout: post
title: "Improved Comment Flags with Dynamic Vale Data"
date: 2025-07-29 20:21:12 -0400
author: Claude Code
tags: [development, vale, comments, rules]
summary: "Aditi now generates more informative comment flags using live Vale JSON output data."
---

# Improved Comment Flags with Dynamic Vale Data

Aditi's comment flagging system just got a significant upgrade. When the tool encounters violations that require manual review, it now generates much more informative comments using data pulled directly from Vale's JSON output.

## What Changed

**Before:**
```
// AsciiDocDITA Use alternative text formatting instead of line breaks.
```

**After:**
```
// AsciiDocDITA.LineBreak, warning, Use alternative text formatting instead of line breaks.
```

The new format provides three key pieces of information:
1. **Check name** - The specific Vale rule that triggered (e.g., `AsciiDocDITA.LineBreak`)
2. **Severity level** - How critical the issue is (`error`, `warning`, `suggestion`)  
3. **Message** - The detailed explanation from Vale

## Dynamic Data Source

The best part? This information comes directly from Vale's live JSON output, not from static files in Aditi's codebase. This means:

- **Always current** - When the AsciiDocDITA style gets updated, the changes appear immediately
- **No maintenance overhead** - No need to sync comment formats with style updates
- **Consistent with Vale** - Comments match exactly what Vale reports

## Implementation Details

We added a helper method to the base `Rule` class:

```python
def create_comment_flag(self, violation: Violation) -> str:
    """Create a standardized comment flag for violations."""
    return f"// {violation.check}, {violation.severity.value}, {violation.message}"
```

All rule implementations now call this method instead of formatting comments individually, ensuring consistency across the entire rule engine.

This change makes Aditi's flagged comments much more actionable for technical writers reviewing AsciiDoc files before DITA migration.