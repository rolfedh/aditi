---
layout: page
title: "Known Issues"
permalink: /known-issues/
---

# Known Issues

## EntityReference Rule Flags Entities in Code Blocks

**Status**: Reported upstream ([Issue #98](https://github.com/jhradilek/asciidoctor-dita-vale/issues/98))

### Description

The AsciiDocDITA EntityReference rule incorrectly flags HTML entity references that appear inside:
- Code blocks (delimited by `----`)
- Source blocks (with `[source,language]` attributes)
- Inline code (wrapped in backticks)

### Example

```asciidoc
----
String text = "Hello&nbsp;World";  // This is incorrectly flagged
----

And inline code: `&nbsp;` is also incorrectly flagged.
```

### Workaround

Until this is fixed upstream:

1. **Ignore these false positives** - The entities in code blocks won't actually be converted during DITA migration, so these warnings can be safely ignored. Focus on fixing entities in regular text content.

2. **BlockIgnores Configuration** - We've added BlockIgnores patterns to the Vale configuration, but they may not fully work with the current Vale/AsciiDoc integration. The configuration is included for future compatibility:

```ini
[*.adoc]
BlockIgnores = \
  (?s)^----\n.*?\n----$, \
  (?s)^\[source.*?\]\n----\n.*?\n----$, \
  `[^`]+`
```

**Note**: The BlockIgnores feature may have limited effect with AsciiDoc files in the current Vale version. The upstream fix to the EntityReference rule itself is the preferred solution.

### Impact

This issue only affects the reporting accuracy. The actual DITA conversion process will correctly preserve entity references in code blocks.