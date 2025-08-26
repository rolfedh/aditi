---
layout: post
title: "Fixing Suggestion-Level Rule Behavior - No More Unwanted Comments"
date: 2025-08-25 22:02:23 -0400
author: Rolfe DH
tags: [bug-fix, rules, workflow, user-experience]
summary: "Fixed issue where suggestion-level informational rules were incorrectly adding comment flags to files, keeping source documents clean."
---

## Keeping Your Files Clean: A Critical Bug Fix

We've just resolved a significant issue that was affecting the core user experience of Aditi. Thanks to community feedback from [GitHub issue #26](https://github.com/rolfedh/aditi/issues/26), we identified and fixed a problem where suggestion-level rules were inappropriately modifying source files.

## The Problem

Previously, when running `aditi fix` or `aditi journey`, certain suggestion-level rules were adding comment flags to AsciiDoc files, even though they were meant to be informational only. This was particularly problematic for rules like:

- **AttributeReference** - Lists attribute references for informational purposes
- **ConditionalCode** - Identifies conditional statements that may need attention  
- **IncludeDirective** - Lists include directives that may need attention
- **TagDirective** - Identifies tag directives that may need attention

For example, a perfectly legitimate include statement like:
```asciidoc
include::file.adoc[leveloffset=+1]
```

Would get flagged with an unwanted comment:
```asciidoc
// AsciiDocDITA.IncludeDirective, suggestion, include::file.adoc[leveloffset=+1]
include::file.adoc[leveloffset=+1]
```

This created unnecessary diff noise and cluttered files with redundant information that writers didn't need.

## The Root Cause

The issue stemmed from how our rule processing system handled different severity levels. While the AsciiDocDITA Vale styles correctly categorize these as "suggestion" level rules, our workflow was still processing them as actionable violations that required flagging.

According to the [AsciiDocDITA documentation](https://github.com/jhradilek/asciidoctor-dita-vale?tab=readme-ov-file#suggestions), suggestion-level rules are:
> convenience rules only and do not report actionable problems with the AsciiDoc markup. They are not intended for use by writers.

Our implementation wasn't respecting this distinction.

## The Solution

We implemented a targeted fix that addresses the issue at multiple levels:

### 1. Journey Workflow Enhancement

The `aditi journey` command now explicitly skips these four informational rules during processing:

```python
# Skip informational suggestion-level rules per GitHub issue #26
if rule_name in ["AttributeReference", "ConditionalCode", "IncludeDirective", "TagDirective"]:
    console.print(f"[dim]Skipping informational rule {rule_name} (suggestion-level only)[/dim]")
    # Mark as applied so it doesn't get processed again
    session.applied_rules.append(rule_name)
    config_manager.save_session(session)
    continue
```

### 2. Fix Command Protection

The `aditi fix` command now filters out violations from these rules before processing:

```python
# Skip informational suggestion-level rules per GitHub issue #26
informational_rules = {"AttributeReference", "ConditionalCode", "IncludeDirective", "TagDirective"}

for violation in violations:
    # Skip informational rules entirely
    if violation.rule_name in informational_rules:
        continue
    # ... continue with other processing
```

### 3. Workflow Continuity

The fix maintains proper session tracking so that skipped rules are marked as "applied" in the journey workflow, preventing them from being processed again in future sessions.

## Impact on User Experience

This change significantly improves the user experience by:

### Clean Diffs
No more cluttered diffs with unnecessary informational comments. Your git commits will show only the meaningful changes you've made.

### Focused Feedback  
Writers now see only actionable violations that require attention, reducing cognitive overhead and improving productivity.

### Legitimate Content Preservation
Include statements, conditional directives, and other legitimate AsciiDoc constructs remain untouched, as they should be.

### Faster Processing
Skipping these rules reduces processing time and eliminates unnecessary file modifications.

## Backward Compatibility

This change is fully backward compatible:
- Existing sessions will continue to work normally
- Previously flagged files won't be affected (the comments are just ignored going forward)
- All other rule processing remains unchanged

## Technical Implementation

The implementation is surgical and targeted:
- **2 files changed**: Only the journey and fix commands were modified
- **15 insertions**: Minimal code additions for maximum impact
- **Zero breaking changes**: All existing functionality preserved
- **Complete test coverage**: All tests continue to pass

## What's Next?

This fix represents our commitment to respecting the original intent of the AsciiDocDITA Vale styles and providing a clean, writer-focused experience. 

Going forward, we're considering additional enhancements:
- Configurable rule severity handling for advanced users
- Better distinction between informational and actionable feedback
- Enhanced reporting that separates convenience information from required fixes

## Community Impact

This fix was driven entirely by community feedback, demonstrating the value of user input in improving Aditi. Special thanks to the contributor who identified this issue and provided clear reproduction steps.

If you encounter similar issues or have suggestions for improvements, please [file an issue](https://github.com/rolfedh/aditi/issues) on our GitHub repository.

## Try It Out

Update to the latest version of Aditi to get this fix:

```bash
# Update Aditi
pip install --upgrade aditi

# Run your journey workflow - cleaner than ever
aditi journey
```

Your AsciiDoc files will stay clean and focused on the changes that matter, while still benefiting from all the valuable DITA compatibility checking that Aditi provides.